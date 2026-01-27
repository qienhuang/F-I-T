# Grokking Hard Indicators: A Preregistered Evaluation Protocol and a Weak Baseline

**Version:** v0.3 (Explore -> Lock -> Evaluate, with explicit FPR controllability checks)
**Date:** January 21, 2026
**Scope:** Protocol specification, evaluability analysis, and risk-constrained early-warning evaluation.
**Results summarized:** v0.2 + v0.2.1 training/eval runs, plus v0.3 diagnostic analyses (A1/A2).
**Claim strength:** We do not claim a validated "hard indicator." We claim a reproducible evaluation protocol and report a weak or invalid baseline under low-FPR constraints.

**Keywords:** grokking; early-warning; preregistration; false-positive rate; evaluation protocol; neural network generalization

## Abstract

"Hard indicators" for grokking—and regime shifts in learning more broadly—are easy to claim and hard to validate, largely because many evaluation setups become non-evaluable: under common event definitions such as fixed accuracy thresholds, the event may not occur, rendering predictive metrics ill-defined. We present a preregistered Explore-Lock-Evaluate pipeline that enforces temporal separation between indicator development and evaluation. We introduce a jump-based regime-shift event definition that yields dense event occurrence in Phase B, enabling meaningful early-warning evaluation. Applying this protocol, we evaluate a baseline composite indicator under explicit false-positive-rate (FPR) control. We find a sharp failure mode: one score orientation achieves higher ranking metrics (AUC) but exhibits an uncontrollable FPR floor of approximately 0.44, rendering it invalid as an alarm; the alternative orientation admits proper FPR control but provides limited coverage at strict FPR (0.05) and a clear coverage-risk tradeoff. These results establish that ranking metrics such as AUC are insufficient for early-warning validity and motivate treating FPR controllability as a necessary condition for "hard indicators."

## 1. Introduction

Grokking refers to the phenomenon where a model initially overfits through memorization and only later "suddenly" generalizes, often after prolonged training (Power et al., 2022). Because grokking resembles a regime shift, it provides a natural benchmark for early-warning research: can we raise alarms before the generalization jump occurs?

However, early-warning evaluation is frequently undermined by a basic methodological problem. If the event definition yields zero events in held-out runs, Phase B becomes non-evaluable. If evaluation focuses on ranking metrics such as AUC without explicit risk constraints, one may report "good indicators" that prove unusable as operational alarms.

We address both problems via a preregistered protocol and explicit alarm validity criteria. Our contributions are fourfold. First, we propose an evaluability-first protocol: a preregistered Explore-Lock-Evaluate pipeline that prevents retrospective tuning. Second, we introduce a dense event definition: a jump-based regime-shift definition (E1) that makes Phase B reliably evaluable. Third, we establish risk-constrained evaluation: explicit FPR control and a validity gate (FPR controllability) that distinguishes "informative" scores from operationally usable alarms. Fourth, we report a negative or weak baseline: a baseline composite indicator whose high-AUC orientation fails operational validity due to an FPR floor, while the usable orientation exhibits limited low-FPR coverage and a clear tradeoff curve.

## 2. Related Work

Grokking was introduced as a stylized phenomenon in algorithmic and synthetic tasks (Power et al., 2022) and has since been used to study optimization dynamics, phase transitions, and generalization delays (Nanda et al., 2023). Early-warning signals for critical transitions have a long history in complex systems research, including autocorrelation and variance-based warnings (Scheffer et al., 2009). In machine learning, numerous "grokking predictors" have been proposed, including loss and accuracy dynamics, spectral and sharpness proxies, and compression proxies.

We position our work differently from this literature. We treat "hard indicators" as a monitoring problem under risk constraints, not merely a ranking problem. The focus here is on protocol and validity, not on proposing a new best indicator.

## 3. Problem Setup and Boundary

### 3.1 Boundary Conditions

