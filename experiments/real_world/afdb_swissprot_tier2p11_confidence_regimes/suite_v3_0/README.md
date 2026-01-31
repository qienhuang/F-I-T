# AFDB Non‑LLM Small‑Models Suite (v3.1)

This suite packages **three** “non‑LLM specialist model” subcases into a single, repo‑ready learning track.
The goal is to train FIT/EST readers on **boundary discipline**, **monitorability gates**, and **active boundary acquisition** using AFDB‑style confidence channels as a measurement system.

> Scope note: this is a systems/measurement case. We make no causal claims about folding.

---

## What you get (the learning track)

### Track A — Proxy alarm (PAE event)  → *monitorability gate*

- Subcase: `subcases/pae_proxy_alarm/`
- Objective: predict a PAE-defined event using only B0-safe features, and operate at **low FPR**.

### Track B — Proxy estimator (MSA channel) → *boundary-safe estimated constraint channel*

- Subcase: `subcases/msa_deficit_proxy/`
- Objective: estimate an otherwise B2-only measurement channel (`msa_depth` / derived deficit) from B0-safe features.

### Track C — Dual-oracle active acquisition → *controlled boundary switch as a learnable strategy*

- Subcase: `subcases/dual_oracle_active_acquisition/`
- Objective: learn an acquisition policy over boundary switches (PAE/MSA retrieval) under explicit budgets, and enforce publishable claims via **robust two-key gates + policy-card overlays**.

---

## Quickstart (suite smoke)

## v3.1 additions

- `requirements.all.txt` — consolidated dependencies for a single-environment install
- `Makefile` — ergonomic entrypoints (`make smoke`, `make pae`, `make msa`, `make dual`, `make clean`)
- `PROMPT_GUIDE.md` — suite-level LLM/coding assistant discipline (PREREG-first, boundary-safe, gate-compliant claims)
- `RELEASE_NOTES.md` — suite evolution notes

From this folder:

```bash
pip install -r requirements.all.txt
bash suite_ci_check.sh
```

This will run the smoke/CI checks for all three subcases, each using **synthetic metrics** generated locally (no AFDB downloads required).

Windows note:

- The suite smoke script is a Bash script. Run it from Git Bash, WSL, or a Linux/macOS shell.
- If you prefer PowerShell-only, run the three subcases individually (each subcase has its own `scripts/ci_check.sh` and `PREREG_SMOKE.yaml`).

---

## Where the “boundary discipline” shows up

- Each subcase has:
  - a prereg file (`PREREG.yaml`) that defines the estimator, event, and boundary contract
  - a smoke prereg (`PREREG_SMOKE.yaml`) that points to synthetic metrics for CI
  - a CI script (`scripts/ci_check.sh`) that:
    1) generates synthetic metrics with missingness (simulated boundary availability)
    2) runs the pipeline
    3) checks required artifacts

Track C additionally hardens claim publication via:
- bilevel robustness + two-key gate
- graded claims
- per-policy “claims overlay” injected into policy cards (operationalization layer)

---

## Recommended learning order

1) Run Track A, read its `eval_report.md`, and inspect the tradeoff PDF.
2) Run Track B, verify you understand the “proxy constraint channel” idea.
3) Run Track C last (it is the most “FIT-complete”).

---

## Suite prereg index

See: `SUITE_PREREG.yaml`
