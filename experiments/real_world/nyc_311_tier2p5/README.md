# NYC 311 (Tier-2.5) - Tempo mismatch + backlog drift (preregistered demo)

## Scope & Claims Notice

This artifact illustrates how the FIT framework can be *applied* under a specific estimator choice and real-world dataset.

It does **not** constitute:
- proof of FIT,
- validation of universal claims,
- or generalization beyond the stated scope.

Any observed behavior is conditional on the chosen estimators, the dataset boundary, and the preregistered configuration. This artifact should be interpreted as an *example of use*, not as theoretical evidence.

---

This folder is a **Tier-2.5** real-world demonstration for FIT: use a high-volume public "governance loop" dataset (NYC 311) to test a **narrow, preregistered** claim about **tempo mismatch** and loss of corrective capacity.

It is **not** a claim that FIT is "validated in the real world". It is a bridge: **auditable metrics + explicit boundaries + success/failure criteria** under real noise.

## What we test (one hard question)

When governance/evaluation closes slower than changes arrive, backlog becomes harder to unwind.

Operationalized in NYC 311:
- "Updates" ~= incoming requests (arrivals)
- "Governance closure" ~= request closure
- "Loss of corrective capacity" ~= backlog drift

The prereg defines a mismatch ratio $ \rho $ and tests whether sustained $ \rho > 1 $ is associated with **positive forward backlog drift** under a fixed boundary.

## Artifacts

- Pre-registration (v1): `prereg.yaml`
- Pre-registration (v2): `prereg_v2.yaml`
- Pre-registration (v3, recommended): `prereg_v3.yaml` (PRIMARY config: `W=14`, `H=14`)
- Scripts (run locally): `scripts/compute_311_metrics.py`
- Decision-maker figure helper: `scripts/plot_decision_view.py`
- Sample data (so scripts run without downloads): `data/sample_311.csv`

## How to run (sample, no network)

From repo root:

`python experiments/real_world/nyc_311_tier2p5/scripts/compute_311_metrics.py --outdir experiments/real_world/nyc_311_tier2p5/outputs/_smoketest --window 14 --horizon 14`

Outputs:
- `experiments/real_world/nyc_311_tier2p5/outputs/_smoketest/metrics_daily.csv`
- `experiments/real_world/nyc_311_tier2p5/outputs/_smoketest/overview.svg` (always)
- `experiments/real_world/nyc_311_tier2p5/outputs/_smoketest/overview.png` (only if `matplotlib` is installed)
- `experiments/real_world/nyc_311_tier2p5/outputs/_smoketest/run_diagnostics.md` (always)
- `experiments/real_world/nyc_311_tier2p5/outputs/_smoketest/run_diagnostics.json` (always)

Diagnostics note:
- For preregistered H1-style checks, use `sustained_event_days_paired` from `run_diagnostics.*` (event days after intersecting with days where `drift_norm` is defined). If `overlap_days = 0`, H1 is **INCONCLUSIVE** under the declared boundary.

Notes:
- Default `--rho-mode` is `window_normalized` (matches `prereg_v3.yaml`, recommended).
- To reproduce the older v1 scaling (`tau_u(t)=1/max(A_t,1)`), run with `--rho-mode per_ticket` (matches `prereg.yaml`).
- In `prereg_v3.yaml`, only the PRIMARY config (`W=14, H=14`) is used for interpretation; other `(W,H)` runs are sensitivity checks and must be reported if run.

## Boundary sanity-check (recommended before interpretation)

If you are using a created-date boundary, run this first to avoid misreading "arrivals=0" and long closure tails:

`python experiments/real_world/nyc_311_tier2p5/scripts/sanity_check_311_boundary.py --created-start 2024-01-01 --created-end 2024-12-31`

## A simpler figure for decision-makers (rho + backlog only)

After you run `compute_311_metrics.py`, you can generate a 2-panel decision-view figure:

`python experiments/real_world/nyc_311_tier2p5/scripts/plot_decision_view.py --metrics experiments/real_world/nyc_311_tier2p5/outputs/_smoketest/metrics_daily.csv --outdir experiments/real_world/nyc_311_tier2p5/figures --created-end 2024-12-31`

Notes:
- The shaded intervals in `decision_view.*` are **illustrative only** (not part of prereg inference).
- The vertical `created_end` marker makes it clear when arrivals become zero by construction, while closures may continue (tail period).

## How not to misread the plots (important)

This demo uses a **created-date boundary** by design.

That implies a simple but easy-to-miss fact:

- After `created_end`, **arrivals must drop to zero** (because we are no longer counting newly created requests).
- Closures can still occur after `created_end` (because requests created before the boundary can close later).

So if you see "arrivals=0 for a long time" or "median close lag spikes in 2025", that is **not** enough to claim:
- the NYC 311 data stream broke, or
- the agency stopped working, or
- the system entered collapse.

Those may be true in reality, but they require a different analysis with boundaries that keep counting arrivals (e.g., an extended created-date range, or an alternative boundary defined on close events).

**What this demo is for**
- Treat the metrics as a **monitoring lens** for tempo mismatch and backlog dynamics under explicitly declared boundaries.
- Demonstrate the FIT discipline: preregistered estimators, explicit boundary markers, and conservative interpretation (including negative results).

**If you want to test "real outage vs boundary artifact"**
Run a follow-up with:
- a created-date range that includes the period you want to diagnose (e.g., full 2025), and/or
- a breakdown by complaint type / geography to detect localized effects.

## How to run (real dataset)

1. Download NYC 311 data as CSV from NYC Open Data (manual export) and put it at:
   - `experiments/real_world/nyc_311_tier2p5/data/raw/nyc_311.csv`
2. Run:
   - `python experiments/real_world/nyc_311_tier2p5/scripts/compute_311_metrics.py --input experiments/real_world/nyc_311_tier2p5/data/raw/nyc_311.csv --created-start 2024-01-01 --created-end 2024-12-31 --agency \"Housing Preservation and Development\" --top-k-types 10 --plot-tail-days 60 --window 14 --horizon 14`

Notes:
- Do **not** edit the prereg after looking at results. If you need changes, create a new prereg file (e.g., `prereg_v4.yaml`) and record the reason.
- Keep the boundary tight (single agency / top complaint types) to avoid "explaining everything".
- If you use a created-date boundary, prefer `--plot-tail-days 60` to keep closure tails from dominating the figure; the full metrics are still in `metrics_daily.csv`.
