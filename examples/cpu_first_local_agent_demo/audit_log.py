from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(s)


@dataclass(frozen=True)
class AuditEvent:
    run_id: str
    timestamp_utc: str
    model_id: str
    prompt_hash: str
    router_hash: str
    plan_hash: str
    tool_call_hash: str
    decision: str
    reason: str
    user_confirmed: bool
    break_glass: bool


def append_audit_event(path: Path, event: AuditEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event.__dict__, ensure_ascii=False) + "\n")

