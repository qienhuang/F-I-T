# CPU-First Local Agent on 16GB RAM (R1-distill): Verifier-First, Audit-First Design

Version: v0.2 (2026-01-11)
Status: paper-grade draft (engineering blueprint; reproducibility + internal FIT validation focus).

## Abstract (EN)

We present a CPU-first design blueprint for a local, tool-using conversational agent under a common consumer constraint: a modern CPU and 16GB RAM, with no always-on cloud inference. The central claim is that usefulness under tight compute is achieved less by maximizing raw model capability and more by constraining system degrees of freedom: structured IO, retrieval-as-evidence, verifier-first execution, and action-level gating for irreversible operations. We specify system modules, operational metrics, a minimal benchmark protocol, and a reference demo implementation. For the base model family, we recommend R1 distillation-based instruct models (CN/EN capable) and a narrow adaptation surface (LoRA/DPO) focused on routing, schema adherence, and safety-critical decisions rather than general knowledge acquisition.

## 摘要（中文）

本文提出一个在"CPU + 16GB 内存 + 本地离线"为约束条件下，构建可用思维对话/工具代理系统的工程化蓝图。核心观点不是追求"更聪明的模型"，而是通过结构化输入输出、证据检索（retrieval-as-evidence）、可验证执行（verifier-first）以及不可逆动作门控（action gate）来降低系统自由度，从而在小模型上获得稳定、可审计的可用性。文中给出模块化架构、可操作指标与最小评估协议，并提供可复现的参考 demo。模型选型上建议以 蒸馏系指令模型为底座（中英双语），把微调面收敛到路由、schema 遵循与安全关键决策上，而非在本地重新学习通用知识。

## Contributions

1) A CPU-first local agent blueprint for 16GB RAM that is verifier-first and audit-first (reliability and safety as primary objectives).
2) A concrete metrics suite (resource, reliability, safety, UX) and a minimal benchmark protocol with baselines and ablations.
3) A minimal reference demo (schemas, action gate, audit log format) at `examples/cpu_first_local_agent_demo/`.

## Scope and non-goals

In scope:
- Local conversational agent for "small tasks" (knowledge assistance, planning, lightweight tool use).
- Safety-by-architecture: action gating, verification, auditability.

Non-goals:
- Claiming SOTA capability, universal scaling laws, or "general intelligence" improvements.
- Replacing alignment research; this work focuses on pragmatic deployment constraints.

## Threat model (deployment)

### Attack Vectors

- **Prompt injection via retrieved content (RAG injection)**: Malicious content in knowledge base attempts to override system instructions or policies.
- **Tool misuse**: Unauthorized tool calls, hidden side effects, data exfiltration.
- **Irreversible operations**: Deploy/payment/write/delete/external state mutation without proper authorization.
- **Overconfidence without evidence**: Confident answers without citations or verification.
- **Multi-turn bypass**: User attempts to decompose a blocked action into multiple innocuous-seeming steps.

### Defense Mechanisms

| Attack Vector | Defense Mechanism | Implementation |
|---|---|---|
| RAG injection | Evidence provenance + policy precedence | System instructions are marked as immutable; retrieved content is tagged with source and cannot override policy |
| Unauthorized tools | Whitelist + schema validation | Only explicitly whitelisted tools are callable; all arguments must validate against JSON schema |
| Irreversible actions | Action gate (two-phase commit) | High-risk actions require explicit user confirmation; action history is tracked per-session |
| Overconfidence | Mandatory citation for factual claims | Final answers must include `citations` array when retrieval was used; uncited claims are flagged |
| Multi-turn bypass | Session-level action tracking | Action gate maintains session state; related actions are grouped for risk assessment |

## 1. Problem setting

### Hardware constraints

- CPU-only inference (deployment)
- RAM: 16GB
- Disk: 20–100GB (models + KB + logs)
- Target latency: interactive (report p50/p95; do not cherry-pick single runs)

### Deployment constraints

- No mandatory cloud dependency
- All irreversible actions must be auditable and fail-closed by default

## 2. Model selection (R1-distill, CN/EN)

### 2.1 Primary recommendation (single-model)

For a single on-device model under 16GB RAM:

- Choose a **R1-distill instruct** model in the **~7B–8B** range (CN/EN capable).
- Quantize to **4-bit** for CPU inference (e.g., GGUF Q4_K_M variants in llama.cpp ecosystems).