We hold several boundary conditions fixed throughout this study. The task is modular addition, specifically \((a+b)\bmod p\). The model family consists of small transformers with a fixed architecture family for the protocol. Data generation follows a synthetic procedure with a fixed generator. Logging captures checkpoint-level metrics including test loss, test accuracy, and estimator tuple values.

The protocol is designed to compare indicators under a fixed boundary; new boundaries involving other tasks or models are out of scope for this manuscript.

### 3.2 Early-Warning as a Risk-Constrained Decision Problem

Early-warning is not merely the question of whether one can rank pre-event versus post-event checkpoints. Rather, it involves three substantive questions: Can one trigger alarms at bounded false-positive rate? How much coverage—the fraction of runs warned—can one obtain under that risk budget? How early are the warnings, measured by lead time?

We therefore evaluate alarms under explicit FPR calibration and report coverage and lead time as primary metrics.

## 4. Protocol: Explore, Lock, Evaluate

### 4.1 Explore (Phase A)

During the exploration phase, researchers develop candidate event definitions and indicators, perform diagnostic analyses and ablations, and iterate on design choices. Critically, no claims are made from Phase A results.

### 4.2 Lock

At the lock stage, we freeze the event definition (E1) and all its parameters, indicator definitions and all hyperparameters, the thresholding and calibration method along with target operating points such as the FPR grid, and validity checks including FPR controllability criteria.

In this repository, the "lock" is represented by versioned specification files plus a preregistration note. The relevant artifacts are `estimator_spec.v0_2.yaml` (Phase B1, seeds 100-119), `estimator_spec.v0_2_1.yaml` (Phase B2, seeds 120-139, fresh held-out), and `prereg_v0_2.md` (protocol narrative specifying what is frozen versus exploratory).

### 4.3 Evaluate (Phase B)

We run held-out seeds with locked definitions and report achieved FPR versus target FPR for calibration sanity, coverage versus FPR and lead time versus FPR for alarm utility, and ranking metrics such as AUC and Average Precision as secondary measures.

## 5. Event Definition (E1): Jump-Based Regime Shift

### 5.1 Motivation

Fixed accuracy thresholds, such as `test_acc >= 0.95`, often lead to zero events in held-out runs, making Phase B non-evaluable. We therefore define an event based on a sustained jump in smoothed performance.

### 5.2 Definition

Let \(\bar{a}(t)\) denote smoothed test accuracy at checkpoint \(t\). The event E1 triggers when three conditions are met: \(\bar{a}(t)\) increases by at least a fixed threshold \(\Delta\) over a short window; the post-jump level exceeds a floor to avoid micro-jumps; and the trajectory does not immediately revert, satisfying a hold condition. Exact parameters are locked in the v0.2 and v0.2.1 protocol specifications.

### 5.3 Evaluability

Across all runs reported here—Phase A seeds 0-4 and Phase B seeds 100-139, totaling 45 runs—E1 yields 100% event density: every run exhibits a detectable jump. On held-out evaluation runs alone (seeds 100-139, 40 runs), event density is also 100%, making Phase B evaluable.

## 6. Indicators and Alarm Construction

### 6.1 Baseline Indicator Tuple

We evaluate a baseline composite indicator that can be decomposed into two conceptual components. The first, which we denote H_spec, is a spectral-entropy-like component that captures distributional or structural changes in representations or dynamics. The second, CorrRate, is a correction-rate-like component that captures changes in self-correction or error dynamics. We treat these as a baseline tuple; the protocol is agnostic to their exact engineering.

### 6.2 Score Orientation

Because many indicators are ambiguous up to sign, we evaluate two orientations: `score_sign = +1` and `score_sign = -1`.

### 6.3 Alarm Thresholding via Target-FPR Calibration

Given a target FPR \(f\), we calibrate a threshold \(\theta_f\) such that on negative checkpoints (no-event windows),

\[
\Pr(s(t) > \theta_f \mid \text{negative}) \approx f.
\]

We then apply this threshold to full trajectories to compute alarm triggers and lead times.

## 7. Metrics

### 7.1 Ranking Metrics (Secondary)

