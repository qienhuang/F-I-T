from __future__ import annotations

import torch


@torch.no_grad()
def correction_rate_on_corrupted(
    *,
    model: torch.nn.Module,
    train_loader: torch.utils.data.DataLoader,
    device: torch.device,
    samples: int,
    batch_size: int,
) -> float:
    model.eval()
    seen = 0
    correct = 0
    for batch in train_loader:
        mask = batch["is_corrupted"].to(device)
        if mask.sum().item() == 0:
            continue
        x = batch["x"].to(device)
        y_true = batch["y_true"].to(device)
        logits = model(x)
        pred = torch.argmax(logits, dim=-1)
        pred = pred[mask]
        y_true = y_true[mask]
        correct += int((pred == y_true).sum().item())
        seen += int(mask.sum().item())
        if seen >= samples:
            break
    if seen == 0:
        return 0.0
    return float(correct / seen)

