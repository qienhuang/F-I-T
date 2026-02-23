from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import sys
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
import torch
import yaml


def _seed_name(seed: int) -> str:
    return f"seed_{seed}"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_diagnostics(path: Path) -> dict[int, dict[str, str]]:
    out: dict[int, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            seed = int(row["seed"].split("_", 1)[1])
            out[seed] = row
    return out


def _coerce_step(v: str | None) -> int | None:
    if v is None:
        return None
    v = str(v).strip()
    if v == "":
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def _find_run_dir(runs_root: Path, phase: str, seed: int) -> Path:
    p1 = runs_root / phase / _seed_name(seed)
    p2 = runs_root / _seed_name(seed)
    if p1.exists():
        return p1
    if p2.exists():
        return p2
    raise FileNotFoundError(f"run directory not found for seed={seed} under {runs_root}")


def _latest_checkpoint(ckpt_dir: Path) -> Path:
    cands = sorted(
        ckpt_dir.glob("step_*.pt"),
        key=lambda p: int(p.stem.split("_", 1)[1]),
    )
    if not cands:
        raise FileNotFoundError(f"no checkpoints in {ckpt_dir}")
    return cands[-1]


def _evaluate_acc(model: torch.nn.Module, loader: Any, device: torch.device) -> float:
    model.eval()
    total = 0
    correct = 0
    with torch.no_grad():
        for batch in loader:
            x = batch["x"].to(device)
            y = batch["y_true"].to(device)
            logits = model(x)
            pred = torch.argmax(logits, dim=-1)
            correct += int((pred == y).sum().item())
            total += int(x.shape[0])
    return float(correct / max(total, 1))


def _apply_noise_(model: torch.nn.Module, epsilon: float, seed: int) -> None:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    with torch.no_grad():
        for p in model.parameters():
            noise = torch.randn(p.shape, generator=g, dtype=p.dtype, device=p.device)
            p.add_(noise * float(epsilon))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _q25(values: list[float]) -> float:
    arr = np.asarray([x for x in values if np.isfinite(x)], dtype=np.float64)
    if arr.size == 0:
        return float("nan")
    return float(np.quantile(arr, 0.25))


def _med(values: list[float]) -> float:
    vals = [x for x in values if np.isfinite(x)]
    if not vals:
        return float("nan")
    return float(median(vals))


def _is_true(x: bool) -> str:
    return "pass" if x else "fail"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase-II attractor stability tests (A/B/C).")
    parser.add_argument("--prereg", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--grokking-root", required=True)
    parser.add_argument("--diagnostics", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    prereg = _load_yaml(Path(args.prereg))
    manifest = _load_manifest(Path(args.manifest))
    diagnostics = _load_diagnostics(Path(args.diagnostics))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Inject grokking package path.
    grokking_root = Path(args.grokking_root).resolve()
    sys.path.insert(0, str((grokking_root / "src").resolve()))

    from grokking.datasets.modular_addition import make_loaders  # pylint: disable=import-outside-toplevel
    from grokking.estimators.spectral import spectral_metrics_from_weight  # pylint: disable=import-outside-toplevel
    from grokking.models.tiny_transformer import TinyTransformer  # pylint: disable=import-outside-toplevel

    upstream_phase = manifest["upstream"].get("phase", "eval")
    runs_root = Path(args.runs_root).resolve()

    checkpoint_spec = _load_yaml(Path(manifest["upstream"]["checkpoint_spec"]))
    boundary = checkpoint_spec["boundary"]
    train_cfg = boundary["training"]
    model_cfg = boundary["model"]
    data_cfg = boundary["dataset"]
    time_cfg = checkpoint_spec["time"]

    epsilons = [float(x) for x in prereg["tests"]["weight_noise"]["epsilons"]]
    eps_recover = float(prereg["tests"]["perturb_recover"]["epsilon"])
    recover_steps = int(prereg["tests"]["perturb_recover"]["recover_steps"])
    eval_every_steps = int(prereg["tests"]["perturb_recover"]["eval_every_steps"])
    recover_target_fraction = float(prereg["tests"]["perturb_recover"]["recover_target_fraction_of_baseline_acc"])
    post_window_steps = int(prereg["tests"]["representation_plateau"]["post_window_steps"])
    repeats = int(prereg["tests"]["weight_noise"]["repeats"])

    spectral_matrix_name = checkpoint_spec.get("state", {}).get("spectral_matrices", ["unembed.weight"])[0]
    normalize_entropy = bool(checkpoint_spec.get("estimators", {}).get("H_spec", {}).get("normalize", True))

    selected_seeds = [int(s) for s in manifest["selected_seeds"]]
    groups = manifest["groups"]
    reg_group = set(groups["registered"])
    no_group = set(groups["no_transition_control"])

    per_seed_rows: list[dict[str, Any]] = []
    missing_seeds: list[int] = []

    for seed in selected_seeds:
        try:
            run_dir = _find_run_dir(runs_root, upstream_phase, seed)
            ckpt_path = _latest_checkpoint(run_dir / "checkpoints")
        except FileNotFoundError:
            missing_seeds.append(seed)
            continue
        ckpt = torch.load(ckpt_path, map_location="cpu")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = TinyTransformer(
            vocab_size=int(boundary["modulus_p"]),
            d_model=int(model_cfg["width"]),
            n_heads=int(model_cfg["heads"]),
            n_layers=int(model_cfg["layers"]),
            dropout=float(model_cfg.get("dropout", 0.0)),
            n_classes=int(boundary["modulus_p"]),
        ).to(device)
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=float(train_cfg["lr"]),
            weight_decay=float(train_cfg["weight_decay"]),
        )
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        base_model_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        base_opt_state = copy.deepcopy(optimizer.state_dict())

        train_loader, test_loader = make_loaders(
            p=int(boundary["modulus_p"]),
            train_size=int(data_cfg["train_size"]),
            test_size=int(data_cfg["test_size"]),
            batch_size=int(train_cfg["batch_size"]),
            seed=seed,
            corruption=data_cfg.get("corruption", {}),
        )
        train_iter = iter(train_loader)
        loss_fn = torch.nn.CrossEntropyLoss()

        baseline_acc = _evaluate_acc(model, test_loader, device)
        row: dict[str, Any] = {
            "seed": _seed_name(seed),
            "group": (
                "REGISTERED_TRANSITION"
                if seed in reg_group
                else ("NO_TRANSITION" if seed in no_group else "OPTIONAL")
            ),
            "checkpoint": str(ckpt_path),
            "baseline_acc": baseline_acc,
        }

        # A) Weight noise stability
        for eps in epsilons:
            drops: list[float] = []
            for rep in range(repeats):
                model.load_state_dict(base_model_state, strict=True)
                _apply_noise_(model, eps, seed=seed * 1000 + rep)
                acc_noisy = _evaluate_acc(model, test_loader, device)
                drops.append(max(0.0, baseline_acc - acc_noisy))
            tag = f"{eps:.0e}"
            row[f"drop_eps_{tag}"] = float(np.median(np.asarray(drops, dtype=np.float64)))

        eps_arr = np.asarray(epsilons, dtype=np.float64)
        drop_arr = np.asarray([row[f"drop_eps_{eps:.0e}"] for eps in epsilons], dtype=np.float64)
        row["noise_slope"] = float(np.polyfit(eps_arr, drop_arr, deg=1)[0]) if len(epsilons) >= 2 else float("nan")

        # B) Perturb + recover
        model.load_state_dict(base_model_state, strict=True)
        optimizer.load_state_dict(base_opt_state)
        _apply_noise_(model, eps_recover, seed=seed * 1000 + 777)
        post_noise_acc = _evaluate_acc(model, test_loader, device)
        row["post_noise_acc_eps_recover"] = post_noise_acc
        row["post_noise_drop_eps_recover"] = max(0.0, baseline_acc - post_noise_acc)

        target_acc = recover_target_fraction * baseline_acc
        recover_hit: int | None = None
        recover_hspec_series: list[float] = []
        for local_step in range(1, recover_steps + 1):
            try:
                batch = next(train_iter)
            except StopIteration:
                train_iter = iter(train_loader)
                batch = next(train_iter)

            model.train()
            x = batch["x"].to(device)
            y = batch["y"].to(device)
            logits = model(x)
            loss = loss_fn(logits, y)

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

            if local_step % eval_every_steps != 0 and local_step != recover_steps:
                continue

            acc_now = _evaluate_acc(model, test_loader, device)
            w = dict(model.named_parameters())[spectral_matrix_name]
            h_spec_now = spectral_metrics_from_weight(w, normalize_entropy=normalize_entropy).h_spec
            recover_hspec_series.append(float(h_spec_now))
            if recover_hit is None and acc_now >= target_acc:
                recover_hit = local_step

        row["recover_target_acc"] = target_acc
        row["recovered"] = recover_hit is not None
        row["t_recover_steps"] = recover_hit if recover_hit is not None else ""
        row["recover_hspec_var"] = (
            float(np.var(np.asarray(recover_hspec_series, dtype=np.float64), ddof=0))
            if len(recover_hspec_series) >= 2
            else float("nan")
        )

        # C) Plateau variance from existing run logs
        diag = diagnostics.get(seed, {})
        fit_t = _coerce_step(diag.get("fit_transition_t"))
        base_t = _coerce_step(diag.get("baseline_transition_t"))
        anchor = fit_t if fit_t is not None else base_t
        row["plateau_anchor_step"] = anchor if anchor is not None else ""

        plateau_var = float("nan")
        if anchor is not None:
            logs = _load_jsonl(run_dir / "logs.jsonl")
            vals = []
            for rec in logs:
                step = int(rec["step"])
                if anchor <= step <= anchor + post_window_steps:
                    h_map = rec.get("H_spec_by_layer", {})
                    if spectral_matrix_name in h_map:
                        vals.append(float(h_map[spectral_matrix_name]))
            if len(vals) >= 2:
                plateau_var = float(np.var(np.asarray(vals, dtype=np.float64), ddof=0))
        row["plateau_hspec_var"] = plateau_var

        per_seed_rows.append(row)

    # Aggregate decision
    eps_ref_tag = f"{eps_recover:.0e}"
    reg_rows = [r for r in per_seed_rows if r["group"] == "REGISTERED_TRANSITION"]
    no_rows = [r for r in per_seed_rows if r["group"] == "NO_TRANSITION"]

    reg_drop = [float(r.get(f"drop_eps_{eps_ref_tag}", float("nan"))) for r in reg_rows]
    no_drop = [float(r.get(f"drop_eps_{eps_ref_tag}", float("nan"))) for r in no_rows]

    reg_trec = [
        float(r["t_recover_steps"]) if str(r["t_recover_steps"]).strip() != "" else float("inf")
        for r in reg_rows
    ]
    no_trec = [
        float(r["t_recover_steps"]) if str(r["t_recover_steps"]).strip() != "" else float("inf")
        for r in no_rows
    ]

    reg_var = [float(r.get("plateau_hspec_var", float("nan"))) for r in reg_rows]
    no_var = [float(r.get("plateau_hspec_var", float("nan"))) for r in no_rows]

    c1 = _med(reg_drop) < _q25(no_drop) if reg_rows and no_rows else False
    c2 = max(reg_trec) < _med(no_trec) if reg_rows and no_rows else False
    c3 = _med(reg_var) < _med(no_var) if reg_rows and no_rows else False

    pass_count = int(c1) + int(c2) + int(c3)
    k_required = int(prereg["decision_rule"]["verdict"]["pass_if_at_least_k_of_3"])
    if pass_count >= k_required:
        verdict = prereg["decision_rule"]["verdict"]["pass_label"]
    elif pass_count == 0:
        verdict = prereg["decision_rule"]["verdict"]["fail_label"]
    else:
        verdict = prereg["decision_rule"]["verdict"]["otherwise_label"]

    summary = {
        "phase2_id": prereg["id"],
        "n_selected_seeds": len(selected_seeds),
        "n_missing_runs": len(missing_seeds),
        "missing_seeds": missing_seeds,
        "n_evaluated_seeds": len(per_seed_rows),
        "n_registered": len(reg_rows),
        "n_no_transition_control": len(no_rows),
        "eps_ref": eps_recover,
        "criterion_1": {
            "name": "registered_drop_vs_control_q25",
            "registered_median_drop": _med(reg_drop),
            "control_q25_drop": _q25(no_drop),
            "pass": c1,
        },
        "criterion_2": {
            "name": "registered_recovery_vs_control_median",
            "registered_max_t_recover": float(max(reg_trec)) if reg_trec else float("nan"),
            "control_median_t_recover": _med(no_trec),
            "pass": c2,
        },
        "criterion_3": {
            "name": "registered_plateau_var_vs_control_median",
            "registered_median_var": _med(reg_var),
            "control_median_var": _med(no_var),
            "pass": c3,
        },
        "pass_count": pass_count,
        "k_required": k_required,
        "verdict": verdict,
    }

    # Save per-seed CSV
    csv_path = out_dir / "per_seed_metrics.csv"
    all_keys = sorted({k for r in per_seed_rows for k in r.keys()})
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        for r in per_seed_rows:
            writer.writerow(r)

    # Save summary JSON
    summary_path = out_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save markdown report
    report_path = out_dir / "report.md"
    report = f"""# Phase-II Attractor Stability Report

## Verdict

- **{verdict}** (pass_count={pass_count}, required={k_required})

## Group sizes

- REGISTERED_TRANSITION: {len(reg_rows)}
- NO_TRANSITION control: {len(no_rows)}
- Total selected: {len(selected_seeds)}
- Missing rerun artifacts: {len(missing_seeds)}

## Criteria

| Criterion | Value | Threshold | Status |
|---|---:|---:|---|
| C1 registered median drop (eps={eps_recover:.1e}) | {summary['criterion_1']['registered_median_drop']:.6f} | < control q25 {summary['criterion_1']['control_q25_drop']:.6f} | {_is_true(c1)} |
| C2 registered max recover steps | {summary['criterion_2']['registered_max_t_recover']:.1f} | < control median {summary['criterion_2']['control_median_t_recover']:.1f} | {_is_true(c2)} |
| C3 registered median plateau var | {summary['criterion_3']['registered_median_var']:.6e} | < control median {summary['criterion_3']['control_median_var']:.6e} | {_is_true(c3)} |

## Files

- `{csv_path}`
- `{summary_path}`
"""
    with report_path.open("w", encoding="utf-8") as f:
        f.write(report)

    print(f"Phase-II completed. verdict={verdict}")
    print(f"- {summary_path}")
    print(f"- {csv_path}")
    print(f"- {report_path}")


if __name__ == "__main__":
    main()
