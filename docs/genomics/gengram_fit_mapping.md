# Gengram × FIT: Mapping Explicit Motif Memory to Constraint-Centric Genomics

**Status**: Research note (Tier-3 mapping)  
**Scope**: Genomic foundation models with explicit motif memory  
**Primary reference**: *Beyond Conditional Computation: Retrieval‑Augmented Genomic Foundation Models with Gengram* (2026‑01‑29)  
**Code**: `https://github.com/zhejianglab/Genos`  
**FIT compatibility**: v2.4.x (no core changes)  

## 1. What becomes explicit (and what does not)

Gengram introduces an explicit **motif memory** (k‑mer lookup, typically k=1..6) with gated injection into a transformer backbone over a local window `W`.

For FIT/EST, it is crucial to distinguish **information substrates** from **constraints**:

- The **motif memory** is an *information carrier* (I): a reusable, addressable store of local sequence regularities.
- **Constraints (C)** arise from *admissibility*: the architectural restrictions induced by a finite k‑mer set, a bounded window `W`, aggregation/deduplication rules, and the requirement that certain interactions be mediated by the memory + gate.

In short: *what is stored* is information; *how it may be used* induces constraint.

## 2. Cross‑level constraint anchors (candidate: W ≈ 21 bp)

Gengram reports that performance peaks near `W ≈ 21 bp` on several motif‑dominated tasks. A natural hypothesis is geometric: ~10.5 bp per DNA helical turn; ~21 bp places sites on similar helical faces.

In FIT terms, this is interesting not as a “cool fact”, but as a **candidate cross‑level anchor**:

- Physical level: DNA helix geometry
- Information level: effective motif interaction range
- Computation level: an optimal window hyperparameter

This is an **edge hypothesis** (Tier‑3): it should be treated as falsifiable and boundary‑conditional, with explicit alternatives (e.g., TF footprint statistics, dataset/task bias, or motif density effects).

## 3. Constraint front‑loading (efficiency mechanism; scope‑conditional)

Gengram is a practical example of **constraint front‑loading**:

- Structural priors (motif grammar) are injected early,
- reducing depth/data required to reach prediction‑ready representations.

In FIT terms, this suggests higher **I/C efficiency** on motif‑dominated tasks, but it is expected to weaken or reverse when long‑range interactions dominate.

## 4. Layered constraint roles (constraint hierarchy interface)

Empirical probes (e.g., layer‑wise prediction readiness, reverse‑complement symmetry checks) support differentiated roles:

- Shallow layers: local boundary encoding (structural constraints)
- Mid layers: task‑ and direction‑sensitive constraints
- Deep layers: integrated, symmetry‑respecting constraints

This aligns with a **constraint hierarchy** view: constraints stabilize and propagate across layers with non‑uniform latencies.

## 5. Dynamic constraint fields via gating

The gating mechanism supports a **dynamic constraint field** view:

`C(s, t) = g(s, t) · C_base`

where `g(s, t)` is context‑ and position‑dependent.

Under EST discipline, gate signals require coherence diagnostics (and controls) to distinguish structure from attention‑like noise.

## 6. What this enables for FIT genomics (Tier‑3)

Gengram provides a concrete platform to:

- Audit explicit vs implicit structure learning,
- Measure I/C efficiency across window scales and tasks,
- Test constraint hierarchy and propagation hypotheses,
- Ground abstract FIT claims in genomic sequence models.

## 7. Risks and alternative explanations (must be preregistered)

- `W ≈ 21 bp` may reflect TF footprint statistics rather than helix geometry.
- Memory tables may encode frequency priors rather than constraints.
- Gate activations may track saliency, not constraint activation.

Tier‑3 claims should therefore be coherence‑gated and benchmarked against strict controls (shuffle memory indices, gate‑off ablations, matched‑compute baselines).

## 8. Summary

Gengram’s distinctive value for FIT is not only performance gains, but **structure externalization**: it makes certain information carriers explicit and certain constraints auditable.

