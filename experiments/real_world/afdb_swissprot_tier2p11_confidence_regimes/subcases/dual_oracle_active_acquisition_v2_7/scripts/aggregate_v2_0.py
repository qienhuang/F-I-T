from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import yaml
import numpy as np
import pandas as pd


def read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def read_locked_cfg(run_dir: Path) -> Dict[str, Any]:
    locked = run_dir / "PREREG.locked.yaml"
    return yaml.safe_load(locked.read_text(encoding="utf-8"))


def step_hold_values(cost_grid: np.ndarray, c: np.ndarray, m: np.ndarray) -> np.ndarray:
    # For each cost in grid, take last value at or below it (step-hold)
    out = []
    for cc in cost_grid:
        idx = np.searchsorted(c, cc, side="right") - 1
        out.append(float(m[idx]) if idx >= 0 else np.nan)
    return np.asarray(out, dtype=float)


def envelope_quantiles(curves: List[Tuple[np.ndarray, np.ndarray]], q_low: float, q_high: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    costs = [c for c, _ in curves if len(c)]
    if not costs:
        return np.array([]), np.array([]), np.array([]), np.array([])
    cost_grid = np.unique(np.concatenate(costs))
    cost_grid = np.sort(cost_grid)

    mat = []
    for c, m in curves:
        if len(c) == 0:
            continue
        n = min(len(c), len(m))
        mat.append(step_hold_values(cost_grid, c[:n], m[:n]))
    M = np.asarray(mat, dtype=float)

    mean = np.nanmean(M, axis=0)
    ql = np.nanquantile(M, q_low, axis=0)
    qh = np.nanquantile(M, q_high, axis=0)
    return cost_grid, mean, ql, qh


def bootstrap_ci(values: np.ndarray, n_boot: int, ci: float, seed: int = 7) -> Tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    vals = []
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return float("nan"), float("nan"), float("nan")
    for _ in range(int(n_boot)):
        samp = rng.choice(v, size=len(v), replace=True)
        vals.append(float(np.mean(samp)))
    vals = np.asarray(vals, dtype=float)
    lo = float(np.quantile(vals, (1-ci)/2))
    hi = float(np.quantile(vals, 1-(1-ci)/2))
    return float(np.mean(vals)), lo, hi


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main_run", required=True, help="path to out/MAIN")
    ap.add_argument("--baseline_root", required=True, help="path to baseline out_root containing BASE_*")
    args = ap.parse_args()

    main_run = Path(args.main_run)
    baseline_root = Path(args.baseline_root)

    policy_table = pd.read_csv(main_run / "policy_table.csv")
    cost_summary = read_json(main_run / "cost_summary.json")
    locked = read_locked_cfg(main_run)

    q_low = float((((locked.get("robustness", {}) or {}).get("baseline", {}) or {}).get("aggregation", {}) or {}).get("band", {}).get("q_low", 0.10))
    q_high = float((((locked.get("robustness", {}) or {}).get("baseline", {}) or {}).get("aggregation", {}) or {}).get("band", {}).get("q_high", 0.90))
    n_boot = int(((locked.get("robustness", {}) or {}).get("bootstrap", {}) or {}).get("n_boot", 2000))
    ci = float(((locked.get("robustness", {}) or {}).get("bootstrap", {}) or {}).get("ci", 0.95))

    # Collect baseline curves
    curves = []
    baseline_seed_values_at_cost = {}  # seed run -> (cost, cov)
    for rd in sorted(baseline_root.glob("BASE_*")):
        cs = read_json(rd / "cost_summary.json")
        byp = cs.get("by_policy", {}) or {}
        if not byp:
            continue
        ps = list(byp.keys())[0]
        c = np.asarray(byp[ps].get("total_cost_curve") or [], dtype=float)
        m = np.asarray(byp[ps].get("cov_joint_curve") or [], dtype=float)
        if len(c) and len(m):
            n = min(len(c), len(m))
            c = c[:n]
            m = m[:n]
            curves.append((c, m))
            baseline_seed_values_at_cost[rd.name] = (c, m)

    cost_grid, mean, ql, qh = envelope_quantiles(curves, q_low=q_low, q_high=q_high)

    baseline_band = {
        "baseline_family": str((((locked.get("robustness", {}) or {}).get("baseline", {}) or {}).get("family_policy", "random_hash__random_hash"))),
        "seeds": list((((locked.get("robustness", {}) or {}).get("baseline", {}) or {}).get("seeds", [])) or []),
        "band": {"method": "quantile", "q_low": q_low, "q_high": q_high},
        "metrics": {
            "cov_joint_at_cost": {
                "grid_cost": cost_grid.tolist(),
                "mean": mean.tolist(),
                "q_low": ql.tolist(),
                "q_high": qh.tolist(),
            }
        },
    }
    write_json(main_run / "baseline_band.json", baseline_band)

    # helper: baseline upper at cost
    def baseline_upper_at(cost: float) -> float:
        if len(cost_grid) == 0:
            return float("nan")
        idx = np.searchsorted(cost_grid, float(cost), side="right") - 1
        if idx < 0:
            return float("nan")
        return float(qh[idx])

    rows = []
    for _, r in policy_table.iterrows():
        pol = str(r["policy"])
        final_cov = float(r.get("final_cov_joint_at_cap", np.nan))
        final_cost = float(r.get("total_cost_final", np.nan))
        base_up = baseline_upper_at(final_cost)
        margin = final_cov - base_up if np.isfinite(base_up) else np.nan

        # approximate margin CI by bootstrapping baseline seeds' cov at the final_cost
        seed_vals = []
        for _, (c, m) in baseline_seed_values_at_cost.items():
            idx = np.searchsorted(c, float(final_cost), side="right") - 1
            if idx >= 0:
                seed_vals.append(float(m[idx]))
        seed_vals = np.asarray(seed_vals, dtype=float)
        if len(seed_vals):
            # treat margin samples as (final_cov - sampled_baseline_value)
            margin_samples = final_cov - seed_vals
            mean_m, lo, hi = bootstrap_ci(margin_samples, n_boot=n_boot, ci=ci)
        else:
            mean_m, lo, hi = float("nan"), float("nan"), float("nan")

        rows.append({
            "policy": pol,
            "final_cov_joint_at_cap": final_cov,
            "total_cost_final": final_cost,
            "baseline_band_upper_at_final_cost": base_up,
            "margin_vs_baseline_upper": margin,
            "dominance_margin_mean": mean_m,
            "dominance_margin_ci_low": lo,
            "dominance_margin_ci_high": hi,
            "claim_outperforms_random_allowed": bool(np.isfinite(lo) and lo > 0),
        })

    robust = pd.DataFrame(rows).sort_values(by=["claim_outperforms_random_allowed", "dominance_margin_mean"], ascending=[False, False])
    robust.to_csv(main_run / "frontier_robust_table.csv", index=False)

    # claims gate
    gate = {
        "rule": "allow 'outperforms random' only if dominance_margin_ci_low > 0",
        "by_policy": {
            row["policy"]: {
                "dominance_margin_ci_low": float(row["dominance_margin_ci_low"]),
                "dominance_margin_ci_high": float(row["dominance_margin_ci_high"]),
                "allowed": bool(row["claim_outperforms_random_allowed"]),
            }
            for _, row in robust.iterrows()
        }
    }
    write_json(main_run / "claims_gate_report.json", gate)

    # jump robustness placeholder: reuse sensitivity mapping from main run
    if (main_run / "jump_type_sensitivity.json").exists():
        write_json(main_run / "jump_robustness.json", read_json(main_run / "jump_type_sensitivity.json"))
    else:
        write_json(main_run / "jump_robustness.json", {})

    print("v2.0 aggregation complete:")
    print("-", main_run / "baseline_band.json")
    print("-", main_run / "frontier_robust_table.csv")
    print("-", main_run / "claims_gate_report.json")
    print("-", main_run / "jump_robustness.json")


if __name__ == "__main__":
    main()
