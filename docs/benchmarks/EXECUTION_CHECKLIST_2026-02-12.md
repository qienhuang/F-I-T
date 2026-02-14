# Execution Checklist (2026-02-12)

This file tracks the minimum next actions for benchmark progression without duplicating completed work.

## 0. Locked Results (do not rerun)

- `AFDB B1 (N~1000)`: `COHERENT`
- `AFDB B2 (N~100 and N~1000)`: `ESTIMATOR_UNSTABLE` with persistent `C3_msa_deficit` event-bin disagreement vs `C1/C2`
- `AFDB B2 split-stability (3 splits, N~1000)`: offset `[6, 6, 6]` confirmed structural channel mismatch
- `Dr.One v0.2 matrix`: 80/80 runs complete, "gating useful" and "gating redundant" regimes both demonstrated
- `GMB v0.5 holdout`: low-FPR utility tradeoff established (`0.05 -> 41%`, `0.10 -> 56%`, `0.20 -> 74%`)

## 1. GPU Queue (priority)

### 1.1 ~~Finish `M=199` pilot~~ DONE

- Output root: `experiments/li2_scaling_law/results/beta_multiseed_v5_M199_pilot/`
- Result: `r_crit` localized to `(0.30, 0.32]` with pilot outcome `0/2@0.30`, `2/2@0.32`

### 1.2 Next decision: `M=199` full-grid expansion

- Optional if publication needs a fully fitted fifth point:
  - expand to full ratio grid and 3+ seeds to compute stable beta/R^2 fit
- Otherwise keep current pilot as boundary-localization evidence and stop here

### 1.3 Documentation after completion

- Update `docs/benchmarks/li2_cross_m_summary.md`
- Add one line to `docs/benchmarks/README.md` with new `M=199` status

## 2. CPU Queue (parallel)

### 2.1 AFDB sign-aware follow-up (high value)

Goal: test whether B2 disagreement is structural sign/phase mismatch rather than random instability.

- Keep boundary fixed (`B2_COORD_PLUS_PAE_PLUS_MSA`)
- Add sign-aware reporting per channel pair:
  - `rho_signed`
  - `abs(rho)`
  - event-bin offset (`|bin_i - bin_j|`)
- Pass criterion for "structural mismatch" label:
  - stable nonzero offset across sample sizes and splits

### 2.2 ~~AFDB split-stability check~~ DONE

- ~~Re-run B2 with 2-3 deterministic accession splits at same `N`~~
- ~~Compare event-bin offsets and verdict consistency~~
- Result: offset `[6, 6, 6]` across splits a/b/c. Structural mismatch confirmed.

### 2.3 Optional: scRNA estimator-family extension

- Add one additional explicit-stage dataset only if no AFDB blocker remains
- Keep same gate semantics; avoid adding new verdict labels

## 3. Decision Gates

- Li2 benchmark is promotable now for `r_crit(M)` monotonicity; full `M=199` beta fit remains optional
- ~~Promote AFDB B2 claim only after split-stability confirms persistent event-bin offset~~ GATE PASSED: offset stable at 6 across 3 splits
- Do not run new repair sweeps for GMB until a non-monotonic score-family change is specified

## 4. Quick Status Commands

```powershell
# active Python jobs
Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' } |
  Select-Object ProcessId,Name,CommandLine

# check Li2 pilot outputs
Get-ChildItem "experiments/li2_scaling_law/results/beta_multiseed_v5_M199_pilot/M199/experiments" -ErrorAction SilentlyContinue

# check AFDB B2 artifacts
Get-ChildItem "experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes" -Recurse -Filter "*B2*" | Select-Object FullName
```
