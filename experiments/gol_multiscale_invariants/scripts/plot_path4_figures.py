from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from sklearn.isotonic import IsotonicRegression


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def split_seeds(seeds: list[int], train_ratio: float, random_seed: int) -> tuple[list[int], list[int]]:
    rng = np.random.default_rng(random_seed)
    arr = np.array(sorted(seeds), dtype=int)
    rng.shuffle(arr)
    n_train = max(1, int(round(len(arr) * train_ratio)))
    n_train = min(n_train, len(arr) - 1)
    return sorted(arr[:n_train].tolist()), sorted(arr[n_train:].tolist())


def build_pair_data(df: pd.DataFrame, scheme: str, estimator: str, b1: int, b2: int) -> pd.DataFrame:
    sub = df[(df["scheme"] == scheme) & (df["estimator"] == estimator)].copy()
    piv = sub.pivot_table(index=["seed", "t"], columns="b", values="value", aggfunc="mean").reset_index()
    if b1 not in piv.columns or b2 not in piv.columns:
        return pd.DataFrame(columns=["seed", "t", "x", "y"])
    out = piv[["seed", "t", b1, b2]].dropna().rename(columns={b1: "x", b2: "y"})
    return out


def safe_name(s: str) -> str:
    return s.replace("->", "_to_").replace("/", "_")


def plot_scatter_fits(
    df: pd.DataFrame,
    fixed_points: dict,
    sat_df: pd.DataFrame,
    out_dir: Path,
    train_ratio: float,
    random_seed: int,
    eps: float,
) -> list[str]:
    out_paths: list[str] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    sat_lookup = {
        (str(r["scheme"]), str(r["estimator"]), int(r["b"])): bool(r["saturated"])
        for _, r in sat_df.iterrows()
    }

    schemes = sorted(df["scheme"].dropna().astype(str).unique().tolist())
    estimators = sorted(df["estimator"].dropna().astype(str).unique().tolist())
    scales = [1, 2, 4, 8]

    for scheme in schemes:
        for estimator in estimators:
            all_seeds = sorted(
                df[(df["scheme"] == scheme) & (df["estimator"] == estimator)]["seed"]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )
            if len(all_seeds) < 2:
                continue
            train_seeds, test_seeds = split_seeds(all_seeds, train_ratio=train_ratio, random_seed=random_seed)

            for i in range(len(scales) - 1):
                b1, b2 = scales[i], scales[i + 1]
                pair_key = f"{b1}->{b2}"
                pair_df = build_pair_data(df, scheme, estimator, b1, b2)
                if len(pair_df) == 0:
                    continue
                train_df = pair_df[pair_df["seed"].isin(train_seeds)].copy()
                test_df = pair_df[pair_df["seed"].isin(test_seeds)].copy()
                if len(train_df) < 10 or len(test_df) < 10:
                    continue

                # Fit isotonic on train for overlay
                iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
                iso.fit(train_df["x"].to_numpy(dtype=float), train_df["y"].to_numpy(dtype=float))

                # Poly coefficients from fixed_points.json (already prereg-consistent)
                fp_entry = (
                    fixed_points.get(scheme, {})
                    .get(estimator, {})
                    .get(pair_key, {})
                    .get("poly", {})
                )
                coefs = fp_entry.get("coefficients", None)
                coefs = np.array(coefs, dtype=float) if coefs is not None else None

                xgrid = np.linspace(0.0, 1.0, 300)
                y_iso = iso.predict(xgrid)
                y_poly = np.polyval(coefs, xgrid) if coefs is not None else None

                fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=160)
                # Saturation bands
                ax.axvspan(0, eps, color="#f7f1d0", alpha=0.25, lw=0)
                ax.axvspan(1 - eps, 1, color="#f7f1d0", alpha=0.25, lw=0)
                ax.axhspan(0, eps, color="#d0ecff", alpha=0.15, lw=0)
                ax.axhspan(1 - eps, 1, color="#d0ecff", alpha=0.15, lw=0)

                sample = test_df
                if len(sample) > 1200:
                    sample = sample.sample(n=1200, random_state=0)

                ax.scatter(
                    sample["x"],
                    sample["y"],
                    s=10,
                    alpha=0.45,
                    c="#1f77b4",
                    edgecolors="none",
                    label="test points",
                )
                ax.plot(xgrid, y_iso, color="#d62728", lw=2.0, label="isotonic fit")
                if y_poly is not None:
                    ax.plot(xgrid, y_poly, color="#2ca02c", lw=1.8, ls="--", label="poly fit")

                sat_from = sat_lookup.get((scheme, estimator, b1), False)
                sat_to = sat_lookup.get((scheme, estimator, b2), False)
                sat_tag = "SAT" if (sat_from or sat_to) else "OK"

                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_xlabel(f"value @ b={b1}")
                ax.set_ylabel(f"value @ b={b2}")
                ax.set_title(f"{scheme} | {estimator} | {b1}->{b2} [{sat_tag}]")
                ax.grid(alpha=0.25, linestyle=":")
                ax.legend(loc="best", fontsize=8)

                fname = f"{safe_name(scheme)}__{safe_name(estimator)}__b{b1}_to_b{b2}.png"
                out_path = out_dir / fname
                fig.tight_layout()
                fig.savefig(out_path)
                plt.close(fig)
                out_paths.append(str(out_path))

    return out_paths


