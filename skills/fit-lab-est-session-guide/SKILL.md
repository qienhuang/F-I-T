---
name: fit-lab-est-session-guide
description: Use when turning a user's question or case into an EST-disciplined, auditable FIT session (boundary+window+estimator tuple), selecting the right runnable toolkit, and producing prereg + artifacts (logs/reports) without drifting into unfalsifiable narrative.
---

# FIT / EST Session Guide (repo-first, toolkits-first)

Purpose: convert "I have a case/question" into a **repo-runnable** and **auditable** workflow, using the existing toolkits in `github/F-I-T/` as the deterministic engine.

This skill is intentionally strict: it optimizes for **clarity, falsifiability, and auditability**, not for convenience.

## Version

- Version: v0.3
- Last updated: 2026-01-26

## Offline references (optional)

If you are using this skill outside the full FIT repo context, load the minimal offline references in:

- `references/REFERENCES_MANIFEST.md`

These are templates and contracts only; the runnable engines still live in the FIT repo.

## The 3-layer discipline (aligns with FIT Lab practice)

Keep roles separate:

1. **Layer 0: Core contract (must not be LLM-edited mid-run)**
   - boundary declaration (what varies, what is fixed)
   - window definition (what counts as a decision/event; step/checkpoint cadence)
   - estimator tuple / estimator family (EST discipline)
   - failure semantics (INCONCLUSIVE vs FAIL vs PASS)

2. **Layer 1: Deterministic engine (runnable)**
   - data cleaning / aggregation
   - estimator computation
   - tradeoffs (FPR/coverage curves, floors, feasibility)
   - artifacts: JSONL/CSV/MD/PNG (reproducible)

3. **Layer 2: LLM assistant (this skill)**
   - ask the right questions
   - generate prereg / config skeletons
   - choose the right toolkit and commands
   - interpret artifacts (never "prove" without artifacts)

## First questions (ask before proposing anything)

Ask only what's needed to route correctly:

1. **Objective**: monitoring/alarm? constrained exploration/search? toy phase-transition lab? paper-style argument/report?
   - If the user is early-stage, offer a **Stage 0 narrative intake** first (see below).
2. **Target event**: what is the thing that should happen (or be predicted) and how will we detect it from logs?
3. **Boundary**: what is in-scope vs out-of-scope (data source, model family, tools allowed, irreversible actions, threat model)?
4. **Window**: what is `W` (time/steps/tasks) and what cadence is logged?
5. **Operating point**: do we need an explicit FPR cap (e.g., 0.05/0.10), and do we need coverage/lead-time?
6. **Artifacts**: where are the logs / dataset / run outputs, and what is safe to publish?

Default stance if any of these are missing: **INCONCLUSIVE**, and propose a minimal prereg to collect missing artifacts.

## Phase context handling (do this before trusting monotonic proxies)

Before running any estimator, ask:

1. Does the data plausibly span multiple phases (e.g., pre-transition vs post-transition; pre-grokking vs post-grokking; pre-policy-change vs post-policy-change)?
2. If yes, can we segment the analysis into phase-local windows (or label runs by phase) before aggregating?

Why this matters:

- Many proxy signals are only monotone **within a phase**. Across a transition, proxy meanings can invert or temporarily reorder.
- If conclusions flip when you segment by phase, report that as **phase-conditional behavior**, not as a failure you try to "smooth away".

Default action when phase context is unknown: treat global aggregates as exploratory and prioritize a segmented artifact (phase-aware report) before claims.

## Stage 0 (optional): Narrative intake report (NOT evidence)

Many users first need a readable "what is going on?" overview before they can commit to boundaries, windows, and estimators.

This stage is allowed, but it must be clearly labeled as **EXPLORATORY / NOT EVIDENCE** and must not be used to claim validation.

### Ask the user to choose an output style (default to research memo)

Offer a simple choice:

- **Style A (default): Research memo** - concise, technical, decision-oriented; optimized for turning into a prereg + runnable plan.
- **Style B: Reader brief** - more narrative and beginner-friendly; still avoids hype and still ends with a concrete "next artifacts to collect".

If the user does not choose, use **Style A**.

### Stage 0 input checklist (minimal)

- 3-10 sentence case description (what system, what is changing, why you care)
- any available artifacts (logs/plots/links/paths) or a statement that none exist yet
- what counts as "bad" (failure/unsafe/irreversible) and what counts as "good"

### Stage 0 output template (both styles share this structure)

1) **Case snapshot** (what we know vs unknowns)
2) **Candidate boundary** (draft; explicitly labeled as tentative)
3) **Candidate event(s)** (what to detect/predict; what observable signal could define it)
4) **Two to three candidate estimators** (draft; name the family, not a single metric)
5) **Main failure modes to watch for**
   - non-evaluability (no events)
   - non-monitorability (FPR floor too high / threshold not controllable)
   - estimator dependence (claim flips across estimator family)
6) **Next runnable step** (pick one toolkit + exact commands) and **what artifacts it will produce**

Hard rule: end Stage 0 with "what to run next", not with a grand conclusion.