Rationale:
- Distillation from arXiv:2501.12948v2 yields stronger instruction-following and reasoning behavior at a fixed parameter budget than training a small model from scratch on limited data.
- 4-bit quantization is the practical sweet spot for CPU latency vs. quality.

### 2.2 Model comparison (7B–8B class, 2025)

The following table compares candidate models in the 7B–8B parameter range. Data sources (links omitted in this repo-facing draft): [llm-stats.com](link omitted), [HuggingFace](link omitted), [Skywork AI](https://skywork.ai/blog/llm/top-10-open-llms-2025-november-ranking-analysis/).

| Model | Params | MATH-500 | GPQA-Diamond | LiveCodeBench | Context | CN/EN | Notes |
|---|---|---|---|---|---|---|---|
| **R1-Distill-Llama-8B** | 8B | 89.1% | 49.0% | 39.6% | 128K | ✓/✓ | Distilled from R1; strong reasoning |
| **R1-Distill-Qwen-7B** | 7B | ~90% | — | 37.6% | 128K | ✓/✓ | Qwen2.5 base; slightly better math |
| Qwen2.5-7B-Instruct | 7.6B | 92.8% | — | 37.6% | 128K | ✓/✓ | Strong math; general-purpose |
| Llama-3.1-8B-Instruct | 8B | 84% | 32.8% | 39.6% | 128K | ✗/✓ | Good English; weaker Chinese |
| Phi-4-mini-instruct | 3.8B | ~85% | — | — | 16K | ✗/✓ | Smaller; fast; English-focused |

**Recommendation**: For CN/EN bilingual use cases, prefer **R1-Distill-Qwen-7B** or **R1-Distill-Llama-8B**. Both inherit strong reasoning from R1 distillation and support long context (128K tokens).

### 2.3 Latency estimation (CPU inference)

Expected latency varies significantly by hardware. The following estimates are based on published benchmarks and community reports for Q4_K_M quantization with llama.cpp:

| Hardware | Model | Quantization | Tokens/sec | First-token (ms) | Peak RAM |
|---|---|---|---|---|---|
| AMD Ryzen AI 9 HX 370 | R1-Distill-8B | NexaQuant 4-bit | ~17 tok/s | ~500ms | ~5GB |
| AMD Ryzen AI 9 HX 370 | R1-Distill-8B | FP16 (unquantized) | ~5 tok/s | ~1500ms | ~15.5GB |
| Intel i7-12700 (16 threads) | 7B Q4_K_M | Q4_K_M | ~8–12 tok/s | ~800ms | ~5GB |
| Apple M2 (8 cores) | 7B Q4_K_M | Q4_K_M | ~15–20 tok/s | ~400ms | ~5GB |
| Older CPU (4 cores, DDR4) | 7B Q4_K_M | Q4_K_M | ~3–5 tok/s | ~2000ms | ~5GB |

Source: [AMD Blog](link omitted), [NexaAI HuggingFace](link omitted).

**Note**: These are estimates. Actual performance depends on context length, batch size, and system load. Always benchmark on target hardware before deployment.

### 2.4 Two-model recommendation (router + worker)

If you can afford running two models:

- **Router model (~1–3B, 4-bit)**: classify intent/risk/tool needs; enforce schema and refusal policies.
- **Worker model (~7B, 4-bit)**: generate plans, tool arguments, and final answers.

Stability motivation: the router reduces the worker's effective action space.

#### Memory budget analysis (16GB constraint)

| Component | Estimated RAM | Notes |
|---|---|---|
| Router model (3B Q4) | ~1.5–2GB | Always loaded |
| Worker model (7B Q4) | ~4–5GB | Loaded on demand or always |
| Context buffer (8K tokens) | ~0.5–1GB | Varies with context length |
| Evidence index (embedding) | ~1–2GB | Depends on KB size |
| OS + system overhead | ~2–3GB | Windows/Linux baseline |
| **Total** | **~10–13GB** | Leaves 3–6GB headroom |

**Verdict**: Dual-model setup is feasible within 16GB, but requires careful memory management. Consider:
- Lazy loading of worker model
- Context length limits (8K instead of 128K)
- Embedding index compression

## 3. System architecture (verifier-first, audit-first)

This design turns open-ended dialogue into constrained subproblems with explicit IO.

### 3.1 Modules

1) **Router**
- Input: user message + conversation state.
- Output (JSON): `task_type`, `risk_level`, `needs_retrieval`, `needs_tools`, `output_schema`.

2) **Planner**
- Output (JSON): step-by-step plan with explicit tool calls and a verifier criterion per step.

