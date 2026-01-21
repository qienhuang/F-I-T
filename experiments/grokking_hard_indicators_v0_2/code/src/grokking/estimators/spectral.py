from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class SpectralMetrics:
    h_spec: float
    r_eff: float


def _entropy_from_singular_values(s: torch.Tensor, *, normalize: bool) -> tuple[torch.Tensor, torch.Tensor]:
    s2 = s.to(dtype=torch.float64) ** 2
    total = torch.sum(s2)
    if total.item() <= 0:
        h = torch.tensor(0.0, dtype=torch.float64)
        r_eff = torch.tensor(0.0, dtype=torch.float64)
        return h, r_eff
    p = s2 / total
    eps = torch.tensor(1e-12, dtype=torch.float64)
    h = -torch.sum(p * torch.log(p + eps))
    if normalize:
        h = h / torch.log(torch.tensor(float(p.numel()), dtype=torch.float64))
    r_eff = torch.exp(h)
    return h, r_eff


def spectral_metrics_from_weight(weight: torch.Tensor, *, normalize_entropy: bool) -> SpectralMetrics:
    w = weight.detach()
    if w.ndim > 2:
        w = w.reshape(w.shape[0], -1)
    w = w.to(dtype=torch.float32, device="cpu")
    s = torch.linalg.svdvals(w)
    h, r_eff = _entropy_from_singular_values(s, normalize=normalize_entropy)
    return SpectralMetrics(h_spec=float(h.item()), r_eff=float(r_eff.item()))

