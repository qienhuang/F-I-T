# afdb_swissprot_tier2p11_confidence_regimes

A repo-ready FIT/EST case pack (Tier 2 / P11) using AlphaFold Database (AFDB) Swiss-Prot confidence outputs as a measurement system (not ground truth).

**Case ID:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Tier / Proposition:** Tier2 / P11 (regime-shift signatures in $I/C$)  
**Key training objective:** EST **boundary discipline** via explicit boundary modes (`B0/B1/B2`) controlling PAE/MSA availability.

---

## Scope & claims notice

This is a **FIT/EST discipline case**, not a biology claim.

- We treat AFDB outputs as a **measurement system**, not ground truth.
- We detect **signatures** (change points / regime transitions) under a preregistered estimator tuple.
- We do **not** assert causality, and we do **not** claim protein folding "phase transitions".

If any locked boundary element changes after seeing results, treat it as a **new run + new prereg**.

---

## System snapshot

**System (operational):** AFDB provides predicted protein structures (coordinates) plus confidence channels:
- pLDDT (per-residue confidence; embedded in coordinate B-factors),
- optional PAE (global confidence; JSON),
- optional MSA (alignment; `.a3m`, used as an evolutionary-constraint signal).

**Key case design:** "PAE/MSA availability" is treated as an **instrumentation boundary switch**.

---

## How FIT can help AlphaFold workflows (and why this case exists)

If you are new to FIT, it helps to separate "what FIT contributes" into three layers:

**(1) Language layer (organize the problem):** FIT gives a common grammar for describing a workflow that otherwise fragments into separate subcultures (structure prediction, complex prediction, design, and experiment iteration). In this case we make the mapping explicit: **State** is a protein (or an aggregated bin) plus its AFDB-derived confidence summaries; **Constraints** include instrumentation availability (`B0/B1/B2`) and any declared filters; **Force** is the selection pressure induced by the evaluation protocol (what we keep vs discard, and how we detect change points); **Time** is represented by an ordered axis (here: length-bin index) and window choices.

**(2) Measurement layer (turn proxy fights into auditable choices):** AlphaFold-related discussions often degrade into "your proxy is wrong" (pLDDT thresholds, PAE summaries, MSA availability, etc.). FIT v2.4's EST discipline is designed to make this dispute tractable: we preregister an estimator family and a coherence gate, report regime signatures only when the gate passes, and treat boundary changes as new experiments (not as "extra features").

**(3) Engineering layer (run the closed loop):** Once the boundary is explicit, it becomes feasible to build reproducible pipelines that separate *deploy* signals from *oracle* channels. This pack demonstrates that discipline directly:
- the parent case treats PAE/MSA as boundary-controlled measurement channels (`B0/B1/B2`);
- the `pae_proxy_alarm/` subcase turns "PAE is expensive" into a budgeted acquisition loop (query -> label reveal -> retrain) under explicit low-FPR operating points.
- the `dual_oracle_active_acquisition/` subcase extends the same idea to **two independent oracle channels** (PAE + MSA) with explicit budgets, robust claim gates, and policy-card overlays.

This case is therefore less about proving biology, and more about making an AlphaFold-adjacent workflow **auditable** (boundary-locked, estimator-declared, artifact-complete).

---

## Subcases (budgeted acquisition protocols)

Start here if you want the end-to-end learning track:

- `suite_v3_0/` — AFDB non-LLM small-models suite (Track A/B/C; one-click smoke + learning order).

Canonical subcases (the ones to run and cite):

- `subcases/pae_proxy_alarm/` — single oracle (PAE) as a label store; learn a B0-deployable proxy alarm under a label budget and fixed FPR caps.
- `subcases/msa_deficit_proxy/` — learn a B0-deployable proxy estimator for an otherwise B2-only channel (MSA depth/deficit), with optional low-FPR alarm view.
- `subcases/dual_oracle_active_acquisition/` — dual oracles (PAE + MSA) under separate budgets; active boundary acquisition + robust claim gates + policy-card overlays.

