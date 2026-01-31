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
        n = min(len(c), len(m))
        mat.append(step_hold_values(cost_grid, c[:n], m[:n]))
    M = np.asarray(mat, dtype=float)

    mean = np.nanmean(M, axis=0)
    ql = np.nanquantile(M, q_low, axis=0)
    qh = np.nanquantile(M, q_high, axis=0)
    return cost_grid, mean, ql, qh


def bootstrap_ci(values: np.ndarray, n_boot: int, ci: float, seed: int = 7) -> Tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return float("nan"), float("nan"), float("nan")
    boots = []
    for _ in range(int(n_boot)):
        samp = rng.choice(v, size=len(v), replace=True)
        boots.append(float(np.mean(samp)))
    boots = np.asarray(boots, dtype=float)
    lo = float(np.quantile(boots, (1-ci)/2))
    hi = float(np.quantile(boots, 1-(1-ci)/2))
    return float(np.mean(boots)), lo, hi


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main_run", required=True, help="path to out/MAIN (single representative run)")
    ap.add_argument("--baseline_root", required=True, help="path to baseline out_root containing BASE_*")
    ap.add_argument("--policy_root", required=True, help="path to policy out_root containing POLICY_*")
    args = ap.parse_args()

    main_run = Path(args.main_run)
    baseline_root = Path(args.baseline_root)
    policy_root = Path(args.policy_root)

    locked = read_locked_cfg(main_run)

    # robustness params
    bcfg = (locked.get("robustness", {}) or {}).get("baseline", {}) or {}
    pcfg = (locked.get("robustness", {}) or {}).get("policy", {}) or {}
    q_low = float(((bcfg.get("aggregation", {}) or {}).get("band", {}) or {}).get("q_low", 0.10))
    q_high = float(((bcfg.get("aggregation", {}) or {}).get("band", {}) or {}).get("q_high", 0.90))
    n_boot = int(((locked.get("robustness", {}) or {}).get("bootstrap", {}) or {}).get("n_boot", 2000))
    ci = float(((locked.get("robustness", {}) or {}).get("bootstrap", {}) or {}).get("ci", 0.95))

    delay_grid = ((locked.get("event", {}) or {}).get("availability_delay_grid", None) or
                  [int((locked.get("event", {}) or {}).get("availability_delay_max_rounds", 0))])

    # ---------- Baseline band ----------
    baseline_curves = []
    baseline_seed_values_at_cost = {}  # run -> (cost, cov_joint)
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
            baseline_curves.append((c, m))
            baseline_seed_values_at_cost[rd.name] = (c, m)

    cost_grid, mean, ql, qh = envelope_quantiles(baseline_curves, q_low=q_low, q_high=q_high)

    def baseline_upper_at(cost: float) -> float:
        if len(cost_grid) == 0:
            return float("nan")
        idx = np.searchsorted(cost_grid, float(cost), side="right") - 1
        if idx < 0:
            return float("nan")
        return float(qh[idx])

    baseline_band = {
        "baseline_family": str(bcfg.get("family_policy", "random_hash__random_hash")),
        "seeds": list(bcfg.get("seeds", []) or []),
        "band": {"method":"quantile", "q_low": q_low, "q_high": q_high},
        "metrics": {"cov_joint_at_cost": {"grid_cost": cost_grid.tolist(), "mean": mean.tolist(), "q_low": ql.tolist(), "q_high": qh.tolist()}},
    }
    write_json(main_run / "baseline_band.json", baseline_band)

# Also write a single-run robust table (v2.0-style) for continuity.
# This is *not* the main robustness result in v2.2; the main result is policy-seed robust.
pol_main = pd.read_csv(main_run / "policy_table.csv")
rows_single = []
for _, rr in pol_main.iterrows():
    pol = str(rr["policy"])
    final_cov = float(rr.get("final_cov_joint_at_cap", np.nan))
    final_cost = float(rr.get("total_cost_final", np.nan))
    bu = baseline_upper_at(final_cost)
    margin = final_cov - bu if np.isfinite(final_cov) and np.isfinite(bu) else np.nan

    # baseline-seed sampling at this cost (approx)
    seed_vals = []
    for _, (c, m) in baseline_seed_values_at_cost.items():
        idx = np.searchsorted(c, float(final_cost), side="right") - 1
        if idx >= 0:
            seed_vals.append(float(m[idx]))
    seed_vals = np.asarray(seed_vals, dtype=float)
    if len(seed_vals):
        margin_samples = final_cov - seed_vals
        mean_m, lo, hi = bootstrap_ci(margin_samples, n_boot=n_boot, ci=ci)
    else:
        mean_m, lo, hi = float("nan"), float("nan"), float("nan")

    rows_single.append({
        "policy": pol,
        "final_cov_joint_at_cap": final_cov,
        "total_cost_final": final_cost,
        "baseline_band_upper_at_final_cost": bu,
        "margin_vs_baseline_upper": margin,
        "dominance_margin_mean": mean_m,
        "dominance_margin_ci_low": lo,
        "dominance_margin_ci_high": hi,
        "claim_outperforms_random_allowed": bool(np.isfinite(lo) and lo > 0),
    })

