from __future__ import annotations

from pathlib import Path
from typing import Any

import torch


def save_checkpoint(
    *,
    path: str | Path,
    step: int,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    extra: dict[str, Any] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "step": step,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
    }
    if extra:
        payload["extra"] = extra
    torch.save(payload, path)

