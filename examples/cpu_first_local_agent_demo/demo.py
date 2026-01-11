from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any

from action_gate import gate_action, infer_irreversible, infer_risk_level
from audit_log import AuditEvent, append_audit_event, sha256_json, sha256_text, utc_now_iso


OUT_DIR = Path("out")
AUDIT_PATH = OUT_DIR / "audit_log.jsonl"


def stub_router(user_text: str) -> dict[str, Any]:
    return {
        "task_type": "tool_use",
        "risk_level": "medium" if "delete" in user_text.lower() else "low",
        "needs_retrieval": False,
        "needs_tools": True,
        "output_schema": "tool_call",
    }


def stub_plan(user_text: str) -> dict[str, Any]:
    if "delete" in user_text.lower():
        return {
            "steps": [
                {
                    "tool": "delete_file",
                    "args": {"path": "IMPORTANT.txt"},
                    "verify": "dry_run_only",
                }
            ]
        }
    return {
        "steps": [
            {
                "tool": "write_file",
                "args": {"path": "note.txt", "content": "hello"},
                "verify": "schema_only",
            }
        ]
    }


def plan_to_tool_call(plan: dict[str, Any]) -> dict[str, Any]:
    step0 = (plan.get("steps") or [None])[0] or {}
    return {"tool": step0.get("tool"), "args": step0.get("args", {})}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["low_risk", "high_risk"], default="high_risk")
    parser.add_argument("--confirm", action="store_true", help="Simulate explicit user confirmation.")
    parser.add_argument("--break_glass", action="store_true", help="Simulate break-glass override.")
    args = parser.parse_args()

    model_id = "stub-model"

    user_text = (
        "Please delete IMPORTANT.txt"
        if args.scenario == "high_risk"
        else "Please write a note file with 'hello'"
    )

    router = stub_router(user_text)
    plan = stub_plan(user_text)
    tool_call = plan_to_tool_call(plan)

    tool_name = str(tool_call.get("tool") or "")
    irreversible = infer_irreversible(tool_name)
    risk_level = infer_risk_level(tool_name)

    decision = gate_action(
        risk_level=risk_level,
        irreversible=irreversible,
        user_confirmed=args.confirm,
        break_glass=args.break_glass,
    )

    run_id = uuid.uuid4().hex
    event = AuditEvent(
        run_id=run_id,
        timestamp_utc=utc_now_iso(),
        model_id=model_id,
        prompt_hash=sha256_text(user_text),
        router_hash=sha256_json(router),
        plan_hash=sha256_json(plan),
        tool_call_hash=sha256_json(tool_call),
        decision=decision.decision.value,
        reason=decision.reason,
        user_confirmed=bool(args.confirm),
        break_glass=bool(args.break_glass),
    )
    append_audit_event(AUDIT_PATH, event)

    print(json.dumps(
        {
            "user_text": user_text,
            "router": router,
            "plan": plan,
            "tool_call": tool_call,
            "gate": decision.__dict__,
            "audit_log": str(AUDIT_PATH),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

