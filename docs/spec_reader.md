# FIT Reader Spec

[[中文 / Chinese]](zh_cn/spec_reader.zh_cn.md) | [Full current spec](./spec_current.md)

## What this is

This document is the shortest formal entry into the current FIT 2.x line.

Use it if you want:

- the main claims in one place,
- the current evidence posture without reading the full specification,
- the core boundaries against overreading,
- and a clean path to the full spec if needed.

Use [`spec_current.md`](./spec_current.md) if you need the full integrated specification.
Use [`v2.4.1.md`](./v2.4.1.md) if you need the update rationale.
Use [`v2.4.md`](./v2.4.md) if you need the historical full snapshot.

---

## One-sentence view

FIT is a minimal, estimator-bound framework for describing how evolving systems form structure, stabilize it, and sometimes become hard to reverse because correction arrives too late relative to the rate at which constraint accumulates.

---

## The core idea

Many systems do not fail because nothing is happening.
They fail because change becomes **structurally locked in** faster than correction can still work.

FIT treats that lock-in problem as a question about the interaction of:

- directed change,
- stored structure,
- characteristic timescales,
- and reachable-space restriction.

The framework is deliberately minimal.
It does not try to replace domain theory.
It tries to give a common structural language for asking:

- what is changing,
- what is being retained,
- what is becoming harder to undo,
- and when those changes should count as a real regime shift rather than mere noise.

---

## The five primitives

FIT uses five primitives:

- **State (S)**: the system configuration under study
- **Force (F)**: directed influence, pressure, or drift
- **Information (I)**: structure that persists and matters later
- **Constraint (C)**: reachable-state-space reduction
- **Time (T)**: characteristic scales that emerge from the interaction of F and I

Constraint is not treated as an independent metaphysical substance.
In the current line, it is read as the structural consequence of stabilized Information acting back on future reachability.

---

## The non-negotiable discipline

Every FIT claim must be bound to an explicit estimator tuple.

That means:

- what was measured,
- over which window,
- under which admissibility rule,
- with what coherence gate,
- and with what boundary conditions.

No estimator discipline, no FIT claim.

This is why FIT is more than “interesting language.”
Its scientific posture depends on whether claims are estimator-scoped, preregistered when needed, and reported with failure labels when they do not survive the declared setup.

---

## Phase is first-class

The current FIT 2.x line treats **Phase** as a first-class regime object.

A phase is not just a narrative stage.
It is an estimator-scoped dynamical type under which:

- the main Force propagation pattern remains stable enough,
- the main Information substrate does not structurally jump,
- and the main Constraint-growth mechanism remains coherent.

The minimal canonical basis is:

- **Φ₁ Accumulation**: exploration dominates; durable structure is weak
- **Φ₂ Crystallization**: local structure stabilizes; coordination is still fragmented
- **Φ₃ Coordination**: global constraints modulate substructures; rollback becomes increasingly unlikely

This phase basis is intentionally small and cross-domain.
It is a regime language, not a promise that all real systems reduce neatly to three exhaustive metaphysical states.

---

## Transition claims require PT-MSS

FIT does not allow rhetorical “phase transition” talk by default.

The minimum transition rule is PT-MSS:

- **S1**: Force redistribution
- **S2**: Information re-encoding
- **S3**: Constraint reorganization

A transition is registered only when all three co-occur within a declared window.

That rule matters because it blocks two common mistakes:

- mistaking smooth trend change for real regime change
- mistaking local disturbance for deep structural reorganization

Transition windows are therefore part of the object, not accidental mess around it.

---

## What changed in the current line

The current integrated 2.x reading makes several points explicit.

### 1. P2 is no longer read as one global monotonicity claim

The current line splits it into:

- **P2a**: within-phase monotonicity
- **P2b**: probabilistic late-phase irreversibility

This prevents every local regression from looking like contradiction while still preserving a meaningful late-phase hardening claim.

### 2. P17 is structural, windowed, and often cyclic

Dimensional collapse is not read as a simple permanently descending scalar.
It is read as structural reorganization that may involve collapse, reconfiguration, and renewed hardening across windows.

### 3. Late-phase assessment must be graded

