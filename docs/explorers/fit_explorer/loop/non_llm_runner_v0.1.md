# Non-LLM Explorer Runner v0.1 (FIT-Explorer add-on)
*A deterministic, auditable runner for budgeted constrained exploration - without LLM dependence.*

**Status**: repo-ready draft  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0

---

## 0) Purpose

This add-on specifies how to run **FIT-Explorer** with **non-LLM** components as the primary engine:

- Candidate generation: random / grid / bandit / ES
- Feasibility gates: deterministic metric computation (FPR controllability, floors)
- Budget policy: successive halving / multi-stage gating
- Failure-map learning: small supervised models (tree/GBDT) over the run log

LLM is optional and should be used only for:

- proposing new feature families
- drafting skills (still subject to Skill Admission Gate)
- summarizing failure maps

---

## 1) Separation of concerns

### 1.1 What must be non-LLM (hard rules)

- Gate evaluation (FPR controllability, floor checks)
- Utility metrics (coverage@FPR, lead time)
- Robustness metrics (pass rate, flip rate)
- Logging + provenance + prereg compliance

### 1.2 Where LLM may help (optional)

- Suggest new families and "actuators" (legal mutations)
- Explain learned failure boundaries
- Generate initial skill skeletons (must pass admission gates)

---

## 2) Budgeted multi-stage evaluation (recommended)

Use 3 stages to avoid wasting compute on infeasible candidates:

### Stage S0 - cheap pre-check

- Effective negative support size (binned entropy)
- Tie/cluster dominance near top quantiles
- Quick floor suspicion test (coarse threshold sweep)

Output: `S0_PASS` or `FPR_FLOOR_SUSPECTED`.

### Stage S1 - gate evaluation (hard feasibility)

- Achieved-vs-target FPR table
- No hard floor

Output: `GATE_PASS` or `RANK_ONLY`.

### Stage S2 - utility + robustness

Only for `GATE_PASS` candidates:

- coverage@FPR
- lead time distribution
- seed stability

Output: `SUPPORTED_FOR_ALARM` or `PARTIAL/SCOPE_LIMITED`.

---

## 3) Candidate generation modes

Non-LLM generator options (ordered by simplicity):

1) Random search (baseline)
2) Grid search (small spaces)
3) Successive Halving / Hyperband (budget-aware)
4) Evolutionary strategies (CMA-ES / regularized evolution)
5) Bandits (treat families as arms)
6) Surrogate-guided sampling (fit a model to failure labels)

All modes MUST write:

- candidate_id
- parameter dict
- boundary scope
- prereg lock record
- evaluation outputs

---

## 4) Output artifacts (minimum)

- `out_dir/run_log.jsonl` (append-only)
- `out_dir/failure_map.yaml` (region -> label -> evidence; may start as counts-only)
- `out_dir/leaderboard.csv` (feasible candidates ranked by utility)
- `out_dir/prereg/` (one prereg lock file per evaluated candidate)

---

## 5) Minimal run (skeleton)

From the repo root:

```bash
python docs/explorers/fit_explorer/code/run_explorer.py \
  --config docs/explorers/fit_explorer/examples/non_llm_explorer_config.yaml \
  --out_dir out/fit_explorer_demo_run
```

If you do not have PyYAML installed:

```bash
python -m pip install pyyaml
```

---

## 6) Integration point

This runner expects the FIT-Explorer schemas:

- `docs/explorers/fit_explorer/loop/prereg_template.yaml`
- `docs/explorers/fit_explorer/loop/results_schema.yaml`

and writes outputs in a compatible structure. The current runner is intentionally minimal and should be extended with domain-specific evaluation code.

