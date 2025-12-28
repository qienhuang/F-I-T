# Changelog

All notable changes to the FIT Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v2.4] - 2025-12-28

**Estimator Selection Theory Edition**

### Added
- **Estimator Selection Theory (EST)**: Formal framework defining admissible estimators to reduce estimator manipulation critiques.
- **Admissibility Axioms (A1-A8)**: Scope, robustness, monotonicity, representation invariance, P10 coherence gate, pre-registration, complexity penalty, task-typed validity.
- **Task-Typed Equivalence Notions (E1-E3)**: Ordinal, metric, and topological equivalence classes specifying what structure different propositions require.
- **Extended P10 consistency gating**: Task-typed coherence requirements for estimator families.
- **Robustness reporting requirements**: Mandatory reporting across admissible estimator families.
- **EST audit artifacts**:
  - Pre-registration protocol template: `est_preregistration_template.yaml`
  - Equivalence + coherence report template: `est_equivalence_and_coherence_report.md`
- **Validation results** (Tier-1 computational validation on Conway's Game of Life and Langton's Ant):
  - Langton's Ant (open boundary): 97.5% theory-observation match for net displacement; strong support for P11, P1, P3.
  - Conway's Game of Life: 0% violation rate on P7 (information bounds); P10 coherence confirmed (rho = 0.775).
- **Chinese translation**: `docs/zh_cn/v2.4.zh_cn.md`

### Changed
- Estimator Specification Layer upgraded from "good methodology" to "auditable measurement theory".
- Refined dependency structure between Core Principles (L1-L3) and Working Hypotheses (H4-H6).

### Key insight
- Boundary conditions fundamentally affect evolutionary dynamics: periodic boundaries in Langton's Ant prevent highway formation by introducing artificial constraints, while open boundaries allow natural constraint accumulation to predicted nirvana states.

---

## [v2.3] - 2025-12

**Estimator Specification Layer Edition**

### Added
- **Estimator Specification Layer**: Explicit recognition that all propositions are evaluated relative to estimator tuples  $ \mathcal{E} = (S_t, \mathcal{B}, \{\hat{F},\hat{C},\hat{I}\}, W) $ .
- **P10 (Estimator Coherence)**: New proposition requiring correlation between independent estimators of the same primitive.
- **18 falsifiable propositions**: Complete set covering thermodynamics, information theory, and complexity science.
- **T-theory sub-framework**: Named sub-framework for late-stage high-constraint dynamics ("nirvana states").
- **Validation roadmap**: Tiered validation strategy (Tier-1 toy systems -> Tier-2 biological -> Tier-3 AI/social).
- **Chinese translation**: `docs/zh_cn/fit_full_v2.3.zh_cn.md`

### Changed
- Propositions now explicitly state estimator dependencies.
- Clear distinction between near-tautological Core Principles and empirical Working Hypotheses.

---

## [v2.2] - 2025-12

### Added
- Refined axiom structure.
- Improved falsifiability criteria.
- Extended application domains.

---

## [v2.1] - 2025-12

### Added
- Initial formalization of Force-Information-Time primitives.
- Six governing principles (L1-L3, H4-H6).
- Basic proposition set.
- Cross-substrate applicability claims.

---

## [v2.0] - 2025-12

### Added
- Major restructuring from v1.0.
- Formal primitive definitions.
- Initial principle hierarchy.

### Archived
- `docs/archive/v2.0/v2.0.archived.md`

---

## [v1.0] - 2025-12-10

### Added
- Initial framework concept.
- Basic Force-Information-Time intuition.
- Preliminary scope definition.

---

## Version naming convention

- **Major versions** (v1, v2, v3): Fundamental framework changes.
- **Minor versions** (v2.1, v2.2, etc.): Significant additions or refinements.
- **Edition names**: Highlight the key contribution of each version.
  - v2.3: "Estimator Specification Layer Edition"
  - v2.4: "Estimator Selection Theory Edition"
  - v3.0-C (planned): "Continuous Time Foundation"

---

## Links

- **Repository**: https://github.com/qienhuang/F-I-T
- **Current spec**: `docs/v2.4.md` (English), `docs/zh_cn/v2.4.zh_cn.md` (Chinese)
- **Contact**: qienhuang@hotmail.com
- **License**: CC-BY-4.0
