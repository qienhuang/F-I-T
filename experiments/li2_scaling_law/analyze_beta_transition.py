#!/usr/bin/env python3
"""
Analyze whether the grok-speed sensitivity parameter (beta) changes with M.

This script is intended for `results/dense_m_sweep/` style runs where each M
has multiple ratios around r_crit.

We deliberately avoid SciPy and use log-linear regression, because:
  - SciPy may not be installed on all machines
  - with only a few points, nonlinear curve_fit can be misleading

Model (candidate):
  T(r) ≈ A * exp(-beta * (r - r_crit))   for r > r_crit

Key caveat:
  A "perfect" R^2 with only 2 points is not evidence; it is algebra.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _parse_filename(stem: str) -> tuple[int, float, int]:
    parts = stem.split("_")
    M = int(parts[0][1:])
    ratio = float(parts[1][5:])
    seed = int(parts[2][4:])
    return M, ratio, seed


def load_results(results_dir: Path) -> dict[tuple[int, float], list[dict]]:
    out: dict[tuple[int, float], list[dict]] = defaultdict(list)
    for json_file in sorted(results_dir.glob("M*.json")):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        M, ratio, seed = _parse_filename(json_file.stem)
        out[(M, ratio)].append(
            {
                "seed": seed,
                "grok_happened": bool(data.get("grok_happened", False)),
                "grok_epoch": data.get("grok_epoch", None),
            }
        )
    return out


def grok_probability(runs: list[dict]) -> float:
    if not runs:
        return 0.0
    return sum(1 for r in runs if r["grok_happened"]) / len(runs)


def grok_epoch_median(runs: list[dict]) -> float | None:
    epochs = [float(r["grok_epoch"]) for r in runs if r["grok_happened"] and r["grok_epoch"] is not None]
    if not epochs:
        return None
    return float(np.median(np.asarray(epochs, dtype=float)))


def estimate_rcrit_50(ratios: list[float], probs: list[float]) -> float | None:
    for i in range(len(ratios) - 1):
        p0, p1 = probs[i], probs[i + 1]
        r0, r1 = ratios[i], ratios[i + 1]
        if (p0 < 0.5 <= p1) or (p0 > 0.5 >= p1):
            if p1 == p0:
                return float((r0 + r1) / 2)
            t = (0.5 - p0) / (p1 - p0)
            return float(r0 + t * (r1 - r0))
    return None


def _linear_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    # y ≈ a + b*x ; return (a, b, R^2)
    b, a = np.polyfit(x, y, 1)
    y_pred = a + b * x
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
    r2 = 1.0 if ss_tot == 0 else (1.0 - ss_res / ss_tot)
    return float(a), float(b), float(r2)


def fit_exponential(delta_r: np.ndarray, t: np.ndarray) -> dict | None:
    # log(t) = log(A) - beta * delta_r
    x = np.asarray(delta_r, dtype=float)
    y = np.asarray(t, dtype=float)
    mask = (x > 0) & (y > 0)
    x, y = x[mask], y[mask]
    if len(x) < 2:
        return None
    a, b, r2 = _linear_fit(x, np.log(y))
    return {"A": float(np.exp(a)), "beta": float(-b), "r2_log": float(r2)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", type=Path, default=Path("results/dense_m_sweep"))
    parser.add_argument("--output_dir", type=Path, default=Path("results/dense_m_sweep/analysis"))
    parser.add_argument("--min_prob", type=float, default=1.0, help="Only fit points with grok probability >= this.")
    parser.add_argument("--min_points", type=int, default=3, help="Minimum points above r_crit to call the fit meaningful.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_results(args.results_dir)
    if not raw:
        print(f"No results found in {args.results_dir}")
        return

    by_M: dict[int, dict[float, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for (M, ratio), runs in raw.items():
        by_M[M][ratio].extend(runs)

    per_M: dict[int, dict] = {}

    print("=" * 72)
    print("beta transition analysis (dense M sweep)")
    print("=" * 72)
    print(f"results_dir={args.results_dir}")
    print(f"min_prob={args.min_prob}  min_points={args.min_points}")

    for M in sorted(by_M.keys()):
        ratios = sorted(by_M[M].keys())
        probs = [grok_probability(by_M[M][r]) for r in ratios]
        rcrit = estimate_rcrit_50(ratios, probs)
        if rcrit is None:
            continue

        # Select fit points above rcrit.
        fit_ratios: list[float] = []
        fit_t: list[float] = []
        for r in ratios:
            p = grok_probability(by_M[M][r])
            if r <= rcrit or p < float(args.min_prob):
                continue
            t_med = grok_epoch_median(by_M[M][r])
            if t_med is None:
                continue
            fit_ratios.append(float(r))
            fit_t.append(float(t_med))

        delta_r = np.asarray([r - rcrit for r in fit_ratios], dtype=float)
        t = np.asarray(fit_t, dtype=float)
        exp_fit = fit_exponential(delta_r, t)

        fit_valid = exp_fit is not None and len(delta_r) >= int(args.min_points)
        per_M[M] = {
            "r_crit": float(rcrit),
            "num_points": int(len(delta_r)),
            "fit_valid": bool(fit_valid),
            "points": [{"ratio": float(r), "delta_r": float(dr), "t": float(tt)} for r, dr, tt in zip(fit_ratios, delta_r, t)],
            "exp_fit": exp_fit,
        }

        if exp_fit is None:
            print(f"M={M}: r_crit~{rcrit:.4f}  (no fit)")
        else:
            note = "" if fit_valid else "  [NOTE: too few points]"
            print(f"M={M}: r_crit~{rcrit:.4f}  beta~{exp_fit['beta']:.3f}  R^2_log={exp_fit['r2_log']:.3f}  N={len(delta_r)}{note}")

    out_json = args.output_dir / "beta_transition_analysis.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(per_M, f, indent=2, ensure_ascii=False)
    print(f"Saved: {out_json}")

    # Plot beta vs M (only valid fits).
    Ms = sorted(m for m, d in per_M.items() if d.get("fit_valid") and d.get("exp_fit"))
    if len(Ms) >= 2:
        betas = [float(per_M[m]["exp_fit"]["beta"]) for m in Ms]
        fig, ax = plt.subplots(1, 1, figsize=(7, 4))
        ax.plot(Ms, betas, "o-", linewidth=2)
        ax.set_xlabel("M")
        ax.set_ylabel("beta (exp decay, log-linear fit)")
        ax.set_title("beta vs M (valid fits only)")
        ax.grid(True, alpha=0.25)
        out_png = args.output_dir / "beta_transition_analysis.png"
        plt.tight_layout()
        plt.savefig(out_png, dpi=160)
        plt.close(fig)
        print(f"Saved: {out_png}")
    else:
        print("Not enough valid fits to plot beta vs M.")

    # Markdown report
    out_md = args.output_dir / "beta_transition_report.md"
    lines: list[str] = []
    lines.append("# Beta Transition Analysis (Dense M Sweep)")
    lines.append("")
    lines.append(f"- results_dir: `{args.results_dir}`")
    lines.append(f"- min_prob: `{args.min_prob}`")
    lines.append(f"- min_points: `{args.min_points}`")
    lines.append("")
    lines.append("## Per-M Summary")
    lines.append("| M | r_crit (p=0.5) | N (above r_crit) | beta (exp) | R^2_log | fit_valid |")
    lines.append("|---:|---:|---:|---:|---:|:---:|")
    for M in sorted(per_M.keys()):
        d = per_M[M]
        rcrit = d.get("r_crit")
        npts = d.get("num_points", 0)
        fit = d.get("exp_fit") or {}
        beta = fit.get("beta", float("nan"))
        r2 = fit.get("r2_log", float("nan"))
        valid = "yes" if d.get("fit_valid") else "no"
        lines.append(f"| {M} | {rcrit:.4f} | {npts} | {beta:.3f} | {r2:.3f} | {valid} |")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Fits with `N < min_points` are marked invalid; do not interpret their beta/R^2 as evidence of a universal law.")
    lines.append("- A dense ratio grid above r_crit is required to distinguish exponential vs power-law vs piecewise behavior.")
    lines.append("")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved: {out_md}")


if __name__ == "__main__":
    main()
