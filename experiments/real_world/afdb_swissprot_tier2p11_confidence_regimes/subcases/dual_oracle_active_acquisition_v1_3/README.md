# Subcase v1.3 — Dual‑Oracle Active Acquisition (Policy Cards + CI‑style Checks)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_3`  
**Pack version:** `v1.3_repo_ready`  
**Lineage:** v1.0 (regimes) → v1.1 (Δ + leakage audit) → v1.2 (policy_table + holdout hash + smoke) → **v1.3 (policy cards + CI checks)**

This pack is meant to be **repo‑ready** and **teaching‑ready**:

- *repo‑ready*: minimal friction to run, validate artifacts, and catch boundary mistakes
- *teaching‑ready*: produces compact, policy‑level “cards” suitable for FIT/EST readers and LLM assistants

---

## 0) What is new in v1.3

### 0.1 Policy cards (one Markdown per policy)

New artifacts under `out/<run_id>/policy_cards/`:

- one `*.md` per policy spec
- `policy_cards_index.md` (links / table-of-contents)

Each card contains:

- boundary summary + cap + thresholds
- event markers: floor‑resolved, enter‑usable, joint‑usable
- Δ‑lag (floor‑clear → joint usable)
- final holdout operating stats: TPR@cap, FPR_floor@TPRmin
- proxy quality: MAE(  $ \widehat{C3} $  )
- leakage audit status
- decision‑trace audit notes (alpha/K/basis)

This turns “reading the run” into a standardized procedure.

### 0.2 CI‑style validation scripts

New scripts:

- `scripts/check_artifacts.py` — verifies the required artifacts exist and key invariants hold  
- `scripts/ci_check.sh` — runs smoke test and then calls the checker

These are not a full CI integration, but they are the minimal “gate” you can plug into GitHub Actions later.

---

## 1) Quickstart (real data)

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent case metrics file (parquet/csv)

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 2) Quickstart (smoke test + CI‑style check)

From this directory:

```bash
bash scripts/ci_check.sh
```

It will:

1) generate `data/synthetic_metrics.csv`  
2) run the case with `PREREG_SMOKE.yaml` to `out_smoke/SMOKE/`  
3) validate required artifacts + boundary invariants

---

## 3) Artifact contract (v1.3)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `holdout_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `regime_timeline.csv`
- `regime_summary.json`
- `policy_table.csv`
- `policy_cards_index.md` (**NEW**)
- `policy_cards/` (**NEW**)
- `leakage_audit.json`
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