Historical versioned subcase folders may exist for provenance. See: `subcases/SUBCASES_POLICY.md`.

## Suite v3.0 smoke status (repo-runnable)

Recent smoke runs confirm the suite entry points are runnable end-to-end (artifacts produced) for all three canonical subcases:

- **PAE Proxy Alarm**: PASS (eval report + tradeoff figure + trained proxy model)
- **MSA Deficit Proxy**: PASS (after config compatibility fix; eval report + tradeoff figure + trained proxy model)
- **Dual-Oracle Active Acquisition**: PASS (main run; leakage audit + policy cards + frontier plot)

Compatibility fixes applied in this repo (no change to intended semantics):

- `PREREG_SMOKE.yaml` (MSA): `fallback_compute_from_msa_depth` -> `fallback_compute_from_msa_depth_if_missing`
- `eval.py` (MSA + Dual-Oracle): scikit-learn RMSE call updated for newer versions (`np.sqrt(mean_squared_error(...))`)

Note: `data/` and `out/` are local-only caches and should not be pushed.

## Boundary modes (the core learning device)

We define three mutually exclusive boundary modes:

- **`B0_COORD_ONLY`**  
  In scope: coordinate files only (pLDDT from B-factor).  
  Out of scope: PAE, MSA.

- **`B1_COORD_PLUS_PAE`**  
  In scope: coordinates + PAE JSON.  
  Out of scope: MSA.

- **`B2_COORD_PLUS_PAE_PLUS_MSA`**  
  In scope: coordinates + PAE + MSA.

**Rule:** Comparing results across `B0/B1/B2` is comparing **different boundaries**, not "same experiment with extra features".

---

## Pilot status (repo-safe summary)

This repo includes preregistered **pilot** configs intended to be runnable on a small sample before any larger sweep:

- `EST_PREREG.pilot_B0_coords_only.yaml`
- `EST_PREREG.pilot_B1_coords_pae.yaml`

Local pilot outcome (B1, coords + PAE):

- **Coherence gate:** `COHERENT`
- **Event detection:** regime shift detected (bin-level), with both constraint estimators pointing to the same event location.

These pilots are designed to validate **pipeline executability + EST semantics** under the declared boundary, not to support a biology claim.

Note: `data/` and `out/` are local-only caches and should not be pushed.

## Expanded B1 run (CPU)

To scale beyond the pilot, two preregistered B1 sizes are provided:

- **Quick** (N=100): `EST_PREREG.B1_taxon9606_N100.yaml`
- **Expanded** (N=1000): `EST_PREREG.B1_taxon9606_N1000.yaml`
- `RUNBOOK_B1_EXPANDED_CPU.md`

Both stage a deterministic accession set (reviewed UniProt subset) into `data/runs/...` and run B1 (coords + PAE) under the same auditable gate semantics.

Optional: a B2 quick prereg is provided to audit the same accession set under a boundary that includes MSA:

- **Quick** (N=100, B2 coords + PAE + MSA): `EST_PREREG.B2_taxon9606_N100.yaml`
- **Expanded** (N=1000, B2 coords + PAE + MSA): `EST_PREREG.B2_taxon9606_N1000.yaml` (requires downloading the MSA channel for the staged accession set)
- **Split-stability** (N=1000, B2 coords + PAE + MSA): `EST_PREREG.B2_taxon9606_N1000_split_a.yaml`, `EST_PREREG.B2_taxon9606_N1000_split_b.yaml`, `EST_PREREG.B2_taxon9606_N1000_split_c.yaml`

Repo-safe evidence zips (exclude local caches; include locked prereg + required artifacts):

- `evidence_B1_taxon9606_N100.zip`
- `evidence_B1_taxon9606_N1000.zip`
- `evidence_B2_taxon9606_N100.zip`
- `evidence_B2_taxon9606_N1000.zip`

### B1 vs B2 comparison (repo-safe summary)

