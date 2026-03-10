
# Prompt Stability Protocol (PSP)

## A Structural Theory of Convergent Interaction

---

## 1. Motivation

Language model interaction is not static generation.
It is a **dynamical process**.

Each turn transforms a state:

```
S_{t+1} = F(S_t, P_t)
```

Where:

* `S_t` is the conversational state
* `P_t` is the prompt perturbation
* `F` is the model’s response operator

Small perturbations in prompts can amplify across iterations.
Definitions drift.
Structures mutate.
Conceptual frames oscillate.

In practice, iterative prompting often behaves as a **locally expansive system**.

PSP is introduced as a structural mechanism to:

> Transform interaction from an open-loop expansion process into a controlled, convergence-oriented dynamical system.

---

## 2. Interaction as a Dynamical System

Let:

* `d_t` = distance between two nearby prompt trajectories
* `r_t = d_{t+1} / d_t` = amplification ratio
* `μ̂_W` = geometric mean of `r_t` over window `W`

Interpretation:

* `μ̂_W > 1` → expansive regime
* `μ̂_W ≈ 1` → marginal regime
* `μ̂_W < 1 − δ` → contractive regime

Convergence requires persistent contraction.

Without structural constraints, large language model interaction has no guarantee of contraction.

---

## 3. Structural Sources of Instability

Instability in iterative prompting typically arises from:

### 3.1 Semantic Drift

Definitions mutate subtly across turns.

### 3.2 Schema Drift

Output structure changes (headings, sections, format).

### 3.3 Scope Expansion

Unbounded conceptual growth without pruning.

### 3.4 Amplified Ambiguity

Minor wording changes produce major trajectory divergence.

These are not model “failures”.
They are properties of high-dimensional response operators.

---

## 4. Control Through Explicit Mode Separation

PSP introduces explicit phase separation:

| Mode    | Function                     | Stability Role            |
| ------- | ---------------------------- | ------------------------- |
| EXPLORE | Controlled expansion         | Allows bounded divergence |
| EXPLOIT | Structural stabilization     | Reduces amplification     |
| AUDIT   | Contraction + falsifiability | Enforces convergence      |
| RESET   | State reinitialization       | Breaks unstable loops     |

This separation prevents uncontrolled mixing of expansion and stabilization behaviors.

---

## 5. The Structural Header as Control Law

PSP requires each prompt to declare:

* Current mode
* Pinned invariants
* Allowed transformations
* Forbidden transformations
* Output projection constraints

This declaration is not stylistic.

It defines the **control law** governing the next state transition.

Formally, it constrains:

```
F : (S_t, P_t) → S_{t+1}
```

By reducing the effective state space reachable from `S_t`.

---

## 6. Projection Operators and Schema Locking

Let `G_D` be an output projection operator defined by a schema.

Examples:

* Required section markers
* Fixed heading structure
* Structured JSON schema

When `G_D` is stable:

* Structural degrees of freedom shrink
* Schema drift is minimized
* Amplification channels are reduced

Schema mutation during stabilization phases is treated as instability.

---

## 7. Convergence Before Finalization

PSP introduces a critical principle:

> Finalization must only occur in a contractive regime.

If `μ̂_W ≥ 1`, the system is still expanding or marginal.

Producing final artifacts under expansion yields:

* Unstable definitions
* Internal contradictions
* Non-reproducible structure

PSP delays finalization until contraction is observed.

---

## 8. RESET as Structural Hygiene

RESET is a deliberate collapse of accumulated drift.

It:

* Removes unstable context
* Preserves only goal + invariants
* Reinitializes in a stabilization mode

RESET prevents long-range amplification chains.

It is a structural reset, not a semantic retreat.

---

## 9. Theoretical Positioning

PSP does not assume:

* Model alignment
* Semantic correctness
* Truthfulness guarantees

It assumes only:

* Interaction is dynamical
* Stability is not automatic
* Convergence requires constraint

PSP operates at the interaction layer.

It is orthogonal to:

* Reinforcement learning
* Fine-tuning
* Alignment techniques
* Model architecture

---

## 10. PSP as a Stability Layer

PSP can be understood as:

* A low-cost stability wrapper
* A convergence enforcement protocol
* A projection-based control layer

It introduces no new model weights.
It modifies only the interaction topology.

---

## 11. Implications

Under PSP:

* Interaction trajectories become more reproducible
* Schema signatures stabilize
* Amplification decreases
* Auditability increases

Without PSP, convergence is accidental.

With PSP, convergence is engineered.

---

## 12. Summary

Large language models operate in high-dimensional response spaces.

Iterative prompting is a dynamical process.
Dynamical processes can expand or contract.

PSP introduces explicit structural constraints and phase separation to:

> Turn interaction into a controlled, convergence-seeking system.

It is not a prompt template.

It is a structural theory of stable interaction.


