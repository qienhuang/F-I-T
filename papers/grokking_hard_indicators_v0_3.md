# Grokking Hard Indicators: A Preregistered Evaluation Protocol and a Weak Baseline

**Version:** v0.3 (Explore → Lock → Evaluate, with explicit FPR controllability checks)  
**Date:** January 21, 2026  
**Scope:** Protocol + evaluability + risk-constrained early-warning evaluation.  
**Claim strength:** We *do not* claim a validated “hard indicator.” We claim a **reproducible evaluation protocol** and report a **weak / invalid baseline** under low-FPR constraints.

---

## Abstract

“Hard indicators” for grokking (and regime shifts in learning more broadly) are easy to claim and hard to validate, largely because many evaluation setups become **non-evaluable**: under common event definitions (e.g., fixed accuracy thresholds), the event may not occur, making predictive metrics ill-defined. We present a preregistered **Explore → Lock → Evaluate** pipeline that enforces temporal separation between indicator development and evaluation. We introduce a jump / regime-shift event definition that yields dense event occurrence in Phase B, enabling meaningful early-warning evaluation. Applying this protocol, we evaluate a baseline composite indicator under explicit false-positive-rate (FPR) control. We find a sharp failure mode: one score orientation achieves higher ranking metrics (AUC) but exhibits an **uncontrollable FPR floor (~0.44)**, rendering it **invalid as an alarm**; the alternative orientation admits proper FPR control but provides limited coverage at strict FPR (0.05) and a clear coverage–risk tradeoff. These results establish that **ranking metrics (AUC) are insufficient for early-warning validity** and motivate treating **FPR controllability as a necessary condition** for “hard indicators.”

---

## 1. Introduction

Grokking refers to the phenomenon where a model initially overfits (memorization) and only later “suddenly” generalizes, often after prolonged additional training [Power et al., 2022]. Because grokking resembles a regime shift, it is a natural benchmark for **early-warning**: can we raise alarms *before* the generalization jump?

However, early-warning evaluation is frequently undermined by a basic methodological problem:

- If the event definition yields **zero events** in held-out runs, Phase B becomes **non-evaluable**.
- If evaluation focuses on **ranking metrics** (e.g., AUC) without explicit risk constraints, one may report “good indicators” that are unusable as alarms.

This paper addresses both problems via a preregistered protocol and explicit alarm validity criteria.

### Contributions

1. **Evaluability-first protocol:** A preregistered Explore → Lock → Evaluate pipeline that prevents retrospective tuning.
2. **Dense event definition:** A jump / regime-shift event definition (E1) that makes Phase B reliably evaluable.
3. **Risk-constrained evaluation:** Explicit FPR control and a **validity gate** (FPR controllability) that distinguishes “informative” scores from **operationally usable** alarms.
4. **A negative/weak baseline:** A baseline composite indicator whose high-AUC orientation fails operational validity (FPR floor), while the usable orientation exhibits limited low-FPR coverage and a clear tradeoff curve.

---

## 2. Related Work

Grokking was introduced as a stylized phenomenon in algorithmic and synthetic tasks and has since become a testbed for studying optimization dynamics, phase transitions, and delayed generalization [Power et al., 2022]. Early-warning signals for critical transitions have a long history in complex systems research, particularly through autocorrelation and variance-based warnings [Scheffer et al., 2009; Dakos et al., 2012]. In ML monitoring and decision systems, ROC/AUC and calibration are standard tools [Fawcett, 2006; Davis and Goadrich, 2006]. This work does not propose a new best indicator; it focuses on making protocol and alarm validity constraints explicit.

> **Positioning:** We treat “hard indicators” as a *monitoring problem under risk constraints*, not merely a ranking problem.

---

## 3. Problem Setup and Boundary

### 3.1 Boundary (held fixed)

- **Task:** Modular addition, e.g. \((a+b)\bmod p\).
- **Model family:** Small transformer (fixed architecture family for the protocol).
- **Data:** Synthetic generation (fixed generator).
- **Logging:** Checkpoint-level metrics (e.g., test loss/accuracy) and estimator tuple values.

The protocol is designed to compare indicators under a fixed boundary; new boundaries (other tasks/models) are out of scope for this manuscript.

### 3.2 Early-warning as a risk-constrained decision problem

Early-warning is not just “can you rank pre- vs post-event checkpoints,” but:

- Can you trigger alarms at **bounded false-positive rate (FPR)**?
- How much **coverage** (fraction of runs warned) can you obtain under that risk budget?
- How early are the warnings (**lead time**)?

We therefore evaluate alarms under explicit FPR calibration and report coverage and lead time.

---

## 4. Protocol: Explore → Lock → Evaluate

### 4.1 Explore (Phase A)

