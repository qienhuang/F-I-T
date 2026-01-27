# Candidate schema (FIT-Explorer v0.1)

A **candidate** is a concrete, runnable configuration.  
It can represent either:

1) a **detector pipeline** (monitorability / early-warning), or  
2) an **agent governance configuration** (authority / skills / ingestion).

All candidates must declare:

- boundary scope,
- estimator tuple (where relevant),
- admissible parameter ranges,
- and the target evaluation protocol.

---

## 1) Canonical fields

```yaml
candidate_id: "det:hc_tauL_p90_w200_v1"
type: "detector"  # detector | agent_config
version: "1.0.0"

boundary:
  system: "grokking"
  event: "E_jump"
  negative_window: "t <= t* - delta_safe"
  positive_window: "t* - H_pos <= t < t*"

estimators:
  score_family: "hierarchical_convergence"
  score_definition: "HC-1 tau_L p90"
  window_W: 200
  smoothing: 0.10

gates:
  monitorability:
    fpr_targets: [0.01, 0.05, 0.10]
    eps: 0.01
    floor_max: 0.20
    min_targets_ok: 2

utility:
  operating_points: [0.05, 0.10]
  lead_time_target: 200

robustness:
  seed_set_eval: [1001, 1002, 1003]
  window_sweep: [150, 200, 250]

budget:
  max_runs: 20
  max_steps_per_run: 20000

output:
  results_schema: "loop/results_schema.yaml"
```

---

## 2) Notes

- `candidate_id` should be stable and content-addressable (recommended: include key params).
- A change in boundary is a new candidate class (no post-hoc boundary edits).
- "Explore" can generate candidates automatically; "Lock" freezes a subset for evaluation.

