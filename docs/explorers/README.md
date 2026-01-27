# Explorers (specs + loop templates)

This folder contains **exploration specifications**: how to search a method/config space under explicit budgets and hard gates.

Explorers are **not** runnable engines by themselves. If you want runnable implementations, start from:
- [tools/README.md](../../tools/README.md)

---

## Design philosophy

FIT-Explorer is inspired by constrained architecture search (BioArc-style), but specialized to FIT/EST:

| Traditional search | FIT-Explorer |
|--------------------|--------------|
| Maximize metric (AUC, accuracy) | Feasibility-first (gate before rank) |
| Single "best" result | Leaderboard + failure map |
| Ad-hoc stopping | Preregistered budgets + Goodhart defense |

---

## Index

| Explorer | Purpose | Status |
|----------|---------|--------|
| [FIT-Explorer v0.1](fit_explorer/README.md) | Budgeted, auditable method search | repo-ready |

### Extensions

| Extension | Purpose | Docs |
|-----------|---------|------|
| [World-Evolution v0.1](../world_evolution/README.md) | Search effective variables in evolving worlds | docs/world_evolution/ |
| [Math-Discovery v0.1](../math_discovery/README.md) | Search representations/lemmas/strategies for proof | docs/math_discovery/ |

---

## Quick start (CPU)

Run the skeleton explorer:

```bash
python docs/explorers/fit_explorer/code/run_explorer.py \
  --config docs/explorers/fit_explorer/examples/non_llm_explorer_config.yaml \
  --out_dir out/fit_explorer_demo_run
```

Try the World-Evolution toy demo (traces -> search -> failure_map):

```bash
python examples/world_evolution_demo/simulate.py --out out/world_evolution_demo/traces.jsonl
python examples/world_evolution_demo/search.py --traces out/world_evolution_demo/traces.jsonl --outdir out/world_evolution_demo/search_run
python examples/world_evolution_demo/summarize.py --indir out/world_evolution_demo/search_run
```

## Relationship to other modules

```text
Explorers (specs) are organized into three parts:

- search_space  -> candidate variants (what can be tried)
- constraints   -> hard gates (what is admissible / monitorable)
- loop          -> evaluation protocol + artifacts (run_log / failure_map / leaderboard)

The gates and artifact formats are meant to be compatible with:
- GMB v0.4 (monitorability / operationality)
- EST (estimator discipline)
- EWBench-style governance executability checks
```

---

## Quick links

- Monitorability gate: [fit_explorer/constraints/monitorability_gate.md](fit_explorer/constraints/monitorability_gate.md)
- Skill admission: [fit_explorer/constraints/skill_admission_gate.md](fit_explorer/constraints/skill_admission_gate.md)
- Prereg template: [fit_explorer/loop/prereg_template.yaml](fit_explorer/loop/prereg_template.yaml)
- Results schema: [fit_explorer/loop/results_schema.yaml](fit_explorer/loop/results_schema.yaml)
