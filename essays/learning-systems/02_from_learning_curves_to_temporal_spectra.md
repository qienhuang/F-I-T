
---

# Chapter 2

## From Learning Curves to Temporal Spectra

### Why Grokking Is Invisible to Time-Domain Metrics

---

### 2.1 The Seduction of Learning Curves

Learning curves are the dominant observational tool in learning systems.

They compress system behavior into a familiar narrative:

* loss decreases
* accuracy increases
* generalization improves

This narrative implies continuity.
It suggests that learning progresses smoothly, and that sufficient time or data will eventually yield understanding.

t-Theory identifies this as a **representational illusion**.

Learning curves are not wrong.
They are **structurally blind**.

---

### 2.2 Time-Domain Observation Erases Structure

Learning curves are time-domain projections.

They collapse all internal dynamics into a single scalar per step.
In doing so, they erase:

* scale separation
* recurrence structure
* phase relations
* bandwidth limits

A learning curve answers only one question:

> *How does an aggregate metric evolve over time?*

It cannot answer:

* *Which temporal structures dominate?*
* *Whether low-frequency coherence exists?*
* *If phase alignment is approaching or drifting away?*

---

### 2.3 Why Grokking Appears as a “Cliff”

In time-domain observation, grokking appears as:

* prolonged flatness
* followed by abrupt improvement

This is misinterpreted as:

* sudden insight
* delayed optimization
* lucky convergence

In t-Theory, the explanation is simpler:

> **A time-domain scalar cannot resolve a frequency-domain phase transition.**

The “cliff” is not a jump in capability.
It is the moment when **previously invisible low-frequency structure becomes dominant enough to affect the scalar metric**.

---

### 2.4 Learning Curves Confound Regimes

Learning curves conflate fundamentally different regimes:

* high-frequency memorization
* low-frequency generalization
* transitional instability

All three can produce similar metric values.

Thus, identical curves may correspond to:

* systems approaching grokking
* systems permanently trapped in memorization
* systems undergoing irreversible drift

The curve cannot tell the difference.

---

### 2.5 Temporal Spectra as Structural Signatures

Temporal spectra decompose learning dynamics into **coexisting scales**.

Instead of asking:

* *How well is the system performing now?*

The spectral view asks:

* *At which temporal scales does coherent structure exist?*
* *Where is energy accumulating?*
* *Which frequencies dominate internal representation?*

This reframes learning as **structural composition**, not progress.

---

### 2.6 High-Frequency Dominance and the Illusion of Learning

In early and memorization-dominated regimes:

* energy concentrates at high frequencies
* updates react to local variation
* feedback closes rapidly but shallowly

Learning curves improve quickly here, creating the illusion of advancement.

Spectrally, however, the system remains **structurally shallow**.

No amount of high-frequency improvement accumulates into low-frequency coherence.

---

### 2.7 Low-Frequency Emergence Precedes Metric Change

Before grokking becomes visible:

* low-frequency components begin to stabilize
* recurrence extends across longer horizons
* phase relations tighten across internal subsystems

These changes **do not immediately affect accuracy or loss**.

Thus, learning curves remain flat while structure reorganizes underneath.

This explains why grokking is often dismissed as “delayed” or “mysterious”.

---

### 2.8 Spectral Crossing as the Grokking Condition

t-Theory identifies a necessary condition for grokking:

> **Low-frequency energy must exceed a dominance threshold over high-frequency modes.**

This is not gradual dominance.

Once the threshold is crossed:

* phase locking occurs
* coherence propagates
* generalization stabilizes

The observable cliff corresponds to this **spectral crossing**, not to sudden learning.

---

### 2.9 Why More Training Time Often Fails

Time-domain intuition suggests:

* “train longer”
* “wait it out”

Spectrally, this fails when:

* high-frequency modes continue absorbing updates
* bandwidth remains saturated
* low-frequency modes never stabilize

In such cases, time reinforces the wrong structure.

Learning curves remain deceptively optimistic.

---

### 2.10 Early Detection Without Prediction

Temporal spectra do not predict outcomes.

They constrain them.

From spectral structure alone, one can determine:

* whether grokking is possible
* whether it is approaching
* whether it has become infeasible

This determination occurs **before** any metric inflection.

Thus, spectral analysis shifts learning assessment from hindsight to **structural diagnosis**.

---

### 2.11 Why Curves Persist Despite Their Limits

Learning curves persist because:

* they are easy to compute
* they align with optimization narratives
* they reward acceleration

t-Theory does not call for their removal.

It calls for recognizing them as **late-stage indicators**, not structural probes.

---

### 2.12 Summary

This chapter establishes a decisive claim:

> **Grokking cannot be observed, explained, or anticipated in the time domain.
> It is a frequency-domain phenomenon projected onto a scalar metric.**

Learning curves show *when* grokking becomes visible.
Temporal spectra explain *why* it becomes possible.

The next chapter will complete this module’s core by formalizing **failure taxonomies**:
why many learning systems **never** transition spectrally—and why no amount of optimization can change that.

---
