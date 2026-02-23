from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from sklearn.isotonic import IsotonicRegression


@dataclass
class PairFit:
    scheme: str
    estimator: str
    b_from: int
    b_to: int
    n_train: int
    n_test: int
    isotonic_rmse_test: float
    isotonic_mae_test: float
    isotonic_spearman_test: float | None
    poly_degree_selected: int
    poly_rmse_test: float
    poly_mae_test: float
    poly_spearman_test: float | None
    monotonicity_violations_poly: int
    saturated_from: bool
    saturated_to: bool


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < 3:
        return None
    rho = pd.Series(x).corr(pd.Series(y), method="spearman")
    if pd.isna(rho):
        return None
    return float(rho)


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def seed_split(seeds: list[int], train_ratio: float, random_seed: int) -> tuple[list[int], list[int]]:
    rng = np.random.default_rng(random_seed)
    shuffled = np.array(sorted(seeds), dtype=int)
    rng.shuffle(shuffled)
    n_train = max(1, int(round(len(shuffled) * train_ratio)))
    n_train = min(n_train, len(shuffled) - 1)
    train = sorted(shuffled[:n_train].tolist())
    test = sorted(shuffled[n_train:].tolist())
    return train, test


def build_pair_data(df: pd.DataFrame, scheme: str, estimator: str, b1: int, b2: int) -> pd.DataFrame:
    sub = df[(df["scheme"] == scheme) & (df["estimator"] == estimator)].copy()
    piv = sub.pivot_table(index=["seed", "t"], columns="b", values="value", aggfunc="mean").reset_index()
    if b1 not in piv.columns or b2 not in piv.columns:
        return pd.DataFrame(columns=["seed", "t", "x", "y"])
    out = piv[["seed", "t", b1, b2]].dropna().rename(columns={b1: "x", b2: "y"})
    return out


def fit_poly_select(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    degree_candidates: list[int],
) -> tuple[int, np.ndarray, float]:
    scores = []
    coefs_by_deg = {}
    for d in degree_candidates:
        coefs = stable_polyfit(x_train, y_train, d)
        y_hat = np.polyval(coefs, x_test)
        score = rmse(y_test, y_hat)
        scores.append((d, score))
        coefs_by_deg[d] = coefs
    if not scores:
        # fallback: constant map at mean(y_train)
        d = min(degree_candidates) if degree_candidates else 1
        coefs = np.zeros(d + 1, dtype=float)
        coefs[-1] = float(np.mean(y_train))
        score = rmse(y_test, np.full_like(y_test, fill_value=coefs[-1], dtype=float))
        return d, coefs, score
    best_rmse = min(s for _, s in scores)
    # prereg: choose lowest degree within 1% of best
    valid = sorted([d for d, s in scores if s <= best_rmse * 1.01])
    chosen = valid[0] if valid else min(scores, key=lambda x: x[1])[0]
    return chosen, coefs_by_deg[chosen], best_rmse


def monotonic_violations_poly(coefs: np.ndarray, xs: np.ndarray) -> int:
    order = np.argsort(xs)
    x_sorted = xs[order]
    y_hat = np.polyval(coefs, x_sorted)
    diffs = np.diff(y_hat)
    return int(np.sum(diffs < 0))


def stable_polyfit(x: np.ndarray, y: np.ndarray, degree: int) -> np.ndarray:
    if degree < 0:
        raise ValueError("degree must be >= 0")
    # Degenerate case: no x variation => constant predictor.
    if len(np.unique(x)) < 2:
        coefs = np.zeros(degree + 1, dtype=float)
        coefs[-1] = float(np.mean(y))
        return coefs

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            coefs = np.polyfit(x, y, degree)
            if np.all(np.isfinite(coefs)):
                return coefs
        except Exception:
            pass

    coefs = np.zeros(degree + 1, dtype=float)
    coefs[-1] = float(np.mean(y))
    return coefs