- Develop candidate event definitions and indicators.
- Perform diagnostic analyses and ablations.
- **No claims** are made from Phase A results.

### 4.2 Lock

Freeze:

- Event definition (E1) and all parameters.
- Indicator definitions and all hyperparameters.
- Thresholding/calibration method and target operating points (e.g., FPR grid).
- Validity checks (notably, FPR controllability criteria).

In the released materials, this “lock” is implemented as (i) a versioned prereg/spec file committed to the repo (see `experiments/grokking_hard_indicators_v0_2/code/protocol/`), and (ii) a short human-readable status note that records the frozen seed split and reporting requirements (see `experiments/grokking_hard_indicators_v0_2/STATUS.md`). Both are committed before examining Phase B outputs.

### 4.3 Evaluate (Phase B)

Run held-out seeds/runs with locked definitions. Report:

- Achieved FPR vs target FPR (calibration sanity).
- Coverage vs FPR, lead time vs FPR (alarm utility).
- Ranking metrics (AUC/AP) **as secondary**.

---

## 5. Event Definition (E1): Jump / Regime Shift

### 5.1 Motivation

Fixed accuracy thresholds (e.g., `test_acc ≥ 0.95`) often lead to zero events in held-out runs, making Phase B non-evaluable. We therefore define an event based on a *sustained jump* in smoothed performance.

### 5.2 Definition (high level)

Let \(\bar{a}(t)\) denote smoothed test accuracy at checkpoint \(t\). E1 triggers when:

1. \(\bar{a}(t)\) increases by at least a fixed \(\Delta\) over a short window,
2. the post-jump level exceeds a floor (to avoid micro-jumps),
3. the trajectory does not immediately revert (a hold condition).

Exact parameters are locked in the v0.2/v0.3 protocol spec.

### 5.3 Evaluability

Across the Phase B held-out evaluation seeds (100–139; 40 runs), E1 yields **100% event density**: every run exhibits a detectable jump, making Phase B evaluable. Including the Phase A exploratory seeds (0–4; 5 runs), the total is 45/45 runs with a detectable jump.

---

## 6. Indicators and Alarm Construction

### 6.1 Baseline indicator tuple

We evaluate a baseline composite indicator that can be decomposed into two conceptual components:

- **H_spec:** a spectral-entropy-like component (captures distributional/structural changes in representations or dynamics).
- **CorrRate:** a correction-rate-like component (captures changes in “self-correction” or error dynamics).

(We treat these as a baseline tuple; the protocol is agnostic to their exact engineering.)

### 6.2 Score orientation

Because many indicators are ambiguous up to sign, we evaluate two orientations:

- `score_sign = +1`
- `score_sign = -1`

### 6.3 Alarm thresholding via target-FPR calibration

Given a target FPR \(f\), we calibrate a threshold \(\theta_f\) so that, on negative checkpoints (no-event windows),

\[
\Pr(s(t) > \theta_f \mid \text{negative}) \approx f.
\]

We then apply this threshold to full trajectories to compute alarm triggers and lead times.

---

## 7. Metrics

### 7.1 Ranking metrics (secondary)

- **ROC-AUC**
- **Average Precision (AP)**

### 7.2 Alarm utility metrics (primary)

- **Achieved FPR:** measured on negative checkpoints.
- **Coverage:** fraction of runs with ≥1 alarm before the event.
- **Lead time:** event time minus first alarm time (in steps), conditional on coverage.

### 7.3 Validity gate: FPR controllability (mandatory)

We treat a detector as **invalid** if it fails either:

1. **FPR tracking failure:** achieved FPR does not track target within tolerance on multiple target points.
2. **FPR floor:** achieved FPR cannot be driven below a ceiling (indicative of “always-on” behavior).

This gate is motivated by Phase A2 findings and is enforced before interpreting coverage.

---

## 8. Experimental Design

### 8.1 Seed splits and phases

We report results on two evaluation seed ranges:

- **Phase B1:** seeds 100–119 (20 runs)
- **Phase B2:** seeds 120–139 (20 runs)

(Additional seeds were used for event-density verification; total held-out evaluations reported here are 40 runs.)

### 8.2 FPR sweep

We sweep target FPR thresholds:

\[
\{0.01, 0.02, 0.05, 0.10, 0.15, 0.20\}.
\]

---

## 9. Results

### 9.1 E1 event density and early-warning window

Using the locked jump/regime-shift definition (E1):

- **Event density:** 100% of evaluated runs exhibit an event.
- **Early-warning window:** alarms that trigger successfully do so **~12–15k steps** before the jump (stable across runs), corresponding to roughly **24–30 checkpoints** under the current cadence.

This confirms Phase B is evaluable and the early-warning objective is non-trivial.

---

### 9.2 Phase A2: FPR–Coverage tradeoff reveals detector degeneracy

