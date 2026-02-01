# From Expression States to Constraint Dynamics:
## A FIT Framework for Fate Commitment in Single-Cell RNA Sequencing

**Author**: Qien Huang  
**Affiliation**: Independent Researcher  
**Framework**: FIT (Force-Information-Time) v2.5  
**License**: CC BY 4.0  
**Keywords**: single-cell RNA-seq, fate commitment, irreversibility, constraint dynamics, phase transition  
**Target venues**: arXiv (q-bio.QM / cs.LG), bioRxiv  
**Version**: 1.2 (2026-02-01)  

---

## Abstract

Single-cell RNA sequencing enables high-resolution trajectory reconstruction, yet prevailing interpretations remain state-centric: differential expression is routinely treated as evidence of fate commitment. This conflates transient expression variation with irreversible structural change.

We propose a constraint-centric reframing using the Force-Information-Time (FIT) framework. Fate commitment corresponds to contraction and reconfiguration of the **reachable expression space**, not expression levels alone. We introduce a Tier-2, estimator-gated protocol comprising: (i) formal boundary and estimator family declaration; (ii) coherence-gated constraint measurement; (iii) phase-conditional interpretation; and (iv) multi-signal registration of commitment points.

The protocol is designed to produce auditable artifacts (coherence reports, fail-window indices, and registered commitment points) rather than post hoc marker narratives. Coherence-gated failures are treated as estimator-family mismatch or scope limitation, not as a reason to force interpretation. This reframing shifts single-cell biology from "what changes in expression" to "what becomes unreachable in expression space."

---

## 1. Introduction

Single-cell trajectory inference has transformed developmental biology, yet a persistent interpretability gap remains. Expression changes are frequently equated with fate decisions, despite extensive evidence that transcriptional states can fluctuate reversibly under noise, stress, or transient signaling.

This paper proposes an alternative framing: **fate commitment is a constraint phenomenon**. Drawing on the FIT framework, we argue that irreversible commitment occurs when the space of reachable transcriptional configurations contracts and reorganizes, forming stable attractors (Figure 1).

> Expression states describe where the system is.
> Constraints determine where it can still go.

The key distinction is between **state change** (movement within a fixed dynamical landscape) and **structural change** (reconfiguration of the landscape itself). Only the latter constitutes genuine commitment.

---

## 2. Conceptual Framework

### 2.1 FIT Primitives in the scRNA-seq Context

| Primitive | Definition | scRNA-seq Operationalization |
|-----------|------------|------------------------------|
| **State (S_t)** | System configuration | Distribution of cells in latent expression space |
| **Force (F)** | Drivers of change | Developmental programs, signaling, selection |
| **Constraint (C)** | Restrictions on reachable configurations | Boundaries of accessible expression space |
| **Useful information (I_useful)** | Predictive information about future fate | Predictive gain for fate/label from current state |
| **Time (T)** | Ordering axis | Developmental time or pseudotime |

### 2.2 Phases of Development

We interpret development as transitions between constraint regimes. In **Phi1 (exploration)** the reachable expression space remains broad, and perturbations tend to be transient. In **Phi2 (constraint accumulation)** the reachable set contracts and may reorganize, as the system approaches a bifurcation. In **Phi3 (stable attractor)** commitment is robust: basin boundaries are established and escape becomes rare under comparable perturbations. In this framing, commitment corresponds to a **Phi2 -> Phi3** transition, not merely marker activation.

---

## 3. Measurement Strategy

### 3.1 Boundary and Scope

All claims are conditional on declared boundaries: dataset identity and preprocessing (filtering, normalization, HVG selection), batch handling strategy, latent space choice (PCA, diffusion map, VAE) and dimensionality, time axis definition (developmental time or pseudotime method), and the windowing scheme with minimum sample requirements.

**Boundary mis-specification is a first-class failure mode**, not a technical detail.

### 3.2 Tier-2 Protocol Box

This protocol is "verifier-first": interpretation is gated by preregistered coherence checks.