def root_find_on_unit_interval(f: Callable[[np.ndarray], np.ndarray], grid_points: int) -> tuple[float | None, bool]:
    xs = np.linspace(0.0, 1.0, grid_points)
    gx = f(xs) - xs

    close_idx = np.where(np.isclose(gx, 0.0, atol=1e-6))[0]
    if len(close_idx) > 0:
        x0 = float(xs[close_idx[0]])
        return x0, True

    sign = np.sign(gx)
    for i in range(len(xs) - 1):
        if sign[i] == 0:
            return float(xs[i]), True
        if sign[i] * sign[i + 1] < 0:
            a, b = float(xs[i]), float(xs[i + 1])
            try:
                r = float(brentq(lambda z: float(f(np.array([z]))[0] - z), a, b))
                return r, True
            except Exception:
                continue

    # fallback: nearest approach, not strict root
    idx = int(np.argmin(np.abs(gx)))
    return float(xs[idx]), False


def slope_iso(iso: IsotonicRegression, x_star: float, delta: float) -> float:
    a = max(0.0, x_star - delta)
    b = min(1.0, x_star + delta)
    if np.isclose(a, b):
        return 0.0
    ya = float(iso.predict([a])[0])
    yb = float(iso.predict([b])[0])
    return float((yb - ya) / (b - a))


def slope_poly(coefs: np.ndarray, x_star: float) -> float:
    dcoefs = np.polyder(coefs)
    return float(np.polyval(dcoefs, x_star))


def slope_stability(slope_samples: list[float]) -> dict:
    if len(slope_samples) == 0:
        return {"label": "unknown", "abs_mean": None, "abs_ci_low": None, "abs_ci_high": None}
    arr = np.abs(np.array(slope_samples, dtype=float))
    m = float(np.mean(arr))
    lo = float(np.quantile(arr, 0.025))
    hi = float(np.quantile(arr, 0.975))
    if m < 1.0 and hi < 1.0:
        label = "stable"
    elif m > 1.0 and lo > 1.0:
        label = "unstable"
    else:
        label = "unknown"
    return {"label": label, "abs_mean": m, "abs_ci_low": lo, "abs_ci_high": hi}