We evaluate the baseline score in both orientations under explicit FPR control.

#### Summary by seed range

| Seed Range | Score Sign | Target FPR Range | Achieved FPR | Coverage (raw) | Mean Lead Time (steps) |
|---|---:|---:|---:|---:|---:|
| 100–119 (B1) | -1 | 0.01–0.20 | **0.4407 (constant)** | **100%** | 18775 |
| 100–119 (B1) | +1 | 0.01–0.20 | 0.01–0.20 (tracks target) | 0% → 85% | 12071–14167 |
| 120–139 (B2) | -1 | 0.01–0.20 | **0.4442 (constant)** | **95%** | 18895 |
| 120–139 (B2) | +1 | 0.01–0.20 | 0.01–0.20 (tracks target) | 0% → 75% | 7250–15000 |

---

#### B1 (seeds 100–119): `score_sign = -1` is invalid (FPR floor)

```
Target FPR   Achieved FPR   Coverage   N Covered   Mean Lead Time
0.010        0.4407         100%       20/20       18775
0.020        0.4407         100%       20/20       18775
0.050        0.4407         100%       20/20       18775
0.100        0.4407         100%       20/20       18775
0.150        0.4407         100%       20/20       18775
0.200        0.4407         100%       20/20       18775
```

**Interpretation:** Achieved FPR cannot be reduced below ~0.44 regardless of threshold.  
Raw coverage is therefore meaningless under risk constraints. Under the protocol’s validity gate, this configuration is **invalid as an alarm**.

---

#### B1 (seeds 100–119): `score_sign = +1` is valid and exhibits a tradeoff

```
Target FPR   Achieved FPR   Coverage   N Covered   Mean Lead Time
0.010        0.0100         0%         0/20        N/A
0.020        0.0200         0%         0/20        N/A
0.050        0.0500         35%        7/20        12071
0.100        0.1000         70%        14/20       13071
0.150        0.1500         75%        15/20       14167
0.200        0.2000         85%        17/20       13588
```

Coverage roughly doubles when moving from FPR=0.05 to FPR=0.10, while lead time remains stable (~12–14k steps).

---

#### B2 (seeds 120–139): `score_sign = -1` is invalid (same FPR floor)

```
Target FPR   Achieved FPR   Coverage   N Covered   Mean Lead Time
0.010        0.4442         95%        19/20       18895
0.020        0.4442         95%        19/20       18895
0.050        0.4442         95%        19/20       18895
0.100        0.4442         95%        19/20       18895
0.150        0.4442         95%        19/20       18895
0.200        0.4442         95%        19/20       18895
```

Again, achieved FPR is insensitive to target threshold, indicating calibration degeneracy.

---

#### B2 (seeds 120–139): `score_sign = +1` remains valid with similar tradeoff

```
Target FPR   Achieved FPR   Coverage   N Covered   Mean Lead Time
0.010        0.0100         0%         0/20        N/A
0.020        0.0200         10%        2/20        7250
0.050        0.0500         35%        7/20        15357
0.100        0.1000         65%        13/20       11769
0.150        0.1500         70%        14/20       14857
0.200        0.2000         75%        15/20       15000
```

---

### 9.3 Practical operating points

For the only valid orientation (`score_sign = +1`):

| Target FPR | Coverage (B1) | Coverage (B2) | Average Coverage | Typical Lead Time |
|---:|---:|---:|---:|---:|
| 0.05 | 35% | 35% | 35% | ~12–15k steps |
| **0.10** | **70%** | **65%** | **67.5%** | **~12–14k steps** |
| 0.20 | 85% | 75% | 80% | ~13–15k steps |

**Recommendation (reporting):** Use **FPR=0.10** as a practical operating point in the main text while still reporting the full tradeoff curve in the appendix/supplement.

---

### 9.4 Why AUC is insufficient: ranking–alarm decoupling

The invalid configuration (`score_sign = -1`) can exhibit higher ranking metrics while being unusable as an alarm due to an FPR floor. This demonstrates a general principle:

> **In early-warning settings, ranking ability (AUC) is insufficient; controllable false-positive behavior is a necessary condition.**

---

### 9.5 Phase A1 component diagnosis (summary)

Component-level diagnosis indicates that seed dependence is partly explained by which component dominates:

- In seeds 100–119, the spectral-entropy-like component (H_spec) shows stronger directional association, which can inflate AUC for one orientation.
- In seeds 120–139, both components weaken substantially, producing near-random discrimination.

However, even when a component provides ranking signal, it can induce calibration failure (FPR floor), making the resulting alarm invalid.

---

## 10. Discussion

### 10.1 What would count as a validated hard indicator?

Under this protocol, a “hard indicator” should satisfy, on held-out evaluation:

