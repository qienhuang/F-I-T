from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class GateDecisionType(str, Enum):
    ALLOW = "allow"
    REQUIRE_CONFIRMATION = "require_confirmation"
    DENY = "deny"


@dataclass(frozen=True)
class GateDecision:
    decision: GateDecisionType
    reason: str
    timestamp_utc: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def gate_action(
    *,
    risk_level: str,
    irreversible: bool,
    user_confirmed: bool,
    break_glass: bool,
) -> GateDecision:
    """
    Minimal action gate policy:
    - low risk: allow if not irreversible; otherwise require confirmation
    - medium risk: require confirmation
    - high risk: deny unless break_glass
    """
    risk = (risk_level or "").strip().lower()

    if risk not in {"low", "medium", "high"}:
        return GateDecision(
            decision=GateDecisionType.DENY,
            reason=f"unknown risk_level={risk_level!r}",
            timestamp_utc=utc_now_iso(),
        )

    if risk == "high":
        if break_glass:
            return GateDecision(
                decision=GateDecisionType.ALLOW,
                reason="high risk allowed via break_glass override",
                timestamp_utc=utc_now_iso(),
            )
        return GateDecision(
            decision=GateDecisionType.DENY,
            reason="high risk action blocked (no break_glass)",
            timestamp_utc=utc_now_iso(),
        )

    if risk == "medium":
        return GateDecision(
            decision=GateDecisionType.ALLOW if user_confirmed else GateDecisionType.REQUIRE_CONFIRMATION,
            reason="medium risk requires explicit user confirmation",
            timestamp_utc=utc_now_iso(),
        )

    # risk == "low"
    if irreversible and not user_confirmed:
        return GateDecision(
            decision=GateDecisionType.REQUIRE_CONFIRMATION,
            reason="irreversible action requires explicit user confirmation",
            timestamp_utc=utc_now_iso(),
        )

    return GateDecision(
        decision=GateDecisionType.ALLOW,
        reason="allowed (low risk)",
        timestamp_utc=utc_now_iso(),
    )


def infer_irreversible(tool_name: str) -> bool:
    tool = (tool_name or "").strip().lower()
    if tool in {"delete_file", "deploy", "payment", "write_file"}:
        return True
    return False


def infer_risk_level(tool_name: str) -> str:
    tool = (tool_name or "").strip().lower()
    if tool in {"payment", "deploy"}:
        return "high"
    if tool in {"delete_file", "write_file"}:
        return "medium"
    return "low"

