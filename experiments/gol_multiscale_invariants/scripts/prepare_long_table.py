from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return "unknown"


def write_csv(df: pd.DataFrame, out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, quoting=csv.QUOTE_MINIMAL)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input_csv",
        default=(
            "d:/FIT Lab/github/F-I-T/experiments/renormalization/"
            "gol_rg_lens_v0_1/out/multiscale_scheme_audit.csv"
        ),
    )
    ap.add_argument("--out_parquet", default="data/multiscale_long.parquet")
    ap.add_argument("--out_csv", default="data/multiscale_long.csv")
    ap.add_argument("--manifest_json", default="data/MANIFEST.json")
    ap.add_argument(
        "--source_summary_json",
        default=(
            "d:/FIT Lab/github/F-I-T/experiments/renormalization/"
            "gol_rg_lens_v0_1/out/run_summary.json"
        ),
    )
    args = ap.parse_args()

    input_csv = Path(args.input_csv)
    source_summary_json = Path(args.source_summary_json)
    out_parquet = Path(args.out_parquet)
    out_csv = Path(args.out_csv)
    manifest_json = Path(args.manifest_json)

    df = pd.read_csv(input_csv)
    required = {"seed", "scheme", "t", "b", "C_frozen", "C_activity", "H"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns in source CSV: {missing}")

    long_df = df.melt(
        id_vars=["seed", "t", "scheme", "b"],
        value_vars=["C_frozen", "C_activity", "H"],
        var_name="estimator_raw",
        value_name="value_raw",
    )

    estimator_map = {
        "C_frozen": "C_frozen",
        "C_activity": "C_activity",
        "H": "H_2x2",
    }
    long_df["estimator"] = long_df["estimator_raw"].map(estimator_map)

    # Normalize 2x2 entropy to [0,1] using max entropy log2(16)=4.
    is_h = long_df["estimator"] == "H_2x2"
    long_df.loc[is_h, "value"] = (long_df.loc[is_h, "value_raw"] / 4.0).clip(0.0, 1.0)
    long_df.loc[~is_h, "value"] = long_df.loc[~is_h, "value_raw"].clip(0.0, 1.0)

    long_df = long_df[["seed", "t", "scheme", "b", "estimator", "value"]].copy()
    long_df["seed"] = long_df["seed"].astype(int)
    long_df["t"] = long_df["t"].astype(int)
    long_df["b"] = long_df["b"].astype(int)
    long_df["scheme"] = long_df["scheme"].astype(str)
    long_df["estimator"] = long_df["estimator"].astype(str)
    long_df["value"] = long_df["value"].astype(float)

    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    wrote_parquet = True
    parquet_error = None
    try:
        long_df.to_parquet(out_parquet, index=False)
    except Exception as e:
        wrote_parquet = False
        parquet_error = str(e)

    write_csv(long_df, out_csv)

    repo_root = Path(__file__).resolve().parents[3]
    created_at = datetime.now(timezone.utc).isoformat()

    artifacts = [
        {"path": str(input_csv), "sha256": sha256_file(input_csv), "kind": "source_csv"},
        {"path": str(out_csv), "sha256": sha256_file(out_csv), "kind": "derived_long_csv"},
    ]
    if source_summary_json.exists():
        artifacts.append(
            {
                "path": str(source_summary_json),
                "sha256": sha256_file(source_summary_json),
                "kind": "source_summary",
            }
        )
    if wrote_parquet and out_parquet.exists():
        artifacts.append(
            {
                "path": str(out_parquet),
                "sha256": sha256_file(out_parquet),
                "kind": "derived_long_parquet",
            }
        )

    manifest = {
        "id": "gol_multiscale_invariants_manifest_v0_1",
        "created_at_utc": created_at,
        "git_commit": git_commit(repo_root),
        "params": {
            "input_csv": str(input_csv),
            "entropy_normalization": "H_2x2 = clip(H/4, 0, 1)",
            "schema": ["seed", "t", "scheme", "b", "estimator", "value"],
        },
        "artifacts": artifacts,
        "parquet_written": wrote_parquet,
        "parquet_error": parquet_error,
        "rows_long": int(len(long_df)),
    }

    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Prepared long table rows: {len(long_df)}")
    print(f"Wrote CSV: {out_csv}")
    if wrote_parquet:
        print(f"Wrote Parquet: {out_parquet}")
    else:
        print(f"Parquet skipped: {parquet_error}")
    print(f"Wrote manifest: {manifest_json}")


if __name__ == "__main__":
    main()

