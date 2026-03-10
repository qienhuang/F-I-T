"""Phase-II v1.0 – Conclusive-first attractor stability protocol.

Grokked (step_300000, test_acc~99%) vs Pre-grok (step_5000, test_acc~15%)
checkpoints from the same seeds (within-seed matched design).

Perturbations
-------------
- Gaussian random noise at relative scales (eps_rel * ||W||_F).
- Structured rank-1 perturbation at relative scales.

Metrics (absolute thresholds – avoids ceiling)
-----------------------------------------------
- t50  : steps to reach test_acc >= 0.50 (capped at recover_steps)
- t90  : steps to reach test_acc >= 0.90 (capped at recover_steps)
- AUC  : mean test_acc over [0, recover_steps] (normalised to [0,1])
- unrecovered@2000 : fraction of (seed × perturb) runs where acc < 0.90 at end

Decision rule (preregistered)
------------------------------
Conclusive if >= 2 metrics show grokked-better in same direction AND
at least one minimum effect threshold is met:
  - t90 ratio pregrok/grokked  >= 1.5
  - unrecovered diff (pp)       >= 20
  - AUC diff grokked-pregrok   >= 0.10
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_checkpoint(ckpt_dir: Path, step: int) -> dict[str, Any]:
    p = ckpt_dir / f"step_{step}.pt"
    if not p.exists():
        raise FileNotFoundError(f"Checkpoint not found: {p}")
    return torch.load(p, map_location="cpu")


def _find_run_dir(runs_root: Path, phase: str, seed: int) -> Path:
    p1 = runs_root / phase / f"seed_{seed}"
    p2 = runs_root / f"seed_{seed}"
    if p1.exists():
        return p1
    if p2.exists():
        return p2
    raise FileNotFoundError(f"Run dir not found for seed={seed} under {runs_root}")


# ---------------------------------------------------------------------------
# Perturbation helpers
# ---------------------------------------------------------------------------

def _weight_by_name(model: torch.nn.Module, name: str) -> torch.nn.Parameter:
    for n, p in model.named_parameters():
        if n == name:
            return p
    raise KeyError(f"Parameter '{name}' not found in model.")


def _apply_gaussian_(
    model: torch.nn.Module,
    matrix_name: str,
    scale_rel: float,
    seed: int,
) -> None:
    """Add Gaussian noise scaled to scale_rel * ||W||_F to named matrix."""
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    with torch.no_grad():
        w = _weight_by_name(model, matrix_name)
        w_norm = float(w.norm(p="fro").item())
        eps_abs = scale_rel * w_norm
        noise = torch.randn(w.shape, generator=g, dtype=w.dtype)
        noise_norm = float(noise.norm(p="fro").item())
        if noise_norm > 0:
            noise = noise * (eps_abs / noise_norm)
        w.add_(noise.to(w.device))


def _apply_rank1_(
    model: torch.nn.Module,
    matrix_name: str,
    scale_rel: float,
    seed: int,
) -> None:
    """Add structured rank-1 perturbation at scale_rel * ||W||_F to named matrix."""
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 100_000)
    with torch.no_grad():
        w = _weight_by_name(model, matrix_name)
        w_norm = float(w.norm(p="fro").item())
        eps_abs = scale_rel * w_norm
        if w.dim() < 2:
            # fallback to gaussian for 1-D params
            noise = torch.randn(w.shape, generator=g, dtype=w.dtype)
            noise_norm = float(noise.norm(p="fro").item())
            if noise_norm > 0:
                noise = noise * (eps_abs / noise_norm)
            w.add_(noise.to(w.device))
            return
        rows, cols = w.shape[0], w.shape[1]
        u = torch.randn(rows, generator=g, dtype=w.dtype)
        v = torch.randn(cols, generator=g, dtype=w.dtype)
        u = u / (u.norm() + 1e-12)
        v = v / (v.norm() + 1e-12)
        rank1 = u.unsqueeze(1) * v.unsqueeze(0)  # [rows, cols]
        rank1_norm = float(rank1.norm(p="fro").item())
        if rank1_norm > 0:
            rank1 = rank1 * (eps_abs / rank1_norm)
        # Handle higher-dim params (e.g. in_proj is [3*d, d]):
        if w.shape == rank1.shape:
            w.add_(rank1.to(w.device))
        else:
            # trim/pad to match first two dims
            r1 = rank1.to(w.device)
            target = torch.zeros_like(w)
            target[: r1.shape[0], : r1.shape[1]] = r1
            w.add_(target)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _evaluate_acc(
    model: torch.nn.Module,
    loader: Any,
    device: torch.device,
) -> float:
    model.eval()
    total, correct = 0, 0
    with torch.no_grad():
        for batch in loader:
            x = batch["x"].to(device)
            y = batch["y_true"].to(device)
            logits = model(x)
            pred = torch.argmax(logits, dim=-1)
            correct += int((pred == y).sum().item())
            total += int(x.shape[0])
    return float(correct / max(total, 1))


# ---------------------------------------------------------------------------
# Recovery loop
# ---------------------------------------------------------------------------

def _run_recovery(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    loss_fn: torch.nn.Module,
    train_loader: Any,
    test_loader: Any,
    device: torch.device,
    recover_steps: int,
    eval_every: int,
) -> list[tuple[int, float]]:
    """Return list of (step, test_acc) tuples from 0 to recover_steps."""
    curve: list[tuple[int, float]] = []
    train_iter = iter(train_loader)

    # Eval at step 0 (post-perturbation, before any recovery)
    acc0 = _evaluate_acc(model, test_loader, device)
    curve.append((0, acc0))

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

        if local_step % eval_every == 0 or local_step == recover_steps:
            acc = _evaluate_acc(model, test_loader, device)
            curve.append((local_step, acc))

    return curve


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------

def _compute_run_metrics(
    curve: list[tuple[int, float]],
    t50_thr: float,
    t90_thr: float,
    recover_steps: int,
) -> dict[str, float]:
    """Compute t50, t90, AUC, unrecovered for a single recovery curve."""
    steps = [s for s, _ in curve]
    accs = [a for _, a in curve]

    t50: float = float(recover_steps)
    t90: float = float(recover_steps)
    for step, acc in curve:
        if t50 == float(recover_steps) and acc >= t50_thr:
            t50 = float(step)
        if t90 == float(recover_steps) and acc >= t90_thr:
            t90 = float(step)

    # AUC via trapezoidal rule, normalised to [0, 1]
    if len(steps) >= 2:
        trapfn = getattr(np, "trapezoid", np.trapz)  # np.trapezoid added in 2.0
        total_area = float(trapfn(accs, steps))
        auc = total_area / float(recover_steps)
    else:
        auc = float(accs[-1]) if accs else 0.0

    final_acc = accs[-1] if accs else 0.0
    unrecovered = 1.0 if final_acc < t90_thr else 0.0

    return {
        "t50": t50,
        "t90": t90,
        "auc": auc,
        "unrecovered": unrecovered,
        "final_acc": final_acc,
        "initial_acc_post_perturb": float(accs[0]) if accs else float("nan"),
    }


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------

def _bootstrap_median_ci(
    values: list[float],
    n_bootstrap: int,
    ci_level: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Return (lo, hi) bootstrap CI for median."""
    arr = np.asarray([v for v in values if np.isfinite(v)], dtype=np.float64)
    if arr.size == 0:
        return (float("nan"), float("nan"))
    boot_medians = []
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_medians.append(float(np.median(sample)))
    alpha = (1.0 - ci_level) / 2.0
    lo = float(np.quantile(boot_medians, alpha))
    hi = float(np.quantile(boot_medians, 1.0 - alpha))
    return (lo, hi)


