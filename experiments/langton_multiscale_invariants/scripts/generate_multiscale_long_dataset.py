from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class SimConfig:
    steps: int = 12000
    burn_in: int = 800
    measure_interval: int = 20
    window: int = 40
    view_size: int = 128
    scales: tuple[int, ...] = (1, 2, 4, 8)
    schemes: tuple[str, ...] = ("majority", "threshold_low", "threshold_high", "average")


class LangtonAntSparse:
    # N,E,S,W
    DIRECTIONS = np.array([[0, -1], [1, 0], [0, 1], [-1, 0]], dtype=int)

    def __init__(self, seed: int, init_radius: int = 8, init_black_prob: float = 0.03):
        self.rng = np.random.default_rng(seed)
        self.pos = np.array([0, 0], dtype=int)
        self.dir_idx = int(self.rng.integers(0, 4))
        self.black_cells: set[tuple[int, int]] = set()
        self.step_count = 0

        # Seed-specific initial perturbation to avoid identical deterministic traces.
        for x in range(-init_radius, init_radius + 1):
            for y in range(-init_radius, init_radius + 1):
                if self.rng.random() < init_black_prob:
                    self.black_cells.add((x, y))

    def step(self) -> None:
        key = (int(self.pos[0]), int(self.pos[1]))
        is_black = key in self.black_cells

        if not is_black:
            # white -> turn right, paint black
            self.dir_idx = (self.dir_idx + 1) % 4
            self.black_cells.add(key)
        else:
            # black -> turn left, paint white
            self.dir_idx = (self.dir_idx - 1) % 4
            self.black_cells.discard(key)

        self.pos += self.DIRECTIONS[self.dir_idx]
        self.step_count += 1

    def snapshot_window(self, view_size: int) -> np.ndarray:
        half = view_size // 2
        cx, cy = int(self.pos[0]), int(self.pos[1])
        x_min, x_max = cx - half, cx + half
        y_min, y_max = cy - half, cy + half

        arr = np.zeros((view_size, view_size), dtype=np.int8)
        for x, y in self.black_cells:
            if x_min <= x < x_max and y_min <= y < y_max:
                arr[x - x_min, y - y_min] = 1
        return arr