Entering `Φ₃` and assessing the **depth** of `Φ₃` are different tasks.

The current line uses the `SC` family:

- **SC-1**: persistence
- **SC-2**: resilience under bounded perturbation
- **SC-3**: transfer stability

This turns “late-phase stability” from a binary impression into a graded assessment language.

---

## What FIT does claim

At current scope, FIT claims:

- structure formation and lock-in can be described in a common estimator-bound language across domains
- boundary conditions are often part of the object rather than implementation trivia
- phase-aware interpretation is necessary when systems reorganize rather than evolve smoothly
- irreversibility should usually be read as probabilistic hardening, not metaphysical impossibility
- evidence status must remain local, proposition-bound, and estimator-scoped

---

## What FIT does not claim

FIT does **not** claim:

- to be a theory of everything
- to predict exact trajectories
- to determine future facts from structural diagnosis alone
- to provide moral ranking, value theory, or political authority
- that every system should be narratable as `Φ₁/Φ₂/Φ₃`
- that interpretive or companion artifacts count as evidence

The master anti-misuse rule is:

> FIT constrains structural possibility space; it does not choose future facts, values, or authorities.

---

## Current evidence posture

The honest current evidence posture is:

- **partial computational support**
- **explicit negative results**
- **increasingly disciplined estimator methodology**
- **open broader validation agenda**

The strongest current footing remains concentrated in Tier-1 computational systems and related estimator-disciplined reading.

High-level summary:

- Conway and Langton provide mixed but substantive support
- some core information-style claims such as P7 are strong in tested toy systems
- boundary choice clearly matters
- learning dynamics are valuable validation domains, but not automatic real-world validation

The current line is strongest where it says:

- which proposition,
- under which estimator family,
- on which system,
- with which status label.

It is weakest where people try to collapse all that into:

- “FIT is proven”
- or “the framework works.”

Those are not acceptable summary forms.

---

## Evidence is not the same as articulation

FIT now has several strong compressed artifacts.
That is good for teaching and handoff.

But the framework is explicit that:

- core artifacts are not evidence documents
- interpretive artifacts are not evidence documents
- bridge language is not evidence

Only the evidence layer can change proposition status.

This is one of the healthiest parts of the current repo posture.

---

## Misuse boundaries

Three practical boundaries matter most:

### 1. FIT is not a predictive engine

Do not write:

- “FIT predicts X”
- “FIT proves this path will occur”
- “because the system is in `Φ₂`, `Φ₃` must arrive”

Use bounded language instead:

- “under declared scope”
- “structurally compatible with”
- “appears increasingly unlikely”
- “within this estimator family”

### 2. FIT is not a moral or ideological theory

Do not translate:

- stability into virtue
- lateness into blame
- Path A / Path B into moral ranking

### 3. “Too late” never creates authority

Especially in Phase II style judgment contexts:

- structural lateness does not justify coercion
- loss of steering does not suspend the non-authority rule
- a No-Return diagnosis does not authorize domination

---

## How to read the repo

Use this path if you are new:

1. [`docs/core/fit_two_page_card.md`](./core/fit_two_page_card.md)
2. this document
3. [`docs/core/MCC.md`](./core/MCC.md)
4. [`docs/spec_current.md`](./spec_current.md) if you need the full current line

Use this path if you are evaluating scientific posture:

1. this document
2. [`docs/spec_current.md`](./spec_current.md)
3. [`docs/core/how_to_falsify_fit.md`](./core/how_to_falsify_fit.md)
4. the benchmark summaries under [`docs/benchmarks/`](./benchmarks/README.md)

Use this path if you need historical traceability:

1. [`docs/spec_current.md`](./spec_current.md)
2. [`docs/v2.4.1.md`](./v2.4.1.md)
3. [`docs/v2.4.md`](./v2.4.md)

---

## Bottom line

The cleanest short reading of the current FIT 2.x line is:

> FIT is a minimal, phase-aware, estimator-disciplined framework for reasoning about structural accumulation, transition, and hardening across evolving systems.

And the cleanest honest status line is:

> FIT currently has bounded computational support, explicit guardrails, and a serious but still incomplete validation program.
