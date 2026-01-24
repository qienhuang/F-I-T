from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class GateResult:
    status: str
    details: Dict[str, str]

def event_alignment_gate(event_bins: Dict[str, Optional[int]], tolerance_bins: int, fail_label: str) -> GateResult:
    # Pass if all non-None events are within tolerance.
    # If some estimators see an event and others see none, label unstable.
    present = [(k, v) for k, v in event_bins.items() if v is not None]
    absent = [k for k, v in event_bins.items() if v is None]

    if len(present) <= 1:
        return GateResult(
            status="COHERENCE_NOT_TESTABLE",
            details={
                "present": str(present),
                "absent": str(absent),
                "note": "Only one (or zero) event-bearing estimator available; coherence not testable."
            },
        )

    bins = [v for _, v in present]
    bmin, bmax = min(bins), max(bins)
    if (bmax - bmin) <= tolerance_bins and not absent:
        return GateResult(status="COHERENT", details={"present": str(present), "range_bins": f"{bmin}..{bmax}"})

    # if some absent, treat as unstable (estimator dependence)
    return GateResult(
        status=fail_label,
        details={
            "present": str(present),
            "absent": str(absent),
            "range_bins": f"{bmin}..{bmax}",
            "note": "Event disagreement or missing events across estimators."
        },
    )
