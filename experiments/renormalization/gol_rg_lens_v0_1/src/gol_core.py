from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class SimConfig:
    grid_size: int = 128
    steps: int = 2000
    burn_in: int = 100
    measure_interval: int = 10
    window: int = 50
    scales: List[int] = None

    def __post_init__(self):
        if self.scales is None:
            self.scales = [1, 2, 4, 8]


class GoL:
    def __init__(self, size: int, seed: int):
        self.size = size
        self.rng = np.random.default_rng(seed)
        self.grid = self.rng.integers(0, 2, (size, size), dtype=np.int8)

    def step(self) -> None:
        g = self.grid
        n = np.zeros_like(g, dtype=np.int16)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                n += np.roll(np.roll(g, di, axis=0), dj, axis=1)
        birth = (g == 0) & (n == 3)
        survive = (g == 1) & ((n == 2) | (n == 3))
        self.grid = (birth | survive).astype(np.int8)


def coarsen_grid(grid: np.ndarray, b: int, scheme: str) -> np.ndarray:
    if b == 1:
        return grid.copy()

    s = grid.shape[0]
    if s % b != 0:
        raise ValueError(f"Grid size {s} is not divisible by b={b}")

    reshaped = grid.reshape(s // b, b, s // b, b)
    block_sum = reshaped.sum(axis=(1, 3))
    block_mean = reshaped.mean(axis=(1, 3))
    area = b * b

    if scheme == "majority":
        threshold = (area + 1) // 2
        return (block_sum >= threshold).astype(np.int8)
    if scheme == "threshold_high":
        threshold = int(np.ceil(0.6 * area))
        return (block_sum >= threshold).astype(np.int8)
    if scheme == "threshold_low":
        threshold = int(np.ceil(0.4 * area))
        return (block_sum >= threshold).astype(np.int8)
    if scheme == "average":
        return (block_mean >= 0.5).astype(np.int8)

    raise ValueError(f"Unknown scheme: {scheme}")


def entropy_2x2(grid: np.ndarray) -> float:
    h, w = grid.shape
    blocks = []
    for i in range(0, h - 1, 2):
        for j in range(0, w - 1, 2):
            blocks.append(tuple(grid[i : i + 2, j : j + 2].flat))
    if not blocks:
        return 0.0
    vals, counts = np.unique(blocks, axis=0, return_counts=True)
    _ = vals  # keep explicit for readability
    p = counts.astype(float) / counts.sum()
    return float(-(p * np.log2(p + 1e-15)).sum())


def frozen_fraction(history: List[np.ndarray], window: int) -> float:
    if len(history) < window:
        return 0.0
    recent = np.stack(history[-window:])
    var_per_cell = np.var(recent, axis=0)
    return float(np.mean(var_per_cell == 0.0))


def activity_fraction(history: List[np.ndarray], window: int) -> float:
    # In this implementation C_activity is complement to C_frozen.
    return 1.0 - frozen_fraction(history, window)


def run_seed(seed: int, cfg: SimConfig, scheme: str) -> List[Dict[str, float]]:
    gol = GoL(cfg.grid_size, seed)
    histories: Dict[int, List[np.ndarray]] = {b: [] for b in cfg.scales}
    rows: List[Dict[str, float]] = []

    for t in range(1, cfg.steps + 1):
        gol.step()
        if t < cfg.burn_in or t % cfg.measure_interval != 0:
            continue

        for b in cfg.scales:
            cg = coarsen_grid(gol.grid, b, scheme)
            histories[b].append(cg)
            if len(histories[b]) > cfg.window + 5:
                histories[b] = histories[b][-cfg.window - 5 :]

            c_frozen = frozen_fraction(histories[b], cfg.window)
            c_activity = activity_fraction(histories[b], cfg.window)
            h = entropy_2x2(cg)

            rows.append(
                {
                    "seed": int(seed),
                    "scheme": scheme,
                    "t": int(t),
                    "b": int(b),
                    "C_frozen": float(c_frozen),
                    "C_activity": float(c_activity),
                    "H": float(h),
                }
            )
    return rows
