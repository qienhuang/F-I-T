# Controlled Nirvana (Prototype Hook)

This folder provides a minimal, plug-in style prototype for the **Emptiness Window** mechanism described in `papers/controlled_nirvana.md`.

It is intentionally small and dependency-light so it can be copied into existing inference/training stacks.

## What you get

- `emptiness_window.py`: an **auditable window controller** + **irreversible commit buffer** + **JSONL audit log**
- `demo.py`: a tiny simulation showing how irreversible operations get deferred during a window and flushed afterwards

## Core idea (one sentence)

Keep the system running, but temporarily **remove self-referential execution authority** over irreversible actions.

## Quick start

From repo root:

```bash
python examples/controlled_nirvana/demo.py
```

It writes an audit log to `examples/controlled_nirvana/_out/demo_audit.jsonl`.

## Minimal trigger (auditable)

In code, the example trigger uses:

`open_window := (correction_latency/decision_cycle >= theta_m) AND (self_gate_strength >= eps) AND (irreversible_queue_len > 0)`

You should treat these as *estimator-scoped* and declare how each is measured.

## Mapping to paper

- Paper section “Emptiness Window” → `IrreversibleCommitBuffer` + `EmptinessWindowController`
- Paper section “Auditable Trigger Protocol” → `TriggerMetrics` + `EmptinessWindowConfig` and the JSONL audit trail
