# CPU-First Local Agent Demo (Verifier-first + Action Gate)

This is a **minimal, model-agnostic** demo that shows how to implement the core mechanisms described in:

- Paper (v0.2): [CPU-first local agent on 16GB RAM](../../papers/cpu-first-local-agent-on-16gb-deepseek-distill.v0.2.md)

The demo focuses on:
- structured IO (JSON-shaped router + plan + tool call)
- an **action gate** for irreversible operations (two-phase commit)
- an **audit log** (JSONL) with hashes

It does **not** ship a full agent stack (RAG, real tools, long-horizon planning). It is meant as a small, auditable reference.

## Quick start

```bash
python demo.py --scenario high_risk
python demo.py --scenario high_risk --confirm
python demo.py --scenario high_risk --break_glass
```

Outputs:
- `out/audit_log.jsonl` (append-only)

## Integrating a real model

In production, the router/planner would be produced by an LLM. In this demo they are sample JSON objects.
To connect a local model, replace the `stub_router()` / `stub_plan()` calls in `demo.py` with your own model invocation.

## Schemas

Schemas live under `schemas/` and define the minimal fields for:
- router output
- plan
- tool call
- final answer
