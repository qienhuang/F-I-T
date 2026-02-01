# From Expression States to Constraint Dynamics:
## A FIT / EST Protocol for Fate Commitment in scRNA-seq (Tier-2, evidence-gated)

**Author**: Qien Huang (Independent Researcher)  
**Framework**: FIT (Force–Information–Time) + EST (Estimator Selection Theory)  
**Status**: Public note / protocol paper (v0.1)  
**Date**: 2026-02-01  
**Keywords**: single-cell RNA-seq; fate commitment; irreversibility; estimator selection; coherence gates; scope-limited interpretation

### What this is

This note reframes “fate commitment” in single-cell RNA sequencing as a **constraint phenomenon**: not merely what expression levels change, but what expression configurations become unreachable under a declared scope.

The goal is not to win a narrative contest about markers. The goal is to provide a **repo-runnable, auditable Tier-2 protocol** that either:

- admits a phase-conditional interpretation (`OK_PER_WINDOW`), or
- produces an explicit non-interpretability verdict (`ESTIMATOR_UNSTABLE`, `SCOPE_LIMITED`, `INCONCLUSIVE`)

without post hoc rescue.

### Where the runnable evidence lives

Repo entry point:

- `experiments/real_world/scrna_commitment_tier2p11/README.md`

Current run portfolio (tables + evidence bundle paths):

- `experiments/real_world/scrna_commitment_tier2p11/RESULTS.md`

Each run produces:

- `coherence_report.json`, `fail_windows.md`, `regime_report.md`, `metrics_log.parquet`, `tradeoff_onepage.png/pdf`, and `PREREG.locked.yaml`
- a zipped “evidence pack” under `experiments/real_world/scrna_commitment_tier2p11/outputs_runs/`

## Abstract

Single-cell trajectory inference is routinely interpreted in an expression-centric way: differential expression and smooth pseudotime trends are taken as evidence of fate commitment. This conflates transient state variation with irreversible structural change.

This note proposes a constraint-centric alternative using FIT/EST. Commitment is treated as a change in the reachable expression space, evaluated through preregistered windows over an explicit axis (stage/day when available; otherwise a declared surrogate) and an estimator family of constraint proxies. Interpretation is granted only if the estimator pair passes a preregistered coherence gate within scope; otherwise the correct output is a failure label rather than a story.

## The protocol (Tier-2, verifier-first)

The protocol has one purpose: to make commitment claims auditable under declared scope.

1. Declare a boundary: dataset identity, preprocessing, latent space, axis for windowing, and minimum per-window sample requirements.
2. Declare an estimator family: at least two constraint proxies `(C1, C2)` and an `expected_sign` with a coherence threshold.
3. Run a deterministic pipeline that computes windowed estimators and applies the coherence gate.
4. Report one of the outcome labels with scope semantics (not “overall” claims).

In this setting, windowing is a diagnostic instrument rather than a universal fix. If coherence only holds locally, the correct output is scope-limited. If coherence fails (including sign mismatch), interpretation is forbidden under that boundary.

## Current evidence snapshot (audit-first)

The repo portfolio includes both “pass” and “fail” outcomes under different datasets and axis choices (see `experiments/real_world/scrna_commitment_tier2p11/RESULTS.md`). The strongest current anchor uses an explicit experimental stage axis (`obs:stage`) on a gastrulation dataset; several other runs are included as negative or weak-support examples.

The intended scientific use is not to claim a universal biological law. It is to show that a commitment narrative can be made conditional on a stated scope and an estimator family that either passes or fails coherence.

## Limitations

This protocol is conservative by design. Many plausible commitment narratives will remain non-admissible under the gate until the estimator family is repaired or the boundary is tightened. When pseudotime is used, claims remain conditional on the ordering method; explicit stage/day axes are preferred when available.

## Citation note

If you cite this note, also cite the runnable experiment folder and its `RESULTS.md` so the claims remain attached to auditable artifacts.

