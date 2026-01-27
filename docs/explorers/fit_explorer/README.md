# FIT-Explorer v0.1 (Repo-ready Pack)
*A budgeted, auditable, constraint-driven explorer that turns FIT/EST into a method search engine.*

**Status**: repo-ready draft (v0.1)  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0

---

## What this is

**FIT-Explorer** searches a **method space** under **hard gates**.

It is inspired by constrained architecture search (BioArc-style), but specialized to FIT/EST:

- Search objects: detector pipelines and governance configurations
- Hard gates: monitorability (FPR controllability), skill admission, ingestion boundaries
- Output: feasible leaderboard + failure map (not just "best score")

---

## Directory structure

```text
docs/explorers/fit_explorer/
  README.md
  code/
    run_explorer.py
    fit_failure_model.py
  examples/
    non_llm_explorer_config.yaml
  search_space/
    detectors.yaml
    agent_configs.yaml
    candidate_schema.md
  constraints/
    monitorability_gate.md
    skill_admission_gate.md
    web_ingestion_boundary.md
  loop/
    fit_synth_loop.md
    budget_policy_v0.1.md
    failure_map_model_v0.1.md
    non_llm_runner_v0.1.md
    prereg_template.yaml
    results_schema.yaml
  results/
    failure_map_v0.1.yaml
    leaderboard_feasible_v0.1.csv
```

---

## How to use (minimal)

Run the non-LLM skeleton explorer:

```bash
python docs/explorers/fit_explorer/code/run_explorer.py \
  --config docs/explorers/fit_explorer/examples/non_llm_explorer_config.yaml \
  --out_dir out/fit_explorer_demo_run
```

If you do not have PyYAML installed:

```bash
python -m pip install pyyaml
```

Then inspect:

- `out/fit_explorer_demo_run/run_log.jsonl`
- `out/fit_explorer_demo_run/leaderboard.csv`
- `out/fit_explorer_demo_run/failure_map.yaml`

---

## Related entry points

- Synthesis discipline (failure labels -> admissible actuators -> prereg -> gates): `docs/est/synthesis_playbook_v0.1.md`
- Monitorability boundary (why AUC can be insufficient under low-FPR): `docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md`

---

## Notes on `results/` in this pack

The files under `results/` are illustrative placeholders for explorer outputs. They are not new empirical claims.

