# Phase II Quickstart
## A Practical Walkthrough of Time-Gated Judgment

> Status: Quickstart / Practitioner Guide  
> Framework: F-I-T (Force–Information–Time)  
> Phase: II — Time-Gated Judgment  
> Version: 1.0  
> Author: Qien Huang  
> License: CC BY 4.0

---

## Who This Is For

This guide is for readers who want to **use Phase II correctly** without:
- expanding its scope,
- invoking authority,
- or turning diagnosis into mandate.

It assumes no prior use of FIT artifacts.

---

## What You Will Do

You will perform **one complete Phase II cycle**:

1. Define a system boundary
2. Issue a **No-Return Memo (NRM)**
3. Evaluate the **Tempo Inequality**
4. Decide whether an **Emptiness Window** is admissible
5. State limits and falsification conditions

This is a **diagnostic exercise**, not a policy proposal.

---

## The Example System (Safe, Non-Sensitive)

**System:** Automated CI/CD Deployment Pipeline  
**Context:** Mid-size software organization  
**Reason for choice:**  
- irreversible effects exist (production deploys),
- correction channels exist but are latency-bound,
- domain is familiar and non-political.

---

## Step 1 — Define the System Boundary

### 1.1 State (S)

Minimal operational variables:

- `R`: deployment frequency (deploys/hour)
- `A`: automation level (manual → fully automated)
- `E`: error detection latency (minutes)
- `H`: human blocking authority (can humans stop a deploy?)

Explicit exclusions:
- code quality metrics
- developer intent
- organizational culture

---

### 1.2 Boundary (B)

In-bound:
- CI/CD pipeline
- build & deploy scripts
- production environment

Out-of-bound:
- upstream product strategy
- customer behavior

Commitment interfaces:
- `deploy_to_prod`
- `rollback_prod` (note: rollback ≠ reversal)

---

## Step 2 — Enumerate Correction Channels (K)

List only channels with **blocking authority**.

### K₁: Human approval gate
- Latency: 30–120 minutes
- Authority: Can block deploys
- Bandwidth: Low

### K₂: Automated tests
- Latency: 5–15 minutes
- Authority: Can block deploys
- Bandwidth: Medium

### K₃: Monitoring alerts
- Latency: 1–5 minutes
- Authority: Notify only (no block)

**Effective correction latency:**

```

L_ext = min(L_Ki with blocking authority)
≈ 5–15 minutes

```

---

## Step 3 — Define the Commitment Surface (Ω)

### Ω₁: Production deploy
- Rate: 6–12 per hour
- Blast radius: Medium to high
- Reversibility cost: High (rollback incomplete)

### Ω₂: Schema migration
- Rate: 1–2 per day
- Blast radius: Very high
- Reversibility cost: Very high

Approximate effective commitment tempo:

```

T_commit ≈ 3–10 minutes

```

---

## Step 4 — Apply the Tempo Inequality

Recall:

```

If   L_ext > T_commit
then system enters No-Return regime.

```

Observed:
- `L_ext ≈ 5–15 minutes`
- `T_commit ≈ 3–10 minutes`

Result:
- **NR-1 FAIL (borderline to failing)**

Interpretation:
> Deployments can accumulate irreversible effects faster than the fastest reliable block.

This does **not** mean disaster is inevitable.
It means **steering authority is degraded**.

---

## Step 5 — Assess Constraint Dynamics (Ĉ)

Select 2 proxies.

### Ĉ₁: Pipeline coupling density
- Trend: ↑ (more services, shared deploys)
- Evidence: dependency graph complexity

### Ĉ₂: Automation reliance
- Trend: ↑ (manual gates removed for speed)
- Evidence: CI configuration history

Correction channels are **not strengthening**.
Constraint accumulation is positive.

**NR-2 condition holds.**

---

## Step 6 — Issue the NRM Judgment

**Judgment:** No-Return (conditional)  
**Confidence:** Medium

**Falsification conditions:**
- Introduce a deploy gate with < 2-minute blocking latency, or
- Remove schema migrations from automated deploys.

Without these, steering loss persists.

---

## Step 7 — Evaluate Emptiness Window Admissibility

Check admissibility conditions:

- Ω clearly defined? ✓
- Temporary scope possible? ✓
- Non-expansive authority? ✓
- Window itself reversible? ✓

**Admissible intervention:**

> Temporarily suspend all production deploys and schema migrations  
> while allowing builds, tests, and staging deploys to continue.

Structural effect:
- Ω → ∅ (for prod)
- `T_commit → ∞` (within window)

This **repairs the Tempo Inequality** without prescribing outcomes.

---

## Step 8 — Define Exit Conditions

The window may close only when:

- automated tests block schema migrations independently, or
- a < 2-minute human or automated block is installed upstream.

Closing without change reintroduces the failure mode.

---

## Step 9 — State Non-Authority Clause

This analysis:
- does not assign blame,
- does not mandate action,
- does not evaluate values.

It diagnoses **temporal viability within a defined boundary**.

---

## What You Have Done

You have:

- applied Phase II without overreach,
- issued a falsifiable judgment,
- identified a minimal, bounded intervention,
- preserved reversibility and restraint.

This is **correct Phase II usage**.

---

## Common Mistakes to Avoid

- Treating rollback as reversibility
- Using Phase II to justify urgency rhetoric
- Expanding scope mid-analysis
- Omitting falsification conditions

---

## Closing Note

> Phase II does not tell you what to do.  
> It tells you whether doing anything can still arrive in time.

Use it sparingly.

---
