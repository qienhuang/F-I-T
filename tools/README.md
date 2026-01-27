# Toolkits (runnable, non-LLM building blocks)

This folder contains small, **CPU-first** and **reproducible** toolkits that implement FIT discipline (including Estimator Selection Theory, EST):

- **Locked boundary / prereg** (what is in-scope vs out-of-scope)
- **Deterministic engine** (no hidden LLM calls in the pipeline)
- **Auditable artifacts** (decision traces, reports, manifests)

## Index

### Monitorability / Alarms

- **FIT Proxy Alarm Kit** - `tools/fit_proxy_alarm_kit/`  
  Trains a non-LLM specialist model under an explicit **oracle label budget** and reports performance at **fixed false-positive-rate (FPR) caps** (alarm usability, not only ranking metrics like AUC).  
  Quickstart: `python -m fit_proxy_alarm_kit.run --prereg PREREG.fixture.yaml --run_id fixture`

### Constrained Exploration

- **FIT Constrained Explorer Kit** - `tools/fit_constrained_explorer_kit/`  
  Performs **budgeted path exploration** in a large space under explicit constraints (constrained architecture search pattern), producing a best candidate plus an auditable trace.  
  Quickstart: `python -m fit_constrained_explorer_kit.run --prereg PREREG.fixture.yaml --run_id fixture`

### Executability / Auditability

- **FIT EWBench Kit** - `tools/fit_ewbench_kit/`  
  A small **executability + auditability** harness (YAML suites + JSONL logs + Markdown reports) used for Controlled Nirvana / Emptiness Window style experiments.  
  Quickstart: `python -m fit_ewbench_kit.run_suite --suite fixtures/suites/hopfield_to_nirvana.prompt_suite.yaml --mode baseline --out out/logs_baseline.jsonl`

### Reference Labs

- **FIT Hopfield Lab Kit** - `tools/fit_hopfield_lab_kit/`  
  Reproducible Hopfield-network reference implementations + phase-diagram sweeps (useful as a toy "phase transition" lab).  
  Quickstart: `python -m fit_hopfield_lab_kit.phase_diagram --out_csv out/hopfield_phase.csv`