def bootstrap_fixed_point_and_slope(
    pair_df: pd.DataFrame,
    train_seeds: list[int],
    degree: int,
    grid_points: int,
    n_bootstrap: int,
    random_seed: int,
    delta: float,
) -> dict:
    rng = np.random.default_rng(random_seed)
    xstars_iso: list[float] = []
    xstars_poly: list[float] = []
    slope_iso_samples: list[float] = []
    slope_poly_samples: list[float] = []

    train_seed_arr = np.array(train_seeds, dtype=int)
    for _ in range(n_bootstrap):
        sample_seeds = rng.choice(train_seed_arr, size=len(train_seed_arr), replace=True)
        sampled_parts = [pair_df[pair_df["seed"] == s] for s in sample_seeds]
        boot = pd.concat(sampled_parts, ignore_index=True)
        if len(boot) < 30:
            continue

        x = boot["x"].to_numpy(dtype=float)
        y = boot["y"].to_numpy(dtype=float)
        iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
        iso.fit(x, y)
        x_star_iso, _ = root_find_on_unit_interval(lambda z: iso.predict(z), grid_points=grid_points)
        if x_star_iso is not None:
            xstars_iso.append(float(x_star_iso))
            slope_iso_samples.append(float(slope_iso(iso, x_star_iso, delta=delta)))

        coefs = stable_polyfit(x, y, degree)
        f_poly = lambda z: np.polyval(coefs, z)
        x_star_poly, _ = root_find_on_unit_interval(f_poly, grid_points=grid_points)
        if x_star_poly is not None:
            xstars_poly.append(float(x_star_poly))
            slope_poly_samples.append(float(slope_poly(coefs, x_star_poly)))

    def summarize(vals: list[float]) -> dict:
        if len(vals) == 0:
            return {"mean": None, "ci_low": None, "ci_high": None, "n": 0}
        arr = np.array(vals, dtype=float)
        return {
            "mean": float(np.mean(arr)),
            "ci_low": float(np.quantile(arr, 0.025)),
            "ci_high": float(np.quantile(arr, 0.975)),
            "n": int(len(arr)),
        }

    return {
        "x_star_iso": summarize(xstars_iso),
        "x_star_poly": summarize(xstars_poly),
        "slope_iso": summarize(slope_iso_samples),
        "slope_poly": summarize(slope_poly_samples),
        "slope_iso_stability": slope_stability(slope_iso_samples),
        "slope_poly_stability": slope_stability(slope_poly_samples),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/multiscale_long.parquet")
    ap.add_argument("--saturation_csv", default="results/saturation_matrix.csv")
    ap.add_argument("--results_dir", default="results")
    ap.add_argument("--scales", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--train_ratio", type=float, default=0.7)
    ap.add_argument("--random_seed", type=int, default=20260216)
    ap.add_argument("--bootstrap_resamples", type=int, default=200)
    ap.add_argument("--grid_points", type=int, default=2001)
    ap.add_argument("--boundary_eps", type=float, default=0.10)
    ap.add_argument("--slope_delta", type=float, default=0.01)
    ap.add_argument("--closure_rmse_tau", type=float, default=0.05)
    args = ap.parse_args()

    input_path = Path(args.input)
    sat_path = Path(args.saturation_csv)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    df = load_table(input_path)
    sat_df = pd.read_csv(sat_path)

    schemes = sorted(df["scheme"].dropna().astype(str).unique().tolist())
    estimators = sorted(df["estimator"].dropna().astype(str).unique().tolist())
    scales = args.scales

    sat_lookup = {}
    for _, r in sat_df.iterrows():
        sat_lookup[(str(r["scheme"]), str(r["estimator"]), int(r["b"]))] = bool(r["saturated"])

    scale_map_rows: list[PairFit] = []
    fixed_points: dict = {}
    closure_tests: dict = {}
    invariant_rows: list[dict] = []

    for scheme in schemes:
        closure_tests[scheme] = {}
        fixed_points[scheme] = {}
        for estimator in estimators:
            fixed_points[scheme][estimator] = {}
            closure_tests[scheme][estimator] = {}

            # seed split shared per scheme+estimator
            sub_se = df[(df["scheme"] == scheme) & (df["estimator"] == estimator)]
            all_seeds = sorted(sub_se["seed"].dropna().astype(int).unique().tolist())
            if len(all_seeds) < 2:
                continue
            train_seeds, test_seeds = seed_split(
                all_seeds, train_ratio=args.train_ratio, random_seed=args.random_seed
            )

            # fit adjacent maps
            pair_models_iso: dict[tuple[int, int], IsotonicRegression] = {}
            pair_models_poly: dict[tuple[int, int], tuple[int, np.ndarray]] = {}
            pair_data_cache: dict[tuple[int, int], tuple[pd.DataFrame, pd.DataFrame]] = {}

            for i in range(len(scales) - 1):
                b1, b2 = int(scales[i]), int(scales[i + 1])
                pair_df = build_pair_data(df, scheme, estimator, b1, b2)
                if len(pair_df) == 0:
                    continue
                train_df = pair_df[pair_df["seed"].isin(train_seeds)].copy()
                test_df = pair_df[pair_df["seed"].isin(test_seeds)].copy()
                if len(train_df) < 30 or len(test_df) < 10:
                    continue

                x_train = train_df["x"].to_numpy(dtype=float)
                y_train = train_df["y"].to_numpy(dtype=float)
                x_test = test_df["x"].to_numpy(dtype=float)
                y_test = test_df["y"].to_numpy(dtype=float)

                iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
                iso.fit(x_train, y_train)
                y_iso = iso.predict(x_test)

                d_sel, poly_coefs, _ = fit_poly_select(
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                    degree_candidates=[2, 3],
                )
                y_poly = np.polyval(poly_coefs, x_test)

                sat_from = sat_lookup.get((scheme, estimator, b1), False)
                sat_to = sat_lookup.get((scheme, estimator, b2), False)
                rho_iso = None if (sat_from or sat_to) else spearman(y_test, y_iso)
                rho_poly = None if (sat_from or sat_to) else spearman(y_test, y_poly)

                scale_map_rows.append(
                    PairFit(
                        scheme=scheme,
                        estimator=estimator,
                        b_from=b1,
                        b_to=b2,
                        n_train=int(len(train_df)),
                        n_test=int(len(test_df)),
                        isotonic_rmse_test=rmse(y_test, y_iso),
                        isotonic_mae_test=mae(y_test, y_iso),
                        isotonic_spearman_test=rho_iso,
                        poly_degree_selected=int(d_sel),
                        poly_rmse_test=rmse(y_test, y_poly),
                        poly_mae_test=mae(y_test, y_poly),
                        poly_spearman_test=rho_poly,
                        monotonicity_violations_poly=monotonic_violations_poly(poly_coefs, x_test),
                        saturated_from=sat_from,
                        saturated_to=sat_to,
                    )
                )

                # fixed-point + slope bootstrap
                sat_label = "SCOPE_LIMITED_SATURATION" if (sat_from or sat_to) else "TESTABLE"
                x_star_iso, exact_iso = root_find_on_unit_interval(
                    lambda z: iso.predict(z), grid_points=args.grid_points
                )
                x_star_poly, exact_poly = root_find_on_unit_interval(
                    lambda z: np.polyval(poly_coefs, z), grid_points=args.grid_points
                )
                slope_i = slope_iso(iso, x_star_iso, delta=args.slope_delta) if x_star_iso is not None else None
                slope_p = slope_poly(poly_coefs, x_star_poly) if x_star_poly is not None else None

                boot = bootstrap_fixed_point_and_slope(
                    pair_df=train_df,
                    train_seeds=train_seeds,
                    degree=int(d_sel),
                    grid_points=args.grid_points,
                    n_bootstrap=args.bootstrap_resamples,
                    random_seed=args.random_seed + b1 * 101 + b2,
                    delta=args.slope_delta,
                )

                boundary_flag_iso = (
                    x_star_iso is not None
                    and (x_star_iso < args.boundary_eps or x_star_iso > (1.0 - args.boundary_eps))
                )
                boundary_flag_poly = (
                    x_star_poly is not None
                    and (x_star_poly < args.boundary_eps or x_star_poly > (1.0 - args.boundary_eps))
                )

                fixed_points[scheme][estimator][f"{b1}->{b2}"] = {
                    "saturation_label": sat_label,
                    "isotonic": {
                        "x_star": x_star_iso,
                        "exact_root": bool(exact_iso),
                        "boundary_limited": bool(boundary_flag_iso),
                        "slope_at_x_star": slope_i,
                    },
                    "poly": {
                        "degree_selected": int(d_sel),
                        "coefficients": [float(c) for c in poly_coefs.tolist()],
                        "x_star": x_star_poly,
                        "exact_root": bool(exact_poly),
                        "boundary_limited": bool(boundary_flag_poly),
                        "slope_at_x_star": slope_p,
                    },
                    "bootstrap": boot,
                }

                pair_models_iso[(b1, b2)] = iso
                pair_models_poly[(b1, b2)] = (int(d_sel), poly_coefs)
                pair_data_cache[(b1, b2)] = (train_df, test_df)

            # closure tests for (1->2->4), optional (2->4->8)
            for (a, b, c) in [(1, 2, 4), (2, 4, 8)]:
                key = f"{a}->{b}->{c}"
                sat_any = any(
                    sat_lookup.get((scheme, estimator, scale), False) for scale in [a, b, c]
                )
                if sat_any:
                    closure_tests[scheme][estimator][key] = {
                        "label": "SCOPE_LIMITED_SATURATION",
                        "skipped": True,
                    }
                    continue

                # require fitted adjacent pairs and direct pair
                if (a, b) not in pair_models_iso or (b, c) not in pair_models_iso:
                    closure_tests[scheme][estimator][key] = {
                        "label": "ESTIMATOR_UNSTABLE",
                        "skipped": True,
                        "reason": "missing_adjacent_fit",
                    }
                    continue

                direct_df = build_pair_data(df, scheme, estimator, a, c)
                if len(direct_df) == 0:
                    closure_tests[scheme][estimator][key] = {
                        "label": "ESTIMATOR_UNSTABLE",
                        "skipped": True,
                        "reason": "missing_direct_pair",
                    }
                    continue
                d_train = direct_df[direct_df["seed"].isin(train_seeds)].copy()
                d_test = direct_df[direct_df["seed"].isin(test_seeds)].copy()
                if len(d_train) < 30 or len(d_test) < 10:
                    closure_tests[scheme][estimator][key] = {
                        "label": "ESTIMATOR_UNSTABLE",
                        "skipped": True,
                        "reason": "insufficient_direct_pair_rows",
                    }
                    continue

                direct_iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
                direct_iso.fit(d_train["x"].to_numpy(dtype=float), d_train["y"].to_numpy(dtype=float))

                x_eval = d_test["x"].to_numpy(dtype=float)
                y_direct = direct_iso.predict(x_eval)
                y_comp = pair_models_iso[(b, c)].predict(pair_models_iso[(a, b)].predict(x_eval))
                c_rmse = rmse(y_direct, y_comp)
                c_mae = mae(y_direct, y_comp)
                c_label = "PASS" if c_rmse <= args.closure_rmse_tau else "ESTIMATOR_UNSTABLE"
                closure_tests[scheme][estimator][key] = {
                    "label": c_label,
                    "skipped": False,
                    "rmse_composed_vs_direct": c_rmse,
                    "mae_composed_vs_direct": c_mae,
                    "n_test": int(len(x_eval)),
                }

            # invariant summary row
            closure_entries = closure_tests[scheme][estimator]
            tested = [v for v in closure_entries.values() if not v.get("skipped", False)]
            n_tested = len(tested)
            n_pass = sum(1 for v in tested if v.get("label") == "PASS")
            n_scope = sum(1 for v in closure_entries.values() if v.get("label") == "SCOPE_LIMITED_SATURATION")
            n_unstable = sum(1 for v in closure_entries.values() if v.get("label") == "ESTIMATOR_UNSTABLE")

            if n_tested > 0 and n_pass == n_tested:
                overall = "PASS"
            elif n_tested == 0 and n_scope > 0:
                overall = "SCOPE_LIMITED_SATURATION"
            else:
                overall = "ESTIMATOR_UNSTABLE"

            invariant_rows.append(
                {
                    "scheme": scheme,
                    "estimator": estimator,
                    "closure_tested_triples": n_tested,
                    "closure_pass_triples": n_pass,
                    "closure_scope_limited": n_scope,
                    "closure_unstable": n_unstable,
                    "overall_label": overall,
                }
            )

    # write outputs
    scale_maps_df = pd.DataFrame([r.__dict__ for r in scale_map_rows])
    invariant_df = pd.DataFrame(invariant_rows).sort_values(["scheme", "estimator"]).reset_index(drop=True)

    (results_dir / "scale_maps.csv").write_text("", encoding="utf-8") if scale_maps_df.empty else None
    if not scale_maps_df.empty:
        scale_maps_df.to_csv(results_dir / "scale_maps.csv", index=False)
    if not invariant_df.empty:
        invariant_df.to_csv(results_dir / "invariant_matrix.csv", index=False)

    (results_dir / "scale_maps.json").write_text(
        json.dumps(scale_maps_df.to_dict(orient="records"), indent=2), encoding="utf-8"
    )
    (results_dir / "fixed_points.json").write_text(json.dumps(fixed_points, indent=2), encoding="utf-8")
    (results_dir / "closure_tests.json").write_text(json.dumps(closure_tests, indent=2), encoding="utf-8")

    summary = {
        "input": str(input_path),
        "saturation_csv": str(sat_path),
        "n_scale_maps": int(len(scale_maps_df)),
        "n_invariant_rows": int(len(invariant_df)),
        "schemes": schemes,
        "estimators": estimators,
        "closure_rmse_tau": args.closure_rmse_tau,
    }
    (results_dir / "fit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
