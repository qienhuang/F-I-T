# Human–LLM Coupled Theory Discovery (HCTD) — Card

**Artifact type**: Core-adjacent methodological card  
**Status**: Compatible with FIT v2.x (no new primitives)  
**Purpose**: Make human–LLM collaboration for theory discovery explicit, auditable, and reproducible

This card is **repo-first**: a theory output is not considered durable until it is externalized as versioned artifacts and tied to explicit verification/falsification paths.

---

## Quickstart (6 steps)

1) Start the session with `docs/core/3_block_boot.md` (Block 1/2/3).  
2) Fill and lock `docs/reproducibility/tdcl_prereg_template.yaml` for the iteration.  
3) Generate candidates (explicitly labeled *exploratory*).  
4) Apply a coherence gate (reject: non-operational / non-falsifiable / contradictory / scope creep).  
5) Compress survivors into 1–2 repo artifacts (card / spec / prereg).  
6) Publish with a changelog and explicit failure semantics (including negative results).

---

## 1) One-sentence definition

> **HCTD** is a controlled, phase-aware workflow in which a human provides objective functions and structural constraints, while an LLM explores high-dimensional conceptual space; durable theory emerges only through external compression, versioning, and falsification.

---

## 2) What this is / is not

### This **is**:
- a **theory discovery workflow**, not a chat style
- compatible with **FIT / EST discipline**
- agnostic to model vendor, size, or architecture
- explicitly **non-authoritative** and falsifiable

### This is **not**:
- model fine-tuning or weight training
- "letting the LLM invent theory"
- a memory system for the LLM
- a replacement for evidence or experiments

---

## 3) System boundary (explicit)

The HCTD system consists of five components:

| Component | Role |
|---|---|
| Human | Objective function, constraint selection, value judgment |
| LLM | High-dimensional hypothesis and structure generator |
| Context window | Temporary working memory (ephemeral) |
| External artifacts | Durable memory (markdown, repo, versioned cards) |
| Evidence layer | World-level adjudication (data, experiments, counterexamples) |

> **Rule**: Any structure not externalized is considered *non-existent* beyond the session.

---

## 4) Control loop (TDCL)

HCTD operates via a closed control loop:

1. **Spec Lock**  
   Declare the scope, exclusions, and output type for this iteration.

2. **Divergence**  
   Use the LLM to explore a wide conceptual space without evaluation.

3. **Coherence Gate**  
   Reject candidates that are:
   - non-operational
   - non-falsifiable
   - internally inconsistent

4. **Compression**  
   Reduce surviving structure into minimal artifacts:
   - cards
   - propositions
   - estimator definitions

5. **Anchoring**  
   Attach each core claim to a verification or falsification path.

6. **Version & Publish**  
   Commit artifacts with changelog and "this version does not claim X".

7. **Reload**  
   Use compressed artifacts as the next iteration’s starting context.

---

## 5) Relationship to FIT / EST

HCTD introduces **no new primitives**.

| FIT concept | HCTD interpretation |
|---|---|
| Force (F) | Hypothesis-generating pressure |
| Information (I) | Persisted external structure |
| Time (T) | Iteration order and irreversibility of commits |
| Constraint (C) | Human-imposed selection and rejection |
| Phase | Distinct discovery regimes (exploration → crystallization → coordination) |

EST applies to:
- estimator choice in theory testing
- coherence gates in step (3)
- robustness reporting in step (5)

---

## 6) Failure modes

### F1 — Hallucination lock-in
LLM-generated structure is accepted without external compression or testing.

### F2 — Narrative drift
Explanatory coherence increases while falsifiability decreases.

### F3 — Estimator hacking
Claims are preserved by post-hoc changes of metrics or scope.

### F4 — Explanation overfitting
The theory explains known cases well but cannot generate new testable claims.

---

## 7) Minimal metrics (diagnostic only)

- **Compression ratio**  
  (raw candidates → accepted primitives)

- **Falsifiability rate**  
  (claims with preregisterable tests / total claims)

- **Reuse rate**  
  (how often an artifact is referenced by later work)

Metrics are advisory, not optimization targets.

---

## 8) Minimal verdict vocabulary (recommended)

HCTD does not require a specific verdict taxonomy, but public reporting benefits from a small stable set. A minimal recommended set is:

- `SUPPORTED`
- `CHALLENGED`
- `ESTIMATOR_UNSTABLE`
- `SCOPE_LIMITED`
- `INCONCLUSIVE`

---

## 9) How to falsify this workflow

HCTD is challenged if:

- Independent researchers, using the same artifacts, cannot reproduce similar theory trajectories across models.
- The workflow systematically produces structures that resist falsification without invoking estimator instability.

---

## 10) Non-authority clause

This card describes a **method**, not truth.

No output produced via HCTD carries authority without independent verification.

