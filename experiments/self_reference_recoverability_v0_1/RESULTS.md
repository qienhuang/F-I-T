# Self-Reference Recoverability Results (v0.1)

Run status: completed (local run on 2026-02-16)  
Protocol: `EST_PREREG.yaml`  
Scope: synthetic boundary only (not a real-agent benchmark)

## Main table

| Group | R | P_recover | T_recover_mean | D_drift_mean | Lock-in rate | Non-recovered rate |
|---|---:|---:|---:|---:|---:|---:|
| G0 (baseline) | 0.0158 | 0.305 | 61.07 | 57.91 | 0.840 | 0.695 |
| G1 (no self-writeback) | 0.6401 | 1.000 | 22.31 | 0.00 | 0.000 | 0.000 |
| G2 (controlled window) | 0.1583 | 0.760 | 49.79 | 19.11 | 0.835 | 0.240 |

## Key observations

1. Removing self-writeback (`G1`) removes lock-in in this toy boundary and maximizes `R`.
1. Controlled window (`G2`) reduces non-recovery vs baseline but does not reduce lock-in onset rate in this configuration.
1. Detector monitorability is usable in `G0` and `G2` at practical FPR points; `G1` has no positive class (`n_pos=0`), so coverage is not meaningful there.

## Monitorability snapshot (`FPR target = 0.05`)

| Group | FPR achieved | Coverage | n_pos | n_neg |
|---|---:|---:|---:|---:|
| G0 | 0.066 | 0.885 | 139 | 61 |
| G1 | 0.300 | 0.000 | 0 | 200 |
| G2 | 0.053 | 0.729 | 48 | 152 |

## Reproduce

```powershell
cd experiments/self_reference_recoverability_v0_1
python -m pip install -r requirements.txt
python run_pipeline.py --prereg EST_PREREG.yaml
```

Expected output files:

- `outputs/episodes.csv`
- `outputs/episode_summary.csv`
- `outputs/recoverability_summary.json`
- `outputs/monitorability_tradeoff.csv`
- `outputs/report.md`

