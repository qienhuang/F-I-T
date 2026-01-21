![Logo](imgs/banner_v2.png)

# F-I-T (Force-Information-Time)

> Canonical entry point for the public distribution layer. Navigation: `MANIFEST.md`. Binding rules: `CHARTER.md`.

A **falsifiable, phase-conditional framework**
for analyzing evolutionary dynamics across systems.

This repository is the **public distribution layer** of FIT (v2.4.x).

---

## What this repository is

FIT is a **descriptive framework**, not a normative system.

It provides:
- a minimal set of primitives
- estimator-bound propositions
- phase-conditional usage discipline

to analyze how systems evolve under force, information, and constraint over time.

This repository exists to make that framework **publicly inspectable, testable, and auditable**.

---

## Intuition and Motivation (Non-Binding)

For non-technical, philosophical intuition behind why a framework like FIT may be needed,
see the essays in [`/essays`](./essays).

These texts are **non-binding** and do not define FIT semantics.
All formal definitions, constraints, and claims are specified elsewhere.

---

## Binding constraint (read first)

All public usage, citation, and contribution is **bound** by explicit rules.

Before using or citing this work, read:

- **CHARTER.md** - binding constraints, scope, and falsifiability discipline

If a claim conflicts with the Charter, the Charter prevails.

---

## What you can do

You may:

- Analyze systems using declared estimators and phase scope
- Compare structural dynamics across domains under the same discipline
- Extend domain indexes **without changing core semantics**
- Propose falsifiable semantic changes through the issue process

All usage must be estimator-bound and phase-declared.

---

## What you cannot do

You may not:

- Treat FIT as a prescriptive, policy, or moral framework
- Invoke propositions without declaring an estimator tuple
- Use FIT to justify coercive decisions or authority
- Rebrand FIT as a total or universal theory
- Introduce new core concepts in the public layer

Such usage is out of scope.

---

## Repository map

- **MANIFEST.md**  
  One-page navigation map for the public layer

- **CHARTER.md**  
  Binding rules and usage discipline

- **overview/**  
  Structural overviews  
  - `temporal-structure.md` - how time is handled  
  - `failure-taxonomy.md` - cross-domain failure patterns

- **domains/**  
  Public domain indexes (where FIT/T-Theory is applied)  
  - `learning/`  
  - `economics/`  
  - `governance/`  
  - `technology/`

- **lenses/**  
  Structural templates ("how to apply"), not essays  
  - `_TEMPLATE/DOMAIN_STRUCTURE.md`  
  - per-domain `STRUCTURE.md`

- **papers/**  
  Publication-grade artifacts (each has its own scope and limits)  
  - `papers/markov-sandbox/README.v2.md` - provable specialization in finite Markov chains

- **CONTRIBUTING.md**  
  Contribution rules and review discipline

- **STYLE.md**  
  Mandatory writing and math hygiene for the public layer

---

## How to start (minimal protocol)

1. Declare the system and boundary
2. Declare phase scope
3. Declare estimator tuple $ \mathcal{E} $
4. Select applicable propositions
5. Analyze behavior
6. Accept or reject claims based on observation

Skipping steps invalidates the analysis.

---

## Contributing

This repository accepts contributions under strict discipline.

- Documentation and navigation fixes  
- Domain index extensions under existing constraints  
- Semantic proposals via structured Issues only

See **CONTRIBUTING.md** before opening a PR.

---

## Version status

- **Public distribution layer**: v2.4.x (stable)  
- Research evolution continues outside this layer

All public claims must specify the version they rely on.

---

## Citation

If you cite this work, cite the repository and the exact version,
and respect the constraints defined in **CHARTER.md**.
