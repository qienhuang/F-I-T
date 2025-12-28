# Irreversible Operations: the safety failure mode you get from shipping faster

This is a draft intended for a LessWrong post. It is written to be actionable for people who ship AI systems (or govern the teams that ship them).

---

## TL;DR

- A lot of AI safety risk is not "the model is misaligned" or "the model is brittle" - it's that the system crosses **irreversibility thresholds** where future correction becomes infeasible.
- Call these changes **Irreversible Operations (IOs)**: actions that permanently remove rollback, transfer control to opaque components, or lock in trajectories.
- The practical driver is **tempo mismatch**: system updates happen faster than evaluation, governance, and incident learning can keep up.
- Proposal: **Minimum Viable Tempo Governance (MVTG)** - five minimal controls that apply *only* to IO-classified actions (slow authority, rollback windows, tempo stratification, circuit breakers, adversarial audit).
- If you manage an AI system: you can audit for IO risk this week using the checklist below.

---

## The intuition: two patterns you have probably seen

### Pattern A: "We just ship faster now"

The team increases release frequency because it feels safer and more responsive. But evaluation and review do not speed up proportionally. Incidents start recurring faster than fixes can be validated. Eventually the org reaches a point where rollback is technically possible but practically meaningless because too many things have changed.

This is a **tempo-escalating IO**: you permanently raise maximum update tempo without synchronizing governance tempo.

### Pattern B: "Rollback exists, until it doesn't"

Rollback procedures exist on paper, but rehearsals get skipped. Backups get thinner. Dependencies accumulate. At some point, an incident happens and rollback fails under real stress.

This is a **rollback-removing IO**: recovery paths erode gradually until they fail when needed.

---

## What is an Irreversible Operation (IO)?

An **Irreversible Operation (IO)** is any system-level action that **permanently reduces your future options to correct the system** within acceptable bounds (time, cost, legal exposure, trust, governance capacity).

IOs can be technical, organizational, or institutional. A change is an IO if it does at least one of the following:

1. **Collapses option space:** some future system states become unreachable again.
2. **Eliminates rollback:** restoring prior behavior is no longer feasible in practice.
3. **Locks in trajectory:** alternative technical or governance pathways become prohibitively costly.
4. **Transfers control:** effective authority shifts to components or actors that cannot be meaningfully audited, paused, or constrained.

Key point: IOs often look like "process optimizations." They can accumulate quietly.

---

## A minimal taxonomy (four IO types)

1. **Tempo-escalating IOs**  
   You permanently increase how fast high-impact changes can be deployed.

2. **Rollback-removing IOs**  
   You remove or degrade the ability to revert (including by neglect).

3. **Control-transferring IOs**  
   You shift decision authority to opaque or non-intervenable components.

4. **Diversity-collapsing IOs**  
   You eliminate alternatives (single vendor, single model, single pathway) and lose fallback routes.

---

## What to measure (IO risk indicators)

You don't need perfect theory to measure risk. Start with auditable signals:

- **Update velocity ratio:** how often you ship consequential changes vs how often you finish meaningful evaluation/review.
- **Rollback success rate + rehearsal frequency:** can you actually revert under stress, and how often do you prove it?
- **Opaque-decision fraction:** what share of critical decisions are mediated by components you can't audit or override in time.
- **Single-point dependency index:** how concentrated are your dependencies on one actor, model, or supplier?

By "can't audit or override in time," I mean the decision takes effect faster than oversight can meaningfully intervene. Example: a model auto-approves a loan (or blocks an account) immediately, but human review happens days later, after the action has already propagated.

Optional (provisional) thresholds, just to make this operational:

- Update velocity ratio: yellow at > 3x, red at > 10x
- Rollback success rate: yellow at < 90%, red at < 50%
- Opaque-decision fraction: yellow at > 20% of critical decisions, red at > 50%
- Single-point dependency: yellow at > 60% reliance, red at > 90%

---

## MVTG: Minimum Viable Tempo Governance (five controls)

MVTG is meant to be minimal: it targets only IOs, not everything.

1. **Slow Authority (for IOs only)**  
   High-impact IO actions require enforced delay, dual authorization, and an auditable rationale.

2. **Rollback Windows**  
   Every IO change ships with a bounded period where rollback is guaranteed to work (and is rehearsed).

3. **Tempo Stratification**  
   Separate your system into tempo layers (fast exploration, medium validation, slow constraints) and prevent fast layers from rewriting slow constraints without slow authority.
   Example: your inference pipeline can update hourly, but changes to safety filters or deployment gates require weekly review.

4. **Circuit Breakers**  
   Predefined triggers that pause or downgrade the system when IO-risk indicators spike (so you don't negotiate safety mid-incident).

5. **Adversarial Audit**  
   A standing "red team" function that tries to bypass IO classification, bypass slow authority, and stress-test rollback and circuit breakers.

---

## Actionable checklist (for AI labs / teams)

- [ ] Compare your update tempo to your evaluation + review tempo (compute the ratio).
- [ ] Run one real rollback drill on a production-relevant system this week (measure success and time).
- [ ] List your top 3 single-point dependencies (models, vendors, decision-makers, infrastructure).
- [ ] Classify your last 10 high-impact changes by IO category (tempo / rollback / control / diversity).
- [ ] Identify one place where a "fast layer can mutate slow constraints" and add a slow-authority gate.
- [ ] Define one circuit-breaker trigger you would be willing to automate (even if conservative).

---

## What this is (and is not)

- This is **not** an alternative to alignment research. It's a proposal for keeping correction possible over time.
- This is **not** a claim that we can predict failures precisely. It's about preventing the loss of control capacity.
- It's a framing: treat tempo and reversibility as safety variables, and govern the thresholds where you lose them.

---

## What I want feedback on

- Are the IO categories missing an important class?
- What are the best *leading* indicators of rollback erosion (before rollback fails)?
- What are the most common ways organizations accidentally create tempo-escalating IOs?
- Has anyone seen MVTG-like controls fail in practice? What broke?
- If you think this is already covered by an existing concept/framework: what's the closest match?

Optional context: this post is a slice of a broader framework (FIT: Force-Information-Time) plus toy-system validation notes: https://github.com/qienhuang/F-I-T
