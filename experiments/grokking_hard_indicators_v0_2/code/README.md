# grokking-fit (code)

This folder is the runnable code for `experiments/grokking_hard_indicators_v0_2/`.

Quick smoke run (not evidence):

```bash
python -m grokking.runner.train --spec protocol/estimator_spec.dev.yaml --out ../runs/dev --seed 0
python -m grokking.analysis.evaluate_detector --run ../runs/dev/seed_0 --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 3
```