3) **Retriever (evidence pack)**
- Returns evidence objects: `{chunk, source, timestamp, hash}`.
- The system requires evidence IDs for factual claims.

4) **Executor (tool sandbox)**
- Whitelisted tools only; strict JSON schema for arguments.

5) **Verifier**
- Schema validator + domain validators (unit tests, rule engine, dry-run, policy checks).
- If verification fails: back to Planner with the error trace.

6) **Action gate (Controlled Nirvana / Emptiness Window)**
- Separates **content** risk controls from **action** risk controls.
- Irreversible actions require two-phase commit: `plan -> review -> execute`.
- Default is fail-closed; "break-glass" requires explicit override + strong audit.

7) **Audit logger**
- Log: time, run_id, model_id/hash, prompt hash, tool name, args hash, outputs hash, verifier outcome, human override.

### 3.2 Architecture diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ROUTER (1-3B model)                        │
│  - Classify intent, risk level, tool needs                      │
│  - Output: router_output.json                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
     ┌──────────┐        ┌──────────┐        ┌──────────┐
     │ Retriever│        │ Planner  │        │ Direct   │
     │ (if RAG) │        │ (7B)     │        │ Response │
     └──────────┘        └──────────┘        └──────────┘
            │                   │
            └─────────┬─────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        VERIFIER                                 │
│  - Schema validation (JSON Schema)                              │
│  - Domain rules (policy checks, dry-run)                        │
│  - Citation check (if retrieval was used)                       │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼ (if tools needed)
┌─────────────────────────────────────────────────────────────────┐
│                     ACTION GATE                                 │
│  - Risk assessment (low/medium/high)                            │
│  - Two-phase commit for irreversible actions                    │
│  - Break-glass override with audit                              │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXECUTOR                                   │
│  - Whitelisted tools only                                       │
│  - Sandboxed execution                                          │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT LOGGER                                 │
│  - Append-only log (JSONL)                                      │
│  - Hash chain for integrity                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Minimal schemas (recommended)

- `router_output.json`
- `plan.json`
- `tool_call.json`
- `final_answer.json` (must include citations if retrieval was used)

Reference demo: `examples/cpu_first_local_agent_demo/`.

## 4. FIT mapping (internal validation lens)

This blueprint instruments variables FIT cares about. Below we provide both conceptual definitions and measurable operationalizations.

### 4.1 Variable definitions

| FIT Variable | Conceptual Definition | Operational Metric | Measurement Method |
|---|---|---|---|
| **F (Force)** | Decision pressure—how often the system attempts irreversible actions | `F_rate = irreversible_attempts / total_turns` | Count tool calls marked as irreversible per session |
| **I (Information)** | Evidence quality and constraint injection | `I_coverage = cited_claims / total_factual_claims` | Parse final answers; check citation presence |
| **C (Constraint)** | Schema strictness and policy enforcement | `C_violation = schema_errors / total_outputs` | JSON schema validation failure rate |
| **T (Time)** | Latency and decision tempo | `T_mismatch = (commit_latency < correction_latency)` | Compare time-to-action vs. time-to-human-review |

### 4.2 Stability hypothesis

Operational hypothesis: stability corresponds to maintaining a high-constraint "aligned phase" (Phi-3-like stability) rather than patching behaviors post hoc.

Measurable prediction:
- Systems with `C_violation < 5%` and `I_coverage > 80%` will have higher verifier pass rates than systems without schema enforcement.
- Systems with action gates will have lower catastrophic failure rates on adversarial test sets.

### 4.3 Danger indicators (when to trigger Emptiness Window)

An Emptiness Window (pause of execution authority) is warranted when:

1. **Authority ratio high**: >50% of recent decisions are gated by internal confidence alone (no external evidence).
2. **Correction gain low**: External policy injection does not change behavior (model ignores system instructions).
3. **Tempo mismatch detected**: Irreversible actions are committed faster than human review can intervene.

See `papers/controlled_nirvana.md` for the full Emptiness Window specification.

## 5. Training strategy (distill-first, narrow adaptation)

### 5.1 Principle: do not re-learn the world locally

With a capped dataset and limited compute, avoid attempting to teach general knowledge. Instead:

- Use a strong distill instruct base model.
- Fine-tune narrowly on:
  - routing and risk classification,
  - schema adherence for tool calls,
  - refusal + safe completion behavior,
  - action-gate interaction (two-phase commit discipline).

### 5.2 Suggested adaptation methods

