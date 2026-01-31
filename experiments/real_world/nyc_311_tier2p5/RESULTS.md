# NYC 311 Tier-2.5 / P5 - Results Summary (EST-gated)

This file summarizes the repo-safe Tier-2.5 results for NYC 311 Service Requests (HPD, 2024) under EST discipline.
It is a pointer-rich results page: quick conclusion first, then auditable artifacts.

Key rule: **interpretation is gated by coherence**. Inconclusive results are preserved as first-class outcomes.

## One-sentence result

The coherence gate **passes** (Spearman rho = 0.234 > 0.2), confirming that backlog changes (dB_t) and forward drift_norm are directionally coherent under the preregistered estimator family. However, the H1 hypothesis test is **INCONCLUSIVE** because sustained tempo-mismatch events (rho > 1 for W days) only occur in the tail period (2025) where drift_norm is undefined by construction.

## Objective (what this result does and does not try to do)

This Tier-2.5 case evaluates a narrow question:

> Under a fixed created-date boundary, is sustained tempo mismatch (governance closure slower than arrivals) associated with positive forward backlog drift?

The goal is not to "validate FIT" but to demonstrate the framework discipline: preregistered estimators, explicit boundaries, and conservative interpretation (including negative/inconclusive results).

## Boundary (what is in scope)

- Dataset: NYC 311 Service Requests (HPD = Housing Preservation and Development)
- Time: 2024-01-01 .. 2024-12-31 (created-date boundary)
- Complaint types: top 10 within HPD
- Closure tail: extends to 2025-10-14 (348 days after created_end)

## Result table (coherence and H1 outcomes)

### Primary Run (v3, W=14, H=14)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Coherence (Spearman rho) | 0.234 | >= 0.2 | **PASS** |
| Coherence sign | +1 | - | Positive (expected) |
| Label | OK_TO_INTERPRET | - | Coherence gate passed |

### H1 Hypothesis Test (tempo mismatch -> backlog drift)

| Metric | Value | Threshold | Notes |
|--------|-------|-----------|-------|
| n_event (sustained rho > 1, paired) | 0 | >= 10 | Events occur in tail only |
| n_non_event (paired) | 366 | - | Full 2024 boundary |
| median(drift_norm \| event) | undefined | - | No paired events |
| median(drift_norm \| non_event) | 0.0091 | - | - |
| delta | undefined | >= 0.05 | - |
| **H1 Status** | **INCONCLUSIVE** | - | Boundary artifact (see below) |

### Why INCONCLUSIVE (not a data problem)

The created-date boundary creates a structural constraint:

1. **drift_norm(t; H)** is only defined for days within the created window where the forward horizon H exists. For 2024 data with H=14, drift_norm is defined for 2024-01-01 to 2024-12-17 (366 days).

2. **Sustained tempo mismatch events** (rho > 1 for W=14 consecutive days) only occur in the tail period (2025-01-24 to 2025-10-03), after the created_end boundary.

3. This is expected behavior: after created_end, arrivals drop to zero by construction, so rho = tau_g / W can become very large even with normal governance latency.

The overlap between "days where drift_norm is defined" and "days where sustained events occur" is **zero**. This is a boundary artifact, not a measurement failure.

**Interpretation**: The H1 test cannot be evaluated under this boundary. To test H1 properly, one would need either:
- A longer created-date range that captures mismatch events within the evaluation window, or
- A different boundary definition (e.g., close-date-based)

## Integrity checks

| Check | Result | Threshold | Notes |
|-------|--------|-----------|-------|
| Longest zero-run (arrivals) within created window | 4 days | ≤ 7 days | **PASS** |
| Longest zero-run (closures) over full series | 16 days | - | Diagnostic only |

## Estimator family (the hard contract)

The core result above uses the cost-family constraint pair defined in prereg_v3.yaml:

- **C_hat primary**: B_t (backlog level)
- **C_hat secondary**: drift_norm(t; H) = (B_{t+H} - B_t) / sum_{i=t..t+H} A_i
- **Tempo mismatch**: rho(t) = median_W(tau_g) / W (window-normalized)

Coherence is measured as Spearman correlation between dB_t (daily backlog change) and drift_norm(t; H) over paired days.

## Archived artifacts (repo-safe)

All artifacts below are small and auditable without shipping raw 311 data.

### Primary run (v3, W=14, H=14)
- `outputs/run003_v3_W14_H14/metrics_daily.csv`
- `outputs/run003_v3_W14_H14/overview.svg`
- `outputs/run003_v3_W14_H14/overview.png`
- `outputs/run003_v3_W14_H14/run_diagnostics.json`
- `outputs/run003_v3_W14_H14/run_diagnostics.md`

### Decision-view figure
- `figures/run003_v3_W14_H14/decision_view.svg`
- `figures/run003_v3_W14_H14/decision_view.png`

Each archive contains:
- `metrics_daily.csv` (daily time series: arrivals, closures, backlog, rho, drift_norm, event flags)
- `overview.*` (multi-panel diagnostic plot)
- `run_diagnostics.*` (machine-readable coherence status and counts)

## Interpretation rules (EST-compliant)

- If coherence gate passes, the estimator family is valid at this scope.
- If H1 is INCONCLUSIVE due to boundary constraints, report this as a structural limitation (not a theory failure).
- "INCONCLUSIVE" is preserved as a diagnostic signal of boundary constraints, not erased by re-framing.
- Do not interpret tail-period artifacts (arrivals=0 after created_end) as system failures.

## Reproduce (local)

```bash
cd experiments/real_world/nyc_311_tier2p5

# Primary run (W=14, H=14)
python scripts/compute_311_metrics.py \
  --input data/raw/nyc_311_hpd_2024.csv \
  --created-start 2024-01-01 \
  --created-end 2024-12-31 \
  --agency "Housing Preservation and Development" \
  --top-k-types 10 \
  --window 14 \
  --horizon 14 \
  --outdir outputs/run003_v3_W14_H14

# Decision-view figure
python scripts/plot_decision_view.py \
  --metrics outputs/run003_v3_W14_H14/metrics_daily.csv \
  --outdir figures/run003_v3_W14_H14 \
  --created-end 2024-12-31
```

## Comparison to TLC case

| Aspect | NYC TLC (Tier-2) | NYC 311 (Tier-2.5) |
|--------|------------------|-------------------|
| Coherence gate | FAIL pooled, PASS windowed | **PASS** |
| H1/P11 interpretable? | Yes (within windows) | **INCONCLUSIVE** (boundary) |
| Boundary issue | Level shifts across COVID | Events in tail only |
| Key insight | Windowing rescues coherence | Created-date boundary limits H1 scope |
