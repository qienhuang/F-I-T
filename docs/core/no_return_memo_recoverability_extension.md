# No-Return Memo Recoverability Extension (NR-R)

Status: core-adjacent extension (v2.x compatible, non-breaking)  
Framework: FIT / EST  
Depends on: `no_return_memo.md`, `recoverability.md`

---

## 1) Purpose

The original No-Return Memo (NRM) uses a tempo gate (`NR-1`) to judge whether correction can arrive before irreversible commitments accumulate.

This extension adds a second gate (`NR-R`):

Even if correction can arrive in time, is the target structure still recoverable under bounded resources?

NR-R is diagnostic only. It does not expand authority.

---

## 2) Dual-gate model

### NR-1 (tempo gate, unchanged)

If `L_ext > T_commit`, correction is too slow for current commitment tempo.

### NR-R (recoverability gate, new)

Declare:

- `Sigma*`: target structural class
- `~`: equivalence relation (ordinal / metric / topological)
- `B`: bounded recovery budget
- `Pi_rec`: admissible recovery protocol family

Compute preregistered recoverability score:

`R(B) = P_recover(B) * exp(-lambda*T_recover) * exp(-mu*D_drift)`

Then:

- If `R(B) < R_min` (preregistered), classify as `IRRECOVERABLE_UNDER_SCOPE`.

---

## 3) Regime table

| NR-1 | NR-R | Interpretation |
|---|---|---|
| PASS | PASS | Reversible under declared scope |
| FAIL | PASS | Tempo-gated failure (timing channel problem) |
| PASS | FAIL | Structurally irrecoverable despite timing |
| FAIL | FAIL | Deep no-return regime |

NR-1 and NR-R are logically independent.

---

## 4) Minimum declaration set (to activate NR-R)

1. Target specification
- `Sigma*`, `~`, `Pi_rec`, `B`

2. Recovery protocol constraints
- bounded resources
- logged interventions
- reproducible replay
- non-authority clause respected

3. Required reporting
- `P_recover`, `T_recover`, `D_drift`, `R(B)`
- seed robustness
- monitorability status (FPR controllability)
- EST label (`SUPPORTED / CHALLENGED / ESTIMATOR_UNSTABLE / SCOPE_LIMITED`)

---

## 5) Interaction with constraint accumulation

Constraint growth can have opposite effects depending on target:

- toward a stable attractor: may increase recoverability
- toward a prior regime: may decrease recoverability

Therefore NR-R is invalid without explicit target (`Sigma*`) declaration.

---

## 6) Clarification on information loss

NR-R does not require ontological information-destruction claims.

It is strictly operational:

- under bounded budget and declared protocol, can target structure be reconstructed?

This keeps the method engineering-relevant and falsifiable.

---

## 7) Suggested NRM template integration

Add to judgment section:

- `NR-1 Result: PASS / FAIL`
- `NR-R Result: PASS / FAIL`

Add overall classification:

- Reversible
- Tempo-Gated
- Structurally Irrecoverable
- Deep No-Return

Add falsification section for NR-R:

- what evidence would overturn the NR-R verdict?
- what alternative recovery protocols were tested?

---

## 8) Practical value

NR-R prevents a common misclassification:

Correction latency appears acceptable, but structure is already irrecoverable under realistic budget.

It helps separate:

- "too late because too fast" (tempo mismatch)
- "too late because too structured" (recoverability collapse)

---

## 9) One-line summary

NR-1 guards tempo mismatch; NR-R guards structural irrecoverability.

