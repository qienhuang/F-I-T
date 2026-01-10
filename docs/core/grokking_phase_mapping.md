# Grokking as FIT Phase Transition

Status: **core-adjacent application**
Purpose: map the ML "grokking" phenomenon to FIT phase structure
Audience: ML researchers, AI safety practitioners, FIT readers

Navigation: [`core index`](./README.md) | [`Two-Page Card`](./fit_two_page_card.md) | [`Φ₃ Stability`](./phi3_stability.md) | [`Post-Φ₃ Bifurcation`](./FIT_Core_Extension_Post_Phi3.md)

Notation: phases are written as `Φ₁/Φ₂/Φ₃` (ASCII: `Phi1/Phi2/Phi3` in filenames/code).

---

## What is grokking?

Grokking is an empirically observed phenomenon in neural network training:

1. The model quickly memorizes training data (near-zero training loss)
2. Test accuracy remains at chance for a prolonged period
3. After many more training steps, test accuracy suddenly improves to near-perfect

This delay between memorization and generalization is the "grokking" phenomenon.

---

## FIT Variable Mapping

| FIT Variable | Grokking Interpretation |
|--------------|------------------------|
| **Force (F)** | Gradient descent updates; optimization pressure |
| **Information (I)** | Learned representations; weight configurations that persist and affect future predictions |
| **Time (T)** | Training steps (epochs); the rhythm of parameter updates |
| **Constraint (C)** | Accumulated structure that restricts the effective hypothesis space |

---

## Phase Mapping

### Φ₁ — Accumulation (Early Training)

**Characteristics:**
- Random initialization; no stable structure
- Force (gradient) is large and noisy
- Information does not persist (weights change rapidly)
- No meaningful constraints yet

**Observable signature:**
- Both training and test loss are high
- Representations are random/unstructured

**Duration:** Brief (typically < 100 steps)

---

### Φ₂ — Crystallization (Memorization)

**Characteristics:**
- Local structures stabilize (memorization of training examples)
- Force is absorbed locally but not globally
- Information is example-specific, not generalizable
- Constraints are local (each example has its own "solution")

**Observable signature:**
- Training loss → 0
- Test accuracy remains at chance
- Representations are high-dimensional, non-transferable

**Duration:** Can be very long (10³–10⁵ steps depending on task/hyperparameters)

**Why Φ₂ persists:**
Memorization is a **stable regime**. The model has found a local attractor that satisfies the training objective. There is no gradient pressure to change—the loss is already zero.

The transition to Φ₃ requires a different mechanism: **weight decay** (or similar regularization) that slowly erodes the high-complexity memorization solution, creating pressure toward simpler, generalizable structure.

---

### Φ₂ → Φ₃ Transition (Grokking Event)

**PT-MSS (Phase Transition Minimal Signal Set) check:**

| Signal Class | Grokking Manifestation |
|--------------|------------------------|
| Force redistribution | Gradient flow shifts from fitting individual examples to reinforcing shared structure |
| Information re-encoding | Representations shift from example-specific to feature-based (e.g., Fourier modes for modular arithmetic) |
| Constraint reorganization | Effective hypothesis class collapses from high-dimensional memorization to low-dimensional generalization |

All three signals co-occur within a narrow training window → **phase transition confirmed**.

**Why it appears sudden:**
The transition is not sudden in internal dynamics—structural alignment accumulates gradually. But the observable metric (test accuracy) only changes once the alignment crosses a threshold. Metrics lag structure.

---

### Φ₃ — Coordination (Generalization)

**Characteristics:**
- Force is globally absorbed; the model has a coherent solution
- Information is reusable across examples (generalizable representations)
- Constraints are strong and stable (low effective dimensionality)

**Observable signature:**
- Training loss ≈ 0
- Test accuracy ≈ 100%
- Representations show structured patterns (e.g., Fourier basis for modular addition)

**Stability criteria (from [`phi3_stability.md`](./phi3_stability.md)):**

| Criterion | Grokking Interpretation |
|-----------|------------------------|
| SC-1 (persistence) | Test accuracy remains high for extended training |
| SC-2 (perturbation resilience) | Accuracy recovers after small weight perturbations |
| SC-3 (transfer stability) | Learned features transfer to related tasks |

---

## Post-Φ₃: What Happens After Grokking?

Per the [Post-Φ₃ Bifurcation](./FIT_Core_Extension_Post_Phi3.md), two paths exist:

### Path A — Overfitting to generalization

Paradoxically, continued training after grokking can degrade performance:

- **Constraint hardening**: The model becomes too rigid, losing ability to adapt to distribution shift
- **Force homogenization**: Continued gradient descent reinforces existing structure without exploring alternatives
- **Information ossification**: Representations become locked to the specific task format

**Outcome:** Brittle generalization; fails under slight task variation.

### Path B — Meta-learning / Transfer

If the training regime deliberately introduces variation:

- **(B1) Force uplift**: New tasks or domains introduce higher-level optimization pressure
- **(B2) Information re-stratification**: The model learns to learn, not just to solve
- **(B3) Constraint enveloping**: Task-specific solutions become sub-modules of a more general structure

**Outcome:** Robust transfer; adaptability to new tasks.

---

## Implications for AI Safety

### 1. Grokking is structurally predictable

FIT suggests that grokking is not mysterious—it is a phase transition with identifiable precursors. The delay is not inefficiency but **structural necessity**.

### 2. Post-grokking is the real risk zone

A model that has "grokked" is in Φ₃. The question is: what happens next?

- If training stops: the model is stable but frozen
- If training continues without diversity: Path A (brittleness)
- If training continues with deliberate exploration: Path B (adaptability)

### 3. Emptiness windows as safety mechanism

The "Controlled Nirvana" paper proposes using the post-grokking regime (Φ₃) to insert safety constraints that become structurally locked. This works because:

- Φ₃ constraints are hard to reverse (MCC-6)
- Inserting safety structure during Φ₃ makes it part of the stable attractor
- Subsequent training cannot easily remove it without re-triggering phase transition

---

## Scaling Law Connection

The Li² experiment demonstrates that grokking time scales as:

> n_grok ~ M · log(M)

where M is the modulus (task complexity) and n_grok is the number of training samples needed.

In FIT terms:
- **M** → size of the state space (Constraint domain)
- **log(M)** → effective information content of the generalizable structure
- **n_grok ~ M · log(M)** → the phase transition requires enough Force exposure to fill the Information structure

This is consistent with FIT's view that phase transitions require **threshold accumulation**, not continuous improvement.

---

## Summary Table

| Training Stage | FIT Phase | Observable | Internal Structure |
|----------------|-----------|------------|-------------------|
| Early training | Φ₁ | High loss | No stable structure |
| Memorization | Φ₂ | Train=0, Test=random | Local, high-dimensional |
| Grokking event | Φ₂→Φ₃ | Test accuracy jumps | PT-MSS satisfied |
| Generalization | Φ₃ | Train=0, Test≈100% | Global, low-dimensional |
| Post-grokking | Φ₃→? | Depends on training regime | Path A or Path B |

---

## References

- Power et al. (2022). "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets"
- Tian et al. (2025). "Provable Scaling Laws of Feature Emergence from Learning Dynamics of Grokking" ([repo](https://github.com/yuandong-tian/understanding))
- FIT v2.4 spec: [`docs/v2.4.md`](../v2.4.md)
- Controlled Nirvana paper: [`papers/controlled_nirvana.md`](../../papers/controlled_nirvana.md)
