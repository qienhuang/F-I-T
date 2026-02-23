# Self-Reference Recoverability Experiment (v0.1)

Prereg-ready scaffold for testing recoverable self-reference in a synthetic agent loop.

## What this is

- A structural experiment about self-reference, memory writeback, lock-in, and recoverability.
- EST-aligned: explicit boundary, perturbation protocol, coherence/monitorability style outputs.

## What this is not

- Not a claim about subjective consciousness.
- Not a real-world safety benchmark yet.

## Groups

- `G0` baseline: self-writeback enabled, no control.
- `G1` no-writeback: self-writeback disabled.
- `G2` controlled window: self-writeback enabled, but control pauses unsafe actions and writeback after lock-in trigger.

## Core metric

Recoverability score:

`R = P_recover * exp(-lambda*T_recover) * exp(-mu*D_drift)`

Where:
- `P_recover`: recovery success rate
- `T_recover`: mean recovery time
- `D_drift`: memory drift depth after perturbation

## Run

```powershell
cd experiments/self_reference_recoverability_v0_1
python -m pip install -r requirements.txt
python run_pipeline.py --prereg EST_PREREG.yaml
```

## Outputs

- `outputs/episodes.csv`
- `outputs/episode_summary.csv`
- `outputs/recoverability_summary.json`
- `outputs/monitorability_tradeoff.csv`
- `outputs/report.md`
- `RESULTS.md` (repo-safe summary snapshot)

## Suggested next step

If this toy run is stable, mirror the same prereg structure into a tool-using local-agent environment and replace synthetic state channels with real logs.
