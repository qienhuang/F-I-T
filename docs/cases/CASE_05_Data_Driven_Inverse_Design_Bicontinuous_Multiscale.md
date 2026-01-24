# Case 05: Data-Driven Inverse Design of Bicontinuous Multiscale Structures

## Scope & Claims Notice

This case is a **FIT reading exercise** for a specific scientific paper on inverse design of bicontinuous multiscale structures (materials / metamaterials).

It is **not** proof of FIT. It is a worked example of how to extract:

- an explicit boundary,
- a concrete oracle (evaluation channel),
- a commit surface,
- and a falsifiable protocol claim,

without post-hoc scope expansion.

## System Snapshot (what the paper actually does)

The paper builds a pipeline for **multifunctional, multiscale** structures by first generating a large dataset of **bicontinuous open-cell microstructures** that share **identical boundary masks**, and then using a data-driven generative model plus **active learning** to expand the dataset and hit target property regions.

Key ingredients (as described in the paper):

- microstructure generation constrained by a boundary mask (“boundary-identical” building blocks),
- an AI generator (described as a denoising U-Net / diffusion-style denoising setup),
- a physics oracle (finite element analysis; and additional validation via simulation/experiments in the paper),
- and a loop: generate -> evaluate -> add to dataset -> retrain / improve coverage.

## Source (paper and public artifacts)

- Paper (Nature Communications, 2026): https://www.nature.com/articles/s41467-025-68089-2
- Project code/data (L-BOM, if still available): https://github.com/llwang91/L-BOM/

## FIT Variable Mapping (one reasonable estimator lens)

This mapping is deliberately operational rather than metaphysical:

- **F (Force)**: selection pressure induced by objective targets (elastic tensor / permeability / porosity goals), plus penalties for constraint violation and manufacturability failures.
- **I (Information)**: the learned generative manifold (model weights) + the curated dataset of viable microstructures (a stabilized library).
- **T (Time / Tempo)**: iteration budget (optimization cost, FEA cost, AL loop cadence, retraining cadence).
- **C (Constraint)**: hard feasibility requirements that shrink the reachable design space:
  - boundary mask identity (interface compatibility),
  - bicontinuity / connectedness (both phases remain connected),
  - manufacturability / defect avoidance,
  - and implicit constraints induced by dataset curation (what gets kept becomes the effective constraint set).

## Phase Map (how the pipeline evolves)

Use `Phi1/Phi2/Phi3` as a teaching shorthand (not a claim that the paper uses FIT).

- **Phi1 (Accumulation)**: initial optimization runs produce a sparse set of viable microstructures under each boundary mask (high compute; low coverage).
- **Phi2 (Crystallization)**: the generator learns a structured representation of viable microstructures given boundary constraints and target properties; feasibility becomes easier to hit than pure optimization.
- **Phi3 (Coordination)**: the active-learning loop coordinates generator + oracle + dataset expansion across a wider property region, and the boundary-identical interface rule makes multiscale assembly tractable.

## PT-MSS (what looks like a phase transition in FIT terms)

If you wanted to argue a PT-MSS-style transition exists in this pipeline, you would look for:

1) **Force redistribution**: from direct topology optimization pressure to data-driven sampling + oracle-driven selection.
2) **Information re-encoding**: from explicit design variables to a learned latent/generative representation.
3) **Constraint reorganization**: the boundary-mask identity becomes the dominant interface constraint that eliminates a class of connectivity failures at assembly time.

If any one of these three is absent, treat phase-transition language as decorative and do not claim it.

## What makes this paper hard (and why it is useful to FIT readers)

This paper’s value is not philosophical; it is **pipeline hardness**:

- it is explicitly a **generate -> evaluate -> curate** loop,
- the oracle is external and measurable (FEA; plus additional validation),
- and the boundary mask acts like a **formal interface contract**, not an after-the-fact story.

For FIT readers, it is an unusually clean example of how to:

- prevent uncontrolled interface failure by enforcing a boundary invariant,
- turn design intuition into an auditable loop with an oracle,
- and treat dataset curation itself as constraint accumulation (C grows as the library stabilizes).

