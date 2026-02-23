# Execution Checklist (2026-02-23)

## Phase 0: package bootstrap

- [x] Create experiment folder structure
- [x] Add prereg YAML (main + smoke)
- [x] Add output schema and summary template
- [x] Add runnable audit pipeline
- [x] Add smoke data generator

## Phase 1: smoke validation

- [x] Generate synthetic per-seed CSV input
- [x] Run pipeline with `EST_PREREG.smoke.yaml`
- [x] Confirm all core labels appear
- [x] Confirm aggregate summary + diagnostics are produced

## Phase 2: real-run prep (pending)

- [ ] Export real per-seed signal logs to `data/real/*.csv`
- [ ] Lock full boundary/threshold fields in `EST_PREREG.v0_1.yaml`
- [ ] Run full evaluation
- [ ] Produce evidence bundle (`summary.json`, `diagnostics.csv`, `report.md`, `per_seed/*.json`)

## Phase 3: publish integration (pending)

- [ ] Add final result note to `docs/benchmarks` or `experiments/.../RESULTS.md`
- [ ] Update landing README if verdict becomes publishable
- [ ] Append final run record in `_registry/runs.jsonl`

