![Logo](imgs/banner_v2.png)

# F-I-T (Force–Information–Time) Dynamics Framework

### A minimal, falsifiable lens for analyzing evolution across physical, biological, cognitive, social, and AI systems.

[[中文/Chinese]](README.zh_cn.md) | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18012401.svg)](https://doi.org/10.5281/zenodo.18012401) | [![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) | [![Read v2.4](https://img.shields.io/badge/Read-v2.4-red)](docs/v2.4.md)

---

## Start Here (choose your path)

| If you are... | Start with |
|---------------|------------|
| **New to FIT** (5 min) | [Core Card](docs/core/fit_core_card.md) — one-page primitives + intuition |
| **Evaluating the framework** | [What FIT claims](#what-fit-claims-and-does-not-claim) → [Tier-1 evidence](#tier-1-evidence-toy-systems) |
| **Working on AI safety** | [AI Safety Index](docs/ai_safety/README.md) → [FIT for AI Safety](docs/ai_safety/fit_ai_safety_mapping.md) |
| **Running experiments** | [Toolkits](#toolkits) → [Li² replication](experiments/li2_scaling_law/README.md) |
| **Reading the full spec** | [v2.4 spec (English)](docs/v2.4.md)  / [v2.4 中文(Chinese)](docs/zh_cn/v2.4.zh_cn.md) |

---

## The Core Idea (30 seconds)

Many systems fail not from lack of power or information, but because **high-impact changes become irreversible faster than correction can occur**.

FIT treats **tempo** (the relationship between action timescales and correction timescales) as a first-class variable.

**Five primitives**:

| Primitive | What it captures |
|-----------|------------------|
| **State (S)** | System configuration |
| **Force (F)** | Directed influence / drift |
| **Information (I)** | Entropy reduction / knowledge gain |
| **Constraint (C)** | Reachable state space reduction |
| **Time (T)** | Characteristic scales emergent from F–I interaction |

**The discipline**: All claims must be bound to an explicit estimator tuple. No estimator → no claim.

---

## What FIT Claims (and Does Not Claim)

| FIT does NOT claim | FIT DOES claim |
|--------------------|----------------|
| ❌ A "theory of everything" | ✅ A minimal meta-language for discussing evolution |
| ❌ Replacement for FEP, Constructor Theory, etc. | ✅ Falsifiable through computational/empirical experiments |
| ❌ Ability to predict exact trajectories | ✅ Initial Tier-1 validation shows promising results |
| ❌ All propositions validated everywhere | ✅ AI safety applications are tractable |

---

## Tier-1 Evidence (toy systems)

| System | Result | Proposition |
|--------|--------|-------------|
| **Langton's Ant** | 97.5% theory–observation match | Phase transition / nirvana predictions |
| **Conway's GoL** | 0% violations | P7 information bounds |
| **Conway's GoL** | ρ = 0.775 | P10 estimator coherence |

![Conway's Game of Life: Tier-1 validation snapshot](experiments/figures/conway_status_overview.png)

*Figure: Conway's Game of Life Tier-1 validation (details in [v2.4 spec](docs/v2.4.md)).*

## Tier-2 Evidence
- **Grokking** experiments are evaluable and reproducible; baseline not yet a stable hard indicator under strict low-FPR constraints. See [tier2_grokking](experiments/tier2_grokking/README.md) and [grokking_hard_indicators_v0.2](experiments/grokking_hard_indicators_v0_2/README.md).
- A real-world Tier-2 / P11 case is now available on **NYC TLC Yellow Taxi** data. Under EST gates, pooled coherence fails while preregistered windowing yields auditable scope-limited validity (`OK_PER_YEAR`, `OK_PER_WINDOW`): [nyc_tlc_tier2p1](experiments/real_world/nyc_tlc_tier2p1/README.md) (results: [RESULTS.md](experiments/real_world/nyc_tlc_tier2p1/RESULTS.md); viz: [summary](experiments/real_world/nyc_tlc_tier2p1/results_runs/figures/nyc_tlc_windowed_coherence_summary.svg), paper: [Phase-Conditioned Constraint Coherence in a Real-World Mobility System](papers\phase-conditioned_constraint_coherence_in_a_real-world_mobility_system.v1.md))  
![process figure](experiments/real_world/nyc_tlc_tier2p1/results_runs/nyc_yellow_2019_2023_v1.6_precovid_postcovid/tradeoff_onepage.png)

---

## Papers

| Topic | Link |
|-------|------|
| **FIT Origin & Design Goals** (start here) | [Zenodo](https://doi.org/10.5281/zenodo.18142211) |
| **AI Safety: Irreversible Operations & Tempo Mismatch** | [Zenodo](https://doi.org/10.5281/zenodo.18142151) |
| **AI Safety (grokking): Controlled Nirvana** | [Zenodo](https://doi.org/10.5281/zenodo.18155425) / [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6023634) |
| **AI Safety (grokking): Hard Indicators Protocol** | [Zenodo](https://doi.org/10.5281/zenodo.18380476) |
| **Markov Sandbox (math.PR)** | [Zenodo](https://doi.org/10.5281/zenodo.18264166) |
| **Beyond Moral Charters** | [Zenodo](https://doi.org/10.5281/zenodo.18341340) |
| **Why Companies Turn Too Late** | [Zenodo](https://doi.org/10.5281/zenodo.18287053) |
| **Phase-Conditioned Constraint Coherence in a Real-World Mobility System** | [Zenodo](https://doi.org/10.5281/zenodo.18420569) |
---

## Case Studies

Self-contained FIT analyses (read-and-apply). Each case has explicit boundaries and observable signals.

| Case | Focus |
|------|-------|
| [Grokking scaling-law (Li²)](experiments/li2_scaling_law/README.md) | ML phase transition |
| [AlphaFold DB confidence regimes](experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes/README.md) | Real-world instrumentation boundaries |
| [NYC TLC (Yellow) regime shifts](experiments/real_world/nyc_tlc_tier2p1/README.md) | Tier-2 P11; coherence windowing and level shifts |
| [Smartphones & Attention](docs/cases/CASE_01_Phone_Attention_System.md) | Attention dynamics + constraint accumulation |
| [Content Platform Involution](docs/cases/CASE_02_Content_Platform_Involution.md) | Feedback loops + coordination failure |
| [Enterprise IT Evolution](docs/cases/CASE_03_Enterprise_IT_Evolution.md) | Infrastructure lock-in + tempo mismatch |
| [Learning: Memory to Understanding](docs/cases/CASE_04_Learning_From_Memory_to_Understanding.md) | Grokking as phase transition |
| [Bicontinuous Multiscale Design](docs/cases/CASE_05_Data_Driven_Inverse_Design_Bicontinuous_Multiscale.md) | Boundary-identical microstructure library |
| [BioArc Architecture Search](docs/cases/CASE_06_BioArc_Constrained_Architecture_Search.md) | Budgeted exploration under constraints |
| [Motor-imagery BCI](docs/cases/CASE_07_Motor_Imagery_BCI_Monitorability.md) | Monitorability under low-FPR budgets |

---

## Toolkits

Runnable, CPU-first building blocks. Each produces auditable artifacts.

| Toolkit | Purpose |
|---------|---------|
| [Toolkits Index](tools/README.md) | Entry point for all runnable demos |
| [FIT Proxy Alarm Kit](tools/fit_proxy_alarm_kit/README.md) | Non-LLM specialist + label budget + fixed FPR |
| [FIT Constrained Explorer Kit](tools/fit_constrained_explorer_kit/README.md) | Budgeted search under hard constraints |
| [FIT EWBench Kit](tools/fit_ewbench_kit/README.md) | Prompt suite runner + logs + report |
| [FIT Hopfield Lab Kit](tools/fit_hopfield_lab_kit/README.md) | Toy associative-memory lab + phase diagrams |
| [Explorers Index (FIT-Explorer + extensions)](docs/explorers/README.md) | Budgeted method search specs + extension docs |
| [World-Evolution Explorer (v0.1)](docs/world_evolution/README.md) | Toy evolving worlds + effective-variable / alarm search demo |
| [Math-Discovery Engine (v0.1)](docs/math_discovery/README.md) | Auditable search over representations/lemmas/strategies (spec-first) |
| [GMB v0.4](docs/benchmarks/gmb_v0_4/README.md) | Grokking alarm admissibility benchmark |

---

## AI Safety Track

| Resource | Description |
|----------|-------------|
| [AI Safety Index](docs/ai_safety/README.md) | Main entry point |
| [FIT for AI Safety](docs/ai_safety/fit_ai_safety_mapping.md) | 5-min overview + 2-hour self-assessment |
| [Self-referential IO standard](docs/ai_safety/self_referential_io.md) | IO constraint specification |
| [CPU-first local agent](papers/cpu-first-local-agent-on-16gb-deepseek-distill.v0.2.md) | 16GB RAM blueprint |
| [Slow-evolving agent architecture (v0.2)](docs/agents/README.md) | FIT/EST-aligned agent specs + runnable pre-validator checklist |
| [Dr.One demo](examples/dr_one_demo/README.md) | Self-edit loop + monitorability gate |
| [DeepSeek R1 case note](docs/ai_safety/deepseek_r1_fit_case_note.md) | R1-style RL + risk control |

### Dr.One: Baseline vs Controlled

![Dr.One policy-eval: baseline vs controlled](examples/dr_one_demo/results/figures/dr_one_gating_readwrite_v1.svg)

*If a low-FPR alarm is feasible, a controller can withhold execution authority for unsafe actions without stopping computation. Reproducibility: [MATRIX_PROTOCOL.md](examples/dr_one_demo/results/MATRIX_PROTOCOL.md)*

---

## Spec Versions

| Version | Description | Link |
|---------|-------------|------|
| **v2.4.1** (current) | EST + Tier-1 validation | [docs/v2.4.md](docs/v2.4.md) |
| v2.3 | Tier-1 validation | [docs/v2.3.md](docs/v2.3.md) |
| v2.1 | Legacy discussion edition | [docs/v2.1.md](docs/v2.1.md) |

**Stability**: 2.x core is stabilized; revisions are counterexample-driven. See [Versioning Policy](docs/core/Versioning_Policy.md).

---

## Roadmap

| Milestone | Goal |
|-----------|------|
| **M0** | Stabilize 2.x spec; publish Tier-1 scripts |
| **M1** | Reference implementations; 5–8 propositions with reproducible status |
| **M2** | Continuous-time FIT (SDE layer); constraint-accumulation theorem |
| **M3** | Quantum FIT (Lindbladian layer) |
| **M4** | Unified v3.0 (discrete / continuous / quantum) |
| **M5** | Applications: AI safety, complexity science, institutional design |

**Full roadmap**: [docs/roadmap.v2.4.md](docs/roadmap.v2.4.md)

---

## Repository Map

```
docs/           Specifications and notes
  ai_safety/    Self-referential IO and governance
  benchmarks/   Specs + prereg templates (e.g., GMB v0.4)
  explorers/    Budgeted method search (FIT-Explorer)
experiments/    Runnable demos and validation artifacts
papers/         Drafts and venue-specific writeups
proposals/      Practitioner pilots and templates
skills/         Codex CLI skills (optional)
tools/          Runnable toolkits
```

---

## Citation

**Zenodo (all versions)**: https://doi.org/10.5281/zenodo.18012401  
**Latest (v2.4.1)**: https://doi.org/10.5281/zenodo.18112020  

See [CITATION.cff](CITATION.cff) for copy/paste formats.

---

## Metadata

**Author**: Qien Huang (Independent Researcher)  
**Email**: qienhuang@hotmail.com  
**License**: CC BY 4.0  
**Repository**: https://github.com/qienhuang/F-I-T  
**ORCID**: https://orcid.org/0009-0003-7731-4294  

**AI-assisted drafting disclosure**: Portions of drafting were assisted by large language models. The author takes full responsibility for all content.

![footer_banner](imgs/footer_banner.png)