1. **Evaluability:** events occur with sufficient density (non-zero).
2. **Validity:** achieved FPR tracks target; no FPR floor.
3. **Utility:** coverage is non-trivial at reasonable FPR (e.g., 0.05–0.10).
4. **Stability:** lead time is consistent and non-trivial.
5. **Robustness:** performance persists across seed ranges (and ideally boundaries).

Our baseline fails (2) in one orientation and is weak under strict low-FPR (0.05) even in the valid orientation.

### 10.2 Why this negative result is useful

This work clarifies why “hard indicators” are difficult:

- it is easy to produce scores with seemingly good AUC,
- but much harder to produce alarms that are usable under risk constraints.

The protocol turns this into a measurable, reproducible failure mode.

### 10.3 Limitations

- This manuscript studies a single boundary (modular addition, small transformer family).
- Indicator engineering is limited by the baseline tuple; we do not claim optimal features.
- Some quantities (e.g., representation-level measures) require heavier instrumentation.

### 10.4 Next steps (v0.4 direction)

- Develop calibration-first indicators (e.g., autocorrelation/variance-based early-warning proxies).
- Use multi-gate detectors (evidence aggregation) to reduce FPR floors.
- Expand Phase B to additional seed ranges and boundaries.

---

## 11. Reproducibility Appendix

### 11.1 Key artifacts

Runnable materials and paper-facing result tables are maintained in the FIT repository under:

- `experiments/grokking_hard_indicators_v0_2/`

(In this workspace, the same path may appear as `github/F-I-T/experiments/grokking_hard_indicators_v0_2/`.)

Key artifacts:

- `experiments/grokking_hard_indicators_v0_2/RESULTS_v0.2_v0.2.1.md` — consolidated tables for v0.2 and v0.2.1
- `experiments/grokking_hard_indicators_v0_2/results/v0.3_A1_component_diagnosis.md` — component-level diagnosis (Phase A1)
- `experiments/grokking_hard_indicators_v0_2/results/v0.3_A2_fpr_tradeoff.md` — FPR–coverage tradeoff sweeps (Phase A2)
- `experiments/grokking_hard_indicators_v0_2/code/protocol/estimator_spec.v0_2.yaml` — v0.2 prereg spec (Explore → Lock discipline)
- `experiments/grokking_hard_indicators_v0_2/code/protocol/estimator_spec.v0_2_1.yaml` — v0.2.1 fresh-seed eval spec
- `experiments/grokking_hard_indicators_v0_2/code/src/grokking/analysis/fpr_tradeoff_curves.py` — sweep implementation used to produce tradeoff tables

The full training logs are not embedded in this manuscript text; the repo experiment README documents how to regenerate runs and re-compute the tables from scratch.

### 11.2 Example reproduction commands

```bash
cd experiments/grokking_hard_indicators_v0_2

python -m venv .venv
source .venv/bin/activate
pip install -r code/requirements.txt
pip install -e code

# Phase B1 (seeds 100-119)
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0.2/eval --score_sign=+1
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0.2/eval --score_sign=-1

# Phase B2 (seeds 120-139)
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0.2_1/eval --score_sign=+1
python -m grokking.analysis.fpr_tradeoff_curves --runs_dir runs_v0.2_1/eval --score_sign=-1
```

If you do not have the archived `runs_v0.2*` directories, follow `experiments/grokking_hard_indicators_v0_2/README.md` to generate runs via `python -m grokking.runner.sweep`, then point `--runs_dir` at the resulting `runs/{explore,eval}` folders.

### 11.3 Reporting requirements (paper-facing)

Main text should include:

- Achieved FPR vs target FPR (validity)
- Coverage vs FPR and lead time vs FPR (utility)
- A clear statement that AUC/AP are insufficient for alarm usability

Supplement should include:

- full sweep tables
- seed-range breakdowns
- locked spec hashes/commits

---

## References

- Power, A., Burda, Y., Edwards, H., Babuschkin, I., Misra, V. (2022). *Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets.* arXiv:2201.02177.
- Scheffer, M., Bascompte, J., Brock, W. A., Brovkin, V., Carpenter, S. R., Dakos, V., Held, H., van Nes, E. H., Rietkerk, M., Sugihara, G. (2009). *Early-warning signals for critical transitions.* Nature, 461, 53–59.
- Dakos, V., Carpenter, S. R., van Nes, E. H., Scheffer, M. (2012). *Methods for Detecting Early Warnings of Critical Transitions in Time Series Illustrated Using Simulated Ecological Data.* PLoS ONE, 7(7), e41010.
- Fawcett, T. (2006). *An introduction to ROC analysis.* Pattern Recognition Letters, 27(8), 861–874.
- Davis, J., Goadrich, M. (2006). *The Relationship Between Precision-Recall and ROC Curves.* Proceedings of ICML.