pd.DataFrame(rows_single).to_csv(main_run / "frontier_robust_table.csv", index=False)


    # ---------- Policy band + robust table ----------
    # Collect per-seed runs
    policy_runs = sorted(policy_root.glob("POLICY_*"))
    if not policy_runs:
        raise SystemExit(f"No POLICY_* runs in policy_root: {policy_root}")

    # Determine policy list from the representative main run (policy_table.csv)
    pol_table_main = pd.read_csv(main_run / "policy_table.csv")
    policies = [str(x) for x in pol_table_main["policy"].tolist()]

    # For each policy, gather curves and final points across seeds
    policy_band = {
        "policy_seeds": list(pcfg.get("seeds", []) or []),
        "band": {"method":"quantile", "q_low": q_low, "q_high": q_high},
        "policies": {}
    }

    robust_rows = []

    # Preload event summaries for jump robustness
    jump_collect: Dict[str, List[Dict[str, Any]]] = {p: [] for p in policies}

    for p in policies:
        curves = []
        finals_cov = []
        finals_cost = []
        margins = []
        # For each seed run, load its policy_table and cost_summary and extract this policy
        for rd in policy_runs:
            pt = pd.read_csv(rd / "policy_table.csv")
            # find row
            row = pt[pt["policy"] == p]
            if row.empty:
                continue
            row = row.iloc[0]
            final_cov = float(row.get("final_cov_joint_at_cap", np.nan))
            final_cost = float(row.get("total_cost_final", np.nan))
            finals_cov.append(final_cov)
            finals_cost.append(final_cost)
            bu = baseline_upper_at(final_cost)
            if np.isfinite(final_cov) and np.isfinite(bu):
                margins.append(final_cov - bu)

            # curve
            cs = read_json(rd / "cost_summary.json")
            byp = cs.get("by_policy", {}) or {}
            if p in byp:
                c = np.asarray(byp[p].get("total_cost_curve") or [], dtype=float)
                m = np.asarray(byp[p].get("cov_joint_curve") or [], dtype=float)
                if len(c) and len(m):
                    n = min(len(c), len(m))
                    curves.append((c[:n], m[:n]))

            # jump info from event_summary.json
            if (rd / "event_summary.json").exists():
                ev = read_json(rd / "event_summary.json")
                e = (ev.get("events_by_policy", {}) or {}).get(p, {}) or {}
                ju = e.get("E_joint_usable", {}) or {}
                cj = e.get("E_covjump_joint", {}) or {}
                r_ju = ju.get("round_index", None)
                r_cj = cj.get("round_index", None) if bool(cj.get("found", False)) else None
                delay = (int(r_cj) - int(r_ju)) if (r_ju is not None and r_cj is not None) else None
                jump_collect[p].append({
                    "run": rd.name,
                    "r_joint_usable": r_ju,
                    "r_covjump_joint": r_cj,
                    "jump_delay_rounds": delay,
                    "covjump_found": bool(cj.get("found", False))
                })

        finals_cov_arr = np.asarray(finals_cov, dtype=float)
        finals_cost_arr = np.asarray(finals_cost, dtype=float)
        margins_arr = np.asarray(margins, dtype=float)

        cov_mean, cov_lo, cov_hi = bootstrap_ci(finals_cov_arr, n_boot=n_boot, ci=ci) if len(finals_cov_arr) else (np.nan, np.nan, np.nan)
        cost_mean, cost_lo, cost_hi = bootstrap_ci(finals_cost_arr, n_boot=n_boot, ci=ci) if len(finals_cost_arr) else (np.nan, np.nan, np.nan)
        m_mean, m_lo, m_hi = bootstrap_ci(margins_arr, n_boot=n_boot, ci=ci) if len(margins_arr) else (np.nan, np.nan, np.nan)

        robust_rows.append({
            "policy": p,
            "n_policy_seeds": int(len(finals_cov_arr)),
            "final_cov_joint_mean": cov_mean,
            "final_cov_joint_ci_low": cov_lo,
            "final_cov_joint_ci_high": cov_hi,
            "total_cost_final_mean": cost_mean,
            "total_cost_final_ci_low": cost_lo,
            "total_cost_final_ci_high": cost_hi,
            "dominance_margin_mean": m_mean,
            "dominance_margin_ci_low": m_lo,
            "dominance_margin_ci_high": m_hi,
            "claim_outperforms_random_allowed": bool(np.isfinite(m_lo) and m_lo > 0),
        })

        # band curves per policy
        if curves:
            cg, cmean, cql, cqh = envelope_quantiles(curves, q_low=q_low, q_high=q_high)
            policy_band["policies"][p] = {
                "grid_cost": cg.tolist(),
                "mean": cmean.tolist(),
                "q_low": cql.tolist(),
                "q_high": cqh.tolist(),
            }
        else:
            policy_band["policies"][p] = {"grid_cost": [], "mean": [], "q_low": [], "q_high": []}

    robust_df = pd.DataFrame(robust_rows).sort_values(by=["claim_outperforms_random_allowed", "dominance_margin_mean"], ascending=[False, False])
    robust_df.to_csv(main_run / "frontier_policy_robust_table.csv", index=False)
    write_json(main_run / "policy_band.json", policy_band)

    # ---------- policy grid manifest copy ----------
    manifest_src = policy_root / "policy_grid_manifest.json"
    if manifest_src.exists():
        write_json(main_run / "policy_grid_manifest.json", read_json(manifest_src))
    else:
        write_json(main_run / "policy_grid_manifest.json", {"note": "manifest missing in policy_root", "policy_root": str(policy_root)})

    # ---------- jump robustness aggregation ----------
    jump_out = {"availability_delay_grid": [int(x) for x in delay_grid], "by_policy": {}}
    for p, lst in jump_collect.items():
        # numeric arrays
        rju = np.asarray([x["r_joint_usable"] for x in lst if x["r_joint_usable"] is not None], dtype=float)
        rcj = np.asarray([x["r_covjump_joint"] for x in lst if x["r_covjump_joint"] is not None], dtype=float)

        rju_mean, rju_lo, rju_hi = bootstrap_ci(rju, n_boot=n_boot, ci=ci) if len(rju) else (np.nan, np.nan, np.nan)
        rcj_mean, rcj_lo, rcj_hi = bootstrap_ci(rcj, n_boot=n_boot, ci=ci) if len(rcj) else (np.nan, np.nan, np.nan)

        # jump type probs by delay threshold
        probs = {}
        for d in delay_grid:
            counts = {"availability_driven": 0, "learning_driven": 0, "none": 0}
            for x in lst:
                if not x.get("covjump_found", False) or x.get("jump_delay_rounds", None) is None:
                    counts["none"] += 1
                else:
                    counts["availability_driven" if int(x["jump_delay_rounds"]) <= int(d) else "learning_driven"] += 1
            tot = sum(counts.values()) or 1
            probs[str(int(d))] = {k: counts[k]/tot for k in counts}

        jump_out["by_policy"][p] = {
            "n_policy_seeds": int(len(lst)),
            "r_joint_usable": {"mean": rju_mean, "ci_low": rju_lo, "ci_high": rju_hi},
            "r_covjump_joint": {"mean": rcj_mean, "ci_low": rcj_lo, "ci_high": rcj_hi},
            "jump_type_prob_by_delay": probs,
        }

    write_json(main_run / "jump_robustness.json", jump_out)

    # ---------- claims gate report (v2.2 uses policy-robust table) ----------
    gate = {
        "rule": "allow 'outperforms random' only if dominance_margin_ci_low > 0 (policy-seed robust)",
        "by_policy": {
            row["policy"]: {
                "dominance_margin_ci_low": float(row["dominance_margin_ci_low"]),
                "dominance_margin_ci_high": float(row["dominance_margin_ci_high"]),
                "allowed": bool(row["claim_outperforms_random_allowed"]),
            }
            for _, row in robust_df.iterrows()
        }
    }
    write_json(main_run / "claims_gate_report.json", gate)

    print("v2.2 aggregation complete:")
    for f in ["baseline_band.json", "policy_band.json", "frontier_policy_robust_table.csv", "jump_robustness.json", "claims_gate_report.json", "policy_grid_manifest.json"]:
        print("-", main_run / f)


if __name__ == "__main__":
    main()