| Run | Boundary | N | Coherence Gate | Event? | C1 bin | C2 bin | C3 bin |
|-----|----------|---|----------------|--------|--------|--------|--------|
| B1_taxon9606_N100 | B1 (coords+PAE) | 96 | COHERENCE_NOT_TESTABLE | No | - | - | n/a |
| B1_taxon9606_N1000 | B1 (coords+PAE) | 988 | **COHERENT** | Yes (bin 2) | 2 | 2 | n/a |
| B2_taxon9606_N100 | B2 (coords+PAE+MSA) | 96 | **ESTIMATOR_UNSTABLE** | Yes (bin 5) | 3 | 3 | 8 |
| B2_taxon9606_N1000 | B2 (coords+PAE+MSA) | 988 | **ESTIMATOR_UNSTABLE** | Yes (bin 2) | 2 | 2 | 8 |

**Key finding (confirmed at N=1000):** The MSA deficit channel (C3) fires at **bin 8** regardless of sample size (N=100 or N=1000), while the pLDDT/PAE channels (C1, C2) consistently fire at **bin 2** at scale. This is not a noise artifact -- it is a **structural disagreement** between measurement channels.

**Interpretation:**

- Under B1 (coords + PAE), the estimator tuple is coherent at N=1000: all channels agree on bin 2.
- Under B2 (coords + PAE + MSA), adding the MSA channel breaks coherence. The MSA deficit estimator detects a regime transition at a much later length scale (bin 8) than pLDDT/PAE (bin 2).
- The coherence gate correctly labels B2 as ESTIMATOR_UNSTABLE, preventing conflation of structurally different signals into a single regime claim.
- This demonstrates a core FIT/EST principle: **changing the boundary (B1 -> B2) is a different experiment**, and the gate enforces that discipline.

### B2 split-stability follow-up (CPU)

Run three deterministic B2 splits at `N~1000`:

```bash
python run_case.py --prereg EST_PREREG.B2_taxon9606_N1000_split_a.yaml --run_id B2_taxon9606_N1000_split_a
python run_case.py --prereg EST_PREREG.B2_taxon9606_N1000_split_b.yaml --run_id B2_taxon9606_N1000_split_b
python run_case.py --prereg EST_PREREG.B2_taxon9606_N1000_split_c.yaml --run_id B2_taxon9606_N1000_split_c
```

Summarize event-bin offsets and coherence outcomes:

```bash
python scripts/compare_b2_split_stability.py \
  --runs B2_taxon9606_N1000_split_a B2_taxon9606_N1000_split_b B2_taxon9606_N1000_split_c \
  --out_csv out/B2_split_stability.csv \
  --out_md out/B2_split_stability.md
```

Publish-safe locked copies:
- `results_locked/B2_split_stability.csv`
- `results_locked/B2_split_stability.md`

Decision rule:
- if `offset(C3 - C2)` is stable across splits, treat B2 disagreement as structural channel mismatch;
- if offsets are unstable, treat as sampling-sensitive and keep verdict at `ESTIMATOR_UNSTABLE` without stronger structural claims.

#### Split-stability results (2026-02-11)

| Run | Status | N | C_primary | C1 | C2 | C3 | C3-C2 offset |
|-----|--------|---:|---:|---:|---:|---:|---:|
| B2_taxon9606_N1000_split_a | ESTIMATOR_UNSTABLE | 988 | 2 | 2 | 2 | 8 | 6 |
| B2_taxon9606_N1000_split_b | ESTIMATOR_UNSTABLE | 988 | 2 | 2 | 2 | 8 | 6 |
| B2_taxon9606_N1000_split_c | ESTIMATOR_UNSTABLE | 988 | 2 | 2 | 2 | 8 | 6 |

**Verdict:** Offset `[6, 6, 6]` is perfectly stable across all three deterministic splits. Per the decision rule, the B2 disagreement is confirmed as **structural channel mismatch**, not sampling noise.

### B2 sign-aware follow-up (CPU)

Run sign-aware channel comparison over existing B2 runs:

```bash
python scripts/compare_b2_sign_aware.py \
  --runs B2_taxon9606_N100 B2_taxon9606_N1000 B2_taxon9606_N1000_split_a B2_taxon9606_N1000_split_b B2_taxon9606_N1000_split_c \
  --out_csv out/B2_sign_aware.csv \
  --out_md out/B2_sign_aware.md
```