def _bootstrap_mean_ci(
    values: list[float],
    n_bootstrap: int,
    ci_level: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Return (lo, hi) bootstrap CI for mean."""
    arr = np.asarray([v for v in values if np.isfinite(v)], dtype=np.float64)
    if arr.size == 0:
        return (float("nan"), float("nan"))
    boot_means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_means.append(float(np.mean(sample)))
    alpha = (1.0 - ci_level) / 2.0
    lo = float(np.quantile(boot_means, alpha))
    hi = float(np.quantile(boot_means, 1.0 - alpha))
    return (lo, hi)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase-II v1.0 conclusive-first attractor protocol."
    )
    parser.add_argument("--prereg", required=True, help="Path to YAML prereg file.")
    parser.add_argument("--grokking-root", required=True, help="Path to grokking package root.")
    parser.add_argument("--runs-root", required=True, help="Path to runs root (contains eval/seed_NNN/).")
    parser.add_argument("--out-dir", required=True, help="Output directory.")
    parser.add_argument("--primary-matrix-only", action="store_true",
                        help="Only run primary matrix (embed.weight); skip optional.")
    parser.add_argument("--seed-override", nargs="*", type=int,
                        help="Override seed list (space-separated integers).")
    args = parser.parse_args()

    prereg = _load_yaml(Path(args.prereg))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Inject grokking package
    grokking_root = Path(args.grokking_root).resolve()
    sys.path.insert(0, str((grokking_root / "src").resolve()))
    from grokking.datasets.modular_addition import make_loaders  # noqa: E402
    from grokking.models.tiny_transformer import TinyTransformer  # noqa: E402

    # ------------------------------------------------------------------
    # Config from prereg
    # ------------------------------------------------------------------
    groups_cfg = prereg["groups"]
    boundary = prereg["upstream_grokking"]["boundary"]
    perturb_cfg = prereg["perturbations"]
    recovery_cfg = prereg["recovery"]
    metrics_cfg = prereg["metrics"]
    decision_cfg = prereg["decision_rule"]

    grokked_step = int(groups_cfg["grokked"]["checkpoint_step"])
    pregrok_step = int(groups_cfg["pregrok"]["checkpoint_step"])
    all_seeds = args.seed_override or [int(s) for s in groups_cfg["grokked"]["seeds"]]

    matrices = [m["name"] for m in perturb_cfg["matrices"] if m.get("primary", False)]
    if not args.primary_matrix_only:
        matrices += [m["name"] for m in perturb_cfg["matrices"] if not m.get("primary", True)]
    optional_matrices = [
        m["name"] for m in perturb_cfg.get("optional_matrices", [])
    ] if not args.primary_matrix_only else []

    perturb_types = perturb_cfg["types"]
    scales_rel = [float(s) for s in perturb_cfg["scales_rel"]]
    n_perturb_seeds = int(perturb_cfg.get("n_perturbation_seeds", 3))

    recover_steps = int(recovery_cfg["steps"])
    eval_every = int(recovery_cfg["eval_every_steps"])
    n_bootstrap = int(metrics_cfg.get("bootstrap_n", 2000))
    ci_level = float(metrics_cfg.get("bootstrap_ci", 0.95))
    t50_thr = float(metrics_cfg["t50_threshold"])
    t90_thr = float(metrics_cfg["t90_threshold"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loss_fn = torch.nn.CrossEntropyLoss()
    runs_root = Path(args.runs_root).resolve()
    rng = np.random.default_rng(seed=42)

    # ------------------------------------------------------------------
    # Per-seed / per-condition loop
    # ------------------------------------------------------------------
    all_rows: list[dict[str, Any]] = []
    print(f"Device: {device}")
    print(f"Seeds ({len(all_seeds)}): {all_seeds}")
    print(f"Matrices: {matrices}")
    print(f"Perturbation types: {perturb_types}, scales: {scales_rel}")
    print(f"Recovery steps: {recover_steps}, eval every: {eval_every}")
    print()

    for seed in all_seeds:
        try:
            run_dir = _find_run_dir(runs_root, "eval", seed)
        except FileNotFoundError as exc:
            print(f"  [SKIP] seed={seed}: {exc}")
            continue

        ckpt_dir = run_dir / "checkpoints"

        for group_name, ckpt_step in [("grokked", grokked_step), ("pregrok", pregrok_step)]:
            try:
                ckpt = _load_checkpoint(ckpt_dir, ckpt_step)
            except FileNotFoundError as exc:
                print(f"  [SKIP] seed={seed} group={group_name}: {exc}")
                continue

            # Build model
            model = TinyTransformer(
                vocab_size=int(boundary["modulus_p"]),
                d_model=int(boundary["width"]),
                n_heads=int(boundary["heads"]),
                n_layers=int(boundary["layers"]),
                dropout=float(boundary.get("dropout", 0.0)),
                n_classes=int(boundary["modulus_p"]),
            ).to(device)
            optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=float(boundary["lr"]),
                weight_decay=float(boundary["weight_decay"]),
            )
            model.load_state_dict(ckpt["model"])
            if "optimizer" in ckpt:
                optimizer.load_state_dict(ckpt["optimizer"])

            base_model_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            base_opt_state = copy.deepcopy(optimizer.state_dict())

            # Make data loaders
            train_loader, test_loader = make_loaders(
                p=int(boundary["modulus_p"]),
                train_size=int(boundary["train_size"]),
                test_size=int(boundary.get("test_size", 2000)),
                batch_size=int(boundary["batch_size"]),
                seed=seed,
                corruption={"enabled": True,
                            "corruption_rate": float(boundary["corruption_rate"]),
                            "corruption_seed": int(boundary["corruption_seed"])},
            )

            baseline_acc = _evaluate_acc(model, test_loader, device)
            print(f"  seed={seed} group={group_name} step={ckpt_step} baseline_acc={baseline_acc:.4f}")

            for matrix_name in matrices + optional_matrices:
                # Check the parameter exists
                try:
                    _weight_by_name(model, matrix_name)
                except KeyError:
                    print(f"    [SKIP] matrix '{matrix_name}' not found")
                    continue

                for perturb_type in perturb_types:
                    for scale_rel in scales_rel:
                        for p_seed_idx in range(n_perturb_seeds):
                            p_seed = seed * 10_000 + p_seed_idx * 1000 + int(scale_rel * 10000)

                            # Reset model to checkpoint state
                            model.load_state_dict(base_model_state, strict=True)
                            optimizer.load_state_dict(base_opt_state)

                            # Apply perturbation
                            if perturb_type == "gaussian_random":
                                _apply_gaussian_(model, matrix_name, scale_rel, p_seed)
                            elif perturb_type == "structured_rank1":
                                _apply_rank1_(model, matrix_name, scale_rel, p_seed)
                            else:
                                print(f"    [WARN] Unknown perturb type: {perturb_type}")
                                continue

                            # Run recovery
                            curve = _run_recovery(
                                model, optimizer, loss_fn,
                                train_loader, test_loader, device,
                                recover_steps, eval_every,
                            )

                            # Compute metrics
                            m = _compute_run_metrics(curve, t50_thr, t90_thr, recover_steps)

                            row = {
                                "seed": seed,
                                "group": group_name,
                                "checkpoint_step": ckpt_step,
                                "matrix": matrix_name,
                                "perturb_type": perturb_type,
                                "scale_rel": scale_rel,
                                "perturb_seed_idx": p_seed_idx,
                                "baseline_acc": baseline_acc,
                                **m,
                            }
                            all_rows.append(row)

                            print(
                                f"    {group_name} seed={seed} {perturb_type}"
                                f" scale={scale_rel:.1%} p_seed={p_seed_idx}"
                                f" | t50={m['t50']:.0f} t90={m['t90']:.0f}"
                                f" auc={m['auc']:.3f} unrecov={m['unrecovered']:.0f}"
                            )

    # ------------------------------------------------------------------
    # Write per-seed CSV
    # ------------------------------------------------------------------
    csv_path = out_dir / "per_seed_metrics.csv"
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nWrote {len(all_rows)} rows -> {csv_path}")

    # ------------------------------------------------------------------
    # Aggregate: primary matrix, averaged over perturb seeds, all scales
    # ------------------------------------------------------------------
    primary_matrix = matrices[0] if matrices else "embed.weight"
    grok_rows = [r for r in all_rows if r["group"] == "grokked" and r["matrix"] == primary_matrix]
    pre_rows = [r for r in all_rows if r["group"] == "pregrok" and r["matrix"] == primary_matrix]

    def _group_medians(rows: list[dict], key: str) -> list[float]:
        """Median of 'key' over perturbation conditions per seed."""
        seeds = sorted({r["seed"] for r in rows})
        out = []
        for s in seeds:
            vals = [r[key] for r in rows if r["seed"] == s and np.isfinite(r[key])]
            if vals:
                out.append(float(np.median(vals)))
        return out

    grok_t50 = _group_medians(grok_rows, "t50")
    grok_t90 = _group_medians(grok_rows, "t90")
    grok_auc = _group_medians(grok_rows, "auc")
    grok_unrecov = _group_medians(grok_rows, "unrecovered")

    pre_t50 = _group_medians(pre_rows, "t50")
    pre_t90 = _group_medians(pre_rows, "t90")
    pre_auc = _group_medians(pre_rows, "auc")
    pre_unrecov = _group_medians(pre_rows, "unrecovered")

    def safe_median(lst: list[float]) -> float:
        v = [x for x in lst if np.isfinite(x)]
        return float(np.median(v)) if v else float("nan")

    def safe_mean(lst: list[float]) -> float:
        v = [x for x in lst if np.isfinite(x)]
        return float(np.mean(v)) if v else float("nan")

    grok_med_t50 = safe_median(grok_t50)
    grok_med_t90 = safe_median(grok_t90)
    grok_mean_auc = safe_mean(grok_auc)
    grok_mean_unrecov_pct = safe_mean(grok_unrecov) * 100

    pre_med_t50 = safe_median(pre_t50)
    pre_med_t90 = safe_median(pre_t90)
    pre_mean_auc = safe_mean(pre_auc)
    pre_mean_unrecov_pct = safe_mean(pre_unrecov) * 100

    # Ratios and differences
    t50_ratio = (pre_med_t50 / grok_med_t50) if grok_med_t50 > 0 else float("nan")
    t90_ratio = (pre_med_t90 / grok_med_t90) if grok_med_t90 > 0 else float("nan")
    auc_diff = grok_mean_auc - pre_mean_auc
    unrecov_diff_pp = pre_mean_unrecov_pct - grok_mean_unrecov_pct

    # Bootstrap CIs
    t50_grok_ci = _bootstrap_median_ci(grok_t50, n_bootstrap, ci_level, rng)
    t50_pre_ci = _bootstrap_median_ci(pre_t50, n_bootstrap, ci_level, rng)
    t90_grok_ci = _bootstrap_median_ci(grok_t90, n_bootstrap, ci_level, rng)
    t90_pre_ci = _bootstrap_median_ci(pre_t90, n_bootstrap, ci_level, rng)
    auc_grok_ci = _bootstrap_mean_ci(grok_auc, n_bootstrap, ci_level, rng)
    auc_pre_ci = _bootstrap_mean_ci(pre_auc, n_bootstrap, ci_level, rng)
    unrecov_grok_ci = _bootstrap_mean_ci(grok_unrecov, n_bootstrap, ci_level, rng)
    unrecov_pre_ci = _bootstrap_mean_ci(pre_unrecov, n_bootstrap, ci_level, rng)

    # ------------------------------------------------------------------
    # Decision rule
    # ------------------------------------------------------------------
    min_t90_ratio = float(decision_cfg["minimum_effects"]["t90_ratio_min"])
    min_unrecov_diff = float(decision_cfg["minimum_effects"]["unrecovered_diff_pp_min"])
    min_auc_diff = float(decision_cfg["minimum_effects"]["auc_diff_min"])
    n_required = int(decision_cfg["n_metrics_required"])

    # Each metric: does it separate in the correct direction AND meet min effect?
    metric_results: dict[str, dict] = {}

    # t50: grokked should recover faster (lower t50)
    t50_direction_ok = grok_med_t50 < pre_med_t50
    t50_effect_ok = (t50_ratio >= min_t90_ratio) if np.isfinite(t50_ratio) else False
    metric_results["t50"] = {
        "grokked_median": grok_med_t50, "pregrok_median": pre_med_t50,
        "ratio_pregrok_over_grokked": t50_ratio,
        "direction_ok": t50_direction_ok, "effect_ok": t50_effect_ok,
        "separating": t50_direction_ok and t50_effect_ok,
        "grokked_ci95": list(t50_grok_ci), "pregrok_ci95": list(t50_pre_ci),
    }

    # t90: grokked should recover faster (lower t90)
    t90_direction_ok = grok_med_t90 < pre_med_t90
    t90_effect_ok = (t90_ratio >= min_t90_ratio) if np.isfinite(t90_ratio) else False
    metric_results["t90"] = {
        "grokked_median": grok_med_t90, "pregrok_median": pre_med_t90,
        "ratio_pregrok_over_grokked": t90_ratio,
        "direction_ok": t90_direction_ok, "effect_ok": t90_effect_ok,
        "separating": t90_direction_ok and t90_effect_ok,
        "grokked_ci95": list(t90_grok_ci), "pregrok_ci95": list(t90_pre_ci),
    }

    # AUC: grokked should have higher AUC
    auc_direction_ok = auc_diff >= 0
    auc_effect_ok = auc_diff >= min_auc_diff
    metric_results["auc"] = {
        "grokked_mean": grok_mean_auc, "pregrok_mean": pre_mean_auc,
        "diff_grokked_minus_pregrok": auc_diff,
        "direction_ok": auc_direction_ok, "effect_ok": auc_effect_ok,
        "separating": auc_direction_ok and auc_effect_ok,
        "grokked_ci95": list(auc_grok_ci), "pregrok_ci95": list(auc_pre_ci),
    }

    # unrecovered@2000: grokked should have lower fraction unrecovered
    unrecov_direction_ok = unrecov_diff_pp >= 0
    unrecov_effect_ok = unrecov_diff_pp >= min_unrecov_diff
    metric_results["unrecovered_2000"] = {
        "grokked_pct": grok_mean_unrecov_pct, "pregrok_pct": pre_mean_unrecov_pct,
        "diff_pregrok_minus_grokked_pp": unrecov_diff_pp,
        "direction_ok": unrecov_direction_ok, "effect_ok": unrecov_effect_ok,
        "separating": unrecov_direction_ok and unrecov_effect_ok,
        "grokked_ci95": [x * 100 for x in unrecov_grok_ci],
        "pregrok_ci95": [x * 100 for x in unrecov_pre_ci],
    }

    n_separating = sum(1 for m in metric_results.values() if m["separating"])

    if n_separating >= n_required:
        verdict = prereg["verdicts"]["pass"]
    elif n_separating == 0 and len(all_rows) > 0:
        verdict = prereg["verdicts"]["fail"]
    else:
        verdict = prereg["verdicts"]["inconclusive"]

    # ------------------------------------------------------------------
    # Write summary.json
    # ------------------------------------------------------------------
    summary: dict[str, Any] = {
        "phase2_id": prereg["id"],
        "version": prereg["version"],
        "n_seeds": len(all_seeds),
        "n_grokked_seeds": len({r["seed"] for r in grok_rows}),
        "n_pregrok_seeds": len({r["seed"] for r in pre_rows}),
        "n_total_runs": len(all_rows),
        "primary_matrix": primary_matrix,
        "grokked_step": grokked_step,
        "pregrok_step": pregrok_step,
        "recover_steps": recover_steps,
        "metrics": metric_results,
        "n_separating_metrics": n_separating,
        "n_required": n_required,
        "verdict": verdict,
    }
    summary_path = out_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWrote summary → {summary_path}")

    # ------------------------------------------------------------------
    # Write report.md
    # ------------------------------------------------------------------
    report_lines = [
        "# Phase-II v1.0 Attractor Stability Report",
        "",
        f"## Verdict: **{verdict}** ({n_separating}/{n_required} metrics required)",
        "",
        "## Setup",
        "",
        f"- Grokked group: step_{grokked_step} checkpoints ({len({r['seed'] for r in grok_rows})} seeds)",
        f"- Pre-grok group: step_{pregrok_step} checkpoints ({len({r['seed'] for r in pre_rows})} seeds)",
        f"- Primary matrix: `{primary_matrix}`",
        f"- Recovery steps: {recover_steps}, eval every {eval_every}",
        "",
        "## Metrics Summary",
        "",
        "| Metric | Grokked | Pre-grok | Effect | Min required | Separating |",
        "|---|---:|---:|---:|---:|:---:|",
    ]

    r_t50 = metric_results["t50"]
    r_t90 = metric_results["t90"]
    r_auc = metric_results["auc"]
    r_unr = metric_results["unrecovered_2000"]

    def _ci_str(ci: list) -> str:
        return f"[{ci[0]:.1f}, {ci[1]:.1f}]"

    report_lines.append(
        f"| t50 (steps) | {r_t50['grokked_median']:.0f} {_ci_str(r_t50['grokked_ci95'])} | "
        f"{r_t50['pregrok_median']:.0f} {_ci_str(r_t50['pregrok_ci95'])} | "
        f"ratio={r_t50['ratio_pregrok_over_grokked']:.2f}x | ≥{min_t90_ratio:.1f}x | "
        f"{'✓' if r_t50['separating'] else '✗'} |"
    )
    report_lines.append(
        f"| t90 (steps) | {r_t90['grokked_median']:.0f} {_ci_str(r_t90['grokked_ci95'])} | "
        f"{r_t90['pregrok_median']:.0f} {_ci_str(r_t90['pregrok_ci95'])} | "
        f"ratio={r_t90['ratio_pregrok_over_grokked']:.2f}x | ≥{min_t90_ratio:.1f}x | "
        f"{'✓' if r_t90['separating'] else '✗'} |"
    )
    report_lines.append(
        f"| AUC [0,{recover_steps}] | {r_auc['grokked_mean']:.3f} {_ci_str(r_auc['grokked_ci95'])} | "
        f"{r_auc['pregrok_mean']:.3f} {_ci_str(r_auc['pregrok_ci95'])} | "
        f"Δ={r_auc['diff_grokked_minus_pregrok']:.3f} | ≥{min_auc_diff:.2f} | "
        f"{'✓' if r_auc['separating'] else '✗'} |"
    )
    report_lines.append(
        f"| Unrecovered@{recover_steps} (%) | {r_unr['grokked_pct']:.1f}% {_ci_str(r_unr['grokked_ci95'])} | "
        f"{r_unr['pregrok_pct']:.1f}% {_ci_str(r_unr['pregrok_ci95'])} | "
        f"Δpp={r_unr['diff_pregrok_minus_grokked_pp']:.1f} | ≥{min_unrecov_diff:.0f}pp | "
        f"{'✓' if r_unr['separating'] else '✗'} |"
    )

    report_lines += [
        "",
        "## Files",
        "",
        f"- `{csv_path}`",
        f"- `{summary_path}`",
    ]

    report_path = out_dir / "report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Wrote report → {report_path}")

    # Final console summary
    print("\n" + "=" * 60)
    print(f"VERDICT: {verdict}")
    print(f"Separating metrics: {n_separating}/{n_required} required")
    for name, mr in metric_results.items():
        sep = "PASS" if mr["separating"] else "fail"
        print(f"  {name:25s}: {sep}")
    print("=" * 60)


if __name__ == "__main__":
    main()
