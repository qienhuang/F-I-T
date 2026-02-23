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
    steps: int = 4000
    burn_in: int = 500
    measure_interval: int = 20
    window: int = 40
    grid_size: int = 128
    temperature: float = 2.269
    scales: tuple[int, ...] = (1, 2, 4, 8)
    schemes: tuple[str, ...] = ("majority", "threshold_low", "threshold_high", "average")


class Ising2DGlauber:
    def __init__(self, seed: int, size: int = 128, temperature: float = 2.269):
        self.rng = np.random.default_rng(seed)
        self.size = size
        self.temperature = temperature
        # +/-1 spins
        self.spins = self.rng.choice(np.array([-1, 1], dtype=np.int8), size=(size, size)).astype(np.int8)
        ii, jj = np.indices((size, size))
        self.mask_even = ((ii + jj) % 2 == 0)
        self.mask_odd = ~self.mask_even

    def _neighbor_sum(self) -> np.ndarray:
        s = self.spins
        return np.roll(s, 1, axis=0) + np.roll(s, -1, axis=0) + np.roll(s, 1, axis=1) + np.roll(s, -1, axis=1)

    def _update_mask(self, mask: np.ndarray) -> None:
        neigh = self._neighbor_sum()
        s = self.spins
        dE = 2.0 * s * neigh  # J=1
        acc = np.zeros_like(dE, dtype=bool)
        accept_downhill = (dE <= 0) & mask
        acc |= accept_downhill

        uphill = (dE > 0) & mask
        if np.any(uphill):
            p = np.exp(-dE[uphill] / self.temperature)
            u = self.rng.random(size=p.shape[0])
            acc[uphill] = (u < p)

        s[acc] *= -1

    def sweep(self) -> None:
        # Checkerboard update: avoids immediate conflicts and is fast vectorized.
        self._update_mask(self.mask_even)
        self._update_mask(self.mask_odd)

    def binary_snapshot(self) -> np.ndarray:
        return (self.spins > 0).astype(np.int8)


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
    sim = Ising2DGlauber(seed=seed, size=cfg.grid_size, temperature=cfg.temperature)
    rows: list[dict] = []
    histories: dict[tuple[str, int], list[np.ndarray]] = {
        (scheme, b): [] for scheme in cfg.schemes for b in cfg.scales
    }

    for t in range(1, cfg.steps + 1):
        sim.sweep()
        if t < cfg.burn_in or (t % cfg.measure_interval != 0):
            continue

        base_grid = sim.binary_snapshot()
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
    ap.add_argument("--seed_start", type=int, default=10000)
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--burn_in", type=int, default=500)
    ap.add_argument("--measure_interval", type=int, default=20)
    ap.add_argument("--window", type=int, default=40)
    ap.add_argument("--grid_size", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=2.269)
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
        grid_size=args.grid_size,
        temperature=args.temperature,
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
        "grid_size": args.grid_size,
        "temperature": args.temperature,
        "scales": list(cfg.scales),
        "schemes": list(cfg.schemes),
        "estimators": ["C_frozen", "C_activity", "H_2x2"],
        "out_parquet": str(out_parquet.as_posix()),
        "out_csv": str(out_csv.as_posix()),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    manifest = {
        "id": "ising_multiscale_invariants_manifest_v0_1",
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