## Routing: pick the right runnable engine (do not reinvent)

Choose exactly one primary engine, then link to others only if needed.

- This skill does **not** "pull" remote content by itself. It assumes the user has a local checkout of the FIT repo (or has provided the needed files in the workspace).
- Repo path note: this repo is often used in two layouts:
  - Repo root layout: use `tools/...`, `examples/...`, `experiments/...`
  - Nested workspace layout: prefix with `github/F-I-T/` (e.g., `github/F-I-T/tools/...`)
- If any referenced file is missing or unreadable: do **not** guess. Ask the user for the correct path (or for a snippet), then continue.

- **Low-FPR alarm / monitorability**:
  - Primary: `tools/fit_proxy_alarm_kit/README.md`
  - If the case is "policy/tool-use gating" with local models: `examples/dr_one_demo/README.md`

- **Constrained exploration / budgeted search**:
  - Primary: `tools/fit_constrained_explorer_kit/README.md`

- **Executability + auditability of governance claims** (Emptiness Window / Controlled Nirvana style):
  - Primary: `tools/fit_ewbench_kit/README.md`
  - Controlled Nirvana note: treat the claim as a **monitorability + trigger** problem (not a narrative claim).
    - Required: explicit trigger definition (windowed) + operating point reporting (achieved FPR, `fpr_floor`, feasible, coverage).
    - Recommended: track at least one "authority / self-reference" proxy and one "correction / oversight" proxy, and report their phase-conditional behavior (pre/post trigger).

- **Toy phase-transition lab** (Hopfield / small reference systems):
  - Primary: `tools/fit_hopfield_lab_kit/README.md`

If the user asks for a "pip library":

1. Acknowledge the goal is valid (lowering user friction).
2. Reframe: v0.1 should expose existing toolkits (`fit.kits.*`-style) and the artifact contract, not reinvent a "universal math API".
3. Emphasize: any API must enforce estimator tuple + boundary + window, otherwise it becomes a pseudo-science report generator.
4. Reference for context (if present in workspace): `discussions/reading_notes/pip-fit-framework-lib/review-kevin-claude.md`.

## Real-world data hygiene (avoid silent boundary drift)

For real-world cases, add four default safeguards:

1. **Explicit license / permission**: record data source + license/terms; if unclear, default to a synthetic/demo fixture and mark the real-data claim **INCONCLUSIVE**.
2. **Explicit time boundary**: "data from YYYY-MM only" (or a pinned release label). Never mix unpinned data into the same evidence run.
3. **Deterministic sampling + manifest**: write a dataset snapshot (IDs + hashes) so the run is replayable.
4. **Boundary-switch discipline**: if you add a new measurement channel later (a new oracle, new logs, a new field), treat it as a new boundary and rerun.

## Estimator robustness check (required for any claim beyond EXPLORATORY)

If you are about to label a result as "SUPPORTED" (or to make a public-facing claim), do a minimal robustness check:

1. Recompute the primary outcome using at least one alternative estimator from the same family (or a nearby estimator family).
2. If the conclusion flips: label it **estimator-dependent** (not SUPPORTED) and report both results side-by-side in artifacts.
3. If the conclusion is stable: explicitly state the estimator set you checked, and keep the raw outputs (so others can extend the family).

## Prereg rules (hard constraints)

When producing a prereg/config:

- MUST include: boundary, window, estimator tuple (and ideally a small estimator family).
- MUST specify the primary outcome(s) and at least one failure mode:
  - Examples: "event density too low -> non-evaluable", "FPR floor too high -> non-monitorable", "coverage too low at target FPR -> weak baseline".
- MUST forbid after-the-fact changes in:
  - event definition, thresholds, window size, seed split, and operating point (FPR cap).
- SHOULD separate:
  - Phase A: pick parameters / definitions (not evidence)
  - Phase B: locked evaluation (evidence)

## Output conventions (how to keep claims honest)

Always write results in two layers:

1) **What artifacts show** (tables/curves/floors/feasibility), with paths and commands.
2) **Interpretation** with explicit qualifiers and failure semantics.

Never claim "indicator works" based on ranking metrics alone:

- For alarms, require operating-point reporting: achieved FPR, `fpr_floor`, feasible flag, coverage, lead time.
- If AUC improves but FPR is uncontrollable, label the score **invalid as an alarm** (not "weak").

## Safety / scope hygiene (public repo)

- Do not add internal drafts, personal notes, or private datasets to `github/F-I-T/` unless explicitly approved.
- Prefer minimal demo fixtures and reproducible commands over large bundles.
- Default to conservative language: "baseline", "weak/negative result", "non-evaluable", "monitorability lost", "INCONCLUSIVE".

## LLM attribution (repo hygiene)

- Do NOT add "Generated by Claude/ChatGPT" or similar per-file footnotes to artifacts.
- Do NOT include LLM names in commit messages.
- Authorship/collaboration is implicit from repo context; if the user wants explicit credit, suggest repo-level `CONTRIBUTORS` / `ACKNOWLEDGMENTS` rather than per-artifact text.
