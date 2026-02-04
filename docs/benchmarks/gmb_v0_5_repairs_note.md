**GMB v0.5 Repair A/B -- Diagnostic note (quick take)**

- **Context:** Ran limited evals (4 seeds) for two preregistered repairs:
  - Repair A: `protocol/estimator_spec.v0_5_holdout_repairA.yaml` (theta_corr=0.75)
  - Repair B: `protocol/estimator_spec.v0_5_holdout_repairB_whspec_1_wcorr_0p5_eps_0p005.yaml` (w_corr=0.5, eps_hspec=0.005)
  - Outputs: `grokking/runs_v0_5_repairs` (Repair A) and `grokking/runs_v0_5_repairs_repairB` (Repair B)
  - Diagnostics produced: `grokking/results/v0_5_repairs/tradeoff_with_abstain.csv` and `diagnostics_per_run.csv`.

- **Key observation (why operating points look the same):**
  - Both repairs act primarily by scaling and/or shifting the detector score (the decision rule parameters change the score magnitude or small additive terms) without reordering the per-example scores produced by the estimator.
  - Threshold selection for a target FPR therefore chooses a different numeric threshold (scale/shift) but ends up selecting the same subset of top-ranked examples (ordering preserved). As a result, the operating point (coverage vs FPR) plots are nearly identical up to a rescaling of the threshold -- ROC/AUC and ranking-based metrics remain unchanged.

- **Evidence to check:**
  - Compare `diagnostics_per_run.csv` for A vs B: identical `roc_auc`/`average_precision` values indicate preserved ranking.
  - Inspect `tradeoff_with_abstain.csv`: similar coverage values at matched FPR targets indicate thresholds rescale but ordering is stable.
  - Per-seed logs: `runs_v0_5_repairs/eval/seed_*` and `runs_v0_5_repairs_repairB/eval/seed_*` (compare score summaries).

- **Operational decision (per your guidance):**
  - Do NOT expand to 40 seeds yet. Only escalate to many seeds if we design or propose a *non-monotonic* repair that intentionally changes ranking (e.g., reweighting per-example features, mixing alternative estimators, or applying a learned calibration that depends on example features).

- **Next steps (optional):**
  - Produce a small one-page comparison figure (A vs B) showing `coverage vs FPR` and a short caption explaining the scaling/ordering explanation (for `docs/benchmarks`).