```
Tier-2 protocol (EST-gated; repo-runnable)

1) Declare boundary:
   - dataset + preprocessing
   - label key (for mixing / composition proxies)
   - time axis (explicit time/stage if present; otherwise pseudotime)
   - windowing scheme and minimum sample requirements

2) Declare an estimator family:
   - choose (C1, C2) constraint proxies
   - preregister expected_sign and a coherence threshold

3) Run deterministic pipeline:
   - compute per-window estimators
   - compute coherence across windows
   - gate interpretation based on the preregistered rule

4) Emit auditable artifacts:
   - PREREG.locked.yaml
   - metrics_log.parquet (per-window estimator values)
   - coherence_report.json (gate input + verdict)
   - fail_windows.md
   - tradeoff_onepage.png/pdf

Failure semantics (non-negotiable):
   - OK_PER_WINDOW: gate passes under this boundary
   - ESTIMATOR_UNSTABLE: gate fails (no regime interpretation)
   - INCONCLUSIVE: too few valid windows / samples

```

### 3.3 Constraint Estimator Families


Multiple independent proxies are required for coherence validation.

In the repo-runnable Tier-2 runs referenced in this paper, constraint proxies are computed per window and then
coherence is evaluated *across windows* (a conservative gate).

**Effective dimension (spectral concentration)**

$$
d_{\text{eff}}(t) = \frac{(\sum_i \lambda_i)^2}{\sum_i \lambda_i^2}, \quad \hat{C}_{\text{dim-collapse}}(t) = \frac{1}{d_{\text{eff}}(t)}
$$

**Window composition (label purity)**

$$
\hat{C}_{\text{purity}}(t) = \max_k p_k(t)
$$

**Local mixing (graph-based; kNN edges)**

$$
\hat{C}_{\text{mix}}(t) = 1 - \mathrm{Pr}\left[\mathrm{label}_{src} \neq \mathrm{label}_{dst}\right]
$$



### 3.4 Useful Information

$$
\hat{I}_{\text{useful}}(t) = \text{PredictiveGain}(X_t \to Y_{\text{fate}})
$$

where $Y_{\text{fate}}$ is terminal lineage identity.

---

## 4. Coherence-Gated Interpretation

Constraint estimators must be coherent within declared scopes (Figure 2).

### 4.1 Coherence Types

| Type | Definition | Failure Semantics |
|------|------------|-------------------|
| **Signed** | Expected correlation direction preregistered | Sign mismatch -> ESTIMATOR_UNSTABLE |
| **Local** | Valid within phase, not across phases | Pooled FAIL + window PASS -> SCOPE_LIMITED |
| **Task-typed** | Ordinal vs metric vs topological | Gate type must match task |

### 4.2 Phase-Conditional Interpretation

Pooled coherence failure across phases should be interpreted as **regime heterogeneity**, not estimator inadequacy.

Example: if two constraint proxies `(C1, C2)` are coherent within a phase but fail when pooled across phases, the correct interpretation is not that the estimators are “bad”, but that the constraint structure differs by regime. Claims must then be phase-qualified (or window-qualified), and pooled statements are out-of-scope for that boundary.

---

## 5. Detecting Commitment: Multi-Signal Registration

A commitment point is registered only when multiple signals co-occur within a coherent window:

### 5.1 PT-MSS Criteria (Phase Transition Multi-Signal Signature)

| Signal | Description | Operationalization |
|--------|-------------|-------------------|
| **S3** | Constraint reconfiguration | Abrupt shift in the constraint family (e.g., a jump in `C_dim_collapse` together with tightening of a second proxy such as `C_label_purity`) |
| **S2** | Information re-encoding | Sharp increase in predictive gain |
| **S1** | Stability change | Increased return tendency, reduced directional variance |

### 5.2 Local Efficiency

Within a window W:
$$
\Gamma_W(t) = \frac{\Delta \hat{I}_{\text{useful}}(t; W)}{\Delta \hat{C}(t; W)}
$$

A pronounced Γ peak indicates efficient information encoding per unit constraint accumulation.

---

## 6. Protocol Specification: Mouse Hematopoiesis

This section specifies a Tier-2 protocol for a canonical dataset. **Results are protocol-conditional and should be regenerated with current code.**

### 6.1 Boundary Declaration

| Parameter | Value |
|-----------|-------|
| Dataset | Paul et al., 2015 (mouse hematopoiesis) |
| Cells | Hematopoietic stem and progenitor populations |
| Latent space | PCA (preprocessing-dependent; typical runs use 20–30 components) |
| Time axis | Prefer an explicit stage/day axis when available; otherwise diffusion pseudotime |
| Windows | Preregistered windows over the chosen axis (default implementation uses 17 windows) |
| Min samples | Preregistered per-window minimum cell count (see locked prereg per run) |