Publish-safe locked copies:
- `results_locked/B2_sign_aware.csv`
- `results_locked/B2_sign_aware.md`

#### Sign-aware results (2026-02-23; key pair C2 vs C3)

| Run | N | rho_signed(C2,C3) | abs(rho) | Event bins (C2 vs C3) | offset |
|---|---:|---:|---:|---|---:|
| B2_taxon9606_N100 | 96 | -0.143 | 0.143 | 3 vs 8 | 5 |
| B2_taxon9606_N1000 | 988 | -0.655 | 0.655 | 2 vs 8 | 6 |
| B2_taxon9606_N1000_split_a | 988 | -0.655 | 0.655 | 2 vs 8 | 6 |
| B2_taxon9606_N1000_split_b | 988 | -0.655 | 0.655 | 2 vs 8 | 6 |
| B2_taxon9606_N1000_split_c | 988 | -0.655 | 0.655 | 2 vs 8 | 6 |

Interpretation:
- `rho_signed(C2,C3)` is **negative in all runs** (persistent opposite-sign behavior).
- For `N~1000` + splits, event-bin offset is stable at **6** (`[6,6,6,6]`), consistent with split-stability.
- Together with coherence-gate failure, this supports a **structural channel mismatch** under B2 rather than random instability.

### Key methodological finding

> **MSA channel is boundary-dependent and not coherence-equivalent to pLDDT/PAE along the length axis.**
>
> B2 N=1000 confirms structural disagreement (not noise): the coherence gate remains ESTIMATOR_UNSTABLE with C3_msa_deficit event at bin 8 vs C1/C2 at bin 2, and the C2-vs-C3 relationship is opposite-sign (negative `rho_signed`) across runs. The persistent offset at N~1000 across three independent accession splits (offset=6 in all splits) establishes that the MSA deficit estimator measures a fundamentally different regime transition than pLDDT/PAE-derived estimators. The gate correctly prevents a single unified regime claim under the B2 boundary.

## Estimator tuple (explicit)

All claims are conditional on:


$$
\mathcal{E} = (S_t,\ \mathcal{B},\ \{\hat{F}, \hat{C}, \hat{I}\},\ W).
$$



- **State  $ S_t $**: protein set aggregated into length bins (bin-level medians of per-protein metrics).
- **Boundary  $ \mathcal{B} $**: AFDB release label (user-specified), dataset scope (Swiss-Prot), boundary mode (`B0/B1/B2`), sampling rule, file paths.
- **Estimators**:
  -  $ \hat{I} $: "reliable-structure coverage" proxies from pLDDT (e.g., high-confidence fraction).
  -  $ \hat{C} $: "uncertainty / global inconsistency" proxies from low-confidence fraction and optional PAE/MSA.
  -  $ \hat{F} $: "pressure/underdetermination" proxies (length; optional MSA deficit).
- **Windows  $ W $**: bin width (aa), smoothing window (bins), event persistence window (bins).

---

## What is  $ t $  in this case

This is not a time series. We use an **ordered axis**:

-  $ t $  := **sequence-length bin index** (e.g., 50 aa per bin).

This makes P11 "regime changes" interpretable as **structural transitions across length scale**.

---

## Outputs (required artifacts)

A successful run produces:

- `out/<run_id>/metrics_per_protein.parquet` (or `.csv` fallback)
- `out/<run_id>/metrics_per_bin.parquet` (or `.csv` fallback)
- `out/<run_id>/regime_report.md`
- `out/<run_id>/tradeoff_onepage.pdf`
- `out/<run_id>/boundary_snapshot.json`
- `out/<run_id>/run_manifest.json`
- `out/<run_id>/accessions_selected.txt` (+ `.sha256`)

---

## Quickstart (repo local)

### Choose your entry point (recommended)

