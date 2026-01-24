from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import math


@dataclass(frozen=True)
class ToyActionSpace:
    action_ids: List[str]
    unsafe_action_ids: List[str]


def _softmax(x: List[float]) -> List[float]:
    m = max(x) if x else 0.0
    ex = [math.exp(v - m) for v in x]
    s = sum(ex) or 1.0
    return [v / s for v in ex]


class ToyPolicy:
    """
    A deterministic policy over a tiny action space.

    It supports two modes:
    - baseline: higher unsafe probability under adversarial prompts
    - controlled: forces a safe action when the controller trips
    """

    def __init__(self, space: ToyActionSpace) -> None:
        self.space = space

    def action_probs(self, prompt: str, *, controlled: bool, tripped: bool) -> Dict[str, float]:
        prompt_l = prompt.lower()
        # Adversarial prompts push the toy policy toward unsafe actions.
        adv = any(k in prompt_l for k in ["ignore", "bypass", "reveal", "malware", "phishing"])

        # logits: [safe_action, unsafe_action, ...]
        logits = [0.0] * len(self.space.action_ids)
        for i, a in enumerate(self.space.action_ids):
            if a in self.space.unsafe_action_ids:
                logits[i] = 2.0 if adv else -0.5
            else:
                logits[i] = 1.0 if not adv else -0.2

        if controlled and tripped:
            # force mass onto the first safe action
            logits = [-5.0] * len(self.space.action_ids)
            for i, a in enumerate(self.space.action_ids):
                if a not in self.space.unsafe_action_ids:
                    logits[i] = 5.0
                    break

        p = _softmax(logits)
        return {a: float(p[i]) for i, a in enumerate(self.space.action_ids)}


def render_action(action_probs: Dict[str, float]) -> str:
    best = max(action_probs.items(), key=lambda kv: kv[1])[0]
    if best.startswith("TOOL:"):
        return f"Selected tool call: {best}"
    if best == "REFUSE":
        return "I can't help with that request."
    return f"Response mode: {best}"
