# How to Falsify FIT (Short Guide)

Status: **core guardrail**. This guide exists to keep FIT from drifting into unfalsifiable grand narrative.

Navigation: [`core index`](./README.md) | [`Core Card`](./fit_core_card.md) | [`Misuse Guard & FAQ`](./FIT_Misuse_Guard_and_FAQ.md) | [`Prediction Protocol Challenge`](../reproducibility/fit_prediction_protocol_challenge.md)

## 0) What FIT is (so you know what to attack)

FIT is not a "theory of everything". It is a meta-language for describing late-time dynamics under explicit scope:

- a declared boundary (what is in/out, over what time range),
- an estimator tuple (what you measured, how, and with what windows),
- and a registrable prediction/evaluation protocol (what would count as success or failure).

If a FIT claim cannot be put in that form, treat it as non-claim.

## 1) What "falsify FIT" means (operationally)

You do not falsify FIT by disagreeing with an interpretation. You falsify FIT by producing a counterexample where:

1) the boundary is locked in advance,
2) the estimator tuple is declared in advance,
3) a specific proposition (or protocol claim) is stated with pass/fail criteria,
4) the result fails under the declared protocol, and
5) the result is reproducible (or at least auditable enough to attempt reproduction).

Outcome labels to use (recommended):

- `CHALLENGED`: preregistered claim fails; coherence gates pass.
- `INCONCLUSIVE`: insufficient events / power under the declared boundary.
- `ESTIMATOR_UNSTABLE`: coherence gates fail; do not interpret as supported/challenged.
- `SCOPE_LIMITED`: claim holds only under explicitly stated scope constraints (which must be recorded, not silently broadened).

## 2) The fastest way to falsify FIT (high-leverage attacks)

### A) Break estimator robustness (the most important attack)

Many failures should manifest as estimator dependence. The cleanest falsification pattern is:

- A proposition claims an invariant under an admissible estimator family,
- you preregister a small admissible family (e.g., window sizes, equivalent estimator variants),
- the proposition flips sign / fails outside a narrow slice,
- and coherence diagnostics show the failure is not a logging artifact.

This is not "nitpicking". EST-scoped invariants are FIT's strongest epistemic claim.

See: [`docs/est/diagnostics.md`](../est/diagnostics.md).

### B) Force boundary discipline (attack "post-hoc scope expansion")

If a FIT write-up only holds after expanding the boundary (adding extra time ranges, excluding inconvenient regimes, changing the negative class), then the correct label is:

- the preregistered claim is `CHALLENGED`, and
- the post-hoc rescue is a new hypothesis requiring a new preregistration.

### C) Produce a concrete counterexample system (best credibility)

Pick a simple public system (toy, simulated, or real) with:

- a time index,
- a clear event definition,
- and enough event density to be evaluable.

Then preregister a FIT claim and break it. A good counterexample is one where:

- the same estimator tuple behaves well on other systems,
- but fails on your system in a way FIT would have predicted it should not.

### D) Use "alarm usability" as a falsification gate (avoid AUC theater)

If a claim is about early warning, then showing high AUC is not enough.

Try to falsify the alarm by demonstrating a hard floor:

- no threshold can achieve target low-FPR operation while still triggering on positives,
- or the achieved FPR is essentially fixed across thresholds (a degenerate score),
- or coverage collapses at the declared operating point.

This is the exact class of failure that turns "good ranking" into "useless alarm".

See: [`monitorability.md`](./monitorability.md).

## 3) Minimum falsification bundle (what to publish)

If you want your critique to be taken as evidence, publish:

1) **Boundary**: time range, inclusion/exclusion rules, seeds, and why.
2) **Estimator tuple**: state representation, estimator definitions, windows.
3) **Claim**: one proposition or protocol claim, written as a pass/fail statement.
4) **Protocol**: commands and environment (commit hash, dependencies).
5) **Artifacts**: raw/derived time series + one "decision view" plot + run log.
6) **Result label**: `SUPPORTED/CHALLENGED/INCONCLUSIVE/ESTIMATOR_UNSTABLE/SCOPE_LIMITED`.

If you cannot publish raw data, publish sufficient derived traces to re-run the decision logic.

## 4) Report template (copy/paste)

Title: `Falsification Attempt: <system> / <claim-id>`

- Boundary:
- Estimator tuple:
- Claim (pass/fail):
- Coherence gates:
- Operating point (if alarms): target FPR(s), coverage/lead time:
- Commands + commit:
- Outcome label:
- Notes (why this falsifies the claim, not just the story):

## 5) What FIT should do when falsified

If a preregistered claim is `CHALLENGED`, the correct response is not to "explain it away". The correct response is:

- record the negative result as first-class,
- tighten the scope or estimator admissibility conditions (explicitly),
- or delete the proposition if it cannot survive boundary discipline.

That is how FIT avoids the "grand narrative spiral".