### 6.2 Estimator Family Declaration

The Tier-2 implementation used in this paper treats constraint measurement as an **estimator family** rather than a single metric. Constraint proxies are computed per window, then coherence is evaluated across windows under a preregistered rule.

In the current repo implementation, the candidate constraint proxies include:

- `C_dim_collapse`: inverse effective dimension within a window (`1 / d_eff`)
- `C_mixing`: inverse label mixing across kNN edges (`1 - Pr[label_src != label_dst]`)
- `C_label_purity`: max label mass within a window (`max_k p_k`)
- `C_label_entropy_inv`: inverse normalized label entropy (`1 - H(labels)/log K`)

The default expected sign for a “coupled tightening” hypothesis is positive (`expected_sign=+1`), but signed coherence explicitly treats sign mismatch as a first-class failure mode rather than something to be explained away post hoc.

### 6.3 Tier-2 evidence (repo-runnable; Phase A -> Phase B)

All empirical results in this paper are backed by a deterministic, repo-runnable pipeline:

- Experiment: `github/F-I-T/experiments/real_world/scrna_commitment_tier2p11/`
- Each run writes an auditable artifact set under `outputs_runs/<run_id>/...`
- Evidence packs (ZIP) bundle the run artifacts for archiving and citation

Phase A is explicitly exploratory: we compare a small estimator family and select a candidate pair.
Phase B locks the pair and evaluates it on explicit-axis datasets. Here “explicit axis” is interpreted narrowly: it can be an experimental stage/time label (`obs:stage`, `obs:day`, `obs:age(days)`), or a dataset-provided progression coordinate that is not computed by this pipeline (e.g., a precomputed embedding axis). In all cases, claims remain conditional on the declared boundary and axis choice.

Not all “explicit axes” carry the same epistemic weight. For the purpose of interpreting windowed coherence and any downstream commitment narrative, the strength ordering is:

`obs:stage/day` (experimental design variable; strongest) > `obs:age` (real time but often sparse; medium) > `obsm:*` axes (explicit coordinate but weakest semantics; useful mainly for sanity / portability).

| Dataset | Axis | Label key | Estimator pair | rho (across windows) | Verdict | Evidence (ZIP) |
|---|---|---|---|---:|---|---|
| Pancreas endocrinogenesis (day15) | pseudotime | obs:clusters | C_dim_collapse vs C_mixing | -0.154 | ESTIMATOR_UNSTABLE | `outputs_runs/evidence_pancreas_day15.zip` |
| Pancreas endocrinogenesis (day15) | pseudotime | obs:clusters | C_dim_collapse vs C_label_purity | +0.353 | OK_PER_WINDOW | `outputs_runs/evidence_pancreas_day15_purity.zip` |
| Mouse gastrulation (E6.5-E8.5) | obs:stage | obs:celltype | C_dim_collapse vs C_label_purity | +0.581 (p=0.0145) | OK_PER_WINDOW | `outputs_runs/evidence_gastrulation_e75_purity.zip` |
| Moignard15 hematopoiesis (explicit stage surrogate) | obs:exp_order | obs:leiden_fixed | C_dim_collapse vs C_label_purity | -1.000 | ESTIMATOR_UNSTABLE | `outputs_runs/evidence_moignard15_exporder_leidenfixed_purity.zip` |
| Nestorowa16 hematopoiesis (Zenodo .h5ad) | obsm:X_pca:0 | obs:cell_types_broad_cleaned | C_dim_collapse vs C_label_purity | +0.447 (p=0.0719) | OK_PER_WINDOW | `outputs_runs/evidence_nestorowa16_zenodo_purity.zip` |
| Dentate gyrus (age axis) | obs:age(days) | obs:clusters | C_dim_collapse vs C_label_purity | +0.500 (p=0.667) | OK_PER_WINDOW | `outputs_runs/evidence_dentategyrus_age_purity.zip` |

Interpretation discipline: a passing verdict supports interpretation **within the declared boundary**, not as a universal biological claim. Failures (including sign mismatch) are reported as estimator-family mismatch under the boundary, not as “absence of commitment”.


---

## 7. Discussion

### 7.1 Why Expression-Centric Interpretation Fails

