# FIT Proxy Alarm Kit (non-LLM + budget + low-FPR)

This tool builds **CPU-deployable, non-LLM specialist models** that act as **proxy alarms**:

- **Cheap signals (deploy boundary)**: features available at deploy time (B0).
- **Expensive oracle channel (train boundary)**: labels revealed only when queried (B1).
- **Explicit budget**: label queries are counted and replayed as a deterministic acquisition loop.
- **Monitorability first**: evaluation is reported at **fixed FPR caps** (operating points), not only AUC.

The kit produces a local model (default: logistic regression) saved as JSON plus a set of auditable artifacts.
The default model implementation is **pure NumPy** (no `scikit-learn`) so it works on newer Python versions.

## Quickstart (smoke test)

From this directory:

```bash
pip install -r requirements.txt
python -m fit_proxy_alarm_kit.run --prereg PREREG.fixture.yaml --run_id fixture
```

Inspect:

- `out/fixture/eval_report.md`
- `out/fixture/tradeoff_onepage.pdf`
- `out/fixture/final_models/`
- `out/fixture/alarm_model.json`

The fixture is synthetic and intended only to verify the pipeline.

## Use on your own data

1) Prepare a metrics table (CSV or Parquet):

- One row per item (e.g., run / seed / sample / protein / conversation).
- Must contain: `id_field`, all `boundary.feature_whitelist` columns, and `boundary.label_field` (oracle store).
- The label is never used as a feature; it is only revealed when the acquisition loop “queries” it.

2) Copy and edit `PREREG.example.yaml` (set `data.input_metrics_path`, fields, and budget).

3) Run:

```bash
python -m fit_proxy_alarm_kit.run --prereg PREREG.example.yaml --run_id my_run
```

## Deploy scoring (CPU inference)

Once you have `out/<run_id>/alarm_model.json`, score a new metrics file that contains only deploy-boundary features:

```bash
python -m fit_proxy_alarm_kit.predict --model out/<run_id>/alarm_model.json --metrics path/to/metrics.csv --out out/<run_id>/preds.csv
```