We report ROC-AUC and Average Precision (AP) as secondary metrics, following standard practice in classification evaluation (Fawcett, 2006).

### 7.2 Alarm Utility Metrics (Primary)

Our primary metrics are achieved FPR measured on negative checkpoints, coverage defined as the fraction of runs with at least one alarm before the event, and lead time defined as event time minus first alarm time in steps, conditional on coverage.

### 7.3 Validity Gate: FPR Controllability

We treat a detector as invalid if it fails either of two conditions. FPR tracking failure occurs when achieved FPR does not track target FPR within tolerance on multiple target points. An FPR floor occurs when achieved FPR cannot be driven below a ceiling, indicative of "always-on" behavior. This validity gate is motivated by Phase A2 findings and is enforced before interpreting coverage.

## 8. Experimental Design

### 8.1 Seed Splits and Phases

We report Phase B results on two held-out evaluation seed ranges: Phase B1 covers seeds 100-119 (20 runs), and Phase B2 covers seeds 120-139 (20 runs). Phase A seeds 0-4 are used only for protocol development and event-density checks; total held-out Phase B evaluations reported here comprise 40 runs.

### 8.2 FPR Sweep

We sweep target FPR thresholds over the set \(\{0.01, 0.02, 0.05, 0.10, 0.15, 0.20\}\).

## 9. Results

### 9.1 E1 Event Density and Early-Warning Window

Using the locked jump-based regime-shift definition (E1), event density reaches 100% of evaluated runs. Alarms that trigger successfully do so approximately 12,000-15,000 steps before the jump, stable across runs, corresponding to roughly 24-30 checkpoints under the current logging cadence. This confirms Phase B is evaluable and the early-warning objective is non-trivial.

### 9.2 Phase A2: FPR-Coverage Tradeoff Reveals Detector Degeneracy

We evaluate the baseline score in both orientations under explicit FPR control. The results reveal a fundamental asymmetry between the two orientations.

**Summary by Seed Range**

| Seed Range | Score Sign | Target FPR Range | Achieved FPR | Coverage (raw) | Mean Lead Time (steps) |
|---|---:|---:|---:|---:|---:|
| 100-119 (B1) | -1 | 0.01-0.20 | 0.4407 (constant) | 100% | 18775 |
| 100-119 (B1) | +1 | 0.01-0.20 | 0.01-0.20 (tracks target) | 0% -> 85% | 12071-14167 |
| 120-139 (B2) | -1 | 0.01-0.20 | 0.4442 (constant) | 95% | 18895 |
| 120-139 (B2) | +1 | 0.01-0.20 | 0.01-0.20 (tracks target) | 0% -> 75% | 7250-15000 |

**B1 (seeds 100-119): `score_sign = -1` is invalid due to FPR floor**

| Target FPR | Achieved FPR | Coverage | N Covered | Mean Lead Time |
|---:|---:|---:|---:|---:|
| 0.010 | 0.4407 | 100% | 20/20 | 18775 |
| 0.020 | 0.4407 | 100% | 20/20 | 18775 |
| 0.050 | 0.4407 | 100% | 20/20 | 18775 |
| 0.100 | 0.4407 | 100% | 20/20 | 18775 |
| 0.150 | 0.4407 | 100% | 20/20 | 18775 |
| 0.200 | 0.4407 | 100% | 20/20 | 18775 |

The achieved FPR cannot be reduced below approximately 0.44 regardless of threshold setting. Raw coverage is therefore meaningless under risk constraints. Under the protocol's validity gate, this configuration is invalid as an alarm.

**B1 (seeds 100-119): `score_sign = +1` is valid and exhibits a tradeoff**

| Target FPR | Achieved FPR | Coverage | N Covered | Mean Lead Time |
|---:|---:|---:|---:|---:|
| 0.010 | 0.0100 | 0% | 0/20 | N/A |
| 0.020 | 0.0200 | 0% | 0/20 | N/A |
| 0.050 | 0.0500 | 35% | 7/20 | 12071 |
| 0.100 | 0.1000 | 70% | 14/20 | 13071 |
| 0.150 | 0.1500 | 75% | 15/20 | 14167 |
| 0.200 | 0.2000 | 85% | 17/20 | 13588 |

