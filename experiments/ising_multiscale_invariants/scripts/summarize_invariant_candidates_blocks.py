from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def interval_overlap(a_lo: float | None, a_hi: float | None, b_lo: float | None, b_hi: float | None) -> bool | None:
    if None in (a_lo, a_hi, b_lo, b_hi):
        return None
    return not (a_hi < b_lo or b_hi < a_lo)


def get_pair(fp: dict, scheme: str, estimator: str, pair: str) -> dict | None:
    return fp.get(scheme, {}).get(estimator, {}).get(pair)


def fmt(x: float | None, nd: int = 4) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{float(x):.{nd}f}"


def to_row(rec: dict, block: str, scheme: str, estimator: str, pair: str) -> dict:
    boot = rec.get("bootstrap", {})
    xs = boot.get("x_star_iso", {})
    sl = boot.get("slope_abs_iso", {})
    if not sl:
        # Backward-compatible fallback
        sl = boot.get("slope_iso_stability", {})
    return {
        "block": block,
        "scheme": scheme,
        "estimator": estimator,
        "pair": pair,
        "saturation_label": rec.get("saturation_label"),
        "x_star_iso_mean": xs.get("mean"),
        "x_star_iso_ci_low": xs.get("ci_low"),
        "x_star_iso_ci_high": xs.get("ci_high"),
        "slope_abs_iso_mean": sl.get("abs_mean"),
        "slope_abs_iso_ci_low": sl.get("abs_ci_low"),
        "slope_abs_iso_ci_high": sl.get("abs_ci_high"),
        "slope_abs_iso_stability_label": sl.get("label"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--block_a_fixed",
        default="d:/FIT Lab/github/F-I-T/experiments/ising_multiscale_invariants/results/temp_compare_full/T2p10/fixed_points.json",
    )
    ap.add_argument(
        "--block_b_fixed",
        default="d:/FIT Lab/github/F-I-T/experiments/ising_multiscale_invariants/results/temp_compare_full_block_b/T2p10/fixed_points.json",
    )
    ap.add_argument("--out_csv", default="results/temp_compare_blocks/invariant_candidates_t210_block_ab.csv")
    ap.add_argument("--out_md", default="results/temp_compare_blocks/invariant_candidates_t210_block_ab.md")
    ap.add_argument("--schemes", nargs="+", default=["average", "majority", "threshold_low", "threshold_high"])
    ap.add_argument("--estimators", nargs="+", default=["C_frozen", "H_2x2"])
    ap.add_argument("--pairs", nargs="+", default=["1->2", "2->4"])
    args = ap.parse_args()

    a = json.loads(Path(args.block_a_fixed).read_text(encoding="utf-8"))
    b = json.loads(Path(args.block_b_fixed).read_text(encoding="utf-8"))

    rows = []
    overlaps = []
    for scheme in args.schemes:
        for estimator in args.estimators:
            for pair in args.pairs:
                ra = get_pair(a, scheme, estimator, pair)
                rb = get_pair(b, scheme, estimator, pair)
                if ra is None or rb is None:
                    continue

                row_a = to_row(ra, "A", scheme, estimator, pair)
                row_b = to_row(rb, "B", scheme, estimator, pair)
                rows.extend([row_a, row_b])

                both_testable = (
                    row_a["saturation_label"] == "TESTABLE" and row_b["saturation_label"] == "TESTABLE"
                )
                x_overlap = interval_overlap(
                    row_a["x_star_iso_ci_low"],
                    row_a["x_star_iso_ci_high"],
                    row_b["x_star_iso_ci_low"],
                    row_b["x_star_iso_ci_high"],
                )
                s_overlap = interval_overlap(
                    row_a["slope_abs_iso_ci_low"],
                    row_a["slope_abs_iso_ci_high"],
                    row_b["slope_abs_iso_ci_low"],
                    row_b["slope_abs_iso_ci_high"],
                )
                overlaps.append(
                    {
                        "scheme": scheme,
                        "estimator": estimator,
                        "pair": pair,
                        "both_testable": both_testable,
                        "x_star_ci_overlap": x_overlap,
                        "slope_abs_ci_overlap": s_overlap,
                        "candidate_consistent_ab": bool(both_testable and x_overlap and s_overlap),
                    }
                )

    df = pd.DataFrame(rows)
    ov = pd.DataFrame(overlaps)
    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    ov.to_csv(out_csv.with_name(out_csv.stem + "_overlap.csv"), index=False)

    lines = [
        "# Ising T=2.10 Invariant Candidates: Block A vs Block B",
        "",
        "Independent estimators only (`C_frozen`, `H_2x2`). `C_activity` is excluded because it is deterministically derived (`1 - C_frozen`).",
        "",
        "## Candidate Table (isotonic bootstrap)",
        "",
        "| Block | Scheme | Estimator | Pair | Saturation | x* mean [CI] | |slope| mean [CI] | Slope label |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in df.sort_values(["pair", "scheme", "estimator", "block"]).iterrows():
        lines.append(
            f"| {r['block']} | {r['scheme']} | {r['estimator']} | {r['pair']} | {r['saturation_label']} | "
            f"{fmt(r['x_star_iso_mean'])} [{fmt(r['x_star_iso_ci_low'])}, {fmt(r['x_star_iso_ci_high'])}] | "
            f"{fmt(r['slope_abs_iso_mean'])} [{fmt(r['slope_abs_iso_ci_low'])}, {fmt(r['slope_abs_iso_ci_high'])}] | "
            f"{r['slope_abs_iso_stability_label']} |"
        )

    lines.extend(
        [
            "",
            "## A/B CI Overlap And Consistency",
            "",
            "| Scheme | Estimator | Pair | Both testable | x* CI overlap | |slope| CI overlap | Candidate consistent (A/B) |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for _, r in ov.sort_values(["pair", "scheme", "estimator"]).iterrows():
        lines.append(
            f"| {r['scheme']} | {r['estimator']} | {r['pair']} | {r['both_testable']} | "
            f"{r['x_star_ci_overlap']} | {r['slope_abs_ci_overlap']} | {r['candidate_consistent_ab']} |"
        )

    req = ov[(ov["pair"].isin(["1->2", "2->4"])) & (ov["both_testable"])]
    n_req = int(len(req))
    n_cons = int(req["candidate_consistent_ab"].sum()) if n_req > 0 else 0
    rate = (n_cons / n_req) if n_req > 0 else None
    lines.extend(
        [
            "",
            "## Required-Pair Readout (`1->2`, `2->4`)",
            "",
            f"- Testable rows: `{n_req}`",
            f"- A/B consistent rows (`x*` CI overlap + `|slope|` CI overlap): `{n_cons}`",
            f"- Consistency rate: `{fmt(rate, 3) if rate is not None else 'n/a'}`",
            "",
            "Interpretation note:",
            "- This is a block-level consistency audit under fixed gates, not a pooled universality claim.",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_csv.with_name(out_csv.stem + '_overlap.csv')}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

