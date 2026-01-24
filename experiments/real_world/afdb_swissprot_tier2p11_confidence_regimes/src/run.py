from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import os
from typing import Dict, Optional

import numpy as np
import pandas as pd
import yaml

from .config import load_prereg
from .utils_hash import stable_hash_order, sha256_hex
from .universe import scan_accessions, is_fragment_name
from .io_coords import load_plddt_from_coords
from .io_pae import load_pae_offdiag_median
from .io_msa import msa_depth_a3m
from .metrics_plddt import frac_ge, frac_lt, mean, hist4_entropy
from .binning import make_length_bins, assign_bins, aggregate_by_bin
from .norm import robust_scale_0_1, geometric_mean
from .change_points import detect_event_E_regime
from .gates_est import event_alignment_gate
from .plot_onepager import plot_onepage

def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def _write_json(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def _safe_to_parquet(df: pd.DataFrame, path: Path) -> None:
    try:
        df.to_parquet(path, index=False)
    except Exception:
        df.to_csv(path.with_suffix(".csv"), index=False)

def _coords_file_for_accession(coords_dir: Path, acc: str) -> Optional[Path]:
    # Prefer .cif; else .pdb.
    cand = list(coords_dir.glob(f"AF-{acc}-*.cif"))
    if cand:
        return cand[0]
    cand = list(coords_dir.glob(f"AF-{acc}-*.pdb"))
    if cand:
        return cand[0]
    return None

def _boundary_mode_resolve(cfg: dict) -> tuple[str, bool, bool]:
    mode = cfg["boundary"]["boundary_mode"]
    if mode == "B0_COORD_ONLY":
        return mode, False, False
    if mode == "B1_COORD_PLUS_PAE":
        return mode, True, False
    if mode == "B2_COORD_PLUS_PAE_PLUS_MSA":
        return mode, True, True
    raise ValueError(f"Unknown boundary_mode: {mode}")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--run_id", default=None)
    args = ap.parse_args()

    cfg = load_prereg(args.prereg).raw

    # Resolve case directory (.../case/src/run.py -> .../case)
    case_dir = Path(__file__).resolve().parents[1]

    coords_dir = case_dir / cfg["boundary"]["paths"]["coords_dir"]
    pae_dir = case_dir / cfg["boundary"]["paths"]["pae_dir"]
    msa_dir = case_dir / cfg["boundary"]["paths"]["msa_dir"]

    boundary_mode, pae_available, msa_available = _boundary_mode_resolve(cfg)

    # Create run dir
    out_root = case_dir / cfg["outputs"]["out_root"]
    out_root.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Lock prereg (copy)
    locked_prereg_path = run_dir / "EST_PREREG.locked.yaml"
    _write_text(locked_prereg_path, Path(args.prereg).read_text(encoding="utf-8"))
    prereg_hash = sha256_hex(locked_prereg_path.read_text(encoding="utf-8"))

    # Universe and deterministic sampling
    universe = scan_accessions(coords_dir)
    seed = cfg["boundary"]["selection"]["sampler"]["seed_string"]
    ordered = stable_hash_order(universe, seed_string=seed)

    target_n = int(cfg["boundary"]["selection"]["sampler"]["target_n_valid"])
    max_draw = int(cfg["boundary"]["selection"]["sampler"]["max_draw_multiplier"]) * target_n

    min_len = int(cfg["boundary"]["selection"]["filters"]["min_length"])
    max_len = int(cfg["boundary"]["selection"]["filters"]["max_length"])
    exclude_frag = bool(cfg["boundary"]["selection"]["filters"]["exclude_fragments_by_name"])

    rows = []
    selected_acc = []
    missing = {"coords": 0, "pae": 0, "msa": 0}
    drawn = 0

    for acc in ordered:
        if len(selected_acc) >= target_n:
            break
        if drawn >= max_draw:
            break
        drawn += 1

        fcoords = _coords_file_for_accession(coords_dir, acc)
        if fcoords is None:
            missing["coords"] += 1
            continue
        if exclude_frag and is_fragment_name(fcoords.name):
            continue

        try:
            plddt, L = load_plddt_from_coords(fcoords)
        except Exception:
            continue

        if L < min_len or L > max_len:
            continue

        pae_off = np.nan
        if pae_available:
            fpae = pae_dir / f"{acc}.json"
            if fpae.exists():
                try:
                    pae_off = load_pae_offdiag_median(fpae, band_k=32)
                except Exception:
                    pae_off = np.nan
            else:
                missing["pae"] += 1

        msa_depth = np.nan
        if msa_available:
            fmsa = msa_dir / f"{acc}.a3m"
            if fmsa.exists():
                try:
                    msa_depth = float(msa_depth_a3m(fmsa))
                except Exception:
                    msa_depth = np.nan
            else:
                missing["msa"] += 1

        rec = {
            "accession": acc,
            "length": int(L),
            "I1_hi_conf_frac": frac_ge(plddt, 70.0),
            "I2_mean_plddt": mean(plddt),
            "I3_plddt_entropy": hist4_entropy(plddt),
            "C1_low_conf_frac": frac_lt(plddt, 50.0),
            "C2_pae_offdiag": float(pae_off) if np.isfinite(pae_off) else np.nan,
            "msa_depth": float(msa_depth) if np.isfinite(msa_depth) else np.nan,
            "C3_msa_deficit": float(-np.log1p(msa_depth)) if np.isfinite(msa_depth) else np.nan,
            "F2_low_msa_pressure": float(-np.log1p(msa_depth)) if np.isfinite(msa_depth) else np.nan,
            "coords_file": fcoords.name,
        }
        rows.append(rec)
        selected_acc.append(acc)

    # Accession list + hash
    accessions_txt = run_dir / "accessions_selected.txt"
    _write_text(accessions_txt, "\n".join(selected_acc) + "\n")
    _write_text(run_dir / "accessions_selected.sha256", sha256_hex(accessions_txt.read_text(encoding="utf-8")) + "\n")

    df = pd.DataFrame(rows)
    _safe_to_parquet(df, run_dir / "metrics_per_protein.parquet")

    # Binning & aggregation
    bin_width = int(cfg["axis"]["bin_width_aa"])
    bins = make_length_bins(min_len=min_len, max_len=max_len, bin_width=bin_width)
    df["bin_id"] = assign_bins(df["length"].to_numpy(), bins)

    metrics_cols = ["I1_hi_conf_frac", "I2_mean_plddt", "I3_plddt_entropy", "C1_low_conf_frac"]
    if pae_available:
        metrics_cols.append("C2_pae_offdiag")
    if msa_available:
        metrics_cols.append("C3_msa_deficit")

    df_bin = aggregate_by_bin(df, "bin_id", metrics_cols, min_items_per_bin=int(cfg["axis"]["min_items_per_bin"]))
    df_bin["len_bin_mid"] = min_len + (df_bin["bin_id"] + 0.5) * bin_width

    # Normalize optional C estimators
    if "C2_pae_offdiag" in df_bin.columns:
        df_bin["C2_pae_offdiag_norm"] = robust_scale_0_1(df_bin["C2_pae_offdiag"].to_numpy(), 0.05, 0.95)
    if "C3_msa_deficit" in df_bin.columns:
        df_bin["C3_msa_deficit_norm"] = robust_scale_0_1(df_bin["C3_msa_deficit"].to_numpy(), 0.05, 0.95)

    # Compute C_primary per boundary
    eps = float(cfg["estimators"]["composites"]["epsilon"])
    if boundary_mode == "B0_COORD_ONLY":
        C_primary = df_bin["C1_low_conf_frac"].to_numpy(dtype=float)
    elif boundary_mode == "B1_COORD_PLUS_PAE":
        C_primary = geometric_mean([
            df_bin["C1_low_conf_frac"].to_numpy(dtype=float) + eps,
            df_bin["C2_pae_offdiag_norm"].to_numpy(dtype=float) + eps,
        ], eps=eps)
    else:
        C_primary = geometric_mean([
            df_bin["C1_low_conf_frac"].to_numpy(dtype=float) + eps,
            df_bin["C2_pae_offdiag_norm"].to_numpy(dtype=float) + eps,
            df_bin["C3_msa_deficit_norm"].to_numpy(dtype=float) + eps,
        ], eps=eps)

    df_bin["C_primary"] = C_primary
    I_primary = df_bin["I1_hi_conf_frac"].to_numpy(dtype=float)
    df_bin["R_primary"] = (I_primary + eps) / (C_primary + eps)

    _safe_to_parquet(df_bin, run_dir / "metrics_per_bin.parquet")

    # Primary event detection
    ev = detect_event_E_regime(df_bin, cfg)

    # Coherence gate: detect event under alternative estimators if available
    event_bins: Dict[str, Optional[int]] = {"C_primary": ev.event_bin}

    # C1-only
    df_tmp = df_bin.copy()
    df_tmp["C_primary"] = df_tmp["C1_low_conf_frac"].to_numpy(dtype=float)
    df_tmp["R_primary"] = (df_tmp["I1_hi_conf_frac"].to_numpy(dtype=float) + eps) / (df_tmp["C_primary"].to_numpy(dtype=float) + eps)
    event_bins["C1_low_conf_frac"] = detect_event_E_regime(df_tmp, cfg).event_bin

    # C2-only
    if pae_available and "C2_pae_offdiag_norm" in df_bin.columns:
        df_tmp2 = df_bin.copy()
        df_tmp2["C_primary"] = df_tmp2["C2_pae_offdiag_norm"].to_numpy(dtype=float)
        df_tmp2["R_primary"] = (df_tmp2["I1_hi_conf_frac"].to_numpy(dtype=float) + eps) / (df_tmp2["C_primary"].to_numpy(dtype=float) + eps)
        event_bins["C2_pae_offdiag"] = detect_event_E_regime(df_tmp2, cfg).event_bin

    # C3-only
    if msa_available and "C3_msa_deficit_norm" in df_bin.columns:
        df_tmp3 = df_bin.copy()
        df_tmp3["C_primary"] = df_tmp3["C3_msa_deficit_norm"].to_numpy(dtype=float)
        df_tmp3["R_primary"] = (df_tmp3["I1_hi_conf_frac"].to_numpy(dtype=float) + eps) / (df_tmp3["C_primary"].to_numpy(dtype=float) + eps)
        event_bins["C3_msa_deficit"] = detect_event_E_regime(df_tmp3, cfg).event_bin

    gate = event_alignment_gate(event_bins, tolerance_bins=int(cfg["coherence_gate"]["tolerance_bins"]), fail_label=cfg["coherence_gate"]["fail_label"])

    # Regime report
    lines = []
    lines.append("# Regime report - afdb_swissprot_tier2p11_confidence_regimes\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- boundary_mode: `{boundary_mode}`\n")
    lines.append(f"- afdb_release_version: `{cfg['boundary']['afdb_release_version']}`\n")
    lines.append(f"- selected_n: `{len(selected_acc)}` (target {target_n}; drawn {drawn}; max_draw {max_draw})\n")
    lines.append(f"- prereg_sha256: `{prereg_hash}`\n\n")

    lines.append("## Coherence gate\n\n")
    lines.append(f"- status: **{gate.status}**\n")
    for k, v in gate.details.items():
        lines.append(f"- {k}: `{v}`\n")
    lines.append("\n")

    lines.append("## Primary event detection (E_regime)\n\n")
    lines.append(f"- event_found: **{str(ev.event_found).lower()}**\n")
    lines.append(f"- event_bin: `{ev.event_bin}`\n")
    lines.append(f"- reason: `{ev.reason}`\n\n")

    lines.append("## Event bins by estimator (audit)\n\n")
    for k, v in event_bins.items():
        lines.append(f"- {k}: `{v}`\n")
    lines.append("\n")

    lines.append("## Interpretation rule\n\n")
    if gate.status == cfg['coherence_gate']['fail_label']:
        lines.append(f"- Label: **{cfg['coherence_gate']['fail_label']}** -> do not interpret event location.\n")
    else:
        lines.append("- If coherent: treat change points as signatures under the preregistered estimator tuple.\n")

    _write_text(run_dir / "regime_report.md", "".join(lines))

    # One-page plot
    plot_onepage(df_bin=df_bin, run_dir=run_dir, cfg=cfg, event_bin=ev.event_bin if ev.event_found else None)

    # Boundary snapshot + manifest
    boundary_snapshot = {
        "case_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "boundary_mode": boundary_mode,
        "afdb_release_version": cfg["boundary"]["afdb_release_version"],
        "dataset_scope": cfg["boundary"]["dataset_scope"],
        "paths": {"coords_dir": str(coords_dir), "pae_dir": str(pae_dir), "msa_dir": str(msa_dir)},
        "artifact_availability": {"pae_available": pae_available, "msa_available": msa_available},
        "filters": {"min_length": min_len, "max_length": max_len, "exclude_fragments_by_name": exclude_frag},
        "selection": {
            "seed_string": seed,
            "target_n_valid": target_n,
            "max_draw": max_draw,
            "universe_size": len(universe),
            "selected_n": len(selected_acc),
            "missing_counts": missing,
        },
        "hashes": {
            "prereg_sha256": prereg_hash,
            "accessions_sha256": (run_dir / "accessions_selected.sha256").read_text(encoding="utf-8").strip(),
        },
    }
    _write_json(run_dir / "boundary_snapshot.json", boundary_snapshot)

    run_manifest = {
        "case_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git_commit": os.environ.get("GIT_COMMIT", "UNKNOWN"),
        "prereg_sha256": prereg_hash,
        "artifacts": {
            "metrics_per_protein": str((run_dir / "metrics_per_protein.parquet").resolve()),
            "metrics_per_bin": str((run_dir / "metrics_per_bin.parquet").resolve()),
            "regime_report": str((run_dir / "regime_report.md").resolve()),
            "tradeoff_onepage": str((run_dir / "tradeoff_onepage.pdf").resolve()),
            "boundary_snapshot": str((run_dir / "boundary_snapshot.json").resolve()),
            "accessions_selected": str((run_dir / "accessions_selected.txt").resolve()),
        },
    }
    _write_json(run_dir / "run_manifest.json", run_manifest)

    print(f"Run complete. Outputs in: {run_dir}")

if __name__ == "__main__":
    main()