## Practical FIT exercises for the reader (do these to learn FIT by observation)

### Exercise A — Write the boundary in one paragraph

State what is in-scope and out-of-scope for the pipeline, including:

- design domain / mask family,
- which properties are targets,
- what counts as a valid microstructure,
- and what oracle outputs are accepted as ground truth.

If you cannot write this boundary, you cannot claim anything FIT-like about the system.

### Exercise B — Declare an estimator tuple

Write down a minimal estimator tuple $\mathcal{E}=(S_t,\mathcal{B},\{\hat{F},\hat{C},\hat{I}\},W)$ suitable for this paper, e.g.:

- $S_t$: dataset state (counts, coverage in property space), generator checkpoints, failure rates
- $\hat{C}$: constraint satisfaction rate + boundary-compatibility violations + bicontinuity failures
- $\hat{F}$: AL selection pressure (distance-to-target / penalty-weighted score)
- $\hat{I}$: diversity/entropy over the viable library + model compression proxies

Optional (local, runnable): if you downloaded the dataset, a small script can generate a quick auditable report over `count.json` and `img.zip`:

- `experiments/l_bom_fit_case_v0_1/analyze_l_bom_dataset.py`

If you want a fill-in worksheet for this case (boundary + estimator tuple), see:

- `docs/cases/CASE_05_LBOM_Workbook.md`

### Exercise C — Add a monitorability criterion (alarm usability)

Treat interface failure at assembly as an event to be predicted early.

Then ask: does any candidate score admit low-FPR operation, or is there an FPR floor (the failure mode you saw in grokking)?

If an indicator cannot be thresholded to control false positives, it is not a usable early-warning signal.

See: `docs/core/monitorability.md`.

### Exercise D — One falsifiable claim (pick exactly one)

Example protocol claim (illustrative, not asserted here):

> Under a fixed boundary mask family, adding AL-generated microstructures increases feasible property coverage by X% without increasing interface-failure rate beyond Y%.

Pre-register X, Y, and the oracle. Then try to break it.

See: `docs/core/how_to_falsify_fit.md`.

## How a FIT lens would improve the paper (if you were revising it)

This is not “add more theory”. It is “add more auditability”:

- preregistered boundary + held-out mask families (avoid post-hoc boundary expansion),
- explicit feasibility/monitorability reporting (constraint violation rates, FPR floors for any quality score),
- publish a minimal decision trace: where AL samples, what the oracle says, and why points are accepted/rejected,
- and report sensitivity across a small admissible estimator family (e.g., different AL acquisition functions / window sizes).

## Cross-domain insight for AI safety / self-evolving agents

Two direct analogies carry over cleanly:

1) **Boundary mask = interface contract**: keep tool/API boundaries invariant across self-modifications; only internal content changes are allowed without review.
2) **FEA oracle = external correction channel**: the strongest way to avoid self-justifying loops is to keep a hard, external evaluator in the loop and log its judgments as first-class artifacts.

## Addendum: a FIT-disciplined research pitch (optional)

If you want a preregisterable, falsifiable research pitch built around this domain, use:

- `docs/cases/CASE_05_Computational_Phase_Transition_Pitch.md`

## Limitations and natural next steps (for FIT readers)

This case is primarily a post-hoc reading exercise. FIT becomes more valuable when it is used to impose discipline on an active research loop.

Three natural extensions (all preregisterable) are:

1) **From post-hoc analysis to online diagnosis**: define a live phase diagnostic for the running AL loop (what signals are monitored, with what windows), and specify the intervention you would take if the loop stalls in a Phi2-like regime.

2) **Quantify PT-MSS candidates instead of narrating them**: if you want to use phase-transition language, preregister operational proxies for force redistribution / information re-encoding / constraint reorganization and test whether they co-occur near E_jump (or demonstrate that they do not).

3) **A FIT-aware inverse design protocol**: treat boundary contracts and external oracles as first-class artifacts (not prose), require an explicit monitorability / FPR-feasibility report for any quality score, and report robustness across a small admissible estimator family.
