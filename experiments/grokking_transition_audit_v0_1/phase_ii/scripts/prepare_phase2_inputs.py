from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

import yaml


def _as_seed_int(seed_name: str) -> int:
    if seed_name.startswith("seed_"):
        return int(seed_name.split("_", 1)[1])
    return int(seed_name)


def _load_prereg(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_diagnostics(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _select_groups(
    rows: list[dict[str, str]],
    control_sample_size: int,
    rng_seed: int,
    include_unstable: bool,
) -> dict[str, list[int]]:
    reg = sorted(_as_seed_int(r["seed"]) for r in rows if r["label"] == "REGISTERED_TRANSITION")
    no = sorted(_as_seed_int(r["seed"]) for r in rows if r["label"] == "NO_TRANSITION")
    unstable = sorted(_as_seed_int(r["seed"]) for r in rows if r["label"] == "ESTIMATOR_UNSTABLE")

    rng = random.Random(rng_seed)
    if len(no) <= control_sample_size:
        no_sel = no
    else:
        no_sel = sorted(rng.sample(no, control_sample_size))

    groups = {
        "registered": reg,
        "no_transition_control": no_sel,
    }
    if include_unstable:
        groups["unstable_optional"] = unstable
    return groups


def _build_checkpoint_spec(
    base_spec: dict[str, Any],
    eval_seeds: list[int],
    checkpoint_every_steps: int | None,
    max_steps_override: int | None,
) -> dict[str, Any]:
    spec = dict(base_spec)
    spec["version"] = f"{base_spec.get('version', 'grokking_fit')}_phase2_checkpoints"

    spec.setdefault("seeds", {})
    spec["seeds"]["eval"] = eval_seeds

    spec.setdefault("time", {})
    spec["time"]["save_checkpoints"] = True
    if checkpoint_every_steps is not None:
        spec["time"]["checkpoint_every_steps"] = int(checkpoint_every_steps)

    if max_steps_override is not None:
        spec.setdefault("boundary", {}).setdefault("training", {})["max_steps"] = int(max_steps_override)

    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Phase-II inputs for grokking transition attractor test.")
    parser.add_argument("--prereg", required=True, help="Path to EST_PREREG.phase_ii.yaml")
    parser.add_argument("--rng-seed", type=int, default=20260223)
    args = parser.parse_args()

    prereg_path = Path(args.prereg).resolve()
    phase2_dir = prereg_path.parent
    prereg = _load_prereg(prereg_path)

    diagnostics_path = (phase2_dir / prereg["inputs"]["diagnostics_csv"]).resolve()
    rows = _read_diagnostics(diagnostics_path)

    groups_cfg = prereg["groups"]
    groups = _select_groups(
        rows=rows,
        control_sample_size=int(groups_cfg["control_sample_size"]),
        rng_seed=int(args.rng_seed),
        include_unstable=bool(groups_cfg.get("include_unstable_as_optional", False)),
    )

    selected = sorted(set(groups["registered"] + groups["no_transition_control"]))
    if "unstable_optional" in groups:
        selected = sorted(set(selected + groups["unstable_optional"]))

    upstream_cfg = prereg["upstream_grokking"]
    grokking_root = (phase2_dir / upstream_cfg["root"]).resolve()
    base_spec_path = (phase2_dir / upstream_cfg["base_spec"]).resolve()
    runs_out = (phase2_dir / upstream_cfg["checkpoint_runs_out"]).resolve()

    with base_spec_path.open("r", encoding="utf-8") as f:
        base_spec = yaml.safe_load(f)

    ckpt_spec = _build_checkpoint_spec(
        base_spec=base_spec,
        eval_seeds=selected,
        checkpoint_every_steps=upstream_cfg.get("checkpoint_every_steps_override"),
        max_steps_override=upstream_cfg.get("max_steps_override"),
    )

    results_dir = (phase2_dir / "results").resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    specs_dir = results_dir / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    main_out_dir = results_dir / "main"
    main_out_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_spec_path = specs_dir / "estimator_spec.phase2_checkpoints.yaml"
    with checkpoint_spec_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(ckpt_spec, f, sort_keys=False, allow_unicode=True)

    manifest = {
        "phase2_id": prereg["id"],
        "source_diagnostics": str(diagnostics_path),
        "groups": groups,
        "selected_seeds": selected,
        "selection_rng_seed": int(args.rng_seed),
        "upstream": {
            "grokking_root": str(grokking_root),
            "base_spec": str(base_spec_path),
            "checkpoint_spec": str(checkpoint_spec_path),
            "runs_out": str(runs_out),
            "phase": upstream_cfg.get("phase", "eval"),
        },
    }

    manifest_path = results_dir / "seed_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    run_ps1_path = results_dir / "run_phase2_gpu.ps1"
    run_ps1 = f"""$ErrorActionPreference = "Stop"
Set-Location "{grokking_root}"

python -m grokking.runner.sweep --spec "{checkpoint_spec_path}" --out "{runs_out}" --phase {upstream_cfg.get("phase", "eval")}

python "{(phase2_dir / "scripts" / "run_attractor_stability.py").resolve()}" `
  --prereg "{prereg_path}" `
  --manifest "{manifest_path}" `
  --runs-root "{runs_out}" `
  --grokking-root "{grokking_root}" `
  --diagnostics "{diagnostics_path}" `
  --out-dir "{main_out_dir}"
"""
    with run_ps1_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(run_ps1)

    run_pilot_ps1_path = results_dir / "run_phase2_gpu_pilot.ps1"
    run_pilot_ps1 = f"""$ErrorActionPreference = "Stop"
Set-Location "{grokking_root}"

# Pilot: first 4 eval seeds from the generated phase-II checkpoint spec.
python -m grokking.runner.sweep --spec "{checkpoint_spec_path}" --out "{runs_out}" --phase {upstream_cfg.get("phase", "eval")} --limit 4

python "{(phase2_dir / "scripts" / "run_attractor_stability.py").resolve()}" `
  --prereg "{prereg_path}" `
  --manifest "{manifest_path}" `
  --runs-root "{runs_out}" `
  --grokking-root "{grokking_root}" `
  --diagnostics "{diagnostics_path}" `
  --out-dir "{main_out_dir}"
"""
    with run_pilot_ps1_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(run_pilot_ps1)

    print("Prepared Phase-II inputs.")
    print(f"- Manifest: {manifest_path}")
    print(f"- Checkpoint spec: {checkpoint_spec_path}")
    print(f"- GPU run script: {run_ps1_path}")
    print(f"- GPU pilot script: {run_pilot_ps1_path}")
    print(f"- Selected seeds: {selected}")


if __name__ == "__main__":
    main()
