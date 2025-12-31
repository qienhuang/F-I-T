# Tempo & Irreversibility Controls: A 2-Week Pilot for AI Teams

*A minimal governance pilot based on the FIT framework (Force–Information–Time)*

---

## Why this matters

Most AI safety discussions focus on capabilities or alignment techniques. This proposal focuses on something more mundane but equally critical: **operational tempo** — how fast your system changes relative to how fast you can evaluate and correct those changes.

When update cycles outpace evaluation cycles, you lose the ability to catch problems before they compound. This isn't a theoretical risk; it's a pattern that shows up in incident post-mortems across the industry.

---

## The core idea

Track two things:

1. **Tempo mismatch**: Are changes happening faster than evaluations can close?
2. **Irreversible operations (IOs)**: Which changes permanently shrink your future correction options?

If tempo mismatch persists and IOs accumulate, your system drifts toward states that are hard to recover from — even if surface metrics look fine.

---

## Three dashboard metrics

These can be computed from existing CI/CD and evaluation logs:

| Metric | Definition | Why it matters |
|--------|------------|----------------|
| **Validation Lag (VL)** | Time from change-effective to evaluation closure | High VL = you're flying blind |
| **Rollback Drill Pass Rate (RDPR)** | % of rollback rehearsals completing within RTO/RPO | Low RDPR = rollback is theater |
| **Gate Bypass Rate (GBR)** | Rate of bypassing required gates for high-impact changes | High GBR = gates are decorative |

---

## Minimal IO register

Define IOs as changes that permanently shrink feasible future correction pathways under bounded cost/time.

| Category | Examples |
|----------|----------|
| **Data IO** | Non-reproducible sources, irreversible filtering, major mixture shifts |
| **Evaluation IO** | Shortening/removing gates, allowing fast paths |
| **Alignment IO** | Policy/execution changes that reduce auditability or override capacity |
| **Deployment IO** | Expanding exposure scope, removing staging boundaries |
| **Supply-chain IO** | Non-auditable components in critical paths |
| **Optionality IO** | Removing redundancy, single-point dependency lock-in |

---

## The pilot (2 weeks)

### Week 1: Baseline

1. Instrument VL, RDPR, GBR from existing logs (no new tooling needed).
2. Label the last 30–90 days of high-impact changes using the IO categories above.
3. Map IOs to any known incidents, rollbacks, or near-misses.

### Week 2: Analysis

1. Compute tempo ratios: `tau_update / tau_evaluation` for different change types.
2. Identify clusters: Which IO categories correlate with incidents?
3. Draft thresholds: What VL/GBR/RDPR values would have caught problems earlier?

### Deliverable

A one-page report answering:
- Where is tempo mismatch highest?
- Which IO categories are accumulating fastest?
- What's the lowest-friction intervention that would improve early warning?

---

## Success criteria

The pilot succeeds if it produces **actionable findings** — even (especially) if those findings reveal problems. The goal is not to prove the framework works; it's to surface patterns that existing metrics miss.

---

## Connection to FIT

This pilot operationalizes two FIT concepts:

- **Tempo (T)**: The ratio between update cadence and governance/evaluation cadence determines whether corrections can keep pace with drift.
- **Constraint structure (C)**: IOs are changes that modify the reachable state space — they're not just "risky changes" but changes that alter what future corrections are even possible.

For the full theoretical background, see:
- [FIT v2.4 specification](https://github.com/qienhuang/F-I-T/blob/main/docs/v2.4.md)
- [Tier-2 predictions register (English)](https://github.com/qienhuang/F-I-T/blob/main/papers/preprint_intl/tier2_predictions_register.en.md)
- [Tier-2 predictions register (中文)](https://github.com/qienhuang/F-I-T/blob/main/papers/chinaxiv/chinaxiv_tier2_predictions_register.zh_cn.md)

---

## Contact

Questions or interested in running a pilot? Open an issue on the [FIT repository](https://github.com/qienhuang/F-I-T) or reach out directly.
