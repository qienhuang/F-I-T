## Roadmap

### Status overview

- **Stable spec (2.x, discrete/classical)**: `docs/v2.3.md`
- **Draft spec (2.x, EST edition)**: `docs/v2.4.md`
- **Recommended entry point**: `docs/v2.1.md`
- **EST artifacts (templates)**: `est_preregistration_template.yaml`, `est_equivalence_and_coherence_report.md`
- **AI safety writing drafts**: `papers/tempo-as-safety-variable.neurips-workshop.md`, `papers/tempo-as-safety-variable.lesswrong.md`
- **Design ethos**: minimal primitives, explicit level-of-description, operational estimators, falsifiable propositions, and auditable estimator choices (EST)

---

### Milestone 0 - Stabilize the 2.x line (0-3 months)

**Goal**: Make the current discrete/classical FIT stack stable and easy to critique.

- [ ] Freeze `docs/v2.3.md` as the authoritative 2.x reference (discrete, classical)
- [ ] Keep `docs/v2.1.md` as the reader-friendly / citation entry point, with a pointer from the README to both
- [ ] Finalize the proposition registry schema (YAML/JSON) for P1-P18:
  - IDs, short names, scope conditions, estimator tuples, boundary declarations, protocol, status
  - EST fields (v2.4): `equivalence_requirement`, coherence gates, admissibility checklist, robustness reporting
- [x] Add EST pre-registration template: `est_preregistration_template.yaml`
- [x] Add EST equivalence + coherence report template: `est_equivalence_and_coherence_report.md`
- [ ] Publish minimal Tier-1 validation scripts for:
  - Conway's Game of Life (P1, P2, P4, P7, P9, P10, P17, P18)
  - Langton's Ant (P1, P3, P4, P10, P11, P18)
- [ ] Add a short "How to falsify FIT" guide (where to attack first, and how to record negative results)

**Success criterion**:  
Anyone can clone the repo, run a small script, and see concrete evidence for or against a subset of P1-P18 on GoL / Langton's Ant.

---

### Milestone 1 - Tier-1 validation & tooling (3-9 months)

**Goal**: Turn FIT from a conceptual framework into a living experimental object.

- [ ] Clean, documented Python reference implementations for:
  - GoL + FIT estimators (`S_t, F, C, I`) and plotting
  - Langton's Ant + estimators and plotting
- [ ] Reproducible validation notebooks for key propositions:
  - P1 / P2 / P4 on GoL
  - P3 / P11 on Langton's Ant
- [ ] Wire validation scripts to the proposition registry:
  - Each proposition has at least one runnable protocol and status field (`Untested | Partial | Supported | Falsified | Scope-limited`)
- [ ] Add CI hooks (optional) to run a light validation suite on push

**Success criterion**:  
At least 5-8 propositions have a clear status on Tier-1 systems, and the repo can be used as a reference implementation for people trying to break or extend FIT.

---

### Milestone 2 - Continuous-time FIT (towards v3.0-C) (6-18 months)

**Goal**: Lift FIT from discrete updates to a continuous-time formulation with real theorems.

Focus on a "mother class" of stochastic differential equations (gradient diffusions):

- [ ] Define a continuous-time FIT layer:
  - State: $ S(t) = X_t \in \mathbb{R}^d $
  - Dynamics: $ dX_t = F(X_t)\,dt + \sigma(X_t)\,dW_t $
  - Information: entropy / relative entropy $ D(\mu_t \Vert \mu_\infty) $
  - Constraint: Lyapunov-style functionals $ C(t) = C_{\max} - \mathbb{E}_\mu[\Phi(X_t)] $
- [ ] Prove at least one "hard" theorem in this setting:
  - Continuous P2: monotone constraint accumulation under suitable conditions
  - Continuous P3: exponential (or power-law) decay of force variance in gradient flows
- [ ] Write a short standalone paper:
  - "Constraint Accumulation and Force-Variance Collapse in Gradient Diffusions: A Continuous-Time Case Study in the FIT Framework."
