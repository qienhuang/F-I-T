# Suite Prompt Guide (v3.1) — local CLI assistant usage

This guide defines a **boundary‑disciplined** workflow for using an LLM as a *coding + analysis assistant* while keeping FIT/EST discipline intact.

The suite contains three subcases:

- Track A: `subcases/pae_proxy_alarm/` — proxy alarm (monitorability gate)
- Track B: `subcases/msa_deficit_proxy/` — proxy constraint channel (MSA depth/deficit)
- Track C: `subcases/dual_oracle_active_acquisition/` — active boundary acquisition + robust publishable claims

---

## 0) Non‑negotiables (EST boundary discipline)

When using an LLM in this repo, treat these as hard rules:

1. **PREREG is the source of truth.**
   - Read `PREREG.yaml` before modifying code.
   - After any run, treat `out*/MAIN/PREREG.locked.yaml` as canonical.

2. **Never “smuggle” boundary information.**
   - If a feature is not in the preregistered whitelist/boundary contract, it cannot enter the estimator.
   - Oracle channels (PAE/MSA) are labels / acquisition targets — not features.

3. **Claims must be gate‑compliant.**
   - Track C enforces this via `claims_gate_report.json`, `Claims.md`, and per‑policy card overlay.
   - If the gate does not pass, “outperforms random” is forbidden.

4. **Prefer falsifiable checks over narrative.**
   - Every claim should link to: (a) artifact path, (b) metric definition, (c) pass/fail condition.

---

## 1) Fast workflow (recommended)

### Step 1 — run suite smoke

From `suite_v3_0/`:

```bash
make smoke
```

(or)

```bash
bash suite_ci_check.sh
```

### Step 2 — inspect artifacts

- Track A: `subcases/pae_proxy_alarm/out_smoke/MAIN/`
- Track B: `subcases/msa_deficit_proxy/out_smoke/MAIN/`
- Track C: `subcases/dual_oracle_active_acquisition/out_smoke/MAIN/`

Start with:
- `eval_report.md`
- `eval_metrics.json`
- `tradeoff_onepage.pdf`

Track C additionally:
- `Claims.md`
- `claims_gate_report.json`
- `policy_cards_index.md`
- `policy_cards/<policy>.md` (look for `## Claims & gate status (generated)`)

---

## 2) Prompt templates (copy/paste)

### Template A — “Boundary check before coding”

> Read `PREREG.yaml` and tell me the **exact boundary contract** (feature whitelist, label fields, and what is forbidden).  
> Then list the 5 most likely ways a patch could accidentally violate boundary discipline in this subcase.

### Template B — “Implement one change, with prereg‑compatible tests”

> Implement the following change **without changing the prereg boundary**: <describe change>.  
> Add one unit-style check (or artifact check) that would fail if the boundary is violated.

### Template C — “Explain results with publishable language discipline”

> Using only artifacts in `out_smoke/MAIN/`, write a short explanation.  
> You must follow `Claims.md` / `claims_gate_report.json`.  
> Forbidden: any wording that contradicts the gate status.

### Template D — “Trade‑off interpretation”

> Explain the trade‑off curve in `tradeoff_onepage.pdf`.  
> Identify the operating point that would be chosen under **low-FPR** constraints, and justify it with numbers.

---

## 3) Best practices for local CLI assistant

- Pin changes to a subcase, not cross‑cutting refactors.
- Before merging, run the subcase CI smoke:
  - `cd subcases/<name> && bash scripts/ci_check.sh`
- When changing claims logic, require:
  - `Claims.md` regeneration and artifact checks passing
  - (Track C) policy-card overlay must still be injected

---

## 4) If you add a new subcase to the suite

Minimum contract:

- `PREREG.yaml`
- `PREREG_SMOKE.yaml`
- `scripts/ci_check.sh` (synthetic‑metrics smoke)
- `scripts/check_artifacts.py`
- `README.md` with:
  - case summary
  - estimator tuple
  - reproducibility checklist
  - one-page tradeoff definition

Update:
- `suite_v3_0/SUITE_PREREG.yaml`
- `suite_v3_0/suite_ci_check.sh`
- `suite_v3_0/REPRO_CHECKLIST.md`
- `subcases/SUBCASES_POLICY.md`
