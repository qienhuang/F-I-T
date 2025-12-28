# FIT Framework – Notes for Complex Systems / Dynamical Systems Researchers

## 0. TL;DR

This repository does **not** propose a new “theory of everything”.  
It offers a **minimal, estimator-aware, falsifiable meta-language** for talking about evolutionary / learning dynamics across systems that exhibit:

- structure formation and sudden generalization (e.g. grokking-like phenomena),
- phase-transition-like regime changes,
- late-time stabilization / lock-in under accumulating constraints.

If you already work with phase transitions, dynamical systems, or complex adaptive systems, you can think of FIT as:

> an attempt to make a small set of recurring primitives and propositions  
> explicit, testable, and comparable across very different substrates.

Counterexamples, scope limitations, and negative results are **first-class outcomes** here.

---

## 1. What problem is FIT trying to address (in your language)?

Modern work on “evolutionary” / “learning” processes is fragmented:

- statistical physics: phase transitions, scaling exponents, critical slowing down;
- dynamical systems: attractors, basins, Lyapunov spectra;
- evolutionary biology: selection, fitness landscapes;
- machine learning: gradient-based optimization, generalization, representation learning;
- institutional / social systems: norms, lock-in, path dependence.

The same qualitative patterns keep reappearing:

- order emerging from high-entropy or noisy dynamics,
- sudden regime shifts,
- multi-timescale behavior,
- late-time stabilization and irreversibility.

But each field uses its own vocabulary and usually **its own state representation and observables**. Cross-domain statements (including many AI-safety-relevant ones) tend to be vague or tied to very specific models.

FIT attempts **only** the following:

1. Pick a very small set of primitives that seem to reoccur:
   - Force (F) – directed influence / drift in state space  
   - Information (I) – uncertainty / structure  
   - Time (T) – ordered index + emergent timescales  
   - Constraint (C) – restrictions on accessible states  
   - State (S) – chosen level-of-description

2. Make **estimator-dependence explicit** via a tuple

   $$
   \mathcal{E} = (S_t, \mathcal{B}, \{\hat F, \hat C, \hat I\}, W)
   $$

   where you must say:
   - what the state is,
   - which boundary conditions you impose,
   - how you operationally estimate F, C, I,
   - what window / hyperparameters you use.

3. Generate a finite list of **falsifiable propositions** (P1–P18) about:
   - nirvana / attractor dynamics (P1–P6),
   - information–constraint relations (P7–P12),
   - scaling / multi-scale structure (P13–P18),

   and test them on simple, fully controllable systems first.

This is closer to a **common protocol for stating and testing claims**  
than to a new set of equations.

---

## 2. What FIT explicitly does *not* claim

To avoid over-expectation upfront:

- It is **not** a “theory of everything” for complex systems.
- It does **not** derive existing frameworks (FEP, RG, constructor theory, etc.) as special cases, although it can often re-express them.
- It does **not** offer training tricks, optimization algorithms, or methods to accelerate grokking / capability acquisition.
- It does **not** claim universality beyond explicitly stated scope conditions (closure, coarse-graining, estimator choices).

Instead, the concrete, checkable claim is weaker:

> *Given a chosen estimator tuple* $\mathcal{E}$,  
> *certain qualitative propositions about late-time behavior, phase transitions, and multi-timescale structure either hold or fail in your system – and we should record both outcomes in a common registry.*

---

## 3. Minimal technical sketch (so you know where to poke)

At the level of formal structure, v2.3 consists of:

1. **Five primitives**  
   Force, Information/Entropy, Time, Constraint, State – each with an *estimator menu* rather than a single sacred definition.

2. **An estimator specification layer**  
   Every proposition is written as $P_i[\mathcal{E}]$, where $\mathcal{E} = (S_t, \mathcal{B}, \{\hat F, \hat C, \hat I\}, W)$.  
   Truth values are **relative to** this choice.

3. **Six principles / working hypotheses**
   - $\mathcal{L}1–\mathcal{L}3$ : near-tautological core (force as drift, entropy capacity bound, coarse-graining asymmetry).
   - $\mathcal{H}4–\mathcal{H}6$ : empirical hypotheses under additional assumptions (late-time constraint accumulation, nirvana condition, information efficiency).

4. **18 falsifiable propositions (P1–P18)**  
   grouped as:
   - **A: Nirvana dynamics** – irreversibility, late-time constraint behavior, force-variance decay, perturbation recovery, multistability.
   - **B: Information–constraint relations** – capacity bounds, redundancy, estimator coherence, phase-transition signatures.
   - **C: Universal scaling & multi-scale** – critical slowing down, scale-free fluctuations, universality classes (in FIT terms), timescale separation, dimensional collapse.

5. **A proposition registry**  
   A simple machine-readable schema (YAML) that records:
   - the proposition ID,
   - the estimator tuple $\mathcal{E}$,
   - the system / dataset tested,
   - status (Supported / Challenged / Partial / Falsified / Scope-limited),
   - links to code and plots.

v2.3 also includes **Tier‑1 computational tests** on Conway’s Game of Life and Langton’s Ant, with both **positive** and **negative** results documented.

---

## 4. How to “attack” or test FIT from a complex systems point of view

If you want to take this seriously as a *fallible* framework, the intended engagement mode is:

1. **Choose your system and level-of-description**
   - e.g. Ising model, coupled map lattice, flocking model, agent-based economy, trained neural network, etc.
   - Specify $S_t$ : micro vs. macro, what coarse-graining you consider natural.