- [ ] Draft a `docs/v3/fit_continuous_v3.0-alpha.md` describing:
  - New notation and assumptions
  - Theorems as continuous-time analogues of v2.x P2/P3/P13
  - How continuous-time T-theory is formulated (hitting times, exit times, quasi-stationary distributions)

**Success criterion**:  
There exists at least one self-contained continuous-time FIT document + math appendix that turns "constraint accumulation & force-variance collapse" into a proper theorem for a non-trivial class of SDEs.

---

### Milestone 3 - Quantum FIT (towards v3.0-Q) (9-24 months)

**Goal**: Define a minimal quantum version of the five primitives and validate FIT-style claims on small Lindbladian models.

- [ ] Specify quantum primitives:
  - State: density matrices $ \rho(t) $
  - Force: generator $ \mathcal{L}[\rho] $ (Lindbladian / Liouvillian)
  - Information: von Neumann entropy, quantum relative entropy
  - Constraints: rank / support restrictions, decoherence functionals, or relative-entropy-to-fixed-point functionals
- [ ] Work through 2-3 solvable toy models:
  - Qubit pure dephasing (pointer basis / decoherence)
  - Amplitude damping (relaxation to a ground state)
  - Simple thermalization to a Gibbs state
- [ ] Demonstrate quantum analogues of core FIT patterns in these models:
  - Monotone "quantum constraint" functional
  - Decay of a suitable "force variance" operator norm
  - A clean notion of "quantum nirvana" (fixed points / pointer states)
- [ ] Draft a `docs/v3/fit_quantum_v3.0-alpha.md` or a short paper:
  - "Quantum FIT: Constraint and Drift Collapse in Simple Lindbladian Systems."

**Success criterion**:  
At least one non-trivial Lindblad model is worked out end-to-end with clear quantum versions of $ C(t) $ monotonicity and "force" collapse, plus a precise definition of quantum T-theory in that setting.

---

### Milestone 4 - FIT v3.0 integration & restructuring (18-36 months)

**Goal**: Merge discrete, continuous, and quantum layers into a coherent "v3.x generation" of FIT.

- [ ] Refactor the main spec into three coordinated parts:
  - Part I: Discrete / classical FIT (2.x line, cleaned up and trimmed)
  - Part II: Continuous-time FIT (SDE / Markov semigroup layer)
  - Part III: Quantum FIT (finite-dimensional Lindblad layer)
- [ ] Reclassify P1-P18 by mathematical status:
  - "Theorem in discrete", "Theorem in continuous", "Theorem in quantum", "Empirical only", "Open problem"
- [ ] Elevate T-theory to a first-class sub-document:
  - T-theory for discrete systems
  - T-theory for continuous-time SDEs
  - T-theory for open quantum systems (pointer states / decoherence)
- [ ] Add a section on scale transformations:
  - How $ F, I, C $ transform under coarse-graining / renormalization
  - When FIT-style laws are preserved or modified across scales

**Success criterion**:  
A reader can see, in one place, how FIT behaves in discrete, continuous, and quantum regimes; which propositions are proved where; and how T-theory sits on top of all three.

---

### Milestone 5 - Applications and external collaborations (parallel / ongoing)

**Goal**: Turn FIT from internal conceptual program into a toolbox for other fields.

- [ ] AI safety:
  - Draft / iterate IO + tempo-governance paper: `papers/tempo-as-safety-variable.neurips-workshop.md`, `papers/tempo-as-safety-variable.lesswrong.md`
  - Formalize "alignment nirvana" and T-theory style monitoring of $ C(t) $ and $ \sigma^2(F) $
  - Release example code for "termination-friendly" RL experiments
- [ ] Complexity / critical phenomena:
  - Work with collaborators on P13 / P14 / P16-P18 in ecosystems, climate models, and ML training dynamics
- [ ] Institutional / governance design:
  - Use $ I/C $ and constraint hierarchy ideas to analyze stability vs adaptability in simple institutional models
- [ ] Keep the repo as the canonical registry for:
  - Proposition definitions and statuses
  - Validation scripts and negative results
  - Links to external papers and implementations

---

If you are interested in collaborating on any milestone, please open an issue or a discussion thread and reference the relevant milestone ID.
