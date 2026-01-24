# Subcase v0.2 - PAE Proxy Alarm with Active Acquisition

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `pae_proxy_alarm_v0_2`  
**Pack version:** `v0.2_repo_ready`  
**Design pattern:** non-LLM specialist proxy + **oracle query budget** + decision trace  
**Primary training target:** monitorability at **low FPR**  
**Secondary training target:** FIT/EST discipline for **generate -> oracle -> curate -> retrain -> repeat** loops

---

## 0) Scope & claims notice

This is a FIT/EST engineering case about **measurement channels and acquisition policies**, not biology.

- We treat AFDB confidence outputs as a **measurement system**, not ground truth.
- We train a small, non-LLM model to predict a PAE-defined target event using only B0-available features (pLDDT-derived).
- We compare **active acquisition policies** under an explicit **oracle query budget**.

No causal claims about folding are made.

---

## Smoke test (included synthetic metrics)

This subcase includes a tiny synthetic metrics file for a smoke test:

- `fixtures/metrics_per_protein.csv`
- `PREREG.fixture.yaml`

Run (from this subcase directory):

```bash
python -m src.run --prereg PREREG.fixture.yaml --run_id fixture
```

Then inspect:

- `out/fixture/eval_report.md`
- `out/fixture/tradeoff_onepage.pdf`

The fixture is intended only to verify the pipeline + artifacts; it is not a meaningful evaluation.

---

## 1) Why v0.2 exists (what v0.1 did not teach)

v0.1 answered: "Can a proxy alarm operate at low FPR?"

v0.2 answers: "If PAE labels are expensive, can an acquisition policy learn the alarm **faster** than random given the same label budget?"

This is the same loop archetype used in inverse-design/AL systems:

`generate -> oracle evaluate -> accept/reject -> curate dataset -> retrain -> repeat`

The difference is that "generate" here is the **selection of accessions to query**.

---

## 2) Boundary contract (EST discipline)

We explicitly separate:

### 2.1 Train boundary  $ \mathcal{B}_{train} $

In scope:
- features: pLDDT-derived / B0-available only
- labels: oracle PAE channel (revealed only when queried)

Out of scope:
- any use of PAE/MSA as a feature

### 2.2 Deploy boundary  $ \mathcal{B}_{deploy} $

In scope:
- pLDDT-derived features only (no oracle access)

Out of scope:
- PAE/MSA access

**Rule:** PAE is a *label store* in this simulation. It must not be consumed as a feature.

---

## 3) Target event (what the alarm predicts)

Binary target event:

- `E_high_global_uncertainty` occurs when



$$
\texttt{C2\_pae\_offdiag} \ge \tau_{pae}.
$$



`tau_pae` is preregistered in `PREREG.yaml` (default 10.0).

---

## 4) Active acquisition protocol (offline simulation of expensive oracle)

We assume you have a parent-run `metrics_per_protein.parquet` that already contains PAE summaries.

In v0.2 we use it as an **offline oracle store**:

- A pool item is "unlabeled" until the policy queries it.
- Querying reveals the stored label and consumes budget.

### 4.1 Cost accounting

- **Training query budget**: counts the number of labels revealed in the active loop.
- **Evaluation labels**: in this offline protocol, the holdout test labels are treated as "free for measurement".
  - This is a simulation convenience and must be declared; in a real deployment you would either pay to label the holdout or accept delayed evaluation.

---

## 5) Estimator tuple (alarm + acquisition)

We treat this as an operations problem:



$$
\mathcal{E}_{acq} = (S_t,\ \mathcal{B},\ \{\hat{F},\hat{C},\hat{I}\},\ W).
$$



Where:

- `S_t`: labeled set, unlabeled pool, current model, remaining budget
- `\hat{F}`: query pressure (labels consumed per round; batch size)
- `\hat{C}`: false-positive constraint (operate at target FPR caps)
- `\hat{I}`: coverage / recall at low FPR on the holdout

---

## 6) Policies compared (v0.2)

Policies are preregistered in `acquisition.policies`:

- `random_hash`: deterministic pseudo-random (stable hash order)
- `uncertainty`: query items closest to 0.5 predicted probability
- `high_score`: query items with highest predicted probability

All ties are broken deterministically (stable hash), so the decision trace is reproducible.

---

## 7) Event definition (optional; phase-like learning jump)

Define a learning event `E_covjump` on the primary operating point (primary FPR target):

`E_covjump` occurs at the first round `t*` where:

- `TPR(t*) - TPR(t* - W_jump) >= delta_tpr`

with `W_jump` and `delta_tpr` preregistered.

This is a "phase-like" event only in the weak, protocol sense: a discrete regime shift in a measured statistic under locked rules.

---

## 8) Inputs

This subcase consumes **one file** from the parent case:

- `metrics_per_protein.parquet` (or `.csv` fallback)

Required columns:

- `accession`
- `length`
- `I1_hi_conf_frac`
- `I2_mean_plddt`
- `I3_plddt_entropy`
- `C1_low_conf_frac`
- `C2_pae_offdiag` (oracle label store)

---

## 9) Quickstart

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:
- set `data.input_metrics_path` to the parent run file

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 10) Required outputs (artifact contract)

A run is "complete" only if these exist:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `round_metrics.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 11) One-page trade-off figure

See `ONE_PAGE_TRADEOFF.md` for the exact 4-panel definition.
