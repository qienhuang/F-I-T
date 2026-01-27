#!/usr/bin/env python3
"""
Minimal non-LLM constrained search for toy world detectors.

- Randomly sample candidate pipelines from a small search space.
- Evaluate with FIT-style gates.
- Emit: run_log.jsonl, leaderboard_feasible.csv, failure_map.yaml

This is a demo: extend with bandit/SH/ES as needed.
"""
import argparse, json, os, random, csv, time, hashlib
from typing import Dict, Any, List, Tuple
from collections import defaultdict

from evaluate import load_traces, eval_candidate

def stable_id(payload: Dict[str, Any]) -> str:
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:10]

def write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    keys = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    run_log_path = os.path.join(args.outdir, "run_log.jsonl")

    runs = load_traces(args.traces)

    # fixed event/boundary for demo
    theta = 0.25
    delta_safe = 80
    H_pos = 120

    fpr_targets = [0.01, 0.05, 0.10]
    eps = 0.01
    floor_max = 0.20
    min_targets_ok = 2

    base_series_choices = ["magnetization", "density", "activity"]
    # Include intentionally degenerate scores to demonstrate failure_map behavior.
    # const_* will fail FPR-control gates because all NEG scores are tied.
    score_choices = ["var_y", "ac1_y", "trend_y", "const_1", "const_0"]
    windows = [25, 50, 100, 200]
    alphas = [0.0, 0.1, 0.2]

    feasible_rows = []
    failure_regions = defaultdict(lambda: {"count": 0, "examples": []})

    for i in range(args.n):
        cand = {
            "base_series": random.choice(base_series_choices),
            "score": random.choice(score_choices),
            "W": random.choice(windows),
            "alpha": random.choice(alphas),
        }
        cid = "we_det:" + stable_id(cand)
        res = eval_candidate(
            runs=runs,
            base_series=cand["base_series"],
            score=cand["score"],
            W=cand["W"],
            smoothing_alpha=cand["alpha"],
            theta=theta,
            delta_safe=delta_safe,
            H_pos=H_pos,
            fpr_targets=fpr_targets,
            eps=eps,
            floor_max=floor_max,
            min_targets_ok=min_targets_ok,
        )

        rec = {"t": time.time(), "candidate_id": cid, "candidate": cand, "result": res}
        with open(run_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        label = res.get("label", "INCONCLUSIVE")
        region = f'{cand["base_series"]}/{cand["score"]}/W{cand["W"]}/a{cand["alpha"]}'
        if label == "SUPPORTED_FOR_ALARM":
            util = res.get("utility", {})
            row = {
                "candidate_id": cid,
                "base_series": cand["base_series"],
                "score": cand["score"],
                "W": cand["W"],
                "alpha": cand["alpha"],
                "coverage@op": util.get("coverage"),
                "lead_time_median": util.get("lead_time_median"),
                "ok_targets": res.get("gate", {}).get("ok_targets"),
                "fpr_min": res.get("gate", {}).get("fpr_min"),
            }
            feasible_rows.append(row)
        else:
            failure_regions[label]["count"] += 1
            if len(failure_regions[label]["examples"]) < 5:
                failure_regions[label]["examples"].append({"candidate_id": cid, "region": region, "gate": res.get("gate", {})})

    # leaderboard
    feasible_rows.sort(key=lambda r: (r.get("coverage@op") or 0, r.get("lead_time_median") or -1), reverse=True)
    write_csv(os.path.join(args.outdir, "leaderboard_feasible.csv"), feasible_rows)

    # failure map (coarse)
    failure_map = {"schema_version": "v0.1", "entries": []}
    for label, info in failure_regions.items():
        failure_map["entries"].append({"label": label, "count": info["count"], "examples": info["examples"]})
    # write yaml-ish as json for simplicity (yaml optional)
    with open(os.path.join(args.outdir, "failure_map.yaml"), "w", encoding="utf-8") as f:
        f.write(json.dumps(failure_map, ensure_ascii=False, indent=2))

    print(f"Done. outdir={args.outdir}")
    print(f"Feasible: {len(feasible_rows)} / {args.n}")

if __name__ == "__main__":
    main()
