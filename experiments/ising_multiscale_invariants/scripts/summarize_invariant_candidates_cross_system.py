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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--langton_fixed",
        default="d:/FIT Lab/github/F-I-T/experiments/langton_multiscale_invariants/results/fixed_points.json",
    )
    ap.add_argument(
        "--ising_fixed",
        default="d:/FIT Lab/github/F-I-T/experiments/ising_multiscale_invariants/results/temp_compare_full/T2p10/fixed_points.json",
    )
    ap.add_argument("--out_csv", default="results/invariant_candidates_langton_vs_ising_t210.csv")
    ap.add_argument("--out_md", default="results/invariant_candidates_langton_vs_ising_t210.md")
    ap.add_argument("--schemes", nargs="+", default=["average", "majority"])
    ap.add_argument("--estimators", nargs="+", default=["C_frozen", "H_2x2"])
    ap.add_argument("--pairs", nargs="+", default=["1->2", "2->4"])
    args = ap.parse_args()

    langton = json.loads(Path(args.langton_fixed).read_text(encoding="utf-8"))
    ising = json.loads(Path(args.ising_fixed).read_text(encoding="utf-8"))

    rows = []
    overlap_rows = []
    for scheme in args.schemes:
        for estimator in args.estimators:
            for pair in args.pairs:
                a = get_pair(langton, scheme, estimator, pair)
                b = get_pair(ising, scheme, estimator, pair)
                if a is None or b is None:
                    continue

                def ext(x: dict, sysname: str) -> dict:
                    boot = x.get("bootstrap", {})
                    xs = boot.get("x_star_iso", {})
                    sl = boot.get("slope_iso_stability", {})
                    return {
                        "system": sysname,
                        "scheme": scheme,
                        "estimator": estimator,
                        "pair": pair,
                        "saturation_label": x.get("saturation_label"),
                        "x_star_iso_mean": xs.get("mean"),
                        "x_star_iso_ci_low": xs.get("ci_low"),
                        "x_star_iso_ci_high": xs.get("ci_high"),
                        "slope_abs_iso_mean": sl.get("abs_mean"),
                        "slope_abs_iso_ci_low": sl.get("abs_ci_low"),
                        "slope_abs_iso_ci_high": sl.get("abs_ci_high"),
                        "slope_abs_iso_stability_label": sl.get("label"),
                    }

                ra = ext(a, "Langton")
                rb = ext(b, "Ising_T2.10")
                rows.extend([ra, rb])

                overlap_rows.append(
                    {
                        "scheme": scheme,
                        "estimator": estimator,
                        "pair": pair,
                        "x_star_ci_overlap": interval_overlap(
                            ra["x_star_iso_ci_low"],
                            ra["x_star_iso_ci_high"],
                            rb["x_star_iso_ci_low"],
                            rb["x_star_iso_ci_high"],
                        ),
                        "slope_abs_ci_overlap": interval_overlap(
                            ra["slope_abs_iso_ci_low"],
                            ra["slope_abs_iso_ci_high"],
                            rb["slope_abs_iso_ci_low"],
                            rb["slope_abs_iso_ci_high"],
                        ),
                    }
                )

    df = pd.DataFrame(rows)
    ov = pd.DataFrame(overlap_rows)
    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    ov.to_csv(out_csv.with_name(out_csv.stem + "_overlap.csv"), index=False)

    lines = [
        "# Invariant Candidates: Langton vs Ising (T=2.10)",
        "",
        "Independent estimators only (`C_frozen`, `H_2x2`). `C_activity` is intentionally excluded as it is deterministically derived from `C_frozen`.",
        "",
        "## Candidate Table (isotonic bootstrap)",
        "",
        "| System | Scheme | Estimator | Pair | Saturation | x* mean [CI] | |slope| mean [CI] | Slope label |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in df.sort_values(["pair", "scheme", "estimator", "system"]).iterrows():
        lines.append(
            f"| {r['system']} | {r['scheme']} | {r['estimator']} | {r['pair']} | {r['saturation_label']} | "
            f"{fmt(r['x_star_iso_mean'])} [{fmt(r['x_star_iso_ci_low'])}, {fmt(r['x_star_iso_ci_high'])}] | "
            f"{fmt(r['slope_abs_iso_mean'])} [{fmt(r['slope_abs_iso_ci_low'])}, {fmt(r['slope_abs_iso_ci_high'])}] | "
            f"{r['slope_abs_iso_stability_label']} |"
        )

    lines.extend(
        [
            "",
            "## Cross-System CI Overlap",
            "",
            "| Scheme | Estimator | Pair | x* CI overlap | |slope| CI overlap |",
            "|---|---|---|---|---|",
        ]
    )
    for _, r in ov.sort_values(["pair", "scheme", "estimator"]).iterrows():
        lines.append(
            f"| {r['scheme']} | {r['estimator']} | {r['pair']} | {r['x_star_ci_overlap']} | {r['slope_abs_ci_overlap']} |"
        )

    lines.extend(
        [
            "",
            "Notes:",
            "- This is a candidate-level comparison, not a universality claim.",
            "- Interpretation remains conditioned on non-saturated labels and preregistered gates.",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_csv.with_name(out_csv.stem + '_overlap.csv')}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
