# Case 06: BioArc (NAS for Biological Foundation Models)

## Scope & Claims Notice

This case is a **FIT reading exercise** for the BioArc paper (arXiv:2512.00283v2).

It is **not** proof of FIT. It is a worked example of how to extract:

- an explicit boundary (what is being optimized, on which modalities/tasks),
- a concrete oracle (what constitutes “performance”),
- a constraint contract (what is enforced vs what is merely hoped),
- and a falsifiable protocol claim about **search under budget**.

## Source (paper)

- Paper (arXiv, 2025-12-02): “BioArc: Discovering Optimal Neural Architectures for Biological Foundation Models”  
  https://arxiv.org/abs/2512.00283

## System Snapshot (what the paper does, in one paragraph)

BioArc frames **architecture design for biological foundation models** as a systematic, automated search problem: rather than importing a single general-purpose architecture (e.g., a vanilla Transformer), it uses **Neural Architecture Search (NAS)** over a broad search space (including blocks such as CNN/LSTM/Transformer/Mamba/Hyena) and evaluates candidates across biological modalities (explicitly DNA and protein; discussed as extensible to RNA and single-cell). It also studies the interaction between **architecture, tokenization, and training strategies**, and proposes **architecture prediction** methods (surrogates) to reduce NAS compute by predicting which architectures will do well on new tasks.

## FIT Variable Mapping (operational lens)

One reasonable mapping (there are others):

- **C (Constraint)**: hard feasibility and design contracts that shape the search space:
  - allowed module families (e.g., CNN/LSTM/Transformer/Mamba/Hyena),
  - depth/width choices,
  - training budget / memory / parameter count limits,
  - tokenization constraints (sequence chunking, k-mer schemes, etc.),
  - downstream task boundary (which benchmarks are “in-scope” for evaluation).
- **F (Force)**: optimization and selection pressure:
  - the NAS policy (evolutionary / one-shot / pruning),
  - gradients during supernet training,
  - the selection rule “keep architectures that score higher under the oracle”.
- **I (Information)**: stabilized structures that persist and enable reuse:
  - the discovered architecture motifs (a “catalog” of viable designs),
  - learned weights (supernet / pretrained weights),
  - learned architecture predictors (surrogates that encode “what works”).
- **T (Time / Tempo)**: budgeted iteration rhythms:
  - number of oracle evaluations (train+eval cycles),
  - supernet training schedule,
  - the cadence of pruning / sampling / retraining.

## Boundary Declaration (what must be written down to stay honest)

If you want to treat BioArc as an auditable “search-under-constraints” claim, the boundary must include:

1) **Modality boundary**: DNA vs protein (and whether results transfer to RNA/single-cell is a new claim).  
2) **Task boundary**: which pretraining corpora and downstream benchmarks are in-scope.  
3) **Search-space boundary**: which block families and hyperparameter ranges are allowed.  
4) **Budget boundary**: compute budget (oracle eval count, GPU-hours, max epochs, max params).  
5) **Oracle definition**: what is measured, when, and with what evaluation protocol.

This is where many “NAS success stories” become unfalsifiable: the boundary is left implicit, then widened post-hoc.

## Oracle (what constitutes success)

The paper’s oracle is an **external evaluation channel**: downstream performance on declared benchmark tasks (plus pretraining objective quality), given a fixed training protocol.

In FIT terms: the oracle is the channel that prevents “self-justifying” narratives. Without an oracle, “architecture discovery” collapses into story-telling.

## Phase Map (teaching shorthand)

Use `Phi1/Phi2/Phi3` as a teaching shorthand (not a claim that the paper uses FIT).

- **Phi1 (Accumulation / exploration)**: define the search space and begin sampling; performance is sparse and noisy; many candidates fail or underperform.
- **Phi2 (Crystallization / efficient search)**: switch from expensive per-architecture training to efficiency tactics (e.g., supernet/one-shot training, pruning, predictors); the search becomes tractable and begins to concentrate on a narrower family of architectures.
- **Phi3 (Coordination / reuse)**: distill empirical design principles and train predictors that generalize (partially) to new tasks; “architecture choice” becomes a reusable decision policy rather than repeated brute-force search.

## PT-MSS (what would justify phase-transition language)

If you want to claim a “phase transition” in this workflow, you should look for **all three** signals:

1) **Force redistribution**: the optimization effort shifts from per-candidate training to supernet/predictor-driven search.
2) **Information re-encoding**: architectures become representations a predictor can operate on (graph/topology features), not just hand-designed templates.
3) **Constraint reorganization**: pruning and supernet design changes the *effective* feasible set (what is reachable within budget), not just the nominal search space.

If any one is missing, treat “phase transition” as metaphor only.

## What makes this case useful to FIT readers

This is a clean example of “**constrained path exploration**”:

- large combinatorial design space,
- explicit budgets,
- explicit feasibility constraints,
- and an oracle-backed evaluation loop.

It is the same structural template as:

- materials inverse design (Case 05),
- architecture search in biology (this case),
- and, later, “self-evolving” AI systems (where the risk is that the system drifts into regimes where monitoring/evaluation becomes non-evaluable).

## Practical FIT exercises for the reader

### Exercise A — Write a prereg for a tiny NAS run

Write a one-page prereg that locks:

- `C`: search space (module set, depth/width range), budget, and feasibility checks,
- `F`: the NAS policy (e.g., evolutionary vs surrogate-guided),
- `I`: what artifacts you will publish (trace, best architectures, predictor weights),
- `T`: number of oracle evals and stopping rules.

### Exercise B — Define “oracle cost accounting”

Decide what counts as an “oracle call”:

- full train+eval,
- partial training proxy,
- one-shot evaluation,
- predictor inference.

Then declare how you will report performance as a function of oracle budget (not only “best score”).

### Exercise C — Monitorability inside search

Add a monitorability section:

- feasibility rate over time (constraint violation frequency),
- diversity collapse (does the search prematurely lock into one family),
- calibration of the predictor (does its error spike out-of-distribution).

If you cannot monitor these, your search loop is not auditable.

## Minimal falsifiable claim template (for this kind of paper)

Here is a falsifiable claim template you can reuse for BioArc-like work:

> Under a fixed boundary (task set, training protocol, and search space) and a fixed oracle-evaluation budget, a constrained explorer achieves a statistically significant improvement over a declared baseline architecture family, while satisfying feasibility constraints at or above a declared rate.

If you cannot name the baseline, budget, and feasibility constraints, you do not yet have a testable claim.

