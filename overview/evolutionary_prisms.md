# Evolutionary Prisms: Natural Phenomena Through the FIT Lens

Status: edge-expansion (v2.x compatible)  
Purpose: map major evolutionary phenomena into FIT/EST form  
Scope: conceptual + estimator-scoped hypotheses  
Does not introduce new primitives or new propositions.

Navigation:
- Core Card: ../core/fit_core_card.md
- Phase Algebra + PT-MSS: ../core/phase_algebra.md
- Φ₃ Stability: ../core/phi3_stability.md
- EST: ../v2.4.md
- Misuse Guard: ../core/FIT_Misuse_Guard_and_FAQ.md


---

# 0. Usage Discipline

This document treats natural phenomena as **hypothesis generators**, not validations.

Each section provides:

1. FIT mapping (F / I / C / Phase)
2. Minimal hypothesis H#
3. Task type (ordinal / metric / topological)
4. Candidate estimator family
5. Explicit falsification route

If any hypothesis fails under preregistered estimator scope and coherence gates, it must be labeled:

* CHALLENGED
* ESTIMATOR_UNSTABLE
* SCOPE_LIMITED

See `how_to_falsify_fit.md`.

---

# 1. Punctuated Equilibrium (Long Plateaus + Sudden Shifts)

## Phenomenon

Long morphological stasis punctuated by short bursts of change.

---

## FIT Mapping

* Stasis ≠ automatically Φ₃
* Must pass Φ₃ Stability Criteria (SC-1 / SC-2 / SC-3)
* Transition must satisfy PT-MSS

---

## Hypothesis H-PE1

Within a declared boundary and estimator tuple:

> Long plateau intervals correspond to SC-1 or SC-2 stable regimes.
> Transition windows satisfy PT-MSS (Force redistribution + Information re-encoding + Constraint reorganization).

---

## Task Type

Topological (event structure consistency)

---

## Candidate Estimators

* Morphological change rate proxy: |dS/dt|
* Constraint proxy: accessible morphological state space contraction
* Information proxy: description length of phenotype encoding
* Force proxy: environmental gradient magnitude

---

## Falsification Route

If:

* Plateau periods fail SC-1 under declared estimator family
* OR transition windows do not satisfy all three PT-MSS components
* OR transition detection is not scale-consistent under admissible coarse-graining

→ H-PE1 is CHALLENGED.

---

# 2. Convergent Evolution (Universality Under Constraint)

## Phenomenon

Different lineages converge to similar functional structures.

---

## FIT Mapping

* Similar external constraint structures
* Different micro-level Force realizations
* Convergence in Information structure

---

## Hypothesis H-CE1

Systems evolving under estimator-equivalent constraint structures
will converge (in Information space) toward structurally similar attractors.

---

## Task Type

Metric + Topological

---

## Candidate Estimators

* Constraint signature embedding
* Information structure embedding (e.g., feature topology)
* Convergence distance in constraint-space trajectory

---

## Falsification Route

If:

* Systems with estimator-equivalent constraint signatures do not converge
* OR convergence is estimator-sensitive
* OR coherence gate fails

→ H-CE1 is CHALLENGED.

---

# 3. Red Queen Dynamics (Coupled Evolution)

## Phenomenon

Systems co-evolve, maintaining relative adaptation without net stabilization.

---

## FIT Mapping

* System boundary must include both agents
* Constraint may not be monotone globally
* Long-term regime may remain Φ₂ or shallow Φ₃

---

## Hypothesis H-RQ1

In coupled systems, Constraint proxies may oscillate or plateau without violating phase-conditional monotonicity (P2a) within sub-phases.

---

## Task Type

Ordinal (trend within phase)

---

## Candidate Estimators

* Mutual information between systems
* Phase lag of constraint trajectories
* Cross-correlation of Force proxies

---

## Falsification Route

If:

* Constraint decreases systematically within declared sub-phase
* AND coherence gates pass
  → H-RQ1 challenged.

---

# 4. Developmental Constraint (Historical Lock-in)

## Phenomenon

Early structural decisions limit later possibilities.

---

## FIT Mapping

I(t0) → C(t1) → restricts future F directions.

---

## Hypothesis H-DC1

KL divergence between final-state distributions under distinct initial I(t0)
remains non-trivial over declared horizon.

---

## Task Type

Metric

---

## Candidate Estimators

* KL divergence of final state distributions
* Wasserstein distance
* Phase classification stability across initial seeds

---

## Falsification Route

If initial differences vanish under long horizon and coherence passes,
→ H-DC1 challenged.

---

# 5. Neutral Evolution (Drift-Dominated Regime)

## Phenomenon

Random variation accumulates without selection advantage.

---

## FIT Mapping

Drift-diffusion regime:

dS = αF dt + Σ dW

Drift small; diffusion dominates.

---

## Hypothesis H-NE1

Under low-drift regimes,
Constraint remains approximately stable,
while Information diversity reservoir increases.

---

## Task Type

Ordinal + Metric

---

## Candidate Estimators

* Variance of state distribution
* Accessible neutral space volume proxy
* Drift-to-diffusion ratio

---

## Falsification Route

If diversity does not accumulate under low-drift regime,
→ H-NE1 challenged.

---

# 6. Niche Construction (Boundary Modification)

## Phenomenon

Agents modify environment, altering future constraints.

---

## FIT Mapping

I_agent → F_environment → ΔC_external → feedback into I_agent.

---

## Hypothesis H-NC1

Agent-induced environmental constraint change
predictably alters subsequent agent information trajectory.

---

## Task Type

Topological + Metric

---

## Candidate Estimators

* ΔC_external proxy
* ΔI_agent
* Coupling efficiency η = ΔC_external / ΔI_agent

---

## Falsification Route

If environmental modification does not feed back into agent information trajectory,
→ H-NC1 challenged.

---

# 7. Meta-Insight

These phenomena do not validate FIT.

They provide structured arenas for testing:

* Phase classification robustness
* Constraint geometry behavior
* Information-constraint coupling
* Coarse-graining consistency
* Monitorability under evolutionary stress

Any failure must be recorded as such.


