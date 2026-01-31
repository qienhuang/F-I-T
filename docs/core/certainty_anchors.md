# Certainty Anchors (Core Artifact)
## How FIT Produces Bounded, Non-Illusory Confidence

**Status**: Core Artifact (v2.4.x compatible)  
**Role**: Guardrail against false certainty, motivational hallucination, and narrative overreach  
**Audience**: Users, practitioners, reviewers, LLM-based tools

---

## 1. Purpose

FIT is explicitly **not** a predictive or normative framework.
Yet users still need *actionable confidence* to decide:

- whether to persist,
- whether to change strategy,
- whether to stop or defer judgment.

This document defines **Certainty Anchors**: minimal, auditable structures that allow FIT analyses to say:

> "We are confident about *this much*, and explicitly uncertain beyond it."

Certainty Anchors do **not** increase confidence arbitrarily; they **cap** it.

---

## 2. What Certainty Anchors Are (and Are Not)

### They ARE
- Structural invariants that survive estimator choice
- Phase-conditional facts, not global truths
- Statements about what has already stabilized

### They are NOT
- Predictions of future success
- Guarantees of outcomes
- Claims of inevitability
- Psychological reassurance

If an analysis increases confidence without specifying **why it is allowed**, it violates FIT discipline.

---

## 3. The Three Classes of Certainty Anchors

FIT permits certainty only through three anchor types.
All valid confidence must attach to at least one.

---

### CA-1: Phase Identification Anchor

**Statement form**
> "Under the declared boundary and estimators, the system is currently in phase Φk."

**Why this is allowed**
- Phase is a descriptive classification, not a forecast.
- It relies on present-tense structure, not future assumptions.

**Requirements**
- Boundary explicitly declared
- Estimator tuple declared
- At least two phase-consistent signals observed

**What it allows**
- Confidence about what kind of dynamics are active
- Rejection of incompatible narratives

**What it forbids**
- Claims about when the phase will end
- Claims that a transition *must* occur

---

### CA-2: Negative Capability Anchor

**Statement form**
> "Given the current phase and constraints, X is *not yet possible*."

Examples:
- "Generalization is not yet structurally available."
- "Transfer should not be expected at this stage."
- "Fast correction is no longer viable."

**Why this is allowed**
- It constrains expectations downward.
- It reduces false hope and premature optimization.

**Requirements**
- Explicit link to constraint structure
- Clear boundary on the claim ("not yet", not "never")

**What it allows**
- Safe discouragement of counterproductive effort
- Explanation of frustration without pathologizing

---

### CA-3: Intervention-Sensitivity Anchor

**Statement form**
> "If the system changes in these specific ways, structural behavior will change."

This is conditional, not predictive.

Examples:
- "If force is redistributed from volume to variation, transfer becomes testable."
- "If constraint hardening is slowed, monitorability improves."

**Why this is allowed**
- It is counterfactual and falsifiable.
- It does not assert that the change will succeed.

**Requirements**
- Intervention targets F, I, or C explicitly
- Observable effect specified
- Failure condition stated

**What it allows**
- Action without illusion of control
- Experimentation with bounded expectations

---

## 4. Confidence Budgeting

Every FIT analysis should include an explicit **confidence budget**:

| Anchor Used | Confidence Type | Typical Level |
|------------|-----------------|---------------|
| CA-1       | Diagnostic      | Medium-High   |
| CA-2       | Exclusionary    | High          |
| CA-3       | Conditional     | Low-Medium    |

If no anchor is present, confidence must be labeled **Low**.

---

## 5. Common Violations (and Why They Matter)

### ❌ "You will definitely succeed if you keep going"
- No anchor
- Pure motivational hallucination

### ❌ "This guarantees a breakthrough"
- Violates CA-3 (claims inevitability)

### ❌ "You are in Φ2, so Φ3 will arrive"
- Phase != trajectory

These failures are especially dangerous when delivered by LLMs.

---

## 6. How LLM Tools Must Use Certainty Anchors

Any LLM-based FIT skill **must**:

1. Explicitly state which Certainty Anchors are invoked
2. Tie each confidence statement to an anchor
3. Downgrade confidence if anchors conflict or are weak

Recommended output footer:

> **Certainty basis**: CA-1 (phase identification), CA-2 (negative capability).  
> **Unanchored areas** remain speculative.

---

## 7. Relationship to Other Core Artifacts

- **Phase Algebra**: supplies CA-1
- **Flexibility Card**: constrains CA-3
- **Non-Use / Misuse Guard**: enforces confidence caps
- **How to Falsify FIT**: defines when anchors fail

Certainty Anchors do not add new primitives. They regulate how certainty is expressed.

---

## 8. One-Sentence Rule

> In FIT, confidence is only allowed where structure has already frozen.

Everywhere else, uncertainty must remain explicit.

---

## 9. Operational tie-ins (examples)

If you want these anchors to be more than rhetoric, tie them to auditable artifacts:

- **Monitorability / alarms (CA-2, CA-3):** if a score cannot achieve the target FPR (or exhibits an FPR floor), label it **invalid for alarms** under that operating point.
- **Coherence gates (CA-1, CA-2):** if pooled coherence fails but preregistered windows pass, interpret only within those windows and preserve the pooled failure as a diagnostic.
