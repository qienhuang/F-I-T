# Prereg Template (Grokking Hard Indicators v0.1)

## 1) Scope / Boundary

- Task: modular addition (`(a+b) mod p`)
- `p`:
- Dataset sizes:
- Model family + size:
- Optimizer + LR + weight decay:
- Max steps:

## 2) Grok Event Definition (LOCKED)

Define `t_grok` as the first checkpoint time `t` such that:

- `test_acc(t..t+K_g-1) >= theta_grok`
- where checkpoints are recorded every `checkpoint_every_steps`

Record:

- `theta_grok`:
- `K_g`:

## 3) Indicators (Estimator Tuple) (LOCKED AFTER PHASE A)

- Which matrices for `H_spec` / `r_eff`:
- Window `W` for moving average deltas:
- Score definition:
- Thresholding policy (if any):

## 4) Phase Discipline

### Phase A (Exploratory; NOT evidence)

- Seeds:
- Allowed changes:
- Lock criteria:

### Phase B (Evaluation; Evidence)

- Seeds:
- Forbidden changes:

## 5) Metrics

Primary:

- ROC-AUC for predicting “grok within next N steps”
- Average Precision (same label)
- Mean lead time @ fixed FPR (e.g. 5%)

Secondary:

- `|t_pred - t_grok| / t_grok` (only after primary is stable)

## 6) Failure Taxonomy (must log)

- FP sources:
- FN sources:
- “No grok” handling:

