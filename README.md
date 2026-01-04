
![Logo](imgs/banner_v2.png)

# The F‑I‑T (Force–Information–Time) Dynamics Framework

## A Constraint‑Driven Lens on Evolution Across Physical, Biological, Cognitive, Social, and AI Systems

[[中文/Chinese]](README.zh_cn.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![Read v2.4](https://img.shields.io/badge/Read-v2.4-red)](docs/v2.4.md)

**Zenodo (all versions):** https://doi.org/10.5281/zenodo.18012401 | **Latest release (v2.4.1):** https://doi.org/10.5281/zenodo.18112020  
**Current spec (v2.4.1):** [docs/v2.4.md](docs/v2.4.md)  
**Framework established:** Dec 10, 2025 (original)

**Author**: Qien Huang (Independent Researcher)  
**E-mail**: qienhuang@hotmail.com  
**License**: CC BY 4.0  
**Repository**: https://github.com/qienhuang/F-I-T  
**ORCID**: https://orcid.org/0009-0003-7731-4294

## Specs (start here)

- **Current spec (v2.4.1, EST + Tier‑1 validation)**: [docs/v2.4.md](docs/v2.4.md) (EN), [docs/zh_cn/v2.4.zh_cn.md](docs/zh_cn/v2.4.zh_cn.md) (中文/Chinese)
- **Previous edition (v2.3, Tier‑1 validation)**: [docs/v2.3.md](docs/v2.3.md)
- **Legacy discussion edition (v2.1)**: [docs/v2.1.md](docs/v2.1.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## Quick Overview

**The problem**: Modern science approaches evolution through fragmented lenses (thermodynamics, information theory, complexity science, ML). They succeed in isolation but lack shared axioms for cross-domain synthesis.

**FIT's response**: Compress "evolution" into five primitives (**Force**, **Information**, **Time**, **Constraint**, **State**) and six principles. Generate 18 falsifiable propositions bound to explicit estimator tuples.

**Core insight**: Many systems fail not from lack of power or information, but because high-impact changes become irreversible faster than correction can occur.

**The five primitives (formal definitions)**:

| Primitive | Definition | Interpretation |
|-----------|------------|----------------|
| **State (S)** | $S_t \in \mathcal{S}$ | System configuration at time $t$ (or $t$ index) |
| **Force (F)** | $\mathbb{E}[S_{t+1} - S_t \mid S_t] = \alpha F(S_t, t)$ | Generalized drift / directed influence |
| **Information (I)** | $I_{\text{gain}} := H(P_0) - H(P_1)$ | Entropy reduction / knowledge gain |
| **Constraint (C)** | $C(t) := \log \lvert \mathcal{S} \rvert - \log \lvert \mathcal{S}_{\text{accessible}}(t) \rvert$ | Reachable state space reduction |
| **Time (T)** | Ordered index $t$ with characteristic scales | Emergent from F–I interaction |

**v2.4 key features**:
- **Estimator Selection Theory (EST)**: 8 admissibility axioms (A1–A8) preventing "estimator-hacking" critiques
- **18 falsifiable propositions** with explicit success/failure criteria
- **Tier-1 validation**: 97.5% theory–observation match (Langton's Ant), P7 bounds 0% violations (Conway's GoL)
- **AI safety track**: tempo mismatch + Irreversible Operations as distinct failure mode

**Read the full spec**: [docs/v2.4.md](docs/v2.4.md)

## Entry points (practical)

- **Two-week pilot (teams)**: [proposals/tempo-io-pilot.md](proposals/tempo-io-pilot.md) + [proposals/tempo-io-pilot-pack/](proposals/tempo-io-pilot-pack/)
- **Self-referential IO standard**: [docs/ai_safety/self_referential_io.md](docs/ai_safety/self_referential_io.md) + [docs/ai_safety/io_sr_mapping.md](docs/ai_safety/io_sr_mapping.md)
- **Runnable demo**: [examples/self_referential_io_demo.ipynb](examples/self_referential_io_demo.ipynb) + [examples/run_demo.py](examples/run_demo.py)
- **arXiv anchor draft (IO × tempo mismatch)**: [papers/irreversible-operations-tempo-mismatch.arxiv.compact.md](papers/irreversible-operations-tempo-mismatch.arxiv.compact.md)

## Tier‑1 evidence (toy systems)

- **Langton's Ant (open boundary)**: 97.5% theory–observation match for net displacement; supports key phase-transition / nirvana predictions.
- **Conway's Game of Life**: P7 information bounds (0% violations), P10 estimator coherence (rho = 0.775); P2 constraint monotonicity challenged under current estimator.

![Conway's Game of Life: Tier-1 validation snapshot (FIT v2.4).](experiments/figures/conway_status_overview.png)

*Figure: Conway's Game of Life Tier‑1 validation snapshot (details in [docs/v2.4.md](docs/v2.4.md)).*

## Why F‑I‑T?

I attempt to answer the same question in a unified way:
From quantum and molecules to cells, individuals, organizations, nations, and civilizations—why do clearly defined hierarchical structures emerge? Why does evolution often manifest as a repeating rhythm of "oscillation—stability—aggregation—re-stability"? Why do many systems fail not because of insufficient power or lack of information, but because the "pace of doing things" is wrong?

I ultimately compressed "evolution" into three minimal variables:

- **Force (F)**: The action that drives or constrains system change (interactions, selection pressures, institutional constraints, objective function gradients).
- **Information (I)**: Structures that can persist in time and produce causal effects (codes, forms, patterns, models).
- **Time (T)**: Not a background scale, but a spectrum of characteristic time scales (rhythms) emergent from the interaction of F and I.

**F‑I‑T is a meta-framework, not a theory of a specific domain.**  
Its purpose is: to first reduce any problem of "evolution, development, origin, collapse, innovation" to `(F, I, T)`, and then discuss levels, critical points, and transition paths.

<details>
<summary>Show the original v1.0 intuition (historical)</summary>

### I. Core Definitions and Basic Propositions

1. **What is F‑I‑T**: It is a meta-framework for observing, analyzing, and explaining the evolution of any complex system. It posits that system evolution can be deconstructed into the interaction of three fundamental elements: **Force**, **Information**, and **Time**.
2. **Basic proposition**: Specific forces act upon a system, shaping or selecting specific information structures; once formed, this structure possesses relative stability and persists within its characteristic time scale, while simultaneously reacting back upon the force field. Evolution is the process of continuous interaction and iteration among these three.

### II. Connotations of the Three Core Elements

1. **Force (F)**: Any energy, pressure, or rule that drives system change or constrains the direction of its change (physical, biological, cognitive, social, algorithmic). Key attributes: directionality and intensity.
2. **Information (I)**: Any structure, pattern, or code within a system that can reduce uncertainty and possesses a certain degree of persistence (DNA, organs, legal systems, linguistic symbols, models, conventions). Key attributes: stability, transmissibility, functionality.
3. **Time (T)**: An intrinsic property endogenous to the system’s evolutionary process. Systems at different levels have characteristic time scales matched to their refresh rates and rhythms. Key attributes: scalability and relativity.

### III. Five Basic Principles of the Framework

1. **Hierarchical nesting**: The world is composed of nested levels; each level emerges from information structures below and serves as platform for force and information above.
2. **Cross-level transition**: Bottom-up interactions can reach critical points where information structures undergo phase transitions, birthing new levels with new F‑I‑T coordinates.
3. **Multi-level time coupling**: Evolution couples processes across fast and slow time scales; macro-evolution is a symphony of temporal rhythms.
4. **Cyclical reinforcement**: Force shapes information; stabilized information becomes a new force (constraint/driver), forming cycles.
5. **Path dependence**: Evolutionary trajectories depend strongly on initial conditions and historical perturbations; history is irreversible.

</details>

## ❗Why tempo matters

Many complex systems fail not because they lack power or information, but because high-impact changes become irreversible faster than the system can correct them.

FIT treats tempo (correction timescales) as a first-class variable.

## Roadmap

- [docs/roadmap.v2.4.md](docs/roadmap.v2.4.md)

## Repository map

- `docs/` - specifications and notes
- `proposals/` - practitioner pilots and templates
- `docs/ai_safety/` - self-referential IO and governance docs
- `examples/` and `experiments/` - runnable demos and validation artifacts
- `papers/` - drafts and venue-specific writeups
- `CITATION.cff` - citation metadata for this repository

## Citation

Use `CITATION.cff` for copy/paste formats, or cite via Zenodo:

- Zenodo (all versions): https://doi.org/10.5281/zenodo.18012401
- Latest release (v2.4.1): https://doi.org/10.5281/zenodo.18112020

## License

Text and documentation in this repository are licensed under **CC BY 4.0**.

## AI-assisted drafting disclosure

Portions of drafting and editing were assisted by large language models. The author takes full responsibility for all content, claims, and errors.

![footer_banner](imgs/footer_banner.png)
