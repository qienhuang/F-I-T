# FIT v3 (Research Annex): Deliverables-First Roadmap

This folder is the **v3 research annex** for FIT. It is intentionally not the place where we "upgrade" the core 2.x spec by adding more mathematics.

**v2.x** governs discipline and evidence format (EST, coherence gates, monitorability/FPR floors, holdouts, repo-safe artifacts).  
**v3** is where new theoretical candidates live **until** they produce runnable artifacts with explicit scope + failure semantics.

## Promotion rule (v3 -> core)

Nothing in v3 is "core" until it has:

1) a preregistered boundary + window,  
2) a runnable protocol (repo command),  
3) auditable artifacts (tables/figures/JSON),  
4) explicit failure semantics (`INCONCLUSIVE` / `ESTIMATOR_UNSTABLE` / `NON_MONITORABLE`, etc.),  
5) at least one negative result recorded as a scope boundary (not silently patched away).

If a claim cannot be expressed as **prereg + artifacts + failure semantics**, it stays a research note.

---

## v3 deliverables (3 falsifiable projects)

Each deliverable must land as: **one toy + one real dataset + one failure mode**.

### Deliverable 1: Windowed I-C coupling efficiency (Gamma_W)

**Question**: when coherence holds, can we estimate a stable, window-scoped "conversion efficiency" between information and constraints?

Candidate estimator family (examples):

- `Gamma_W := slope(I ~ C) within window W` (robust regression)
- `Gamma_W := Delta I / Delta C` between window endpoints (guarded by Delta C != 0)

**Toy** (ML dynamics):

- Target: grokking-style regime shift windows (event E1), then compute `Gamma_W` pre/post event.
- Required artifacts:
  - `gamma_windowed.csv` (per-run, per-window)
  - `gamma_summary.md` (mean, dispersion, failure labels)
  - `gamma_windows.png` (one figure)

**Real** (NYC TLC):

- Target: compute `Gamma_W` only within coherence-passing windows (`OK_PER_YEAR` / `OK_PER_WINDOW`), and explicitly refuse pooled claims if pooled coherence fails.
- Suggested entry point:
  - `experiments/real_world/nyc_tlc_tier2p1/RESULTS.md`

**Failure semantics**:

- `ESTIMATOR_UNSTABLE` if coherence fails at the claimed scope.
- `DATA_MISSING` if the window has too few points.
- `UNDEFINED` if `Delta C` is too small / numerically unstable.

---

### Deliverable 2: Minimal constraint structure (2x2 / 3x3) as an estimator-family extension

**Question**: can we make "constraint structure" more explicit without turning FIT into an unfalsifiable tensor narrative?

Minimal move:

- Treat structured constraints as estimators, not as a re-definition of FIT primitives:
  - `C_hat(t)` as a small matrix/graph derived from a constraint proxy family within a window.
  - Report only **window-scoped** summaries (eigenvalues, conditioning, stability), not universal metaphysics.

**Toy**:

- Use any toy system with at least 2-3 constraint proxies and known perturbations (e.g., a small simulator or training loop) to test whether the structure estimate is stable under resampling.

**Real**:

- NYC TLC already provides a clean 2-proxy cost family; additional proxies should be preregistered and treated as an estimator-family extension (not retrofitted).
- AFDB-style cases provide natural multi-proxy confidence families for 3x3 structure checks.

**Required artifacts**:

- `constraint_structure_windowed.csv` (per-window matrix summary)
- `eigs_windowed.csv`
- `structure_stability_report.md` (explicitly lists where it breaks)

**Failure semantics**:

- `ESTIMATOR_UNSTABLE` if structure flips sign/ordering across reasonable estimator variants.
- `ILL_CONDITIONED` if the matrix is numerically degenerate at the declared scale.

---

### Deliverable 3: Detectable phase-break signatures (PT-MSS-lite, without new topological invariants)

**Question**: can we preregister a *minimal* signature set for "structure break" that is detectable and honest about non-evaluability?

Minimal signature set (example; must be preregistered per domain):

- **S0 (Scope break)**: coherence status changes across scopes (e.g., pooled FAIL but windowed PASS).
- **S1 (Force redistribution)**: a robust change-point signal in a declared observable (e.g., `dR/dt` peaks).
- **S2 (Information re-encoding)**: a stable shift in an information proxy within a window (entropy/MI-like estimator).

**Toy**:

- Grokking: E1 jump event + alarm usability (FPR floor, abstain/coverage).
- Required artifacts: event times, usability at operating points, and a "do not interpret" label if non-monitorable.

**Real**:

- NYC TLC: treat pooled-vs-windowed coherence as S0, and any change-point outputs as diagnostic unless coherence passes at that scope.

**Required artifacts**:

- `phase_break_events.json` (machine-readable)
- `pt_mss_summary.md` (what passed/failed where)
- `pt_mss_onepage.png` (optional)

**Failure semantics**:

- `NON_EVALUABLE` (no events / no negative support)
- `NON_MONITORABLE` (FPR floor too high / threshold not controllable)
- `ESTIMATOR_UNSTABLE` (coherence fails)

---

## What is already "hard" evidence (v2.x layer)

If you want runnable, auditable Tier-2 material, start here:

- Tier-2 plan: `docs/TIER_2_DETAILED_PLAN.md`
- Monitorability benchmark: `docs/benchmarks/gmb_v0_4/README.md`
- Real-world EST-gated case: `experiments/real_world/nyc_tlc_tier2p1/RESULTS.md`
- Policy/tool-use gating demo: `examples/dr_one_demo/results/README.md`

## Continuous-time track (theorem-first)

If you want the continuous-time v3.0-C "toy theorem" direction:

- `docs/v3/fit_continuous_toy_paper.md`
- `docs/v3/fit_continuous_toy_paper.zh_cn.md`

