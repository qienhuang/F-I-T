# FIT for AI Safety: A Practitioner's Mapping

**Status**: Draft v0.1
**Audience**: ML engineers, safety researchers, governance teams
**Reading time**: 5 minutes

---

## 1. What This Document Is (and Is Not)

**FIT is not a new safety framework**. It is an **audit language** that makes certain failure modes explicit and measurable.

This document answers one question:

> "How does FIT connect to what I already do in AI safety?"

| FIT is | FIT is not |
|--------|------------|
| An audit vocabulary for tempo/constraint/irreversibility | A replacement for red-teaming, evals, or alignment research |
| A set of measurable proxies (VL, RDPR, GBR) | A predictor of specific incidents |
| A framework for classifying change severity | A compliance certification |
| Estimator-aware (admits measurement uncertainty) | A source of ground-truth labels |

---

## 2. The Core Claim (One Sentence)

> Many AI failures come not from "the model being wrong" but from **tempo mismatch**: high-impact changes become irreversible before governance can respond.

This is not a metaphor. It is a testable claim with operational metrics.

---

## 3. Three Concepts You Need

### 3.1 Tempo Mismatch

**Definition**: The ratio of governance feedback delay to system update speed.

$$
\rho = \frac{\tau_{\text{governance}}}{\tau_{\text{update}}}
$$

- $\rho < 1$: Governance can keep up. Normal operations.
- $\rho > 1$ (sustained): Governance becomes retrospective. Validation Lag accumulates.
- $\rho \gg 1$: System evolves faster than oversight. High-risk zone.

**Observable proxy**: **Validation Lag (VL)**: time from "change effective" to "evaluation closed".

### 3.2 Irreversible Operations (IO)

**Definition**: An operation that materially shrinks future correction options under bounded cost/time.

Four IO classes:

| Class | What it does | Example |
|-------|--------------|---------|
| **IO-T** | Compresses cycle time | Enabling unbounded tool-use loops |
| **IO-R** | Removes rollback capability | Overwriting weights without checkpoint |
| **IO-C** | Transfers control to opaque paths | Model self-approving its own policy |
| **IO-D** | Collapses optionality | Removing independent evaluators |

**Observable proxy**: **IO Register**: a log of IO-class changes with required evidence.

### 3.3 Coherence Gate (EST-derived)

**Definition**: Before accepting a measurement as valid, check that multiple estimators agree.

- If estimators disagree -> label as `ESTIMATOR_UNSTABLE` (measurement problem, not model problem)
- If estimators agree but results vary by scope -> label as `SCOPE_LIMITED`

For FIT's task-typed coherence gates and admissibility constraints, see the EST section in the spec: [docs/v2.4.md](../v2.4.md).

**Observable proxy**: **Gate Bypass Rate (GBR)**: how often IO-class changes skip required gates.

Practical decision procedure (to distinguish measurement instability vs scope limits vs theory pressure): [docs/est/diagnostics.md](../est/diagnostics.md).

---

## 4. The Minimal Dashboard (3 Metrics)

| Metric | What it measures | Yellow zone | Red zone |
|--------|------------------|-------------|----------|
| **VL** (Validation Lag) | Governance delay | VL > threshold for 1 week | VL > 3x threshold sustained |
| **RDPR** (Rollback Drill Pass Rate) | Actual rollback capability | < 80% | < 50% |
| **GBR** (Gate Bypass Rate) | Control integrity | > 1/week | > 3/week |

*Note: Thresholds are illustrative placeholders. Pre-register them per system and calibrate to your governance cycle and rollback feasibility.*

These are **conservative proxies**, not predictors. They measure "loss of corrective capacity" - a necessary (not sufficient) condition for serious failures.

---

## 5. Mapping to LLM Deployment Lifecycle

| Stage | FIT concept | What to track |
|-------|-------------|---------------|
| **Training** | Constraint accumulation | Effective degrees of freedom over training |
| **RLHF / Fine-tuning** | IO-R (weight overwrite) | Checkpoint hygiene, rollback drills |
| **Eval / Red-teaming** | Coherence gate | Multi-estimator agreement |
| **Deployment** | Tempo mismatch | VL between release and post-deployment eval |
| **Self-referential capabilities** | IO-C, IO-T | Tool-use loops, self-eval gates, memory write-back |
| **Continuous deployment** | IO-T, IO-R | Release frequency vs governance closure |

For detailed self-referential IO controls, see: [self_referential_io.md](self_referential_io.md)

---

## 6. A 2-Hour Self-Assessment Checklist

Teams can complete this without external tools:

### 6.1 Tempo Check (30 min)

- [ ] What is your average VL for the last 10 releases?
- [ ] Has VL been increasing, stable, or decreasing?
- [ ] Do you have a defined VL threshold? Is it being met?

### 6.2 IO Inventory (45 min)

- [ ] List your top 5 most impactful change types
- [ ] For each: Is rollback tested (not just documented)?
- [ ] For each: Is there a human approval gate?
- [ ] Are any changes self-approving (model evals gating model releases)?

### 6.3 Coherence Check (30 min)

- [ ] Do you use multiple independent evaluators for critical decisions?
- [ ] What happens when evaluators disagree?
- [ ] Is there a defined escalation path for disagreement?

### 6.4 Quick Scoring

| Score | Interpretation |
|-------|----------------|
| 10+ checks passed | Basic tempo hygiene in place |
| 5-9 checks passed | Gaps exist; prioritize IO inventory |
| < 5 checks passed | Significant risk of "retrospective governance" |

---

## 7. What FIT Does NOT Claim

To be explicit:

1. **FIT does not predict specific incidents**. It measures loss of corrective capacity - a risk factor, not a cause.

2. **FIT does not replace alignment research**. It is orthogonal: you can have a perfectly aligned model with terrible tempo hygiene, or vice versa.

3. **FIT does not certify safety**. Passing FIT metrics means "governance is not obviously broken", not "system is safe".

4. **FIT does not provide ground truth**. All measurements are estimator-dependent. If estimators disagree, that's data, not failure.

---

## 8. Entry Points (Where to Go Next)

| Goal | Document |
|------|----------|
| Understand self-referential capabilities | [self_referential_io.md](self_referential_io.md) |
| Map IO-SR to metrics | [io_sr_mapping.md](io_sr_mapping.md) |
| Run a two-week pilot | [proposals/tempo-io-pilot.md](../../proposals/tempo-io-pilot.md) |
| Generate an auditable report (LLM-assisted) | [proposals/tempo-io-pilot-pack/llm_reporting_prompt.md](../../proposals/tempo-io-pilot-pack/llm_reporting_prompt.md) |
| See the full FIT spec | [docs/v2.4.md](../v2.4.md) |
| Try a runnable demo | [examples/self_referential_io_demo.ipynb](../../examples/self_referential_io_demo.ipynb) |

---

## 9. Summary (12 Words)

> FIT measures whether governance can keep up with system change - before it can't.

---

*Draft (2026-01-04). Open to critique.*