Single-cell biology's interpretive practice remains expression-centric: fate commitment is inferred from differential expression, marker activation, or smooth transcriptional trends. This paradigm systematically conflates **state variation** with **structural irreversibility**.

#### 7.1.1 Expression Is a State Variable, Not a Structural Variable

Gene expression describes instantaneous configuration—a **state variable** that can fluctuate rapidly under noise, stress, or transient signaling. Fate commitment, however, is a **structural property**: which expression configurations remain reachable.

A system may traverse a wide range of expression states while remaining confined to the same attractor basin. Expression changes—even large and reproducible ones—do not imply altered controllability or fate.

**Expression-centric analyses routinely mistake within-basin motion for basin reconfiguration.**

#### 7.1.2 Marker Dynamics Cannot Identify Irreversibility

A central question is not whether a gene is upregulated, but whether a cell has crossed a point beyond which reversal is unlikely.

Expression-centric methods lack a principled answer. Marker genes often increase smoothly along pseudotime, but smooth trajectories provide no criterion for **irreversible boundaries**. Statements like "commitment begins when marker X becomes highly expressed" are not operationally testable without structural assumptions.

**Irreversibility is a property of constraint accumulation, not expression magnitude.**

#### 7.1.3 Expression-Centric Analyses Are Blind to Non-Stationarity

Single-cell systems are inherently non-stationary. Expression-centric analyses typically pool cells across broad pseudotime ranges. When correlations weaken or reverse under pooling, the result is attributed to noise or batch effects.

However, pooled failure frequently reflects **regime heterogeneity**, not estimator inadequacy.

Without explicit phase awareness, expression-centric interpretation cannot distinguish true estimator failure, phase-local validity, and structural reconfiguration across regimes.

#### 7.1.4 Differential Expression Does Not Measure Predictive Information

Expression-centric workflows prioritize statistical significance and effect size, but rarely evaluate **predictive power** about future behavior.

Many differentially expressed genes carry little *useful information* about fate outcomes. They may correlate with trajectory position without contributing to fate predictability.

**Expression-centric interpretation conflates descriptive information with useful information.**

#### 7.1.5 Drivers Versus Attractor Passengers

Perhaps the most damaging limitation is the inability to distinguish **driver regulators** from **attractor passengers** (Figure 3).

In a stable attractor, many genes exhibit consistent expression patterns reflecting the basin's internal structure rather than causal control. These genes are reproducible markers but poor intervention targets.

Expression-centric approaches elevate such genes based on state correlation, not constraint relationship. Causal leverage is overestimated, and regulatory models are saturated with passenger effects.

### 7.2 The Constraint-Centric Alternative: A Verifier-First Interpretation Discipline

The practical distinction between expression-centric and constraint-centric analysis is not philosophical; it is **procedural**. Expression-centric workflows typically treat differential expression and smooth pseudotime trends as sufficient for mechanistic interpretation. The constraint-centric workflow proposed here treats interpretation as a **privilege granted by gates**, not a default.

Under this paper's Tier-2 discipline, a commitment claim is admissible only if it can be expressed as an auditable bundle: a boundary declaration (dataset, preprocessing, latent space, time axis, windowing), an estimator family declaration (at least two independent constraint proxies, optionally paired with an information proxy), a coherence report (pass/fail per window plus pooled-versus-windowed diagnosis), explicit failure labels (`ESTIMATOR_UNSTABLE`, `SCOPE_LIMITED`, `INCONCLUSIVE`) attached to scopes, and (when available) a registered boundary via PT-MSS (S1+S2+S3) within a coherence-passing window.

This shifts the default output of single-cell trajectory analysis from "markers along pseudotime" to one of the following **auditable outcomes**:

1. **REGISTERED COMMITMENT**: A Phi2 -> Phi3 boundary is registered (S1+S2+S3 co-occur) within windows that pass coherence gates.
2. **SCOPE_LIMITED COMMITMENT**: Windowed coherence passes but pooled coherence fails, implying regime heterogeneity; any commitment claim must be phase-qualified.
3. **INCONCLUSIVE**: Signals exist but are undefined or underpowered in key windows (e.g., boundary artifacts, insufficient cell counts).
4. **ESTIMATOR_UNSTABLE**: Coherence gates fail; interpretation is forbidden until the estimator family is repaired.

