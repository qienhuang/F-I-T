# Representation Sweeps v0.1.1
*Minimal, automatable robustness tests so `REPRESENTATION_UNSTABLE` becomes measurable.*

**Status**: repo-ready patch (v0.1.1)  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0  

---

## 0. Purpose

A discovery system can “succeed” only because of a representation quirk.
To prevent this, we preregister a sweep family:

- generate equivalent or near-equivalent representations,
- rerun the candidate pipeline,
- measure label flip rate.

---

## 1. Minimal sweep set (v0.1.1)

### S1 — Alpha-renaming (variable renaming)
- rename bound variables / identifiers
- should not change outcomes

### S2 — Definitional unfolding / folding
- expand a definition once
- refold where possible
- checks for brittleness to definitional choices

### S3 — Harmless reparameterization
- apply known equivalences (e.g., change basis, reorder constructors, normalize signs)
- domain-specific but should preserve meaning

### S4 — Budget micro-sweeps (for discovery reliability)
- steps: 0.8× / 1.0× / 1.2×
- time: 0.8× / 1.0× / 1.2×
This detects “knife-edge success” that disappears with tiny budget changes.

---

## 2. Flip-rate definition

Let the preregistered primary label be  L .  
For each sweep instance  j  we obtain label  L_j .

Define flip rate:



$$
\mathrm{flip\_rate} = \frac{1}{n} \sum_{j=1}^n \mathbf{1}[L_j \ne L]
$$



A candidate is considered robust if:



$$
\mathrm{flip\_rate} \le q_{\max}
$$



where  q_max  is preregistered.

---

## 3. Evidence required per sweep

Record:
- sweep id
- transformation type (S1–S4)
- verifier verdict id and hashes (if applicable)
- budgets used
- resulting label

---

## 4. Toy-world analog (bridging from world-evolution to math)

If your discovery environment is a toy evolving world rather than Lean/Coq:

- S1: rename features / reorder feature stack (shouldn’t matter)
- S2: unfold/fold = swap equivalent feature definitions
- S3: reparameterize = equivalent normalization of signals
- S4: micro-sweeps = window length  W  and smoothing  \alpha  sweeps

The point is not the specific transformation, but the existence of a preregistered equivalence family.

---

## 5. Implementation interface (suggested)

A sweep generator returns a list of transformed candidates:

```yaml
sweeps:
  - sweep_id: "S1_rename_01"
    kind: "alpha_rename"
    params: {}
  - sweep_id: "S2_unfold_01"
    kind: "def_unfold"
    params: {depth: 1}
```

The runner records `flip_rate` and attaches it to the results schema.