Coverage roughly doubles when moving from FPR=0.05 to FPR=0.10, while lead time remains stable at approximately 12,000-14,000 steps.

**B2 (seeds 120-139): `score_sign = -1` is invalid (same FPR floor)**

| Target FPR | Achieved FPR | Coverage | N Covered | Mean Lead Time |
|---:|---:|---:|---:|---:|
| 0.010 | 0.4442 | 95% | 19/20 | 18895 |
| 0.020 | 0.4442 | 95% | 19/20 | 18895 |
| 0.050 | 0.4442 | 95% | 19/20 | 18895 |
| 0.100 | 0.4442 | 95% | 19/20 | 18895 |
| 0.150 | 0.4442 | 95% | 19/20 | 18895 |
| 0.200 | 0.4442 | 95% | 19/20 | 18895 |

Again, achieved FPR is insensitive to target threshold, indicating calibration degeneracy.

**B2 (seeds 120-139): `score_sign = +1` remains valid with similar tradeoff**

| Target FPR | Achieved FPR | Coverage | N Covered | Mean Lead Time |
|---:|---:|---:|---:|---:|
| 0.010 | 0.0100 | 0% | 0/20 | N/A |
| 0.020 | 0.0200 | 10% | 2/20 | 7250 |
| 0.050 | 0.0500 | 35% | 7/20 | 15357 |
| 0.100 | 0.1000 | 65% | 13/20 | 11769 |
| 0.150 | 0.1500 | 70% | 14/20 | 14857 |
| 0.200 | 0.2000 | 75% | 15/20 | 15000 |

### 9.3 Practical Operating Points

For the only valid orientation (`score_sign = +1`):

| Target FPR | Coverage (B1) | Coverage (B2) | Average Coverage | Typical Lead Time |
|---:|---:|---:|---:|---:|
| 0.05 | 35% | 35% | 35% | ~12-15k steps |
| 0.10 | 70% | 65% | 67.5% | ~12-14k steps |
| 0.20 | 85% | 75% | 80% | ~13-15k steps |

We recommend FPR=0.10 as a practical operating point for main text reporting while providing the full tradeoff curve in supplementary materials.

### 9.4 Why AUC is Insufficient: Ranking-Alarm Decoupling

The invalid configuration (`score_sign = -1`) can exhibit higher ranking metrics while being unusable as an alarm due to an FPR floor. This demonstrates a general principle: in early-warning settings, ranking ability as measured by AUC is insufficient; controllable false-positive behavior is a necessary condition.

### 9.5 Phase A1 Component Diagnosis

Component-level diagnosis indicates that seed dependence is partly explained by which component dominates. In seeds 100-119, the spectral-entropy-like component (H_spec) shows stronger directional association, which can inflate AUC for one orientation. In seeds 120-139, both components weaken substantially, producing near-random discrimination. However, even when a component provides ranking signal, it can induce calibration failure through an FPR floor, making the resulting alarm invalid.

## 10. Discussion

### 10.1 What Would Count as a Validated Hard Indicator?

Under this protocol, a "hard indicator" should satisfy several conditions on held-out evaluation. Evaluability requires that events occur with sufficient density. Validity requires that achieved FPR tracks target FPR without an FPR floor. Utility requires that coverage is non-trivial at reasonable FPR levels such as 0.05-0.10. Stability requires that lead time is consistent and non-trivial. Robustness requires that performance persists across seed ranges and ideally across boundaries.

Our baseline fails validity in one orientation and is weak under strict low-FPR (0.05) even in the valid orientation.

### 10.2 Why This Negative Result is Useful

This work clarifies why "hard indicators" are difficult. It is easy to produce scores with seemingly good AUC, but much harder to produce alarms that are usable under risk constraints. The protocol turns this into a measurable, reproducible failure mode.

