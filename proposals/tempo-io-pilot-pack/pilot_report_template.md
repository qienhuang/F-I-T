# 2‑Week Pilot Report (Template)

> Scope: operational tempo + irreversibility risk.  
> Output: 1–2 pages. Keep it auditable.

## 0) Metadata

- Org / team (optional):  
- System name:  
- Date range covered:  
- Pilot mode: Shadow / Enforced  
- RTO / RPO used for drills:  
- Who reviewed this report:  

## 1) System boundary (what we included)

In one paragraph, describe what counted as “the system” for this pilot.

- Change sources included (code, model, data, policy, infra):  
- What “change-effective” means (merge / deploy / training start / release):  
- What “closure” means (eval completion / sign-off / audit ticket closed):  

## 2) Metrics snapshot (VL / RDPR / GBR)

### 2.1 Validation Lag (VL)

- N changes measured:  
- Median VL (hours):  
- P90 VL (hours):  
- P99 VL (hours):  
- Fraction over SLO threshold (if any):  

### 2.2 Rollback Drill Pass Rate (RDPR)

- N drills in range:  
- Declared RTO (minutes):  
- Declared RPO (minutes):  
- RDPR (%):  
- Notes on failures (if any):  

### 2.3 Gate Bypass Rate (GBR)

- Define “bypass” in this context:  
- IO‑relevant changes counted:  
- Bypass events counted:  
- GBR (%):  

## 3) IO register summary (classification, not blame)

- N IO‑tagged changes:  
- Breakdown by category (counts):
  - Self‑eval gating:  
  - Tool loops / tool autonomy:  
  - Memory write‑back / data write‑back:  
  - Policy / access / authority transfer:  
  - Optionality / single‑point dependency:  
  - Other:  

Brief notes (1–3 bullets): which category is accumulating fastest and why.

## 4) Drill details (one concrete test)

Pick one recent IO‑tagged change and record the drill.

- Change ID / description:  
- Drill type: rollback / purge / disable / staged rollback  
- Result: PASS / FAIL  
- Time to recover:  
- What broke (if fail):  
- What would have prevented the failure:  

## 5) Findings (what is the risk mechanism?)

Write 3–6 bullets only:

- Which feedback loop(s) are amplifying constraints (and why)?
- Where does option space collapse show up operationally?
- Which metric moved first (VL/RDPR/GBR), and what did it reveal?

## 6) Proposed thresholds (provisional)

These are not universal constants. They are “first pass” triggers.

- VL yellow / red thresholds:  
- RDPR minimum thresholds:  
- GBR yellow / red thresholds:  
- Mandatory human review trigger (if applicable):  
  - condition: repeated self‑eval vs external‑eval disagreement for N runs  
  - action: pause + human sign‑off + logged escalation  

## 7) Recommended next step (lowest friction)

Choose exactly one:

- Add/strengthen IO‑only gate for one category
- Increase drill frequency for one pipeline
- Add an independent evaluator (coherence gate)
- Add a circuit breaker trigger based on VL/RDPR/GBR

## 8) Known limitations / boundary cases

List 1–3 items:

- Missing logs / ambiguous timestamps  
- Changes without clear closure definition  
- Drills not representative of real rollback  

