# GMB v0.5 repairs: Repair A vs Repair B (pilot, seeds 140-143)

This note compares two "minimal repair" configurations on the same small pilot slice (seeds 140-143, n=4). It is **not** a replacement for the full v0.5 hold-out evidence.

## What changed

- Repair A: stricter correction threshold (`theta_corr = 0.75`)
- Repair B: reduced correction weight + higher eps_hspec (`w_corr = 0.5`, `eps_hspec = 0.005`)

## Key finding (pilot)

On this pilot slice, Repair A and Repair B are indistinguishable in the main alarm-operating metrics:

- Both are **FPR-controllable** at targets 0.01 / 0.05 / 0.10 / 0.20.
- Coverage is `2/4` (50%) at `FPR=0.05` and `FPR=0.10`.
- Mean lead time (covered runs) is `12250` steps at `FPR=0.05/0.10/0.20`.

The primary difference is the **raw score scale** (the selected thresholds differ). This is expected when adjusting score-component weights without changing score ordering: ranking metrics and operating-point outcomes can remain unchanged under monotone rescaling.

## Operating point table (pilot)

From each run folder's `tables/tradeoff_with_abstain.csv`:

| FPR target | Coverage | Abstain | Lead time (mean, steps) |
|---:|---:|---:|---:|
| 0.01 | 0/4 | 1.00 | - |
| 0.05 | 2/4 | 0.50 | 12250 |
| 0.10 | 2/4 | 0.50 | 12250 |
| 0.20 | 2/4 | 0.50 | 12250 |

## Files

- Repair A: `../run_grokking_v0_5_repairA_pilot_140_143/tables/`
- Repair B: `../run_grokking_v0_5_repairB_pilot_140_143/tables/`
