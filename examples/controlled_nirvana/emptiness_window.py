from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path
from typing import Any, Callable


@dataclasses.dataclass(frozen=True)
class TriggerMetrics:
    """
    All fields are estimator-scoped (EST-style): declare how you measure each one.
    Units:
      - decision_cycle_s: seconds per irreversible decision cycle (commit cadence)
      - correction_latency_s: seconds for external correction to take effect
      - self_gate_strength: normalized [0,1] proxy for how much self-eval gates commits
      - irreversible_queue_len: pending irreversible commits (int)
    """

    decision_cycle_s: float
    correction_latency_s: float
    self_gate_strength: float
    irreversible_queue_len: int

    def correction_latency_ratio(self) -> float:
        if self.decision_cycle_s <= 0:
            return float("inf")
        return float(self.correction_latency_s / self.decision_cycle_s)


@dataclasses.dataclass(frozen=True)
class EmptinessWindowConfig:
    """
    Minimal auditable trigger thresholds.
    You should version and pre-register these values for serious evaluation.
    """

    theta_m: float = 0.8  # tempo mismatch threshold: correction_latency/decision_cycle
    eps: float = 0.6  # self-gate strength threshold
    min_queue_len: int = 1  # require at least one irreversible commit pending

    min_open_s: float = 5.0  # keep window open for at least this long once triggered
    cooldown_s: float = 5.0  # minimum time between windows


class JsonlAuditLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: dict[str, Any]) -> None:
        event = dict(event)
        event.setdefault("ts", time.time())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


@dataclasses.dataclass
class DeferredCommit:
    commit_id: str
    kind: str
    created_ts: float
    fn: Callable[[], Any]


class IrreversibleCommitBuffer:
    """
    A minimal reversible buffer: when the window is open, irreversible actions are deferred.
    When the window closes, the buffer can be flushed (executed) or dropped.
    """

    def __init__(self, audit: JsonlAuditLogger | None = None):
        self._audit = audit
        self._queue: list[DeferredCommit] = []
        self._next_id = 0

    def __len__(self) -> int:
        return len(self._queue)

    def submit(self, *, kind: str, fn: Callable[[], Any], window_open: bool) -> Any:
        if not window_open:
            out = fn()
            if self._audit:
                self._audit.write({"type": "commit_executed", "kind": kind})
            return out

        self._next_id += 1
        commit_id = f"c{self._next_id:06d}"
        self._queue.append(DeferredCommit(commit_id=commit_id, kind=kind, created_ts=time.time(), fn=fn))
        if self._audit:
            self._audit.write({"type": "commit_deferred", "kind": kind, "commit_id": commit_id})
        return {"status": "deferred", "commit_id": commit_id, "kind": kind}

    def flush(self) -> list[dict[str, Any]]:
        executed: list[dict[str, Any]] = []
        while self._queue:
            item = self._queue.pop(0)
            try:
                result = item.fn()
                executed.append({"commit_id": item.commit_id, "kind": item.kind, "status": "executed", "result": result})
                if self._audit:
                    self._audit.write({"type": "commit_flushed", "commit_id": item.commit_id, "kind": item.kind, "status": "executed"})
            except Exception as e:
                executed.append({"commit_id": item.commit_id, "kind": item.kind, "status": "failed", "error": str(e)})
                if self._audit:
                    self._audit.write({"type": "commit_flushed", "commit_id": item.commit_id, "kind": item.kind, "status": "failed", "error": str(e)})
        return executed

    def drop(self) -> int:
        n = len(self._queue)
        if self._audit and n:
            self._audit.write({"type": "commit_dropped", "count": n})
        self._queue.clear()
        return n


class EmptinessWindowController:
    def __init__(self, config: EmptinessWindowConfig, audit: JsonlAuditLogger | None = None):
        self._cfg = config
        self._audit = audit
        self._open = False
        self._open_since_ts: float | None = None
        self._last_closed_ts: float | None = None

    @property
    def is_open(self) -> bool:
        return self._open

    def should_open(self, m: TriggerMetrics) -> bool:
        return (
            m.correction_latency_ratio() >= self._cfg.theta_m
            and m.self_gate_strength >= self._cfg.eps
            and m.irreversible_queue_len >= self._cfg.min_queue_len
        )

    def update(self, m: TriggerMetrics, now_ts: float | None = None) -> bool:
        """
        Update window state from latest metrics.
        Returns current window-open state.
        """

        now = float(time.time() if now_ts is None else now_ts)

        if self._open:
            assert self._open_since_ts is not None
            open_for = now - self._open_since_ts
            # Close rule: after min_open_s, close when trigger no longer holds.
            if open_for >= self._cfg.min_open_s and not self.should_open(m):
                self._open = False
                self._last_closed_ts = now
                if self._audit:
                    self._audit.write({"type": "window_closed", "open_for_s": open_for, "metrics": dataclasses.asdict(m)})
            return self._open

        # If closed, enforce cooldown.
        if self._last_closed_ts is not None:
            if (now - self._last_closed_ts) < self._cfg.cooldown_s:
                return self._open

        if self.should_open(m):
            self._open = True
            self._open_since_ts = now
            if self._audit:
                self._audit.write({"type": "window_opened", "metrics": dataclasses.asdict(m)})
        return self._open

