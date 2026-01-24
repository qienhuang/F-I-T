# Case 05 Workbook: L-BOM / Boundary-Identical Constraints

This workbook is a fill-in template for FIT readers. It is designed to be completed in one pass and then backed by an auditable artifact (a small dataset report).

## 0) Anchors (fill in)

- Paper: https://www.nature.com/articles/s41467-025-68089-2
- Public repo (if available): https://github.com/llwang91/L-BOM/
- Local artifact you will analyze (dataset dir): `<PATH_TO_LBOM_DATASET_DIR>`

## 1) Boundary (write as a contract; one paragraph)

Write a one-paragraph boundary statement that locks:

- **Mask family**: what boundary masks are in-scope (and what is held out).
- **Validity**: what counts as a valid microstructure (e.g., bicontinuity / open-cell / manufacturability filters).
- **Oracle**: what evaluator is treated as ground truth (FEA / simulation / experiments) and what failure modes count as invalid outputs.
- **Objective region**: what property region is targeted and how distance/coverage is computed.
- **Budget**: what iteration budgets (AL rounds, candidates per round, retrain cadence) are allowed.

Rule: if you change any locked element after seeing results, treat it as a new study.

## 2) State choice (pick one)

Choose one state representation $S_t$ and stick to it.

**Option A — Dataset-only state (lowest barrier):**

$$
S_t := (D_t,\ \Pi,\ \text{mask}(k))
$$

- $D_t$: microstructures observed up to iteration/index $t$ (you can define $t$ by AL round, or by a synthetic ordering if you only have a static dataset).
- $\Pi$: a property table mapping each structure to its property vector.
- $\text{mask}(k)$: which boundary-identical family you condition on (Mask1–Mask4, if applicable).

**Option B — Closed-loop design system state (full reproduction):**

$$
S_t := (D_t,\ \theta_t,\ \phi_t,\ \mathcal{A}_t,\ \text{mask}(k))
$$

- $\theta_t$: generator parameters.
- $\phi_t$: surrogate / evaluator (if used).
- $\mathcal{A}_t$: acquisition policy (active learning rule).

## 3) Estimator tuple (declare the minimum you will log)

Declare an estimator tuple:

$$
\mathcal{E}=(S_t,\ \mathcal{B},\ \{\hat{F},\hat{C},\hat{I}\},\ W).
$$

Fill in:

- $\mathcal{B}$ (boundary conditions): how the boundary-identical rule is operationalized (hard vs soft vs baseline-free).
- Window $W$: the fixed window(s) used for smoothing/aggregation.
- $\hat{C}$ (constraint proxy): at least one operational proxy for feasibility/constraint pressure (e.g., validity pass rate, defect rate).
- $\hat{I}$ (information proxy): at least one operational proxy for library diversity / coverage (e.g., property-space coverage entropy).
- $\hat{F}$ (force proxy): at least one operational proxy for selection pressure / drift (e.g., penalty-weighted distance-to-target statistics over selected candidates).

## 4) Monitorability gate (required for early-warning claims)

Pick a target event and define what an alarm means.

- **Target event (choose one)**: interface failure at assembly; connectivity defect spike; feasibility-rate collapse; coverage-stall.
- **Score candidate**: any scalar used for selection or quality control (uncertainty, novelty, quality, feasibility score).

Minimum reporting:

- achieved FPR vs target FPR under thresholding,
- coverage vs FPR sweep,
- lead time (when coverage is nonzero),
- and whether an FPR floor exists (degenerate score).

## 5) One falsifiable claim (pick exactly one)

Write one claim that can fail cleanly under the locked boundary:

> Under a locked mask family and locked oracle, the loop increases feasible coverage in a target region by at least X% without increasing constraint-violation rate beyond Y%.

Lock X, Y, and the oracle definition before evaluation.

## 6) Dataset-only audit (runnable; produces an artifact)

If you have the released dataset files, run the local analysis script and attach its output to your case study notes:

```bash
cd github/F-I-T
python experiments/l_bom_fit_case_v0_1/analyze_l_bom_dataset.py --dataset_dir "<PATH_TO_LBOM_DATASET_DIR>" --out_dir out/l_bom_case_05
```

Expected outputs:

- `out/l_bom_case_05/report.md`
- `out/l_bom_case_05/summary.json`

These provide a minimal "hard" anchor for the case study (what files exist, basic property quantiles, simple coverage counts, and voxel sanity checks).

## 7) What to paste into `CASE_05_Data_Driven_Inverse_Design_Bicontinuous_Multiscale.md`

After completing this workbook, add a short note to the case file that:

- states your boundary paragraph (Section 1),
- states the estimator tuple you actually used (Section 3),
- links to the generated artifact (`out/.../report.md`),
- and states one falsifiable claim (Section 5).
