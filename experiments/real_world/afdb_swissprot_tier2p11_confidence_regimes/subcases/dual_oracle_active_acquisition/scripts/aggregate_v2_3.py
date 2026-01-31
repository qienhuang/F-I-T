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


def _step_hold_at_cost(cost_curve: np.ndarray, metric_curve: np.ndarray, cost: float) -> float:
    # step-hold last observed at or below cost; if before first point, return 0.0
    idx = int(np.searchsorted(cost_curve, float(cost), side="right") - 1)
    if idx < 0:
        return 0.0
    idx = min(idx, len(metric_curve) - 1)
    v = float(metric_curve[idx])
    if not np.isfinite(v):
        return 0.0
    return v


def _bootstrap_ci(values: np.ndarray, n_boot: int, ci: float, seed: int = 7) -> Tuple[float, float, float]:
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


def _bilevel_bootstrap_margin(
    cov_vec: np.ndarray,
    cost_vec: np.ndarray,
    baseline_cost_curves: List[np.ndarray],
    baseline_cov_curves: List[np.ndarray],
    q_high: float,
    n_boot: int,
    ci: float,
    rng_seed: int = 7,
) -> Tuple[float, float, float, float]:
    # Bilevel bootstrap:
    #   - resample baseline seeds with replacement
    #   - resample policy seeds with replacement
    #   - compute baseline upper (q_high) at each policy-seed cost under the baseline sample
    #   - margin statistic = mean over resampled policy seeds of (cov - baseline_upper_at_cost)
    # Returns: (mean, ci_low, ci_high, p_adv) where p_adv = P(margin_stat > 0)

    rng = np.random.default_rng(rng_seed)

    cov_vec = np.asarray(cov_vec, dtype=float)
    cost_vec = np.asarray(cost_vec, dtype=float)
    mask = np.isfinite(cov_vec) & np.isfinite(cost_vec)
    cov_vec = cov_vec[mask]
    cost_vec = cost_vec[mask]
    n_policy = len(cov_vec)
    n_base = len(baseline_cost_curves)
    if n_policy == 0 or n_base == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")

    # Precompute baseline cov at each policy cost for each baseline seed: B[b, i]
    B = np.zeros((n_base, n_policy), dtype=float)
    for b in range(n_base):
        cc = np.asarray(baseline_cost_curves[b], dtype=float)
        mm = np.asarray(baseline_cov_curves[b], dtype=float)
        if len(cc) == 0 or len(mm) == 0:
            continue
        n = min(len(cc), len(mm))
        cc = cc[:n]
        mm = mm[:n]
        for i in range(n_policy):
            B[b, i] = _step_hold_at_cost(cc, mm, float(cost_vec[i]))

    stats = []
    adv = 0
    for _ in range(int(n_boot)):
        idx_b = rng.integers(0, n_base, size=n_base)  # resample baseline seeds
        idx_p = rng.integers(0, n_policy, size=n_policy)  # resample policy seeds

        upper = np.quantile(B[idx_b, :], q_high, axis=0)
        m = float(np.mean(cov_vec[idx_p] - upper[idx_p]))
        stats.append(m)
        if m > 0:
            adv += 1

    stats = np.asarray(stats, dtype=float)
    lo = float(np.quantile(stats, (1-ci)/2))
    hi = float(np.quantile(stats, 1-(1-ci)/2))
    return float(np.mean(stats)), lo, hi, float(adv / max(1, len(stats)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main_run", required=True, help="path to out/MAIN (representative single run)")
    ap.add_argument("--baseline_root", required=True, help="path to baseline out_root containing BASE_*")
    ap.add_argument("--policy_root", required=True, help="path to policy out_root containing POLICY_*")
    args = ap.parse_args()

    main_run = Path(args.main_run)
    baseline_root = Path(args.baseline_root)
    policy_root = Path(args.policy_root)

    locked = read_locked_cfg(main_run)

    bcfg = (locked.get("robustness", {}) or {}).get("baseline", {}) or {}
    pcfg = (locked.get("robustness", {}) or {}).get("policy", {}) or {}
    bb = (locked.get("robustness", {}) or {}).get("bilevel_bootstrap", {}) or {}

    q_high = float(bb.get("baseline_upper_quantile", ((bcfg.get("aggregation", {}) or {}).get("band", {}) or {}).get("q_high", 0.90)))
    n_boot = int(bb.get("n_boot", 5000))
    ci = float(bb.get("ci", 0.95))
    rng_seed = int(bb.get("rng_seed", 7))

    # ---------- Load baseline curves ----------
    baseline_cost_curves = []
    baseline_cov_curves = []
    baseline_runs = sorted(baseline_root.glob("BASE_*"))
    for rd in baseline_runs:
        cs = read_json(rd / "cost_summary.json")
        byp = cs.get("by_policy", {}) or {}
        if not byp:
            continue
        ps = list(byp.keys())[0]
        c = np.asarray(byp[ps].get("total_cost_curve") or [], dtype=float)
        m = np.asarray(byp[ps].get("cov_joint_curve") or [], dtype=float)
        if len(c) and len(m):
            n = min(len(c), len(m))
            baseline_cost_curves.append(c[:n])
            baseline_cov_curves.append(m[:n])

    # baseline band for plotting/continuity
    q_low = float(((bcfg.get("aggregation", {}) or {}).get("band", {}) or {}).get("q_low", 0.10))
    q_high_band = float(((bcfg.get("aggregation", {}) or {}).get("band", {}) or {}).get("q_high", 0.90))

    if baseline_cost_curves:
        cost_grid = np.unique(np.concatenate([c for c in baseline_cost_curves if len(c)]))
        cost_grid = np.sort(cost_grid)
        mat = []
        for c, m in zip(baseline_cost_curves, baseline_cov_curves):
            vals = [_step_hold_at_cost(c, m, float(cc)) for cc in cost_grid]
            mat.append(vals)
        M = np.asarray(mat, dtype=float)
        mean = np.mean(M, axis=0)
        ql = np.quantile(M, q_low, axis=0)
        qh = np.quantile(M, q_high_band, axis=0)
    else:
        cost_grid = np.array([])
        mean = ql = qh = np.array([])

    write_json(main_run / "baseline_band.json", {
        "baseline_family": str(bcfg.get("family_policy", "random_hash__random_hash")),
        "seeds": list(bcfg.get("seeds", []) or []),
        "band": {"method":"quantile", "q_low": q_low, "q_high": q_high_band},
        "metrics": {"cov_joint_at_cost": {"grid_cost": cost_grid.tolist(), "mean": mean.tolist(), "q_low": ql.tolist(), "q_high": qh.tolist()}},
    })

    # ---------- Load representative policy list ----------
    pol_table_main = pd.read_csv(main_run / "policy_table.csv")
    policies = [str(x) for x in pol_table_main["policy"].tolist()]

    # Also write a single-run robust table (baseline-seed uncertainty only) for continuity with v2.0/v2.2.
    # This table is *not* used for v2.3 claims (claims use the bilevel table).
    rows_single = []
    for _, rr in pol_table_main.iterrows():
        pol = str(rr["policy"])
        final_cov = float(rr.get("final_cov_joint_at_cap", np.nan))
        final_cost = float(rr.get("total_cost_final", np.nan))

        if np.isfinite(final_cost) and baseline_cost_curves:
            vals = [_step_hold_at_cost(bc, bm, float(final_cost)) for bc, bm in zip(baseline_cost_curves, baseline_cov_curves)]
            base_upper = float(np.quantile(np.asarray(vals, dtype=float), q_high))
        else:
            base_upper = float("nan")

        margin = (final_cov - base_upper) if (np.isfinite(final_cov) and np.isfinite(base_upper)) else float("nan")

        # bootstrap margin over baseline seeds only (approx)
        if np.isfinite(final_cov) and np.isfinite(final_cost) and baseline_cost_curves:
            seed_vals = np.asarray([_step_hold_at_cost(bc, bm, float(final_cost)) for bc, bm in zip(baseline_cost_curves, baseline_cov_curves)], dtype=float)
            margin_samples = final_cov - seed_vals
            m_mean, m_lo, m_hi = _bootstrap_ci(margin_samples, n_boot=min(2000, n_boot), ci=ci, seed=rng_seed)
        else:
            m_mean = m_lo = m_hi = float("nan")

        rows_single.append({
            "policy": pol,
            "final_cov_joint_at_cap": final_cov,
            "total_cost_final": final_cost,
            "baseline_upper_at_final_cost": base_upper,
            "margin_vs_baseline_upper": margin,
            "dominance_margin_mean": m_mean,
            "dominance_margin_ci_low": m_lo,
            "dominance_margin_ci_high": m_hi,
            "claim_outperforms_random_allowed": bool(np.isfinite(m_lo) and m_lo > 0),
        })

    pd.DataFrame(rows_single).to_csv(main_run / "frontier_robust_table.csv", index=False)

    # ---------- Load policy seed runs ----------
    policy_runs = sorted(policy_root.glob("POLICY_*"))
    if not policy_runs:
        raise SystemExit(f"No POLICY_* runs in policy_root: {policy_root}")

    delay_grid = ((locked.get("event", {}) or {}).get("availability_delay_grid", None) or
                  [int((locked.get("event", {}) or {}).get("availability_delay_max_rounds", 0))])

    policy_band = {
        "policy_seeds": list(pcfg.get("seeds", []) or []),
        "band": {"method":"quantile", "q_low": q_low, "q_high": q_high_band},
        "policies": {}
    }
    jump_collect: Dict[str, List[Dict[str, Any]]] = {p: [] for p in policies}
    finals: Dict[str, List[Tuple[float, float]]] = {p: [] for p in policies}
    curves_by_policy: Dict[str, List[Tuple[np.ndarray, np.ndarray]]] = {p: [] for p in policies}

    for rd in policy_runs:
        pt = pd.read_csv(rd / "policy_table.csv")
        cs = read_json(rd / "cost_summary.json")
        byp = cs.get("by_policy", {}) or {}
        ev = read_json(rd / "event_summary.json") if (rd / "event_summary.json").exists() else {}

        for p in policies:
            row = pt[pt["policy"] == p]
            if not row.empty:
                rr = row.iloc[0]
                finals[p].append((float(rr.get("final_cov_joint_at_cap", np.nan)), float(rr.get("total_cost_final", np.nan))))

            if p in byp:
                c = np.asarray(byp[p].get("total_cost_curve") or [], dtype=float)
                m = np.asarray(byp[p].get("cov_joint_curve") or [], dtype=float)
                if len(c) and len(m):
                    n = min(len(c), len(m))
                    curves_by_policy[p].append((c[:n], m[:n]))

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
                "covjump_found": bool(cj.get("found", False)),
            })

    def envelope_quantiles(curves: List[Tuple[np.ndarray, np.ndarray]], qlq: float, qhq: float):
        if not curves:
            return np.array([]), np.array([]), np.array([]), np.array([])
        cg = np.unique(np.concatenate([c for c,_ in curves if len(c)]))
        cg = np.sort(cg)
        mat = []
        for c, m in curves:
            vals = [_step_hold_at_cost(c, m, float(cc)) for cc in cg]
            mat.append(vals)
        M = np.asarray(mat, dtype=float)
        return cg, np.mean(M, axis=0), np.quantile(M, qlq, axis=0), np.quantile(M, qhq, axis=0)

    for p in policies:
        cg, cm, cql, cqh = envelope_quantiles(curves_by_policy[p], q_low, q_high_band)
        policy_band["policies"][p] = {"grid_cost": cg.tolist(), "mean": cm.tolist(), "q_low": cql.tolist(), "q_high": cqh.tolist()}
    write_json(main_run / "policy_band.json", policy_band)

    # policy grid manifest
    manifest_src = policy_root / "policy_grid_manifest.json"
    if manifest_src.exists():
        write_json(main_run / "policy_grid_manifest.json", read_json(manifest_src))
    else:
        write_json(main_run / "policy_grid_manifest.json", {"note": "manifest missing", "policy_root": str(policy_root)})

    # ---------- Frontier tables ----------
    rows_policy = []
    rows_bi = []
    for p in policies:
        covs = np.asarray([x[0] for x in finals[p]], dtype=float)
        costs = np.asarray([x[1] for x in finals[p]], dtype=float)

        cov_mean, cov_lo, cov_hi = _bootstrap_ci(covs, n_boot=min(2000, n_boot), ci=ci, seed=rng_seed) if len(covs) else (np.nan, np.nan, np.nan)
        cost_mean, cost_lo, cost_hi = _bootstrap_ci(costs, n_boot=min(2000, n_boot), ci=ci, seed=rng_seed) if len(costs) else (np.nan, np.nan, np.nan)

        # policy-only margin vs baseline upper under full baseline seed set
        if len(covs) and baseline_cost_curves:
            upp = []
            for cst in costs:
                vals = [_step_hold_at_cost(bc, bm, float(cst)) for bc, bm in zip(baseline_cost_curves, baseline_cov_curves)]
                upp.append(float(np.quantile(np.asarray(vals, dtype=float), q_high)))
            upp = np.asarray(upp, dtype=float)
            margin_samples = covs - upp
            m_mean, m_lo, m_hi = _bootstrap_ci(margin_samples, n_boot=min(2000, n_boot), ci=ci, seed=rng_seed)
            allow = bool(np.isfinite(m_lo) and m_lo > 0)
        else:
            m_mean = m_lo = m_hi = np.nan
            allow = False

        rows_policy.append({
            "policy": p,
            "n_policy_seeds": int(len(covs)),
            "final_cov_joint_mean": cov_mean,
            "final_cov_joint_ci_low": cov_lo,
            "final_cov_joint_ci_high": cov_hi,
            "total_cost_final_mean": cost_mean,
            "total_cost_final_ci_low": cost_lo,
            "total_cost_final_ci_high": cost_hi,
            "dominance_margin_mean": m_mean,
            "dominance_margin_ci_low": m_lo,
            "dominance_margin_ci_high": m_hi,
            "claim_outperforms_random_allowed": allow,
        })

        bm_mean, bm_lo, bm_hi, p_adv = _bilevel_bootstrap_margin(
            cov_vec=covs,
            cost_vec=costs,
            baseline_cost_curves=baseline_cost_curves,
            baseline_cov_curves=baseline_cov_curves,
            q_high=q_high,
            n_boot=n_boot,
            ci=ci,
            rng_seed=rng_seed,
        )
        allow_bi = bool(np.isfinite(bm_lo) and bm_lo > 0)
        rows_bi.append({
            "policy": p,
            "n_policy_seeds": int(len(covs)),
            "n_baseline_seeds": int(len(baseline_cost_curves)),
            "bilevel_margin_mean": bm_mean,
            "bilevel_margin_ci_low": bm_lo,
            "bilevel_margin_ci_high": bm_hi,
            "bilevel_p_advantage": p_adv,
            "claim_outperforms_random_allowed": allow_bi,
        })

    pd.DataFrame(rows_policy).to_csv(main_run / "frontier_policy_robust_table.csv", index=False)
    df_bi = pd.DataFrame(rows_bi).sort_values(by=["claim_outperforms_random_allowed","bilevel_margin_mean"], ascending=[False, False])
    df_bi.to_csv(main_run / "frontier_bilevel_robust_table.csv", index=False)

    # claims gate report uses bilevel
    gate = {
        "mode": "bilevel_bootstrap",
        "rule": "allow 'outperforms random' only if bilevel_margin_ci_low > 0",
        "by_policy": {
            row["policy"]: {
                "bilevel_margin_ci_low": float(row["bilevel_margin_ci_low"]),
                "bilevel_margin_ci_high": float(row["bilevel_margin_ci_high"]),
                "allowed": bool(row["claim_outperforms_random_allowed"]),
            }
            for _, row in df_bi.iterrows()
        }
    }
    write_json(main_run / "claims_gate_report.json", gate)

    # jump robustness across policy seeds
    jump_out = {"availability_delay_grid": [int(x) for x in delay_grid], "by_policy": {}}
    for p, lst in jump_collect.items():
        rcj = np.asarray([x["r_covjump_joint"] for x in lst if x["r_covjump_joint"] is not None], dtype=float)
        rju = np.asarray([x["r_joint_usable"] for x in lst if x["r_joint_usable"] is not None], dtype=float)
        rcj_mean, rcj_lo, rcj_hi = _bootstrap_ci(rcj, n_boot=min(2000, n_boot), ci=ci, seed=rng_seed) if len(rcj) else (np.nan, np.nan, np.nan)
        rju_mean, rju_lo, rju_hi = _bootstrap_ci(rju, n_boot=min(2000, n_boot), ci=ci, seed=rng_seed) if len(rju) else (np.nan, np.nan, np.nan)

        probs = {}
        for d in delay_grid:
            counts = {"availability_driven": 0, "learning_driven": 0, "none": 0}
            for x in lst:
                if (not x.get("covjump_found", False)) or (x.get("jump_delay_rounds", None) is None):
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

    write_json(main_run / "bilevel_bootstrap_summary.json", {
        "n_boot": int(n_boot),
        "ci": float(ci),
        "rng_seed": int(rng_seed),
        "baseline_upper_quantile": float(q_high),
        "n_baseline_runs": int(len(baseline_cost_curves)),
        "n_policy_runs": int(len(policy_runs)),
    })

    print("v2.3 aggregation complete:")
    for f in [
        "baseline_band.json",
        "policy_band.json",
        "frontier_policy_robust_table.csv",
        "frontier_bilevel_robust_table.csv",
        "jump_robustness.json",
        "claims_gate_report.json",
        "bilevel_bootstrap_summary.json",
    ]:
        print("-", main_run / f)


if __name__ == "__main__":
    main()
