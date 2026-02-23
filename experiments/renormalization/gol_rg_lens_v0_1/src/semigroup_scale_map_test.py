from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.isotonic import IsotonicRegression


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0.0:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def bin_conditional_std(x: np.ndarray, y: np.ndarray, n_bins: int = 20) -> Dict[str, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < n_bins * 5:
        n_bins = max(5, len(x) // 10)
    qs = np.quantile(x, np.linspace(0.0, 1.0, n_bins + 1))
    edges = np.unique(qs)
    if len(edges) < 3:
        return {"mean_bin_std": float("nan"), "max_bin_std": float("nan"), "bins_used": 0}
    idx = np.digitize(x, edges[1:-1], right=False)
    bin_stds = []
    for b in range(len(edges) - 1):
        mask = idx == b
        if np.sum(mask) >= 10:
            bin_stds.append(float(np.std(y[mask])))
    if not bin_stds:
        return {"mean_bin_std": float("nan"), "max_bin_std": float("nan"), "bins_used": 0}
    return {
        "mean_bin_std": float(np.mean(bin_stds)),
        "max_bin_std": float(np.max(bin_stds)),
        "bins_used": int(len(bin_stds)),
    }


@dataclass
class FitResult:
    model: str
    r2_test: float
    spearman_rho_test: float
    spearman_p_test: float
    mean_bin_std_test: float
    max_bin_std_test: float
    bins_used: int
    y_dynamic_range_test: float
    y_std_test: float
    n_train: int
    n_test: int


def fit_isotonic(x_train: np.ndarray, y_train: np.ndarray) -> IsotonicRegression:
    iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
    iso.fit(x_train, y_train)
    return iso


def evaluate_fit(model, x_test: np.ndarray, y_test: np.ndarray, n_bins: int = 20) -> FitResult:
    y_pred = model.predict(x_test)
    r2 = r2_score(y_test, y_pred)
    rho, p = spearmanr(y_test, y_pred)
    noise = bin_conditional_std(x_test, y_test, n_bins=n_bins)
    q05, q95 = np.quantile(y_test, [0.05, 0.95])
    return FitResult(
        model="isotonic",
        r2_test=float(r2),
        spearman_rho_test=float(rho),
        spearman_p_test=float(p),
        mean_bin_std_test=float(noise["mean_bin_std"]),
        max_bin_std_test=float(noise["max_bin_std"]),
        bins_used=int(noise["bins_used"]),
        y_dynamic_range_test=float(q95 - q05),
        y_std_test=float(np.std(y_test)),
        n_train=0,
        n_test=int(len(x_test)),
    )


def load_multiscale_table(
    path: str,
    estimator: str,
    seed_col: str,
    time_col: str,
    scale_col: str,
    scales: List[int],
    scheme: str | None,
) -> pd.DataFrame:
    df = pd.read_csv(path)
    if scheme is not None:
        if "scheme" not in df.columns:
            raise ValueError("Input does not contain 'scheme' column but --scheme was provided.")
        df = df[df["scheme"] == scheme].copy()
        if df.empty:
            raise ValueError(f"No rows found for scheme={scheme}")

    cols = set(df.columns)
    wide_cols = [f"C_b{s}" for s in scales]
    if all(c in cols for c in wide_cols):
        keep = [c for c in [seed_col, time_col] if c in cols] + wide_cols
        out = df[keep].copy().dropna()
        return out

    if scale_col in cols and estimator in cols:
        piv = df.pivot_table(index=[seed_col, time_col], columns=scale_col, values=estimator, aggfunc="mean")
        missing = [s for s in scales if s not in piv.columns]
        if missing:
            raise ValueError(f"Missing scales in data: {missing}. Available: {sorted(list(piv.columns))}")
        piv = piv[scales].copy()
        piv.columns = [f"C_b{s}" for s in scales]
        return piv.reset_index().dropna()

    raise ValueError("Unsupported input format.")


def split_seeds(df: pd.DataFrame, seed_col: str, test_fraction: float, random_state: int):
    seeds = sorted(df[seed_col].unique().tolist())
    rng = np.random.default_rng(random_state)
    rng.shuffle(seeds)
    n_test = max(1, int(round(len(seeds) * test_fraction)))
    test_seeds = set(seeds[:n_test])
    train_seeds = set(seeds[n_test:])
    train_df = df[df[seed_col].isin(train_seeds)].copy()
    test_df = df[df[seed_col].isin(test_seeds)].copy()
    return train_df, test_df, sorted(list(train_seeds)), sorted(list(test_seeds))


def check_saturation(values: np.ndarray, near_bound_threshold: float, saturation_fraction_gate: float) -> dict:
    near_zero = np.sum(values < near_bound_threshold)
    near_one = np.sum(values > 1 - near_bound_threshold)
    total = len(values)
    sat_frac = float((near_zero + near_one) / total) if total > 0 else 1.0
    return {
        "is_saturated": sat_frac > saturation_fraction_gate,
        "saturation_fraction": sat_frac,
        "near_zero_fraction": float(near_zero / total) if total > 0 else 1.0,
        "near_one_fraction": float(near_one / total) if total > 0 else 1.0,
        "near_bound_threshold": near_bound_threshold,
        "saturation_fraction_gate": saturation_fraction_gate,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV file in long or wide format")
    ap.add_argument("--outdir", default="out_semigroup")
    ap.add_argument("--scheme", default=None, help="Optional scheme filter for long-format data")
    ap.add_argument("--estimator", default="C_frozen")
    ap.add_argument("--seed_col", default="seed")
    ap.add_argument("--time_col", default="t")
    ap.add_argument("--scale_col", default="b")
    ap.add_argument("--scales", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--test_fraction", type=float, default=0.33)
    ap.add_argument("--random_state", type=int, default=0)
    ap.add_argument("--bins", type=int, default=20)
    ap.add_argument("--clip01", action="store_true")
    ap.add_argument("--sat_near_bound_threshold", type=float, default=0.1)
    ap.add_argument("--sat_fraction_gate", type=float, default=0.9)
    ap.add_argument("--min_non_saturated_pairs", type=int, default=2)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = load_multiscale_table(
        path=args.input,
        estimator=args.estimator,
        seed_col=args.seed_col,
        time_col=args.time_col,
        scale_col=args.scale_col,
        scales=args.scales,
        scheme=args.scheme,
    )

    if args.clip01:
        for s in args.scales:
            df[f"C_b{s}"] = df[f"C_b{s}"].clip(lower=0.0, upper=1.0)

    train_df, test_df, train_seeds, test_seeds = split_seeds(df, args.seed_col, args.test_fraction, args.random_state)

    summary = {
        "input": args.input,
        "scheme": args.scheme,
        "estimator": args.estimator,
        "scales": args.scales,
        "n_rows_total": int(len(df)),
        "train_seeds": train_seeds,
        "test_seeds": test_seeds,
        "n_rows_train": int(len(train_df)),
        "n_rows_test": int(len(test_df)),
        "saturation_settings": {
            "near_bound_threshold": args.sat_near_bound_threshold,
            "saturation_fraction_gate": args.sat_fraction_gate,
            "min_non_saturated_pairs": args.min_non_saturated_pairs,
        },
        "saturation_checks": {},
        "pair_fits": {},
        "semigroup_tests": {},
        "notes": [
            "R2 can be misleading under saturation; interpret with Spearman and dynamic range.",
            "Saturation gate skips semigroup tests with saturated scales.",
        ],
    }

    for b in args.scales:
        sat_check = check_saturation(
            train_df[f"C_b{b}"].to_numpy(),
            near_bound_threshold=args.sat_near_bound_threshold,
            saturation_fraction_gate=args.sat_fraction_gate,
        )
        summary["saturation_checks"][f"b={b}"] = sat_check

    pair_models = {}
    for i in range(len(args.scales) - 1):
        b = args.scales[i]
        b2 = args.scales[i + 1]
        x_train = train_df[f"C_b{b}"].to_numpy()
        y_train = train_df[f"C_b{b2}"].to_numpy()
        x_test = test_df[f"C_b{b}"].to_numpy()
        y_test = test_df[f"C_b{b2}"].to_numpy()

        iso = fit_isotonic(x_train, y_train)
        pair_models[(b, b2)] = iso
        fit_eval = evaluate_fit(iso, x_test, y_test, n_bins=args.bins)
        fit_eval.n_train = int(len(x_train))
        fit_eval.n_test = int(len(x_test))
        summary["pair_fits"][f"{b}->{b2}"] = fit_eval.__dict__

    for b in args.scales:
        b2 = b * 2
        b4 = b * 4
        if (b, b2) in pair_models and (b2, b4) in pair_models and f"C_b{b4}" in df.columns:
            sat_b = summary["saturation_checks"].get(f"b={b}", {}).get("is_saturated", False)
            sat_b2 = summary["saturation_checks"].get(f"b={b2}", {}).get("is_saturated", False)
            sat_b4 = summary["saturation_checks"].get(f"b={b4}", {}).get("is_saturated", False)
            key = f"{b}->{b2}->{b4}"

            if sat_b or sat_b2 or sat_b4:
                summary["semigroup_tests"][key] = {
                    "skipped_due_to_saturation": True,
                    "saturated_scales": [s for s, flag in [(b, sat_b), (b2, sat_b2), (b4, sat_b4)] if flag],
                }
                continue

            x_train = train_df[f"C_b{b}"].to_numpy()
            y_train = train_df[f"C_b{b4}"].to_numpy()
            direct = fit_isotonic(x_train, y_train)

            x_test = test_df[f"C_b{b}"].to_numpy()
            y_test = test_df[f"C_b{b4}"].to_numpy()
            y_mid = pair_models[(b, b2)].predict(x_test)
            y_comp = pair_models[(b2, b4)].predict(y_mid)
            y_direct = direct.predict(x_test)

            summary["semigroup_tests"][key] = {
                "skipped_due_to_saturation": False,
                "n_test": int(len(x_test)),
                "mae_composed_vs_direct": float(np.mean(np.abs(y_comp - y_direct))),
                "rmse_composed_vs_direct": float(np.sqrt(np.mean((y_comp - y_direct) ** 2))),
                "r2_truth_composed": r2_score(y_test, y_comp),
                "r2_truth_direct": r2_score(y_test, y_direct),
                "dynamic_range_truth_q95_q05": float(np.quantile(y_test, 0.95) - np.quantile(y_test, 0.05)),
            }

    non_saturated_adjacent_pairs = []
    for i in range(len(args.scales) - 1):
        b = args.scales[i]
        b2 = args.scales[i + 1]
        sat_b = summary["saturation_checks"].get(f"b={b}", {}).get("is_saturated", False)
        sat_b2 = summary["saturation_checks"].get(f"b={b2}", {}).get("is_saturated", False)
        if not (sat_b or sat_b2):
            non_saturated_adjacent_pairs.append(f"{b}->{b2}")

    evaluated_semigroup_triples = [
        k for k, v in summary["semigroup_tests"].items() if not v.get("skipped_due_to_saturation", False)
    ]
    summary["saturation_gate"] = {
        "non_saturated_adjacent_pairs": non_saturated_adjacent_pairs,
        "n_non_saturated_adjacent_pairs": len(non_saturated_adjacent_pairs),
        "evaluated_semigroup_triples": evaluated_semigroup_triples,
        "n_evaluated_semigroup_triples": len(evaluated_semigroup_triples),
        "required_min_pairs": int(args.min_non_saturated_pairs),
        "pass": (
            len(non_saturated_adjacent_pairs) >= args.min_non_saturated_pairs
            and len(evaluated_semigroup_triples) >= 1
        ),
    }

    out_path = os.path.join(args.outdir, "semigroup_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
