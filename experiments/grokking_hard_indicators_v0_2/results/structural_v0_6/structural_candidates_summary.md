# Structural Candidate Summary (v0.6)

- task: modular-addition grokking hard-indicator screening on held-out seeds 140–179
- comparison rule: pick the score sign with better low-FPR coverage for each candidate, then compare against the fixed control run
- source: `D:/FIT Lab/grokking/runs_v0_6_structural/*/eval_summary_sign_{pos1,neg1}.md`

## Preferred-sign comparison

| Candidate | Preferred sign | median AUC | mean AUC | median AP | lead@FPR seeds | lead rate | median lead steps | Delta median AUC vs control | Delta lead rate vs control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Control | +1 | 0.4546 | 0.4354 | 0.0597 | 17/40 | 0.4250 | 11500 | 0.0000 | 0.0000 |
| Candidate A | +1 | 0.5874 | 0.5965 | 0.0793 | 30/40 | 0.7500 | 15250 | 0.1328 | 0.3250 |
| Candidate B | -1 | 0.3871 | 0.3965 | 0.0553 | 12/40 | 0.3000 | 9000 | -0.0675 | -0.1250 |
| Candidate C | +1 | 0.5969 | 0.6444 | 0.0799 | 24/40 | 0.6000 | 14750 | 0.1423 | 0.1750 |

## Sign-level detail

| Candidate | sign | median AUC | mean AUC | median AP | lead rate | median lead steps |
|---|---:|---:|---:|---:|---:|---:|
| Control | +1 | 0.4546 | 0.4354 | 0.0597 | 0.4250 | 11500 |
| Control | -1 | 0.5417 | 0.5901 | 0.0742 | 0.0000 | NA |
| Candidate A | +1 | 0.5874 | 0.5965 | 0.0793 | 0.7500 | 15250 |
| Candidate A | -1 | 0.4049 | 0.4031 | 0.0569 | 0.0000 | NA |
| Candidate B | +1 | 0.6129 | 0.6038 | 0.0827 | 0.2000 | 19000 |
| Candidate B | -1 | 0.3871 | 0.3965 | 0.0553 | 0.3000 | 9000 |
| Candidate C | +1 | 0.5969 | 0.6444 | 0.0799 | 0.6000 | 14750 |
| Candidate C | -1 | 0.4031 | 0.3556 | 0.0539 | 0.0000 | NA |

## Readout

- Control preferred sign is `+1` with median AUC `0.4546` and lead rate `0.4250`.
- Candidate verdicts are not auto-assigned here. This artifact is a screening summary for deciding whether any structural candidate meaningfully improves low-FPR usefulness over the control family.
