from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset


@dataclass(frozen=True)
class ModularAdditionBatch:
    x: torch.Tensor  # [B, 2] tokens in [0, p-1]
    y: torch.Tensor  # [B] label used for training (may be corrupted)
    y_true: torch.Tensor  # [B] true modular addition label
    is_corrupted: torch.Tensor  # [B] bool


class ModularAdditionDataset(Dataset[ModularAdditionBatch]):
    def __init__(
        self,
        p: int,
        size: int,
        *,
        seed: int,
        corruption_enabled: bool,
        corruption_rate: float,
        corruption_seed: int,
    ) -> None:
        rng = np.random.default_rng(seed)
        a = rng.integers(0, p, size=size, dtype=np.int64)
        b = rng.integers(0, p, size=size, dtype=np.int64)
        y_true = (a + b) % p

        is_corrupted = np.zeros(size, dtype=np.bool_)
        y_used = y_true.copy()

        if corruption_enabled and corruption_rate > 0:
            rng_corrupt = np.random.default_rng(corruption_seed)
            corrupt_mask = rng_corrupt.random(size) < corruption_rate
            is_corrupted = corrupt_mask
            random_labels = rng_corrupt.integers(0, p, size=size, dtype=np.int64)
            y_used[corrupt_mask] = random_labels[corrupt_mask]

        self._x = np.stack([a, b], axis=1)
        self._y = y_used
        self._y_true = y_true
        self._is_corrupted = is_corrupted

    def __len__(self) -> int:
        return int(self._x.shape[0])

    def __getitem__(self, idx: int) -> ModularAdditionBatch:
        x = torch.tensor(self._x[idx], dtype=torch.long)
        y = torch.tensor(self._y[idx], dtype=torch.long)
        y_true = torch.tensor(self._y_true[idx], dtype=torch.long)
        is_corrupted = torch.tensor(self._is_corrupted[idx], dtype=torch.bool)
        return ModularAdditionBatch(x=x, y=y, y_true=y_true, is_corrupted=is_corrupted)


def collate(batch: list[ModularAdditionBatch]) -> dict[str, torch.Tensor]:
    x = torch.stack([b.x for b in batch], dim=0)
    y = torch.stack([b.y for b in batch], dim=0)
    y_true = torch.stack([b.y_true for b in batch], dim=0)
    is_corrupted = torch.stack([b.is_corrupted for b in batch], dim=0)
    return {"x": x, "y": y, "y_true": y_true, "is_corrupted": is_corrupted}


def make_loaders(
    *,
    p: int,
    train_size: int,
    test_size: int,
    batch_size: int,
    seed: int,
    corruption: dict[str, Any],
    num_workers: int = 0,
) -> tuple[DataLoader, DataLoader]:
    train_ds = ModularAdditionDataset(
        p=p,
        size=train_size,
        seed=seed,
        corruption_enabled=bool(corruption.get("enabled", False)),
        corruption_rate=float(corruption.get("corruption_rate", 0.0)),
        corruption_seed=int(corruption.get("corruption_seed", 0)),
    )
    test_ds = ModularAdditionDataset(
        p=p,
        size=test_size,
        seed=seed + 10_000,
        corruption_enabled=False,
        corruption_rate=0.0,
        corruption_seed=0,
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        collate_fn=collate,
        drop_last=True,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate,
        drop_last=False,
    )
    return train_loader, test_loader

