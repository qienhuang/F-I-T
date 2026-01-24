# Toolkits (Runnable, non-LLM building blocks)

This folder contains small, **CPU-first** and **reproducible** toolkits that implement FIT/EST-style discipline:

- **Locked boundary / prereg** (what is in-scope vs out-of-scope)
- **Deterministic engine** (no hidden LLM calls in the pipeline)
- **Auditable artifacts** (decision traces, reports, manifests)

## Index

### Monitorability / Alarms

- **FIT Proxy Alarm Kit** — `tools/fit_proxy_alarm_kit/`  
  Trains a non-LLM specialist model under an explicit **oracle label budget** and reports performance at **fixed FPR caps** (alarm usability, not only AUC).  
  Quickstart: `python -m fit_proxy_alarm_kit.run --prereg PREREG.fixture.yaml --run_id fixture`

### Constrained Exploration

- **FIT Constrained Explorer Kit** — `tools/fit_constrained_explorer_kit/`  
  Performs **budgeted path exploration** in a large space under explicit constraints (BioArc/NAS-like pattern), producing a best candidate plus an auditable trace.  
  Quickstart: `python -m fit_constrained_explorer_kit.run --prereg PREREG.fixture.yaml --run_id fixture`

