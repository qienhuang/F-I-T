# GMB v0.5 repair pilot: Repair A (seeds 140-143)

This folder contains a **small pilot** for a single "minimal repair" configuration on the grokking v0.5 hold-out setting.

## Scope

- Seeds: **140-143** (4 runs)
- Event: jump-style grokking target (same family as the v0.5 hold-out)
- Score: `score_sign = +1` (alarm-usable direction)
- Repair A: **stricter correction threshold** (`theta_corr = 0.75`)

This pilot is intended as a **sanity check** before running a full hold-out sweep; it is **not** a replacement for the full v0.5 hold-out evidence.

## What the artifacts show (pilot only)

See `tables/tradeoff_with_abstain.csv`:

- FPR is controllable at all target operating points tested (0.01 / 0.05 / 0.10 / 0.20).
- At `FPR=0.05` and `FPR=0.10`, coverage is `2/4` (50%) with abstain rate 50%.
- Mean lead time for the covered runs is `12250` steps (at `FPR=0.05/0.10/0.20`).

Diagnostics are in `tables/diagnostics_per_run.csv` and summarized in `tables/summary.json` (effective-n collapse remains present).

## How to interpret

- Treat all numbers here as **pilot estimates** (n=4).
- Any apparent improvement vs the full hold-out must be confirmed by running a larger hold-out slice (ideally the same 140-179 range used in the baseline hold-out report).

## Files

- `tables/tradeoff_with_abstain.csv`
- `tables/diagnostics_per_run.csv`
- `tables/summary.json`

