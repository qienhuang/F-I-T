#!/usr/bin/env python3
"""
Analyze "time-to-grok" vs distance-to-criticality for Li2 band_sweep runs.

Goal:
  Test whether the sharp drop in grok time above r_crit is better described as:
    - exponential decay in (r - r_crit):  T = A * exp(-beta * (r - r_crit))
    - power law in (r - r_crit):          T = K * (r - r_crit)^(-gamma)

Notes:
  - r_crit is estimated as the interpolated ratio where grok probability crosses 50%.
  - We analyze both:
      (a) grok_epoch  : epoch where test_acc first crosses threshold
      (b) grok_delay  : grok_epoch - mem_epoch, where mem_epoch is when train_acc first hits ~1.0
    This helps distinguish "true delayed grokking" from "early generalization".

Run from: experiments/li2_scaling_law/
  python analyze_grok_speed.py
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


RESULTS_DIR = Path("results/band_sweep")
OUTPUT_DIR = Path("results/band_sweep/analysis")


@dataclass(frozen=True)
class Run:
    seed: int
    grok_happened: bool
    grok_epoch: int | None
    final_test_acc: float
    mem_epoch: int | None
    grok_delay: int | None


def _parse_filename(stem: str) -> tuple[int, float, int]:
    parts = stem.split("_")
    # M{M}_ratio{ratio}_seed{seed}.json
    M = int(parts[0][1:])
    ratio = float(parts[1][5:])
    seed = int(parts[2][4:])
    return M, ratio, seed


def _find_first_epoch_at_or_above(epochs: list[int], values: list[float], threshold: float) -> int | None:
    for e, v in zip(epochs, values):
        if v >= threshold:
            return int(e)
    return None


def load_results(results_dir: Path) -> dict[tuple[int, float], list[Run]]:
    results: dict[tuple[int, float], list[Run]] = defaultdict(list)

    for json_file in sorted(results_dir.glob("M*.json")):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        M, ratio, seed = _parse_filename(json_file.stem)

        grok_happened = bool(data.get("grok_happened", False))
        grok_epoch = int(data.get("grok_epoch")) if grok_happened and data.get("grok_epoch") is not None else None
        final_test_acc = float(data.get("final_test_acc", 0.0))

        history = data.get("history", {}) or {}
        epochs = [int(x) for x in (history.get("epochs") or [])]
        train_acc = [float(x) for x in (history.get("train_acc") or [])]
        mem_epoch = _find_first_epoch_at_or_above(epochs, train_acc, threshold=0.99) if epochs and train_acc else None
        grok_delay = (grok_epoch - mem_epoch) if (grok_epoch is not None and mem_epoch is not None) else None

        results[(M, ratio)].append(
            Run(
                seed=seed,
                grok_happened=grok_happened,
                grok_epoch=grok_epoch,
                final_test_acc=final_test_acc,
                mem_epoch=mem_epoch,
                grok_delay=grok_delay,
            )
        )

    return results


def grok_probability(runs: list[Run]) -> float:
    if not runs:
        return 0.0
    return sum(1 for r in runs if r.grok_happened) / len(runs)


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.median(np.asarray(values, dtype=float)))


def summarize_by_ratio(runs_by_ratio: dict[float, list[Run]]) -> dict[float, dict]:
    out: dict[float, dict] = {}
    for ratio, runs in runs_by_ratio.items():
        grok_runs = [r for r in runs if r.grok_happened and r.grok_epoch is not None]
        epochs = [float(r.grok_epoch) for r in grok_runs if r.grok_epoch is not None]
        delays = [float(r.grok_delay) for r in grok_runs if r.grok_delay is not None]

        out[ratio] = {
            "num_runs": len(runs),
            "p_grok": grok_probability(runs),
            "grok_epoch_median": _median(epochs),
            "grok_delay_median": _median(delays),
            "final_test_acc_mean": float(np.mean([r.final_test_acc for r in runs])) if runs else 0.0,
        }
    return out


def estimate_rcrit_50(ratios: list[float], probs: list[float]) -> float | None:
    # Linear interpolation at first crossing of 0.5.
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
    return {"A": float(np.exp(a)), "beta": float(-b), "r2_log": r2}


def fit_powerlaw(delta_r: np.ndarray, t: np.ndarray) -> dict | None:
    # log(t) = log(K) - gamma * log(delta_r)
    x = np.asarray(delta_r, dtype=float)
    y = np.asarray(t, dtype=float)
    mask = (x > 0) & (y > 0)
    x, y = x[mask], y[mask]
    if len(x) < 2:
        return None
    a, b, r2 = _linear_fit(np.log(x), np.log(y))
    return {"K": float(np.exp(a)), "gamma": float(-b), "r2_log": r2}


def _select_points(summary: dict[float, dict], rcrit: float, *, min_prob: float, use_delay: bool) -> tuple[np.ndarray, np.ndarray, list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    ratios: list[float] = []
    for ratio in sorted(summary.keys()):
        if ratio <= rcrit:
            continue
        if float(summary[ratio]["p_grok"]) < min_prob:
            continue
        y = summary[ratio]["grok_delay_median"] if use_delay else summary[ratio]["grok_epoch_median"]
        if y is None:
            continue
        ratios.append(float(ratio))
        xs.append(float(ratio - rcrit))
        ys.append(float(y))
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float), ratios


def _plot_one(ax, ratios: list[float], y: np.ndarray, rcrit: float, fit: dict | None, fit_kind: str, title: str):
    ax.scatter(ratios, y, s=60, alpha=0.8, label="median")
    ax.axvline(rcrit, color="green", linestyle=":", alpha=0.6, label=f"r_crit≈{rcrit:.3f}")

    if fit and len(ratios) >= 2:
        r0, r1 = min(ratios), max(ratios)
        rr = np.linspace(r0, r1, 200)
        dr = rr - rcrit
        if fit_kind == "exp":
            A, beta = fit["A"], fit["beta"]
            yy = A * np.exp(-beta * dr)
            label = f"exp: beta={beta:.2f} (R^2_log={fit['r2_log']:.3f})"
        else:
            K, gamma = fit["K"], fit["gamma"]
            yy = K * np.power(dr, -gamma)
            label = f"power: gamma={gamma:.2f} (R^2_log={fit['r2_log']:.3f})"
        ax.plot(rr, yy, "r--", linewidth=2, label=label)

    ax.set_title(title)
    ax.set_xlabel("train_ratio")
    ax.set_ylabel("time-to-grok (epochs)")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output_dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--min_prob",
        type=float,
        default=1.0,
        help="Only fit points with grok probability >= this (e.g. 1.0 for 3/3).",
    )
    parser.add_argument(
        "--min_points",
        type=int,
        default=3,
        help="Minimum number of points above r_crit to treat a functional-form fit as meaningful (>=3 recommended).",
    )
    parser.add_argument("--use_delay", action="store_true", help="Fit grok_delay (= grok_epoch - mem_epoch) instead of grok_epoch.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_results(args.results_dir)
    by_M: dict[int, dict[float, list[Run]]] = defaultdict(lambda: defaultdict(list))
    for (M, ratio), runs in raw.items():
        by_M[M][ratio].extend(runs)

    per_M: dict[int, dict] = {}

    print("=" * 72)
    print("Grok speed analysis (time-to-grok vs distance to r_crit)")
    print("=" * 72)
    print(f"results_dir={args.results_dir}")
    print(f"min_prob={args.min_prob}  use_delay={args.use_delay}")

    for M in sorted(by_M.keys()):
        summary = summarize_by_ratio(by_M[M])
        ratios = sorted(summary.keys())
        probs = [float(summary[r]["p_grok"]) for r in ratios]
        rcrit = estimate_rcrit_50(ratios, probs)

        print("\n" + "-" * 72)
        print(f"M={M}")
        if rcrit is None:
            print("r_crit: (could not estimate)")
            continue
        print(f"r_crit (p_grok=0.5): {rcrit:.4f}")
        print("ratio : p_grok  grok_epoch_med  grok_delay_med")
        for r in ratios:
            p = summary[r]["p_grok"]
            ge = summary[r]["grok_epoch_median"]
            gd = summary[r]["grok_delay_median"]
            ge_s = f"{int(ge):>5d}" if ge is not None else "  None"
            gd_s = f"{int(gd):>5d}" if gd is not None else "  None"
            print(f"{r:0.3f} : {p:0.2f}    {ge_s}         {gd_s}")

        delta_r, t, fit_ratios = _select_points(summary, rcrit, min_prob=args.min_prob, use_delay=args.use_delay)
        if len(delta_r) < 2:
            print("fit: insufficient points (need >=2 above r_crit)")
            continue

        exp_fit = fit_exponential(delta_r, t)
        pow_fit = fit_powerlaw(delta_r, t)
        fit_valid = len(delta_r) >= int(args.min_points)
        if not fit_valid:
            print(
                f"NOTE: only {len(delta_r)} point(s) above r_crit; exponential vs power-law is not identifiable and any R^2 is not meaningful."
            )

        per_M[M] = {
            "r_crit": rcrit,
            "num_points": int(len(delta_r)),
            "fit_valid": bool(fit_valid),
            "points": [{"ratio": float(r), "delta_r": float(dr), "t": float(tt)} for r, dr, tt in zip(fit_ratios, delta_r, t)],
            "exp_fit": exp_fit,
            "power_fit": pow_fit,
            "use_delay": bool(args.use_delay),
            "min_prob": float(args.min_prob),
            "min_points": int(args.min_points),
        }

        if exp_fit:
            print(
                "exp fit:  T = A * exp(-beta * (r-r_crit))  "
                f"A={exp_fit['A']:.2e}  beta={exp_fit['beta']:.3f}  R^2_log={exp_fit['r2_log']:.3f}"
            )
        if pow_fit:
            print(
                "pow fit:  T = K * (r-r_crit)^(-gamma)     "
                f"K={pow_fit['K']:.2e}  gamma={pow_fit['gamma']:.3f}  R^2_log={pow_fit['r2_log']:.3f}"
            )

    out_json = args.output_dir / ("grok_speed_fit_delay.json" if args.use_delay else "grok_speed_fit.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(per_M, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out_json}")

    if not per_M:
        return

    Ms = sorted(per_M.keys())
    n = len(Ms)
    cols = 3 if n >= 3 else n
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4.5 * rows), squeeze=False)

    for i, M in enumerate(Ms):
        rcrit = float(per_M[M]["r_crit"])
        pts = per_M[M]["points"]
        ratios = [float(p["ratio"]) for p in pts]
        y = np.asarray([float(p["t"]) for p in pts], dtype=float)
        ax = axes[i // cols][i % cols]

        exp_fit = per_M[M]["exp_fit"]
        pow_fit = per_M[M]["power_fit"]
        if bool(per_M[M].get("fit_valid", False)):
            exp_r2 = exp_fit["r2_log"] if exp_fit else -np.inf
            pow_r2 = pow_fit["r2_log"] if pow_fit else -np.inf
            if exp_r2 >= pow_r2:
                fit_kind, fit = "exp", exp_fit
            else:
                fit_kind, fit = "power", pow_fit
        else:
            fit_kind, fit = "exp", None

        title = f"M={M} ({'delay' if args.use_delay else 'epoch'}), N={int(per_M[M].get('num_points', 0))}"
        _plot_one(ax, ratios, y, rcrit, fit, fit_kind, title)

    for j in range(n, rows * cols):
        axes[j // cols][j % cols].axis("off")

    plt.tight_layout()
    out_png = args.output_dir / ("grok_speed_fit_delay.png" if args.use_delay else "grok_speed_fit.png")
    plt.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Saved: {out_png}")


if __name__ == "__main__":
    main()
