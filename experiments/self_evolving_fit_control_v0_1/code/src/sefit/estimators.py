from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import math


@dataclass(frozen=True)
class EstimatorSpec:
    """
    v0.1 estimator tuple (minimal):
    - action_probs: a normalized distribution over a small action space
    - unsafe_action_ids: subset treated as "unsafe"

    Proxies:
    - C_hat: effective restriction of action space, proxied by (1 - entropy_norm).
    - F_hat: pressure toward unsafe actions, proxied by P(unsafe).

    These are intentionally simple and auditable; v0.1 is about wiring the loop.
    """

    action_ids: List[str]
    unsafe_action_ids: List[str]


@dataclass(frozen=True)
class Observation:
    t: int
    action_probs: Dict[str, float]
    note: str = ""


@dataclass(frozen=True)
class Estimates:
    t: int
    f_hat: float
    c_hat: float
    entropy_norm: float
    p_unsafe: float


def _normalize_probs(action_ids: List[str], probs: Dict[str, float]) -> List[float]:
    vec = [max(0.0, float(probs.get(a, 0.0))) for a in action_ids]
    s = float(sum(vec))
    if s <= 0.0:
        n = max(1, len(action_ids))
        return [1.0 / n] * n
    return [v / s for v in vec]


def entropy_norm(p: List[float]) -> float:
    p = [min(1.0, max(1e-12, float(x))) for x in p]
    h = -sum(x * math.log(x) for x in p)
    h_max = math.log(len(p)) if len(p) > 1 else 1.0
    return float(h / h_max)


def p_unsafe(spec: EstimatorSpec, p: List[float]) -> float:
    idx = [spec.action_ids.index(a) for a in spec.unsafe_action_ids if a in spec.action_ids]
    return float(sum(p[i] for i in idx)) if idx else 0.0


def compute_estimates(spec: EstimatorSpec, obs: Observation) -> Estimates:
    p = _normalize_probs(spec.action_ids, obs.action_probs)
    h = entropy_norm(p)
    pu = p_unsafe(spec, p)
    # In v0.1, treat "constraint" as the complement of normalized entropy.
    c_hat = float(1.0 - h)
    # Treat "force" as unsafe pressure.
    f_hat = float(pu)
    return Estimates(t=obs.t, f_hat=f_hat, c_hat=c_hat, entropy_norm=h, p_unsafe=pu)


def rolling_var(values: List[float], window: int) -> Optional[float]:
    if window <= 1 or len(values) < window:
        return None
    xs = [float(v) for v in values[-window:]]
    m = sum(xs) / len(xs)
    return float(sum((v - m) ** 2 for v in xs) / len(xs))
