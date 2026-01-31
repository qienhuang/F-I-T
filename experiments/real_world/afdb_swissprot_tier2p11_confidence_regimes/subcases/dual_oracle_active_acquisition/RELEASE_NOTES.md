# Release notes — Dual‑Oracle Active Acquisition subcase

This file documents how the subcase evolved across releases **v2.0 → v2.8**, and how **v2.9** converges the repo to a canonical subcase name.

> Important: the “version number” refers to the **subcase pack evolution** (how we enforce boundary discipline and publishable claims), not to changes in the underlying AFDB dataset or the core estimator semantics.

---

## v2.9 — Canonicalization (repo convergence)

**Goal:** stop proliferating subcase directories; keep one canonical subcase:

- Canonical directory name: `dual_oracle_active_acquisition/`
- The functional core is unchanged relative to v2.8:
  - bilevel robustness evaluation
  - two‑key gate + graded claims
  - policy-card claims overlay operationalization

**What changed:**

- Updated `PREREG.yaml` / `PREREG_SMOKE.yaml` metadata (`case_id`, `pack_version`).
- Updated CI messages and Claims Pack headers to use “canonical v2.9”.
- Added `scripts/aggregate.py` as a stable, version‑agnostic aggregation entrypoint (wraps the latest stable aggregator implementation).
- Added this `RELEASE_NOTES.md` and a `MIGRATION_GUIDE.md`.

---

## v2.8 — Policy-card operationalization layer

**Added:** a “claims overlay” layer that **propagates gate/claim constraints into each policy card**, so narrative cannot silently diverge from preregistered gates.

**Key artifacts:**

- `policy_cards/claims_overlay.json`
- each `policy_cards/<policy>.md` includes `## Claims & gate status (generated)`

---

## v2.7 — Two‑key gate + graded claims

**Upgraded:** from a single robustness gate to a **two‑key gate** and introduced **graded claims**:

- `strong`: both keys pass ⇒ allow “outperforms random”
- `weak_*`: only one key passes ⇒ allow directional/qualified language only
- `none`: no advantage language

(Exact gate metrics are specified in `PREREG.yaml` and exported in `claims_gate_report.json`.)

---

## v2.6 — CVaR / expected shortfall gate

**Primary gate:** moved from tail-quantile summaries to **CVaR (expected shortfall)**:

- operationally: “the average of the worst α‑fraction of outcomes must still show positive margin”
- more stable than one-point quantiles

Tail quantile metrics remain as audit views.

---

## v2.5 — Tail-quantile sweep discipline

**Added:** preregistered **tail quantile sweep** and removed analyst freedom to cherry-pick a tail quantile.

**Primary statistic:** min-over-q tail margin (for preregistered `tail_quantiles`).

---

## v2.4 — Tail-robust operational advantage gate

**Strengthened:** from mean‑margin robustness to a **tail‑margin** robustness gate to reduce sensitivity to rare bad runs.

---

## v2.3 — Bilevel bootstrap robustness

**Added:** bilevel bootstrap (baseline seeds × policy seeds) to separate:

- baseline uncertainty
- policy-run stochasticity

and to produce robust margin confidence intervals.

---

## v2.2 / v2.1 / v2.0 — Early hardening line

These releases established the “hardening” discipline:

- multi‑seed random baseline band (not a single baseline run)
- CI‑gated “outperforms random” claim rule
- cost-aware baseline comparison (baseline upper band at the same cost)

They also stabilized the artifact contract that later versions extended.

---

## Compatibility notes

- The canonical subcase uses `scripts/aggregate.py` and `bash scripts/ci_check.sh`.
- Older versioned aggregators remain in `scripts/aggregate_v2_*.py` for traceability.
- Claims discipline is enforced via `claims_gate_report.json` + `Claims.md` + per-policy card overlay.
