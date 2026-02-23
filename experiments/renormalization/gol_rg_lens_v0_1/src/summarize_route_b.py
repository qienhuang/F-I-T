from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def decide(df: pd.DataFrame, rmse_threshold: float, near_bound_threshold: float, saturation_fraction_gate: float, min_non_saturated_pairs: int) -> dict:
    labels = df["label"].fillna("MISSING")
    counts = labels.value_counts().to_dict()

    supported = int(counts.get("SUPPORTED", 0))
    challenged = int(counts.get("CHALLENGED", 0))
    scoped = int(counts.get("SCOPE_LIMITED_SATURATION", 0))
    missing = int(counts.get("MISSING", 0))
    total = int(len(df))

    n_eval = int((df["n_evaluated_semigroup_triples"].fillna(0) > 0).sum())
    n_sat = scoped

    if challenged > 0:
        verdict = "NONCLOSURE_OR_CHALLENGED"
        rationale = "At least one evaluated configuration exceeds RMSE threshold."
    elif supported > 0:
        verdict = "SUPPORTED_WITH_SCOPE_LIMITS" if scoped > 0 else "SUPPORTED"
        rationale = "No challenged cells; semigroup closure holds on evaluated non-saturated cells."
    else:
        verdict = "INCONCLUSIVE"
        rationale = "No supported and no challenged cells; likely all scope-limited or missing."

    return {
        "verdict": verdict,
        "rationale": rationale,
        "counts": {
            "total": total,
            "evaluated_cells": n_eval,
            "saturated_scope_limited_cells": n_sat,
            "supported": supported,
            "scope_limited_saturation": scoped,
            "challenged": challenged,
            "missing": missing,
        },
        "thresholds": {
            "rmse_threshold": rmse_threshold,
            "near_bound_threshold": near_bound_threshold,
            "saturation_fraction_gate": saturation_fraction_gate,
            "min_non_saturated_adjacent_pairs": min_non_saturated_pairs,
        },
    }


def write_markdown(df: pd.DataFrame, decision: dict, out_md: Path) -> None:
    lines = []
    lines.append("# Route B Hard-Gate Summary (Semigroup Closure)")
    lines.append("")
    lines.append(f"- Verdict: **{decision['verdict']}**")
    lines.append(f"- Rationale: {decision['rationale']}")
    c = decision["counts"]
    th = decision["thresholds"]
    lines.append("")
    lines.append("## Decision Table")
    lines.append("")
    lines.append("| N | N_eval | N_sat | rmse_th | near_bound_th | sat_frac_gate | min_non_sat_pairs |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| {c['total']} | {c['evaluated_cells']} | {c['saturated_scope_limited_cells']} | "
        f"{th['rmse_threshold']:.3f} | {th['near_bound_threshold']:.3f} | "
        f"{th['saturation_fraction_gate']:.3f} | {th['min_non_saturated_adjacent_pairs']} |"
    )
    lines.append("")
    lines.append(
        f"- Counts: supported={c['supported']}, scope_limited_saturation={c['scope_limited_saturation']}, "
        f"challenged={c['challenged']}, missing={c['missing']}"
    )
    lines.append("")
    lines.append("## Matrix")
    lines.append("")
    lines.append("| Scheme | Estimator | Label | Best RMSE | Non-sat pairs | Evaluated triples |")
    lines.append("|---|---|---|---:|---:|---:|")
    for _, r in df.iterrows():
        rmse = ""
        if pd.notna(r.get("best_rmse_composed_vs_direct")):
            rmse = f"{float(r['best_rmse_composed_vs_direct']):.6f}"
        n1 = "" if pd.isna(r.get("n_non_saturated_adjacent_pairs")) else str(int(r["n_non_saturated_adjacent_pairs"]))
        n2 = "" if pd.isna(r.get("n_evaluated_semigroup_triples")) else str(int(r["n_evaluated_semigroup_triples"]))
        lines.append(f"| {r['scheme']} | {r['estimator']} | {r['label']} | {rmse} | {n1} | {n2} |")
    lines.append("")
    lines.append("## Decision Rule (v0.1)")
    lines.append("")
    lines.append("- Any `CHALLENGED` cell => `NONCLOSURE_OR_CHALLENGED`.")
    lines.append("- No `CHALLENGED` and >=1 `SUPPORTED` cell => `SUPPORTED` (or `SUPPORTED_WITH_SCOPE_LIMITS` if saturation exists).")
    lines.append("- Otherwise => `INCONCLUSIVE`.")
    lines.append("")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix_csv", default="out/scheme_matrix_v0_1.csv")
    ap.add_argument("--out_json", default="out/route_b_hard_gate_summary.json")
    ap.add_argument("--out_md", default="out/route_b_hard_gate_summary.md")
    ap.add_argument("--rmse_threshold", type=float, default=0.05)
    ap.add_argument("--near_bound_threshold", type=float, default=0.1)
    ap.add_argument("--saturation_fraction_gate", type=float, default=0.9)
    ap.add_argument("--min_non_saturated_pairs", type=int, default=2)
    args = ap.parse_args()

    df = pd.read_csv(args.matrix_csv)
    decision = decide(
        df,
        rmse_threshold=args.rmse_threshold,
        near_bound_threshold=args.near_bound_threshold,
        saturation_fraction_gate=args.saturation_fraction_gate,
        min_non_saturated_pairs=args.min_non_saturated_pairs,
    )

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(df, decision, out_md)

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
