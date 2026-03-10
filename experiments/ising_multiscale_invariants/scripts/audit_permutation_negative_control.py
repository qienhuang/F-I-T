from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


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


def fit_iso(x: np.ndarray, y: np.ndarray) -> IsotonicRegression:
    iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
    iso.fit(x, y)
    return iso


def evaluate_one(
    df: pd.DataFrame,
    sat_df: pd.DataFrame,
    scheme: str,
    estimator: str,
    train_ratio: float,
    split_seed: int,
    n_perm: int,
    perm_seed: int,
) -> dict | None:
    # Required triple only: 1->2->4
    sat_flags = sat_df[
        (sat_df["scheme"] == scheme)
        & (sat_df["estimator"] == estimator)
        & (sat_df["b"].isin([1, 2, 4]))
    ]["saturated"].tolist()
    if len(sat_flags) < 3:
        return None
    if any(bool(x) for x in sat_flags):
        return {
            "scheme": scheme,
            "estimator": estimator,
            "tested": False,
            "reason": "saturated_required_scales",
        }

    p12 = build_pair_data(df, scheme, estimator, 1, 2)
    p24 = build_pair_data(df, scheme, estimator, 2, 4)
    p14 = build_pair_data(df, scheme, estimator, 1, 4)
    if len(p12) == 0 or len(p24) == 0 or len(p14) == 0:
        return {
            "scheme": scheme,
            "estimator": estimator,
            "tested": False,
            "reason": "missing_pairs",
        }

    seeds = sorted(
        set(p12["seed"].astype(int).unique())
        & set(p24["seed"].astype(int).unique())
        & set(p14["seed"].astype(int).unique())
    )
    if len(seeds) < 2:
        return {
            "scheme": scheme,
            "estimator": estimator,
            "tested": False,
            "reason": "insufficient_seeds",
        }
    train_seeds, test_seeds = seed_split(seeds, train_ratio=train_ratio, random_seed=split_seed)

    t12 = p12[p12["seed"].isin(train_seeds)]
    t24 = p24[p24["seed"].isin(train_seeds)]
    t14 = p14[p14["seed"].isin(train_seeds)]
    e14 = p14[p14["seed"].isin(test_seeds)]
    if min(len(t12), len(t24), len(t14), len(e14)) < 20:
        return {
            "scheme": scheme,
            "estimator": estimator,
            "tested": False,
            "reason": "insufficient_rows",
        }

    iso12 = fit_iso(t12["x"].to_numpy(float), t12["y"].to_numpy(float))
    iso24 = fit_iso(t24["x"].to_numpy(float), t24["y"].to_numpy(float))
    iso14 = fit_iso(t14["x"].to_numpy(float), t14["y"].to_numpy(float))

    x_eval = e14["x"].to_numpy(float)
    y_comp = iso24.predict(iso12.predict(x_eval))
    y_dir = iso14.predict(x_eval)
    rmse_real = rmse(y_dir, y_comp)

    rng = np.random.default_rng(perm_seed)
    x_train = t14["x"].to_numpy(float)
    y_train = t14["y"].to_numpy(float)
    perm_rmses: list[float] = []
    for _ in range(n_perm):
        y_perm = y_train[rng.permutation(len(y_train))]
        iso_perm = fit_iso(x_train, y_perm)
        y_perm_pred = iso_perm.predict(x_eval)
        perm_rmses.append(rmse(y_perm_pred, y_comp))

    arr = np.array(perm_rmses, dtype=float)
    mean_perm = float(np.mean(arr))
    std_perm = float(np.std(arr))
    p_emp = float((1 + np.sum(arr <= rmse_real)) / (len(arr) + 1))
    effect_sigma = float((mean_perm - rmse_real) / std_perm) if std_perm > 0 else float("nan")
    neg_ctrl_pass = bool((rmse_real < mean_perm) and (p_emp <= 0.05))

    return {
        "scheme": scheme,
        "estimator": estimator,
        "tested": True,
        "reason": "",
        "n_train_direct": int(len(t14)),
        "n_test_direct": int(len(e14)),
        "n_perm": int(n_perm),
        "rmse_real": rmse_real,
        "rmse_perm_mean": mean_perm,
        "rmse_perm_std": std_perm,
        "p_emp_lower_tail": p_emp,
        "effect_sigma": effect_sigma,
        "negative_control_pass": neg_ctrl_pass,
        "independent_estimator": estimator in {"C_frozen", "H_2x2"},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_block_a_root", default="data/temp_compare_full")
    ap.add_argument("--data_block_b_root", default="data/temp_compare_full_block_b")
    ap.add_argument("--results_block_a_root", default="results/temp_compare_full")
    ap.add_argument("--results_block_b_root", default="results/temp_compare_full_block_b")
    ap.add_argument("--temps", nargs="+", default=["T2p10", "T2p269"])
    ap.add_argument("--n_perm", type=int, default=200)
    ap.add_argument("--train_ratio", type=float, default=0.7)
    ap.add_argument("--split_seed", type=int, default=20260216)
    ap.add_argument("--perm_seed", type=int, default=20260223)
    ap.add_argument("--out_csv", default="results/temp_compare_blocks/permutation_negative_control.csv")
    ap.add_argument("--out_md", default="results/temp_compare_blocks/permutation_negative_control.md")
    args = ap.parse_args()

    rows: list[dict] = []
    blocks = [
        ("A", Path(args.data_block_a_root), Path(args.results_block_a_root)),
        ("B", Path(args.data_block_b_root), Path(args.results_block_b_root)),
    ]
    for block_name, data_root, res_root in blocks:
        for temp in args.temps:
            data_path = data_root / temp / "multiscale_long.parquet"
            sat_path = res_root / temp / "saturation_matrix.csv"
            if not data_path.exists() or not sat_path.exists():
                continue
            df = pd.read_parquet(data_path)
            sat_df = pd.read_csv(sat_path)
            schemes = sorted(df["scheme"].dropna().astype(str).unique().tolist())
            estimators = sorted(df["estimator"].dropna().astype(str).unique().tolist())
            for scheme in schemes:
                for estimator in estimators:
                    rec = evaluate_one(
                        df=df,
                        sat_df=sat_df,
                        scheme=scheme,
                        estimator=estimator,
                        train_ratio=args.train_ratio,
                        split_seed=args.split_seed,
                        n_perm=args.n_perm,
                        perm_seed=args.perm_seed,
                    )
                    if rec is None:
                        continue
                    rec["block"] = block_name
                    rec["temp_tag"] = temp
                    rec["temperature"] = 2.10 if temp == "T2p10" else 2.269 if temp == "T2p269" else None
                    rows.append(rec)

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out = pd.DataFrame(rows).sort_values(["temperature", "block", "scheme", "estimator"]).reset_index(drop=True)
    df_out.to_csv(out_csv, index=False)

    tested = df_out[df_out["tested"] == True].copy()
    lines = [
        "# Ising Permutation Negative Control (`1->2->4`, direct vs composed)",
        "",
        "Goal: verify that observed closure quality is not reproduced by random direct-map alignment.",
        "",
        "| Block | T | Scheme | Estimator | Tested | RMSE(real) | RMSE(perm mean) | p_emp (lower-tail) | Effect sigma | Neg-ctrl pass |",
        "|---|---:|---|---|---|---:|---:|---:|---:|---|",
    ]
    for _, r in df_out.iterrows():
        if not bool(r["tested"]):
            lines.append(
                f"| {r['block']} | {r['temperature']:.3f} | {r['scheme']} | {r['estimator']} | no ({r.get('reason','')}) | - | - | - | - | - |"
            )
            continue
        lines.append(
            f"| {r['block']} | {r['temperature']:.3f} | {r['scheme']} | {r['estimator']} | yes | "
            f"{float(r['rmse_real']):.5f} | {float(r['rmse_perm_mean']):.5f} | {float(r['p_emp_lower_tail']):.4f} | "
            f"{float(r['effect_sigma']):.3f} | {bool(r['negative_control_pass'])} |"
        )

    lines.append("")
    lines.append("## Aggregate readout")
    if len(tested) > 0:
        agg = (
            tested.groupby(["temperature", "block"])["negative_control_pass"]
            .agg(["sum", "count"])
            .reset_index()
        )
        lines.append("")
        lines.append("| T | Block | Neg-ctrl pass / tested | pass rate |")
        lines.append("|---:|---|---:|---:|")
        for _, a in agg.iterrows():
            rate = float(a["sum"]) / float(a["count"]) if a["count"] else float("nan")
            lines.append(f"| {a['temperature']:.3f} | {a['block']} | {int(a['sum'])}/{int(a['count'])} | {rate:.3f} |")
    else:
        lines.append("- No testable rows (all saturation-limited or insufficient data).")

    lines.extend(
        [
            "",
            "Notes:",
            "- Lower-tail p-value uses permutation baseline on direct-map training labels (`y` shuffled).",
            "- This is a negative-control audit; it does not replace prereg closure verdicts.",
            "- `C_activity` is derived (`1 - C_frozen`), so independent-evidence emphasis should remain on `C_frozen` and `H_2x2`.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

