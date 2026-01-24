"""
Optional: estimator sketches for gradients/activations.

This file is not used by the default demo and intentionally has no hard deps.
It exists to answer the critique: "where is the estimator code that maps
observables (gradients/activations/output distribution) to F/C proxies?"

If you want to run this, you need:
  pip install torch transformers

Then you can implement a concrete model+tokenizer load and call these helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class TorchEstimates:
    grad_norm: float
    act_norm: float
    notes: Dict[str, Any]


def estimate_from_gradients(loss) -> float:
    """
    Minimal gradient proxy: ||∇ loss||.

    In practice you would:
    - compute a supervised loss on a probe task (or next-token loss),
    - backprop,
    - aggregate gradient norms over selected parameters.
    """
    total = 0.0
    for p in loss.parameters():  # type: ignore[attr-defined]
        if getattr(p, "grad", None) is None:
            continue
        g = p.grad.detach()
        total += float(g.norm().item())
    return float(total)


def estimate_from_activations(hidden_states) -> float:
    """
    Minimal activation proxy: ||h|| on the last layer.

    `hidden_states` can be the returned tuple from a Transformers model with
    output_hidden_states=True.
    """
    if not hidden_states:
        return 0.0
    h = hidden_states[-1]
    return float(h.detach().norm().item())

