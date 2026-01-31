# AFDB Non‑LLM Specialist Models — Bundle v0.6

This bundle contains repo‑ready subcases under:

`experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes/subcases/`

Note (canonicalization):

- This file documents an earlier "bundle of versions" snapshot.
- For the current repo-ready entrypoints, prefer the canonical subcase folders:
  - `pae_proxy_alarm/`
  - `msa_deficit_proxy/`
  - `dual_oracle_active_acquisition/`
- See also: `SUBCASES_POLICY.md` and the suite entrypoint `../suite_v3_0/`.

Included:

1) `pae_proxy_alarm_v0_1`  
   - B0→B1 alarm: predict PAE high‑uncertainty event with low‑FPR monitorability gate.

2) `pae_proxy_alarm_v0_2`  
   - Single‑oracle active acquisition (offline oracle store): compare policies under label budget; logs decision traces.

3) `msa_deficit_proxy_v0_1`  
   - B0→B2 proxy estimator: estimate an MSA deficit channel and evaluate low‑FPR usability.

4) `dual_oracle_active_acquisition_v0_3`  
   - Dual‑oracle baseline: separate budgets; unified decision trace.

5) `dual_oracle_active_acquisition_v0_4`  
   - Dual‑oracle + joint gate + MSA regression proxy channel  C3 := -log(1+msa_depth) .

6) `dual_oracle_active_acquisition_v0_5`  
   - Policy grammar <allocation>__<ranking> + composite ranking + allocation curves.

7) `dual_oracle_active_acquisition_v0_6`  
   - Union universe mode (oracle may be missing) + **batch‑aware diversity** ranking (`composite_batch_ff`)
     under a preregistered candidate pool cap.

Each subcase is self‑contained with:
- README.md
- PREREG.yaml
- ONE_PAGE_TRADEOFF.md
- REPRO_CHECKLIST.md
- PROMPT_GUIDE.md
- src/ (runnable)

Run from each subcase directory:

```bash
pip install -r requirements.txt
python -m src.run --prereg PREREG.yaml
```

You must set `data.input_metrics_path` in each PREREG.yaml to point to the relevant parent-run artifact.
