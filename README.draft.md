# FIT Framework

*A minimal axiomatic framework for evolutionary dynamics across substrates*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18039307.svg)](https://doi.org/10.5281/zenodo.18039307)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Author**: Qien Huang  
**ORCID**: https://orcid.org/0009-0003-7731-4294  
**Status**: Research preprint (v2.3, revised with Tier-1 computational validation)

---

## What is FIT?

FIT (Force–Information–Time) is a minimal, level-aware axiomatic framework for
describing evolutionary dynamics across physical, biological, cognitive, social,
and AI systems.

It is built on five primitives — **Force, Information, Time, Constraint, State** —
and six principles that generate **18 falsifiable propositions** about nirvana
dynamics, information–constraint relationships, and universal scaling.  
v2.3 introduces an explicit **Estimator Specification Layer** and a named
late-stage sub-framework **T-theory**. 

---

## What’s new in v2.3?

Compared to v2.2: 

- Estimator tuple  $\mathcal{E} = (S_t, \mathcal{B}, \{\hat{F},\hat{C},\hat{I}\}, W)$  
  → all propositions are stated as  $P_i[\mathcal{E}]$ .
- Clear separation between core principles ( $\mathcal{L}1$–$\mathcal{L}3$ ) and
  working hypotheses ( $\mathcal{H}4$–$\mathcal{H}6$ ).
- Completed **Tier-1 validation** on Conway’s Game of Life and Langton’s Ant
  (97.5% theory–observation match for the Langton highway).
- T-theory: a named sub-framework for late-time, high-constraint (“nirvana”)
  dynamics with direct applications to AI safety.

See the full revised paper for details:

- **FIT v2.3 (Revised Edition, EN)** – [`docs/FIT_v2.3_Revised_en.md`](docs/FIT_v2.3_Revised_en.md)  
- **FIT v2.3 中文版** – [`docs/fit_full_v2.3.zh_cn.md`](docs/fit_full_v2.3.zh_cn.md)

---

## Repository structure

```text
F-I-T/
├── docs/
│   ├── FIT_v2.3_Revised_en.md    # main paper (EN)
│   ├── fit_full_v2.3.zh_cn.md    # main paper (ZH)
│   └── AI_SAFETY_T_THEORY_outline.md
├── experiments/
│   ├── conway/
│   │   ├── conway_fit_experiment.py
│   │   ├── figures/              # P2/P7/P10 plots, dashboards
│   │   └── RESULTS.md
│   └── langton/
│       ├── langton_open.py       # correct open-boundary version
│       ├── langton_periodic.py   # periodic version (teaching counterexample)
│       └── RESULTS.md
├── registry/
│   └── propositions_v2.3.yaml    # machine-readable proposition registry
└── README.md