In this view, "constraint-centric" means: **the system is described by what becomes unreachable**, and the paper's primary contribution is to make that description **auditable and falsifiable under explicit scope** rather than narrative.

> **Expression-centric interpretation describes what a cell looks like.**
> **Constraint-centric interpretation explains what a cell can no longer become.**

#### 7.2.1 Externalizing structure as an audit shortcut (a genomics analogy)

The verifier-first discipline is easiest to apply when the system makes its structure explicit. Recent work in genomic foundation models illustrates this point cleanly: rather than asking a transformer to implicitly rediscover motif grammar from scratch, the model can be augmented with an explicit motif memory and a gate that controls when local structure is injected. The scientific virtue of such a design is not merely improved performance; it is that *where the structure lives* becomes an object one can perturb, disable, shuffle, and audit.

This paper’s scRNA-seq setting is different in every biological sense, but the methodological lesson transfers. A preregistered window axis (stage/day when available, age when sparse, pseudotime when necessary) plays a role analogous to an explicit window size: it is a boundary that can be declared, stress-tested, and compared across runs. Likewise, an estimator family that is computed per window and coherence-gated is a way of externalizing interpretive structure: it forces the “commitment narrative” to be earned by auditable artifacts rather than implied by marker smoothness. The analogy should be read as a guide to *how to make claims testable*, not as evidence that a specific hyperparameter in genomics explains commitment in single-cell systems.

### 7.3 Implications for Experimental Design: From Markers to Reversibility Tests

A constraint-centric theory becomes scientifically useful only if it changes what we consider a valid experiment. Expression-centric analysis tends to validate commitment by showing "different expression." In contrast, the operational definition of commitment implied by this paper is: **a change in reversibility**, observable as phase-structured constraint dynamics.

#### 7.3.1 Minimal Perturbation Test for Commitment

A minimal falsifiable design is a 2×2 perturbation matrix around a candidate Phi2 -> Phi3 boundary:

| | Early (pre-boundary) | Late (post-boundary) |
|---|---|---|
| **Weak perturbation** | Expected: transient deviation, full recovery | Expected: minimal deviation |
| **Strong perturbation** | Expected: possible basin escape | Expected: constrained response, no escape |

**Operational prediction**: If a boundary is truly Phi2 -> Phi3, then under comparable perturbation budgets, late interventions should show **reduced basin escape** and stronger return dynamics than early interventions.

This can be evaluated without claiming a specific gene-level mechanism by measuring constraint proxies and return metrics, e.g. (SC-1) structural persistence of constraint proxies within tolerance after the candidate boundary and (SC-2) recovery of constraint proxies after perturbation within a declared time budget.

(If perturbation data are unavailable, this section defines a testable future requirement rather than a completed validation.)

#### 7.3.2 Driver Identification as "Constraint Interface" Localization

In expression-centric practice, "drivers" are often selected by differential expression or association with pseudotime. Under the present framework, driver-like candidates are operationally those whose changes align with **constraint reconfiguration windows** (S3) and improve fate predictability (S2) within coherence-passing scopes.

Practical implication: the candidate set is reduced by requiring co-occurrence of proximity to a registered (or candidate) boundary, alignment with S3 (constraint proxy reorganization), and contribution to S2 (predictive gain).

This is more restrictive than expression correlation alone, and provides a principled filter for intervention targets.

#### 7.3.3 Validation Criterion: Commitment Claims Must Survive Scope Discipline

A commitment claim should be reported in one of the auditable forms defined in Section 7.2, explicitly including scope labels. If pooled coherence fails but windowed coherence passes, the correct output is **SCOPE_LIMITED** and the claim must be written as phase-conditional. If coherence fails at all scopes, the correct output is **ESTIMATOR_UNSTABLE** and no “commitment” claim is permitted.

This discipline shifts validation away from "story strength" toward **scope-correctness**: the claim is only as strong as the estimator family and the declared boundary

---

## 8. Limitations

Force proxies are indirect: scRNA-only data cannot directly measure forces, so force claims should be labeled “indirect” unless supported by perturbation experiments. Pseudotime is not physical time; all scope claims remain conditional on the preregistered ordering method. The framework is conservative by design: many transitions will remain SCOPE_LIMITED or INCONCLUSIVE under EST discipline, and this is treated as an outcome rather than a defect. Finally, multi-proxy coherence validation carries a computational cost because multiple estimators must be computed per window.