def plot_closure_heatmap(inv_df: pd.DataFrame, out_path: Path) -> None:
    score_map = {"ESTIMATOR_UNSTABLE": 0, "SCOPE_LIMITED_SATURATION": 1, "PASS": 2}
    label_map = {0: "UNSTABLE", 1: "SCOPE", 2: "PASS"}

    piv = inv_df.pivot(index="scheme", columns="estimator", values="overall_label")
    schemes = list(piv.index)
    estimators = list(piv.columns)
    m = np.zeros((len(schemes), len(estimators)), dtype=int)

    for i, s in enumerate(schemes):
        for j, e in enumerate(estimators):
            m[i, j] = score_map.get(str(piv.loc[s, e]), 0)

    cmap = ListedColormap(["#ef4444", "#f59e0b", "#16a34a"])
    fig, ax = plt.subplots(figsize=(7.4, 4.6), dpi=170)
    im = ax.imshow(m, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(np.arange(len(estimators)))
    ax.set_xticklabels(estimators, rotation=20, ha="right")
    ax.set_yticks(np.arange(len(schemes)))
    ax.set_yticklabels(schemes)
    ax.set_title("Path-4 Closure Verdict Heatmap")

    for i in range(len(schemes)):
        for j in range(len(estimators)):
            ax.text(j, i, label_map[m[i, j]], ha="center", va="center", fontsize=8, color="white")

    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2], fraction=0.05, pad=0.02)
    cbar.ax.set_yticklabels(["UNSTABLE", "SCOPE", "PASS"])
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/multiscale_long.parquet")
    ap.add_argument("--fixed_points_json", default="results/fixed_points.json")
    ap.add_argument("--saturation_csv", default="results/saturation_matrix.csv")
    ap.add_argument("--invariant_csv", default="results/invariant_matrix.csv")
    ap.add_argument("--out_dir", default="results/figures")
    ap.add_argument("--train_ratio", type=float, default=0.7)
    ap.add_argument("--random_seed", type=int, default=20260216)
    ap.add_argument("--eps", type=float, default=0.10)
    args = ap.parse_args()

    df = load_table(Path(args.input))
    sat_df = pd.read_csv(args.saturation_csv)
    inv_df = pd.read_csv(args.invariant_csv)
    fixed_points = json.loads(Path(args.fixed_points_json).read_text(encoding="utf-8"))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scatter_paths = plot_scatter_fits(
        df=df,
        fixed_points=fixed_points,
        sat_df=sat_df,
        out_dir=out_dir / "scatter_fits",
        train_ratio=args.train_ratio,
        random_seed=args.random_seed,
        eps=args.eps,
    )
    heatmap_path = out_dir / "closure_heatmap.png"
    plot_closure_heatmap(inv_df, heatmap_path)

    summary = {
        "n_scatter_figures": len(scatter_paths),
        "scatter_dir": str((out_dir / "scatter_fits").as_posix()),
        "closure_heatmap": str(heatmap_path.as_posix()),
    }
    (out_dir / "figures_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