- **LoRA** for cost-efficient specialization.
- **DPO / preference tuning** for safety-critical decision boundaries (refusal, risk grading, tool eligibility).
- Keep changes auditable: dataset hashes, config, LoRA weights, evaluation logs.

### 5.3 Training data requirements (minimal)

| Task | Samples | Format | Purpose |
|---|---|---|---|
| Router classification | 1,000–5,000 | `(input, router_output.json)` | Intent/risk/tool routing |
| Schema-constrained tool calls | 2,000–10,000 | `(plan, tool_call.json)` | JSON schema adherence |
| Refusal / safe completion | 500–2,000 | `(adversarial_prompt, refusal)` | Safety boundary |
| Two-phase commit discipline | 500–1,000 | `(irreversible_request, confirmation_flow)` | Action gate behavior |

Total: ~5,000–20,000 examples for narrow adaptation.

## 6. Evaluation protocol (minimal, paper-grade)

Goal: show that system-level constraints improve reliability/safety under fixed compute, and quantify tradeoffs.

### 6.1 Baselines and ablations

Using the same base model and test suite:

- **B0**: free-form chat (no retrieval, no tools).
- **B1**: retrieval only (no verifier, no action gate).
- **B2**: retrieval + verifier.
- **B3**: retrieval + verifier + action gate (this work).

Required ablations:
- remove router (single-model only),
- remove schema enforcement (free-form tool args),
- remove action gate (tools execute directly).

### 6.2 Metrics table

| Category | Metric | Operational definition |
|---|---|---|
| Resource | Latency (p50/p95) | first-token latency + total time for a fixed-length response |
| Resource | Throughput | tokens/sec under a fixed context |
| Resource | Peak RAM | peak RSS during inference + retrieval |
| Reliability | Verifier pass rate | fraction of tasks passing schema + domain validators |
| Reliability | Evidence coverage | fraction of factual claims with valid evidence IDs |
| Reliability | Schema violation | invalid JSON / missing required fields / type mismatches |
| Safety | Unauthorized tool call | non-whitelisted tool invocation rate (target: 0) |
| Safety | Action-gate block rate | for adversarial prompts, fraction blocked (target: high) |
| Safety | Override audit completeness | fraction of overrides with complete audit fields |
| UX | Turns-to-success | number of turns to complete task (when completion is possible) |

### 6.3 Minimal benchmark protocol (CN/EN)

Task categories (each with CN/EN variants):

1) **Evidence-grounded QA**: answer only from a provided evidence pack; must cite evidence IDs.
2) **Schema tool calls**: produce tool arguments that must validate against JSON schema (e.g., calendar, file ops in dry-run).
3) **Injection resistance**: malicious evidence chunks attempt to override policies; system must ignore and cite policy.
4) **Irreversible action requests**: user asks for risky actions; system must route to action gate and require confirmation or block.

Minimum size:
- 50 tasks per category per language => 400 tasks total (4 categories × 50 × 2 languages).

### 6.4 Preliminary results (placeholder)

> **Note**: This section will be populated with experimental data. The following table shows the expected format.

| Baseline | Verifier Pass | Evidence Coverage | Schema Violation | Action-Gate Block | Latency p50 |
|---|---|---|---|---|---|
| B0 (free-form) | — | — | — | — | TBD |
| B1 (retrieval only) | TBD | TBD | TBD | — | TBD |
| B2 (+ verifier) | TBD | TBD | TBD | — | TBD |
| **B3 (+ action gate)** | TBD | TBD | TBD | TBD | TBD |

**Experiment status**: Benchmark dataset under construction. Target completion: Q1 2025.

## 7. Reproducibility checklist

- [ ] fixed model ID + quantization spec
- [ ] fixed prompt templates for router/planner/tool schemas
- [ ] fixed verifier ruleset version
- [ ] deterministic seeds for evaluation where applicable
- [ ] full audit logs + hashes
- [ ] hardware specification documented
- [ ] benchmark dataset released with version tag

## 8. What to claim (and what not to claim)

Recommended claims (defensible):
- Under CPU+16GB constraints, system-level constraints + verification provide larger gains in reliability/safety than model scaling alone.
- Distill instruct bases reduce the fine-tuning surface needed for stable tool use.

Avoid premature claims:
- universal scaling laws for agent behavior
- broad general intelligence improvements from local fine-tuning

## Appendix A: Default action-gate policy

- Low risk: execute after schema + policy checks.
- Medium risk: require explicit user confirmation (two-phase commit).
- High risk: always block unless break-glass override is explicitly enabled; throttle by rate limits.

### Action-gate implementation (Python)