### 10.3 Limitations

This manuscript studies a single boundary (modular addition, small transformer family). Indicator engineering is limited by the baseline tuple; we do not claim optimal features. Some quantities, such as representation-level measures, require heavier instrumentation.

### 10.4 Future Directions

Future work should develop calibration-first indicators such as autocorrelation and variance-based early-warning proxies, use multi-gate detectors with evidence aggregation to reduce FPR floors, and expand Phase B to additional seed ranges and boundaries.

## 11. Reproducibility Appendix

### 11.1 Key Artifacts

The locked protocol specifications and results are available in the following repository paths:

- `experiments/grokking_hard_indicators_v0_2/code/protocol/estimator_spec.v0_2.yaml`
- `experiments/grokking_hard_indicators_v0_2/code/protocol/estimator_spec.v0_2_1.yaml`
- `experiments/grokking_hard_indicators_v0_2/code/protocol/prereg_v0_2.md`
- `experiments/grokking_hard_indicators_v0_2/RESULTS_v0.2_v0.2.1.md`
- `experiments/grokking_hard_indicators_v0_2/results/v0.3_A1_component_diagnosis.md`
- `experiments/grokking_hard_indicators_v0_2/results/v0.3_A2_fpr_tradeoff.md`

### 11.2 Example Reproduction Commands

```bash
cd experiments/grokking_hard_indicators_v0_2

# Environment setup
python -m venv .venv
source .venv/bin/activate
pip install -r code/requirements.txt
pip install -e code

# Phase B1 (seeds 100-119): generate runs, then sweep FPR operating points
python -m grokking.runner.sweep --spec code/protocol/estimator_spec.v0_2.yaml --out runs_v0_2 --phase eval
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0_2/eval --score_sign=+1
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0_2/eval --score_sign=-1

# Phase B2 (seeds 120-139): fresh held-out seeds
python -m grokking.runner.sweep --spec code/protocol/estimator_spec.v0_2_1.yaml --out runs_v0_2_1 --phase eval
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0_2_1/eval --score_sign=+1
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0_2_1/eval --score_sign=-1
```

If you do not have the archived `runs_v0.2*` directories, follow `experiments/grokking_hard_indicators_v0_2/README.md` to generate runs via `python -m grokking.runner.sweep`, then point `--runs_dir` at the resulting `runs/{explore,eval}` folders.

### 11.3 Reporting Requirements

Main text should include achieved FPR versus target FPR for validity assessment, coverage versus FPR and lead time versus FPR for utility assessment, and a clear statement that AUC and AP are insufficient for alarm usability. Supplementary materials should include full sweep tables, seed-range breakdowns, and locked specification hashes or commits.

## References

Fawcett, T. (2006). An introduction to ROC analysis. *Pattern Recognition Letters*, 27(8), 861-874.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of the 34th International Conference on Machine Learning* (ICML 2017). arXiv:1706.04599.

Nanda, N., Chan, L., Lieberum, T., Smith, J., & Steinhardt, J. (2023). Progress measures for grokking via mechanistic interpretability. In *Proceedings of the 11th International Conference on Learning Representations* (ICLR 2023). arXiv:2301.05217.

Power, A., Burda, Y., Edwards, H., Babuschkin, I., & Misra, V. (2022). Grokking: Generalization beyond overfitting on small algorithmic datasets. arXiv:2201.02177.

Scheffer, M., Bascompte, J., Brock, W. A., Brovkin, V., Carpenter, S. R., Dakos, V., Held, H., van Nes, E. H., Rietkerk, M., & Sugihara, G. (2009). Early-warning signals for critical transitions. *Nature*, 461, 53-59.

Dakos, V., Carpenter, S. R., van Nes, E. H., & Scheffer, M. (2012). Methods for detecting early warnings of critical transitions in time series illustrated using simulated ecological data. *PLoS ONE*, 7(7), e41010.

Davis, J., & Goadrich, M. (2006). The relationship between precision-recall and ROC curves. In *Proceedings of ICML*.