2. **Specify an estimator tuple $\mathcal{E}$**
   - Boundary $\mathcal{B}$ : open / periodic / reflecting / absorbing.
   - $\hat F$ : drift estimator, gradient proxy, local rule deviation, etc.
   - $\hat C$ : frozen fraction, intrinsic dimension, covariance collapse, compression ratio…
   - $\hat I$ : entropy, block entropy, predictive information, mutual information, etc.
   - Window $W$ : measurement window / smoothing scale.

3. **Pick a small subset of propositions P\_i**
   - For attractor / late-time behavior: P1–P6, P18.
   - For phase transitions: P11, P13–P15.
   - For multi-scale constraints: P16–P17.

4. **Run tests and classify outcomes**
   - SUPPORTED (robust across reasonable estimator choices),
   - CHALLENGED (fails under current $\mathcal{E}$),
   - PARTIAL (regime-dependent),
   - SCOPE-LIMITED (works only under very specific conditions),
   - FALSIFIED (fails under multiple reasonable $\mathcal{E}$).

5. **Record results in the registry**
   - Add your system + $\mathcal{E}$ + status + links to code / plots.
   - Negative results are very welcome – they drive v2.4+ revisions.

If you find a **clean counterexample** (especially to the A/B-class propositions under multiple sane \(\mathcal{E}\)), that is more valuable than “yet another compatible example”.

---

## 5. Where we *expect* FIT to be fragile / wrong (honest weak spots)

From a complex systems / dynamical systems perspective, there are several obvious attack surfaces:

1. **Estimator dependence & coarse-graining**
   - Many propositions are only plausible under “reasonable, coherent” estimators.
   - P10 (“estimator coherence”) is itself a meta-proposition; if you can show natural estimators of C or I systematically disagree in your system, that weakens the overall structure.

2. **Open, strongly driven systems**
   - $\mathcal{H}4$ (late-time constraint accumulation) is plausibly false in many far-from-equilibrium open systems.
   - If you can show long-run cyclic or chaotic behavior with **no meaningful notion of increasing constraint** at any useful level-of-description, that is a serious challenge.

3. **Multi-scale renormalization**
   - v2.3 barely touches “how F, C, I transform under coarse-graining”.
   - If you can show that plausible RG-style flows **systematically break** FIT’s propositions (e.g. P13–P18) across scales, that’s important.

4. **Critical phenomena beyond simple embeddings**
   - P13–P15 are deliberately phrased to *resemble* standard critical phenomena, but FIT does not (yet) provide a clean derivation.
   - If you can exhibit systems with well-understood critical behavior that **refuse to be sensibly mapped** into the F–I–T–C primitive set, that would illuminate missing structure.

5. **Late-time AI / learning dynamics**
   - T-theory (late-time, high-constraint dynamics) is most speculative.
   - If you work with realistic learning systems (e.g. large-scale SGD, RL, evolutionary algorithms) and can show that the proposed nirvana / force-variance picture is systematically misleading, that would be a strong reason to revise or even drop T-theory.

In short: **this is not trying to be unassailable**.  
It is trying to be **structured enough that you know exactly where to hit it.**

---

## 6. How to navigate this repository (for researchers)

If you are coming from a complex systems / dynamical systems background, a reasonable reading path is:

1. `docs/FIT_v2.3_revised.md`  
   – Main text: primitives, estimator layer, principles, 18 propositions, T-theory, Tier‑1 results.

2. `docs/T_theory.md` (if present)  
   – Sub-framework focusing on late-time, high-constraint dynamics and “nirvana” states.

3. `registry/propositions.yaml`  
   – Machine-readable proposition registry; current validation status across systems and estimator tuples.

4. `experiments/`  
   - `experiments/langton_*` – Langton’s Ant (open vs periodic boundary) as a case study in “boundary as constraint”.  
   - `experiments/gol_*` – Conway’s Game of Life; information-theoretic success + constraint-estimator challenges.

Code quality here is functional rather than polished; the goal is **conceptual validation**, not software engineering excellence.

---

## 7. How this relates (and does not relate) to what you may already know

- **To statistical mechanics / RG**  
  FIT borrows intuitions from phase transitions and scaling, but does not (yet) have a renormalization treatment. You can think of many C-class propositions as “stat-mech-flavored conjectures” expressed in FIT primitives.

- **To dynamical systems theory**  
  Attractors, basins, multistability, and timescale separation reappear as nirvana states, constraint landscapes, and P18. FIT does not replace standard dynamical systems tools; it tries to give a language for comparing “attractor-like” behavior across very different state spaces.

- **To AI / learning theory**  
  Grokking, late-stage training dynamics, and lock-in behavior are viewed as **instances** of more general phenomena. The framework is explicitly **not** an optimization or generalization theory in the classical sense.

- **To AI safety / governance**  
  T-theory is motivated by late-time, high-constraint regimes where **capability has already emerged** and the main question becomes “what does the system do next, and can it safely stop?”. This is downstream from your usual complex systems concerns, not a precondition to engaging with FIT.

---

## 8. If you only skim one thing…

If you only have 5–10 minutes, the most honest “entry point” is:

- the **list of propositions (P1–P18)** and their current statuses in the registry,  
- plus the short discussion of **Langton’s Ant with open vs periodic boundary conditions** as a demonstration that **boundary choice = constraint structure**, with qualitative changes in reachable dynamics.

If after that you think:

> “This is either obviously wrong or obviously missing X”  

you are exactly the kind of reader this framework was written for.

Critiques, counterexamples, and alternative formalisms are very welcome.