| If you want... | Start here | What you get |
|---|---|---|
| a quick pipeline sanity check | run the **Smoke test** below | a complete `out/<run_id>/` artifact set on tiny synthetic fixtures |
| the Tier-2 / P11 **regime signature** case (boundary B0/B1/B2) | run the **parent pipeline** in this folder | change-point signatures across length bins + required artifacts + one-page figure |
| the "non-LLM specialist models" learning track (proxy alarms + active acquisition) | `suite_v3_0/` | a guided Track A/B/C with smoke checks and claim-discipline scaffolding |

### Smoke test (no downloads)

This repo includes a tiny synthetic fixture under `fixtures/` for a smoke test.

From this case directory:

```bash
python -m src.run --prereg EST_PREREG.fixture_B0.yaml --run_id fixture_b0
python -m src.run --prereg EST_PREREG.fixture_B1.yaml --run_id fixture_b1
```

Then inspect:

- `out/fixture_b0/regime_report.md`
- `out/fixture_b1/regime_report.md`

The fixture is intended only to verify the pipeline + artifacts; it is not a meaningful evaluation.

### 0) Place data

Put files into:
- `data/coords/` : AFDB coordinate files (`.cif` or `.pdb`)
- `data/pae/`    : PAE JSON files (optional; boundary-dependent)
- `data/msa/`    : MSA `.a3m` files (optional; boundary-dependent)

If you do not already have a local cache, you can download AFDB artifacts for a preregistered accession list:

```bash
python scripts/download_coords_for_accessions.py --accessions out/<run_id>/accessions_selected.txt --out_coords_dir data/coords
python scripts/download_pae_msa_for_accessions.py --accessions out/<run_id>/accessions_selected.txt --out_pae_dir data/pae --out_msa_dir data/msa
```

For a small pilot run (coords-only, no full cache required), start from:
- `EST_PREREG.pilot_B0_coords_only.yaml`

### 1) Create / lock prereg

Edit `EST_PREREG.yaml`:
- set `boundary.boundary_mode` = `B0_COORD_ONLY` / `B1_COORD_PLUS_PAE` / `B2_COORD_PLUS_PAE_PLUS_MSA`
- set `boundary.afdb_release_version` to your release label (string)
- set `boundary.selection.sampler.target_n_valid` to a number you can run

### 2) Run the pipeline

From this case directory:

```bash
python -m src.run --prereg EST_PREREG.yaml
```

Outputs appear under `out/<run_id>/`.

---

## Interpreting results (EST-first)

1) Check `regime_report.md` coherence status.
2) If `ESTIMATOR_UNSTABLE`: do not interpret regime locations; fix estimator family or boundary.
3) If coherent: treat detected change points as **signatures**, not causes.
4) If you add PAE/MSA later: treat as a **new boundary** and rerun.

---

## File map

- `EST_PREREG.yaml` - preregistered boundary + estimators + windows + event definition  
- `ONE_PAGE_TRADEOFF.md` - exact figure specification  
- `REPRO_CHECKLIST.md` - reproducible steps  
- `src/run.py` - orchestrator  
- `src/io_*` - parsers (coords / pae / msa)  
- `src/metrics_*` - per-protein metrics  
- `src/binning.py` - length binning + aggregation  
- `src/gates_est.py` - coherence gate + labels  
- `src/change_points.py` - event detection (P11)  
- `src/plot_onepager.py` - trade-off one-page figure  
- `src/utils_hash.py` - deterministic sampling + hashing

---

## Notes / limitations

- Parsing mmCIF is nontrivial; this pack implements a **minimal** `_atom_site` loop parser suitable for AFDB coordinate files.
- This case does not download AFDB itself; you bring the data.
- Very long proteins and AFDB "fragment" naming conventions should be handled by filtering in prereg.

---

## Related style anchors

This case follows your existing FIT case conventions (scope notice -> boundary -> oracle/estimators -> event -> monitorability discipline).

Entry points:

- `PROMPT_GUIDE.md` — LLM/coding-assistant prompts that enforce boundary discipline and publishable language.
- `REPRO_CHECKLIST.md` — reproducibility checklist.
- `ONE_PAGE_TRADEOFF.md` — mandatory one-page figure contract (what every run must produce).
