# Suite reproducibility checklist (v3.0)

## Environment

Single-env option (suite):

```bash
cd suite_v3_0
pip install -r requirements.all.txt
```



- Python 3.10+
- Install each subcase requirements in an isolated env (recommended):

For Track A:

```bash
cd ../subcases/pae_proxy_alarm
pip install -r requirements.txt
```

For Track B:

```bash
cd ../subcases/msa_deficit_proxy
pip install -r requirements.txt
```

For Track C:

```bash
cd ../subcases/dual_oracle_active_acquisition
pip install -r requirements.txt
```

> If you prefer, you may create a single env and install all three requirements, but keep dependency pins consistent.

---

## Smoke / CI run

Preferred:

```bash
cd suite_v3_0
make smoke
```

Alternative:



From `suite_v3_0/`:

```bash
bash suite_ci_check.sh
```

Expected:
- each subcase prints `CI-style check PASSED.`
- artifacts appear under each subcase’s `out_smoke/MAIN/`

---

## Artifact locations

- Track A: `../subcases/pae_proxy_alarm/out_smoke/MAIN/`
- Track B: `../subcases/msa_deficit_proxy/out_smoke/MAIN/`
- Track C: `../subcases/dual_oracle_active_acquisition/out_smoke/MAIN/`

---

## What to inspect first

- `eval_report.md` (narrative, checks, metrics)
- `tradeoff_onepage.pdf` (one-page tradeoff)
- Track C: `policy_cards_index.md` and individual policy cards (claims overlay)
