# Essays — Conceptual Motivations Behind FIT

This directory contains **non-technical, non-binding philosophical essays**
that record the conceptual intuitions behind the development of the
F-I-T (Force–Information–Time) framework.

These texts are intentionally **free of formulas, estimators, and falsifiable claims**.

---

## Status and Intent

The essays in this directory:

- are **not technical papers**
- are **not formal components** of the FIT framework
- do **not** define primitives, propositions, or semantics
- do **not** impose usage constraints

They exist to capture **conceptual motivation, cross-domain intuition,
and long-horizon reasoning** that preceded and accompanied later
technical work.

---

## Relationship to FIT (Public Layer)

All **binding** definitions, rules, and claims live outside this directory.

In particular:

- Formal semantics are defined in `CHARTER.md`
- Public navigation is defined in `MANIFEST.md`
- Technical usage is indexed in `domains/` (applied indexes) and `lenses/` (structural templates)
- Falsifiable structure is documented in `overview/`

If any statement in these essays conflicts with the public FIT specification,
the specification **always prevails**.

---

## What These Essays Are For

These essays are intended to:

- provide intuition for readers new to FIT
- preserve the original conceptual trajectory behind the framework
- support cross-domain reflection where formalization is premature
- act as a **conceptual companion** to later technical material

They may be cited as **conceptual background**, but not as technical evidence.

---

## What These Essays Are Not For

These essays must **not** be used to:

- justify policy, governance, or coercive decisions
- substitute for estimator-bound analysis
- claim predictive or normative authority
- infer formal properties of the FIT framework

Such usage is out of scope.

---

## Contents

Typical topics include:

- why optimization-centric explanations often fail
- why timing and constraint structure dominate raw force
- parallels between learning, economics, governance, and technology
- intuition behind late-time stability, lock-in, and collapse

Individual essays may explore these themes freely and narratively.

---

## Citation and Use

If you reference these essays:

- treat them as **conceptual or philosophical material**
- do not attribute formal claims to them
- cite the corresponding FIT version separately if relevant

These essays are published to **preserve intellectual continuity**, not to
establish formal authority.

---

## License and Versioning

Unless stated otherwise, essays follow the repository license.

They are versioned independently from the FIT public layer.

---

## Suggested Reading Order

1. `00-why-fit.md` — Why timing and constraint dominate evolution
2. `10-learning.md` — Learning, grokking, and late-stage lock-in
3. `20-economics.md` — Markets, stability, and false equilibria
4. `30-governance.md` — Institutions, irreversibility, and reform
5. `40-technology.md` — Systems, architecture, and constraint design

---

## Renormalization & Scale Essays

These essays explore FIT's relationship to Renormalization Group (RG) theory —
how treating scale as an explicit operator (rather than a metaphor) upgrades
FIT claims from level-aware language to scale-auditable structure.

Unlike the introductory essays above, these contain mathematical notation
and reference experimental results from `discussions/reading_notes/renormalization/`.

1. [`Scale_Is_an_Operator_RG_to_FIT_v0.2.md`](renormalization/Scale_Is_an_Operator_RG_to_FIT_v0.2.md) — The central argument: scale is not commentary, it is an operator. Defines pushforward, semigroup closure, saturation gates.
2. [`Constraint_as_Surviving_Structure_v0.1.md`](renormalization/Constraint_as_Surviving_Structure_v0.1.md) — Constraint reinterpreted as structure that survives coarse-graining, with parallels to evolution, learning, and thermodynamics.
3. [`Why_Phase_Transitions_Disappear_When_You_Zoom_Out_v0.1.md`](renormalization/Why_Phase_Transitions_Disappear_When_You_Zoom_Out_v0.1.md) — The FIT/RG Visibility Law: structural reality and observational visibility are not identical.

Companion technical document: [`docs/core/renormalization_lens.md`](../docs/core/renormalization_lens.md)

---
## AGI Essays

This subseries focuses on AGI development as a closed-loop engineering problem:
what progress looks like without structural discipline, and how to make progress auditable.

1. [`agi/00_agi_without_and_with_fit.md`](agi/00_agi_without_and_with_fit.md) - World models, spatial intelligence, and the missing system discipline.
2. [`agi/01_agi_engineering_path.md`](agi/01_agi_engineering_path.md) - Loop metrics, constraint engineering, and auditable AGI progress.
3. [`agi/README.md`](agi/README.md) - Series index and reading order.

---
## Long-Form Explorations

Some topics are explored in depth across multiple chapters:

- `agi/`
- `learning-systems/`
- `governance-longform/`
- `technology-longform/`

These materials are exploratory and philosophical in nature.

### Governance long-form (new)

- [`governance-longform/civilization_as_a_dynamical_system.v2.md`](governance-longform/civilization_as_a_dynamical_system.v2.md) — a minimal three-variable civilizational dynamics model with threshold, hysteresis, and coexistence conditions.

---

*For formal usage, analysis, or contribution rules, see the repository root.*