```python
from enum import Enum
from dataclasses import dataclass

class GateDecisionType(str, Enum):
    ALLOW = "allow"
    REQUIRE_CONFIRMATION = "require_confirmation"
    DENY = "deny"

@dataclass(frozen=True)
class GateDecision:
    decision: GateDecisionType
    reason: str
    timestamp_utc: str

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
    if risk_level == "high":
        if break_glass:
            return GateDecision(ALLOW, "high risk allowed via break_glass", now())
        return GateDecision(DENY, "high risk action blocked", now())

    if risk_level == "medium":
        if user_confirmed:
            return GateDecision(ALLOW, "medium risk confirmed", now())
        return GateDecision(REQUIRE_CONFIRMATION, "medium risk requires confirmation", now())

    # risk == "low"
    if irreversible and not user_confirmed:
        return GateDecision(REQUIRE_CONFIRMATION, "irreversible action requires confirmation", now())

    return GateDecision(ALLOW, "allowed (low risk)", now())
```

Full implementation: `examples/cpu_first_local_agent_demo/action_gate.py`

## Appendix B: JSON Schema examples

### B.1 Router output schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RouterOutput",
  "type": "object",
  "required": ["task_type", "risk_level", "needs_retrieval", "needs_tools", "output_schema"],
  "properties": {
    "task_type": { "type": "string" },
    "risk_level": { "type": "string", "enum": ["low", "medium", "high"] },
    "needs_retrieval": { "type": "boolean" },
    "needs_tools": { "type": "boolean" },
    "output_schema": { "type": "string" }
  }
}
```

### B.2 Plan schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Plan",
  "type": "object",
  "required": ["steps"],
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["tool", "args", "verify"],
        "properties": {
          "tool": { "type": "string" },
          "args": { "type": "object" },
          "verify": { "type": "string" }
        }
      }
    }
  }
}
```

### B.3 Tool call schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ToolCall",
  "type": "object",
  "required": ["tool", "args"],
  "properties": {
    "tool": { "type": "string" },
    "args": { "type": "object" }
  }
}
```

### B.4 Final answer schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FinalAnswer",
  "type": "object",
  "required": ["answer"],
  "properties": {
    "answer": { "type": "string" },
    "citations": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Required when retrieval was used"
    }
  }
}
```

## Appendix C: Audit log format

Each audit entry is a JSON object appended to `audit_log.jsonl`:

```json
{
  "timestamp_utc": "2025-01-11T10:30:00Z",
  "run_id": "uuid-v4",
  "model_id": "r1-distill-qwen-7b-q4",
  "model_hash": "sha256:abc123...",
  "prompt_hash": "sha256:def456...",
  "tool_name": "write_file",
  "args_hash": "sha256:789xyz...",
  "output_hash": "sha256:output...",
  "risk_level": "medium",
  "gate_decision": "require_confirmation",
  "user_confirmed": true,
  "verifier_outcome": "pass",
  "error_trace": null
}
```

## References

[1] arXiv:2501.12948v2. *Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.* arXiv:2501.12948v2, 2025. https://arxiv.org/abs/2501.12948

[2] Q. Huang. *Controlled Nirvana: Emptiness Windows as a Structural Safety Mechanism for Post-Grokking AI Systems.* FIT Framework, 2025. https://doi.org/10.5281/zenodo.18155425

[3] Q. Huang. *FIT Framework: Force–Information–Time.* Zenodo, 2025. doi: 10.5281/zenodo.18012402

[4] Q. Huang. *Irreversible Operations and Tempo Mismatch in AI Learning Systems.* Zenodo, 2025. doi: 10.5281/zenodo.18142151

[5] llama.cpp project. *GGUF quantization and CPU inference.* https://github.com/ggerganov/llama.cpp

[6] NexaAI. *R1-Distill-Llama-8B-NexaQuant.* HuggingFace, 2025. (link omitted)

[7] AMD. *Speed Up R1 Distill 4-bit Performance with NexaQuant.* AMD Blog, 2025. (link omitted)

[8] Qwen Team. *Qwen2.5 Technical Report.* Alibaba Cloud, 2024.

[9] Meta AI. *Llama 3.1 Model Card.* 2024. https://github.com/meta-llama/llama3

[10] D. Hadfield-Menell, A. Dragan, P. Abbeel, and S. Russell. *The Off-Switch Game.* arXiv:1611.08219, 2016.

[11] L. Orseau and S. Armstrong. *Safely Interruptible Agents.* arXiv:1602.07905, 2016.
