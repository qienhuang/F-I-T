# FIT-Explorer x World-Evolution v0.1

**Date**: 2026-01-27  
**What**: A repo-ready experimental design pack that uses FIT-Explorer to search for **effective variables** / **effective early-warning methods** in toy evolving worlds, under hard feasibility gates.

This pack includes:
- experiment design docs (micro->macro, coarse-graining, event definitions)
- search spaces (coarse-graining operators, detector pipelines)
- gates (monitorability-first feasibility)
- prereg + results schemas
- a runnable toy demo (stochastic majority CA) to generate traces and run a minimal constrained search

## Quick start (toy demo)

```bash
# 1) Generate traces (multiple runs)
python examples/world_evolution_demo/simulate.py --out out/world_evolution_demo/traces.jsonl

# 2) Run a minimal random search over detector candidates
python examples/world_evolution_demo/search.py --traces out/world_evolution_demo/traces.jsonl --outdir out/world_evolution_demo/search_run

# 3) Summarize results
python examples/world_evolution_demo/summarize.py --indir out/world_evolution_demo/search_run
```

Outputs:
- out/world_evolution_demo/search_run/leaderboard_feasible.csv
- out/world_evolution_demo/search_run/failure_map.yaml
- out/world_evolution_demo/search_run/run_log.jsonl

Notes:

- The default toy world starts from an ordered initial condition (init_p biased toward 1s) so a threshold-crossing macro-event can occur later under the noise schedule.
- The demo search space includes intentionally degenerate scores (const_*) so failure_map is non-empty and illustrates monitorability / FPR-control failure modes.

## How to integrate into your repo

Suggested placement:
- docs/world_evolution/
- docs/explorers/fit_explorer/
- reports/templates/
- examples/world_evolution_demo/ (optional demo)