---

## 9. Conclusion

FIT reframes single-cell fate commitment as a constraint-driven phase transition rather than a state change. The Tier-2 protocol produces auditable, scope-aware interpretations—or explicit non-interpretability labels—separating “marker narratives” from preregistered, coherence-gated claims.

The key conceptual shift is from “Gene X increases during differentiation, therefore X drives commitment” to “constraint proxies reconfigure at time T with coherent information gain; commitment is registered at T conditional on boundary B”.

This reframing aligns interpretation with the dynamical nature of living systems and provides a principled basis for identifying irreversible commitment.

---

## Data and Code Availability

Code and runnable protocol: `github/F-I-T/experiments/real_world/scrna_commitment_tier2p11/` (repo path).  
Coherence semantics: `github/F-I-T/docs/est/coherence.md` (repo path).  
EST preregistration template: `github/F-I-T/docs/core/est_prereg_v2.5.md` (repo path).

---

## Figures

**Figure 1**: Expression Space vs Reachable Space
Expression levels (colored curves) vary along pseudotime, but fate commitment corresponds to contraction of the **reachable expression space** (blue funnel). Irreversibility emerges when the reachable space collapses to a stable attractor.

**Figure 2**: Phase-Local Coherence
Coherence (green curve) may be valid within each phase (Phi1, Phi2, Phi3) but fail when pooled across phases. This reflects regime heterogeneity, not estimator failure.

**Figure 3**: Drivers vs Attractor Passengers
Attractor passengers (gray curves) change expression along pseudotime but do not interface with constraints. Drivers (red curve) are associated with constraint reconfiguration at the Phi2 -> Phi3 boundary.

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Coherence** | Agreement between independent estimators within a declared scope |
| **Constraint** | Restriction on reachable system configurations |
| **ESTIMATOR_UNSTABLE** | Coherence gate failed; interpretation forbidden |
| **Phase** | Dynamical regime with distinct constraint structure |
| **PT-MSS** | Phase Transition Multi-Signal Signature (S1+S2+S3 co-occurrence) |
| **SCOPE_LIMITED** | Pooled failure but window-level pass; interpret locally only |
| **Tier-2** | Estimator-gated protocol with auditable failure modes |

---

## Appendix B: Tier-2 Preregistration Template

```yaml
# EST Prereg: scRNA Fate Commitment
meta:
  case_id: scrna_hematopoiesis_tier2
  version: "1.0"
  tier: 2
  status: preregistered

boundary:
  dataset: "Paul et al., 2015"
  preprocessing: [filtering, normalization, HVG_selection]
  latent_space: {type: PCA, dims: 20}
  time_axis: {type: diffusion_pseudotime}  # prefer explicit stage/time when available
  windows: {n: 5, type: equal_width, min_cells: 50, warmup_exclude: 0}

estimators:
  constraint:
    C_dim_collapse: {type: dim_collapse, expected_sign: +1}
    C_label_purity: {type: label_purity, expected_sign: +1}
  information:
    I_pred: {type: knn_fate_accuracy}  # optional; not required for Tier-2 coherence

coherence:
  metric: spearman
  threshold_rho: 0.2
  expected_sign: +1
  pairs: [[C_dim_collapse, C_label_purity]]
  windowing: {type: preregistered_windows, aggregate: all_pass}  # OK_PER_WINDOW iff all windows pass

outputs:
  coherence_report: "outputs/coherence_report.json"
  fail_windows: "outputs/fail_windows.md"
  summary_figure: "outputs/tradeoff_onepage.pdf"

failure_labels:
  ESTIMATOR_UNSTABLE: "Coherence gate failed"
  SCOPE_LIMITED: "Pooled FAIL, windows PASS"
  INCONCLUSIVE: "Insufficient data or undefined metrics"
```

---

## References

1. Paul, F., et al. (2015). Transcriptional heterogeneity and lineage commitment in myeloid progenitors. *Cell*, 163(7), 1663-1677.

2. Huang, Q. (2026). Force-Information-Time: A Framework for Constraint-Driven Dynamics. FIT Lab.

3. Trapnell, C. (2015). Defining cell types and states with single-cell genomics. *Genome Research*, 25(10), 1491-1498.