def coarsen_grid(grid: np.ndarray, b: int, scheme: str) -> np.ndarray:
    if b == 1:
        return grid.copy()
    s = grid.shape[0]
    if s % b != 0:
        raise ValueError(f"grid size {s} not divisible by b={b}")

    resh = grid.reshape(s // b, b, s // b, b)
    block_sum = resh.sum(axis=(1, 3))
    block_mean = resh.mean(axis=(1, 3))
    area = b * b

    if scheme == "majority":
        return (block_sum >= ((area + 1) // 2)).astype(np.int8)
    if scheme == "threshold_high":
        return (block_sum >= int(np.ceil(0.6 * area))).astype(np.int8)
    if scheme == "threshold_low":
        return (block_sum >= int(np.ceil(0.4 * area))).astype(np.int8)
    if scheme == "average":
        return (block_mean >= 0.5).astype(np.int8)
    raise ValueError(f"unknown scheme: {scheme}")


def entropy_2x2(grid: np.ndarray) -> float:
    h, w = grid.shape
    blocks: list[tuple[int, int, int, int]] = []
    for i in range(0, h - 1, 2):
        for j in range(0, w - 1, 2):
            blocks.append(tuple(list(grid[i : i + 2, j : j + 2].flat)))  # type: ignore[arg-type]
    if not blocks:
        return 0.0
    _, counts = np.unique(blocks, axis=0, return_counts=True)
    p = counts.astype(float) / counts.sum()
    return float(-(p * np.log2(p + 1e-15)).sum())


def frozen_fraction(history: list[np.ndarray], window: int) -> float:
    if len(history) < window:
        return 0.0
    rec = np.stack(history[-window:])
    var_cell = np.var(rec, axis=0)
    return float(np.mean(var_cell == 0.0))


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


def run_sim(seed: int, cfg: SimConfig) -> list[dict]:
    ant = LangtonAntSparse(seed=seed)
    rows: list[dict] = []
    histories: dict[tuple[str, int], list[np.ndarray]] = {
        (scheme, b): [] for scheme in cfg.schemes for b in cfg.scales
    }

    for t in range(1, cfg.steps + 1):
        ant.step()
        if t < cfg.burn_in or (t % cfg.measure_interval != 0):
            continue

        base_grid = ant.snapshot_window(view_size=cfg.view_size)
        for scheme in cfg.schemes:
            for b in cfg.scales:
                cg = coarsen_grid(base_grid, b=b, scheme=scheme)
                key = (scheme, b)
                histories[key].append(cg)
                if len(histories[key]) > (cfg.window + 5):
                    histories[key] = histories[key][-cfg.window - 5 :]

                c_frozen = frozen_fraction(histories[key], cfg.window)
                c_activity = 1.0 - c_frozen
                h_norm = float(np.clip(entropy_2x2(cg) / 4.0, 0.0, 1.0))

                rows.append(
                    {"seed": seed, "t": t, "scheme": scheme, "b": b, "estimator": "C_frozen", "value": c_frozen}
                )
                rows.append(
                    {"seed": seed, "t": t, "scheme": scheme, "b": b, "estimator": "C_activity", "value": c_activity}
                )
                rows.append(
                    {"seed": seed, "t": t, "scheme": scheme, "b": b, "estimator": "H_2x2", "value": h_norm}
                )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--seed_start", type=int, default=7000)
    ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--burn_in", type=int, default=800)
    ap.add_argument("--measure_interval", type=int, default=20)
    ap.add_argument("--window", type=int, default=40)
    ap.add_argument("--view_size", type=int, default=128)
    ap.add_argument("--out_parquet", default="data/multiscale_long.parquet")
    ap.add_argument("--out_csv", default="data/multiscale_long.csv")
    ap.add_argument("--summary_json", default="data/run_summary.json")
    ap.add_argument("--manifest_json", default="data/MANIFEST.json")
    args = ap.parse_args()

    cfg = SimConfig(
        steps=args.steps,
        burn_in=args.burn_in,
        measure_interval=args.measure_interval,
        window=args.window,
        view_size=args.view_size,
    )

    rows: list[dict] = []
    for i in range(args.seeds):
        rows.extend(run_sim(seed=args.seed_start + i, cfg=cfg))

    df = pd.DataFrame(rows)
    df["seed"] = df["seed"].astype(int)
    df["t"] = df["t"].astype(int)
    df["scheme"] = df["scheme"].astype(str)
    df["b"] = df["b"].astype(int)
    df["estimator"] = df["estimator"].astype(str)
    df["value"] = df["value"].astype(float).clip(0.0, 1.0)

    out_parquet = Path(args.out_parquet)
    out_csv = Path(args.out_csv)
    summary_json = Path(args.summary_json)
    manifest_json = Path(args.manifest_json)
    out_parquet.parent.mkdir(parents=True, exist_ok=True)

    wrote_parquet = True
    parquet_error = None
    try:
        df.to_parquet(out_parquet, index=False)
    except Exception as e:
        wrote_parquet = False
        parquet_error = str(e)

    df.to_csv(out_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    summary = {
        "rows": int(len(df)),
        "seeds": args.seeds,
        "seed_start": args.seed_start,
        "steps": args.steps,
        "burn_in": args.burn_in,
        "measure_interval": args.measure_interval,
        "window": args.window,
        "view_size": args.view_size,
        "scales": list(cfg.scales),
        "schemes": list(cfg.schemes),
        "estimators": ["C_frozen", "C_activity", "H_2x2"],
        "out_parquet": str(out_parquet.as_posix()),
        "out_csv": str(out_csv.as_posix()),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    manifest = {
        "id": "langton_multiscale_invariants_manifest_v0_1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(repo_root),
        "params": summary,
        "artifacts": [
            {"path": str(out_csv), "sha256": sha256_file(out_csv), "kind": "derived_long_csv"},
            {"path": str(summary_json), "sha256": sha256_file(summary_json), "kind": "run_summary"},
        ],
        "parquet_written": wrote_parquet,
        "parquet_error": parquet_error,
        "rows_long": int(len(df)),
    }
    if wrote_parquet and out_parquet.exists():
        manifest["artifacts"].append(
            {"path": str(out_parquet), "sha256": sha256_file(out_parquet), "kind": "derived_long_parquet"}
        )
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote rows: {len(df)}")
    print(f"CSV: {out_csv}")
    print(f"PARQUET: {out_parquet if wrote_parquet else 'SKIPPED'}")
    print(f"summary: {summary_json}")
    print(f"manifest: {manifest_json}")


if __name__ == "__main__":
    main()
