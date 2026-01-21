# Grokking Early Warning Experiment Results (v0.2 & v0.2.1)

**Date**: January 21, 2026  
**Task**: Modular addition (p=97), 2-layer transformer  
**Event Definition**: Jump events (`w_jump=2`, `delta_jump=0.04`, `theta_floor=0.85`)

This note records held-out evaluation outcomes for the v0.2 family. The primary event is **E1 (jump / regime shift)**.

## Summary of Findings

1. **Jump events** achieve **100% detection rate** across all 45 seeds (vs 60% for v0.1 plateau-based).
2. **Score polarity** has **seed-dependent effects**:
   - v0.2 seeds (100-119): `score_sign=-1` improves mean AUC by **+31.6%**.
   - v0.2.1 seeds (120-139): `score_sign=+1` achieves **35% coverage** at `FPR=0.05`.
3. **Hold-out validation** (v0.2.1) shows modest performance: mean AUC `0.503–0.507` (near random).

## Complete Results Table

### v0.2 Phase A (Explore): Seeds 0-4 (5 runs)

| Metric | Score Sign +1 | Score Sign -1 |
|--------|--------------|---------------|
| Grok Detection | 5/5 (100%) | 5/5 (100%) |
| ROC-AUC (pooled) | 0.524 | 0.524 |
| ROC-AUC (mean±std) | 0.427±0.245 | **0.548±0.228** |
| AP (mean±std) | 0.087±0.078 | **0.109±0.069** |
| Lead Time @ FPR=0.05 | 15750 steps | 15750 steps |

### v0.2 Phase B (Eval): Seeds 100-119 (20 runs)

| Metric | Score Sign +1 | Score Sign -1 |
|--------|--------------|---------------|
| Grok Detection | 20/20 (100%) | 20/20 (100%) |
| ROC-AUC (pooled) | 0.430 | 0.430 |
| ROC-AUC (mean±std) | 0.430±0.119 | **0.566±0.168** (+31.6%) |
| AP (mean±std) | 0.065±0.023 | **0.099±0.051** (+52.3%) |
| Lead Time @ FPR=0.05 | 12071 steps | NaN (no feasible low-FPR threshold; see v0.3-A2) |
| Coverage @ FPR=0.05 | 10/20 (50%) | 0/20 (0%) |

### v0.2.1 Phase B (Fresh Eval): Seeds 120-139 (20 runs)

| Metric | Score Sign +1 | Score Sign -1 |
|--------|--------------|---------------|
| Grok Detection | 20/20 (100%) | 20/20 (100%) |
| ROC-AUC (pooled) | 0.502 | 0.504 |
| ROC-AUC (mean±std) | **0.503±0.102** | 0.507±0.173 |
| AP (mean±std) | 0.075±0.022 | 0.089±0.056 |
| Lead Time @ FPR=0.05 | **15286 steps** | NaN (no feasible low-FPR threshold) |
| **Coverage @ FPR=0.05** | **7/20 (35%)** | **0/20 (0%)** |

## Key Observations

### 1. Event Detection Reliability

- **Jump events** detect grokking in **45/45 seeds (100%)** across all experiments.
- Much more reliable than v0.1 plateau-based detection (60% success rate).

### 2. Score Polarity is Seed-Dependent

- v0.2 seeds (100-119): `score_sign=-1` dramatically improves performance:
  - Mean AUC: `0.430 → 0.566` (+31.6%)
  - Mean AP: `0.065 → 0.099` (+52.3%)
- v0.2.1 seeds (120-139): `score_sign=+1` shows better operational utility:
  - Achieves 35% coverage at `FPR=0.05` (vs 0% for `score_sign=-1`)
  - More stable std (`0.102` vs `0.173` for AUC)

**Interpretation**: The optimal score polarity varies across seed ranges, suggesting the indicator's relationship to grokking onset is not universally consistent.

### 3. Hold-Out Performance

- v0.2.1 fresh evaluation seeds show **near-random performance**: AUC ≈ `0.50`.
- Suggests limited generalization of the detector beyond initial seed ranges.
- Coverage at `FPR=0.05` is only 35% (with the better orientation), meaning the alarm fires in only 7/20 runs.

### 3.1 Alarm feasibility (why `score_sign=-1` can yield coverage=0)

Follow-up diagnostics (v0.3 Phase A2) suggest the `score_sign=-1` orientation can enter a regime where **FPR cannot be controlled** (reported achieved FPR around `~0.44`), so no threshold satisfies `FPR ≤ 0.05`. In that case, the correct interpretation is:

- `score_sign=-1` may still improve ranking metrics (AUC/AP) within a seed block, but
- it is not usable as a strict low-FPR alarm (`FPR=0.05`) because the operating point is infeasible.

See: `results/v0.3_A2_fpr_tradeoff.md`.

Concrete numbers from the tradeoff sweep:

- Seeds `100–119`, `score_sign=-1`: minimum achievable FPR stays at `FPR≈0.4407` (an **FPR floor**), so strict targets like `0.05` are infeasible; at that floor the alarm covers `20/20` with lead `~18,775` steps.
- Seeds `120–139`, `score_sign=-1`: minimum achievable FPR stays at `FPR≈0.4442` (an **FPR floor**), so strict targets like `0.05` are infeasible; at that floor the alarm covers `19/20` with lead `~18,895` steps.
- Seeds `120–139`, `score_sign=+1`: at `FPR=0.05`, coverage `7/20`; at `FPR=0.10`, coverage `13/20`.

### 4. Lead Time Consistency

- When detectable, lead time is consistent: **~12–15k steps** before grokking.
- At `FPR=0.05`, this translates to an early warning window of ~`24–30` checkpoints (given `checkpoint_every_steps=500`).

## Implications

1. Jump-based events are more reliable for grokking detection than plateau-based thresholds.
2. Score polarity must be tuned per seed range (no universal “correct” sign).
3. Detector generalization is limited (new seeds show near-random discrimination).
4. Practical utility is unclear under strict low-FPR operation (35% coverage at `FPR=0.05`).

## Recommendations

1. For v0.3: investigate why score polarity effects vary across seed ranges.
2. Consider ensemble approaches or adaptive sign selection based on early behavior.
3. Explore alternative indicators that may generalize better to new seeds.
4. Consider less strict FPR targets (e.g., `0.10`) to improve coverage while maintaining utility.

## v0.3 Phase A (diagnosis addendum)

Two diagnostic notes were added after v0.2.1 to explain the observed behavior:

- **A1 (component diagnosis):** `results/v0.3_A1_component_diagnosis.md`
- **A2 (FPR tradeoff curves):** `results/v0.3_A2_fpr_tradeoff.md`

## Data Locations

- v0.2 Phase A: `runs_v0.2/explore/` (seeds 0-4, 5 runs)
- v0.2 Phase B: `runs_v0.2/eval/` (seeds 100-119, 20 runs)
- v0.2.1 Phase B: `runs_v0.2_1/eval/` (seeds 120-139, 20 runs)
- All runs retain `logs.jsonl` only (checkpoints deleted to save space).

## Reproduction Commands

```bash
# v0.2 evaluation with both signs
python -m grokking.analysis.evaluate_suite --runs_dir runs_v0.2/eval --event jump --score_sign=+1
python -m grokking.analysis.evaluate_suite --runs_dir runs_v0.2/eval --event jump --score_sign=-1

# v0.2.1 evaluation with both signs
python -m grokking.analysis.evaluate_suite --runs_dir runs_v0.2_1/eval --event jump --score_sign=+1
python -m grokking.analysis.evaluate_suite --runs_dir runs_v0.2_1/eval --event jump --score_sign=-1
```
