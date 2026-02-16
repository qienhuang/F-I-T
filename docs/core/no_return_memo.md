# No-Return Memo (NRM)
## A Time-Gated Judgment Instrument for Evolutionary Systems

Status: core artifact  
Framework: FIT (Force-Information-Time)  
Version: 1.1 (cleaned, v2.x compatible)  
License: CC BY 4.0

---

## Purpose

The No-Return Memo (NRM) is a structured instrument for issuing a time-sensitive, non-normative judgment on whether a system remains within a reversible correction window, or has entered a no-return regime.

The NRM answers one operational question:

Can meaningful correction still arrive before irreversible commitment accumulates?

It does not prescribe values, goals, or coercive action.

---

## Core idea

A system enters a no-return regime when the tempo of irreversible commitments exceeds the fastest effective correction channel that can block them.

---

## 0) Metadata

- System name:
- Scope boundary:
- Observation window:
- Author:
- Date / Version:

---

## 1) System definition

### 1.1 State `S`

Define the minimal operational state variables required for this judgment.

- Included variables:
  - `S1`:
  - `S2`:
- Explicit exclusions:
  - (variables intentionally not modeled)

Rule: if a variable is not listed here, it must not be used later in the memo.

### 1.2 Boundary `B`

Define what is inside vs outside the judged system.

- In-boundary components / actors:
- Out-of-boundary components / actors:
- Interfaces capable of irreversible effects:

Ambiguous boundaries invalidate tempo judgments.

---

## 2) Correction channels `K`

A correction channel is any mechanism that can reliably alter or block behavior before irreversible effects accumulate.

List channels `K1 ... Kn`. For each `Ki`, specify:

- Latency `L_Ki`: time from error emergence to effective behavior change
- Bandwidth `BW_Ki`: correction capacity per unit time
- Authority `A_Ki`: can it block irreversible actions, or only recommend

Only channels with blocking authority count toward effective correction latency.

---

## 3) Commitment surface `Omega`

`Omega` is the set of actions that generate irreversible (or high-cost-to-reverse) effects.

List commitments `Omega_1 ... Omega_m`. For each `Omega_j`, report:

- Commit rate `R_Omega_j`
- Blast radius `BR_Omega_j`
- Reversibility cost `C_rev_Omega_j`

Reversibility must be evaluated in practice, not only in principle.

---

## 4) Tempo inequality (NR-1 gate)

Define:

- External correction latency:
  - `L_ext = min(L_Ki)` over channels with blocking authority
- Effective commitment tempo:
  - `w_j`: irreversibility weight increasing in `BR_Omega_j` and `C_rev_Omega_j`
  - Example: `w_j = (BR_Omega_j / BR_ref) * (C_rev_Omega_j / C_rev_ref)`
  - `R_eff = sum_j (w_j * R_Omega_j)`
  - `T_commit ~= 1 / R_eff`

NR-1 condition:

- If `L_ext > T_commit`, the system is tempo-gated no-return under declared scope.

Record:

- Estimated `L_ext`
- Estimated `T_commit`
- `NR-1` result: PASS / FAIL

---

## 5) Constraint dynamics `C_hat`

Constraints represent structural lock-in that reduces future maneuverability.

Select 1-3 proxies `C_hat_1 ... C_hat_k` and report:

- Proxy definition
- Trend direction (up / down / flat)
- Evidence source

NR-2 lock-in clause (supporting diagnostic):

- If `C_hat` trends upward and correction channels are not strengthening (`L_ext` not decreasing), structural lock-in is increasing.

---

## 6) Primary failure mode

Choose one dominant failure mode:

- `F1` lock-in: correction arrives but cannot change behavior
- `F2` drift: behavior changes faster than monitoring tracks
- `F3` estimator instability: metrics lose decision relevance
- `F4` tempo inversion: commitment accelerates under uncertainty

Secondary modes may be noted, but one primary mode must be declared.

---

## 7) Judgment

- Judgment: Reversible / No-Return
- Confidence: Low / Medium / High

### Falsifiability clause

Specify minimum evidence that would overturn this judgment.

If no falsification condition can be stated, the memo is invalid.

---

## 8) Minimal intervention (optional, bounded)

Interventions may be listed only if they:

- reduce `Omega` (commitment surface), or
- reduce `L_ext` (correction latency),

without expanding system scope.

For each intervention:

- Which `Omega` component is reduced
- Which `K` channel is strengthened
- Residual risks

---

## 9) Non-authority clause

The NRM is advisory. It must not be used as an autonomous basis for coercive action.

Its function is structural time judgment under declared scope.

---

## 10) Interpretation note

A no-return judgment does not imply:

- moral failure
- inevitable collapse
- absence of alternative systems

It implies only that local correction within declared boundary is no longer temporally viable.

---

## 11) Position in FIT

NRM operationalizes:

- `T` as a gate (not background time)
- `C_hat` as directional accumulation
- failure as tempo mismatch under constraints

It is a selection-relevant diagnostic instrument, not a total theory.

---

## 12) Optional extension (NR-R)

Use recoverability gate when needed:

- Extension document: `docs/core/no_return_memo_recoverability_extension.md`
- Companion lens: `docs/core/recoverability.md`

NR-R answers a distinct question:

Even if correction can arrive in time, is target structure still recoverable under bounded budget?

