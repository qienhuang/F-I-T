# Explorer–Verifier Interface v0.1.1
*A hard boundary to prevent “discovery narratives” from being confused with “verified results”.*

**Status**: repo-ready patch (v0.1.1)  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0  

---

## 0. Purpose

This interface makes explicit a high-risk ambiguity flagged in review:

> **The explorer is not the prover. The prover is not the explorer.**

In practice they may be coupled in one system (e.g., one agent that proposes steps and triggers checks),
but their roles must remain **logically separated** and **audit-separated**.

---

## 1. Roles

### 1.1 Explorer
The Explorer is a **proposer**. It may be stochastic, heuristic, or LLM-assisted.

It can produce:
- candidate definitions / invariants
- candidate lemmas / tactics
- candidate proof plans (strategy graphs)
- candidate representations (normal forms)

The Explorer is allowed to be wrong.

### 1.2 Verifier
The Verifier is a **validator** with a strict acceptance interface.

It can:
- type-check / compile / kernel-check proofs
- enforce budget limits (steps/time/memory)
- provide pass/fail and minimal diagnostics

The Verifier is **non-LLM**, deterministic (or at least reproducible), and trusted up to its soundness assumptions.

---

## 2. Trust boundary and the “FPR≈0” nuance

In a proof assistant setting:

- If the kernel is sound and the encoding is correct, the probability of a *false accept* is treated as approximately 0.  
- However, discovery is upstream of verification. The Explorer can still:
  - propose misleading steps,
  - overfit to representation quirks,
  - succeed only under lucky search traces,
  - exhibit `HEURISTIC_FLOOR` (no discriminative guidance).

Therefore:
- **Verifier correctness is not the same thing as discovery reliability.**
- FIT-Math is primarily about making discovery reliability **measurable and auditable**.

---

## 3. Mandatory evidence chain for claims

A candidate may be labeled `SUPPORTED` only if all are true:

1. Verifier artifact exists (proof object / check log / kernel acceptance record).  
2. The artifact is linked by hash/id in the run record.  
3. The run states the boundary and budgets used for verification.  
4. Robustness sweeps (if preregistered) do not flip the outcome beyond the allowed rate.

If any is missing, the strongest allowed label is `BUDGET_INCONCLUSIVE` or `SCOPE_LIMITED` (depending on failure mode).

---

## 4. Coupled systems (search + proof in one loop)

Real systems often interleave proposing and checking.
Examples include “suggest-then-check” workflows and integrated search/prove engines.

FIT-Math treats these as **a coupled system with two channels**:

- Propose channel: Explorer emissions (untrusted)  
- Check channel: Verifier verdicts (trusted gate)  

**Hard rule**: the final label is determined by the check channel, never by the propose channel.

---

## 5. Minimal interface schema (recommended)

### 5.1 Explorer output artifact (proposal)
```yaml
proposal:
  proposal_id: "prop:..."
  candidate_id: "math:..."
  kind: "definition|lemma|tactic|plan"
  content_hash: "sha256:..."
  provenance:
    parent_runs: ["run:..."]
    derived_from: ["candidate:..."]
  notes: "free text"
```

### 5.2 Verifier output artifact (verdict)
```yaml
verdict:
  verdict_id: "ver:..."
  candidate_id: "math:..."
  status: "PASS|FAIL|TIMEOUT|OOM"
  budgets:
    steps: 50000
    wall_time_s: 120
  kernel:
    name: "Lean4"
    version: "x.y.z"
  evidence:
    proof_object_hash: "sha256:..."
    log_hash: "sha256:..."
```

---

## 6. Reporting requirement

Every `SUPPORTED` entry in a leaderboard must contain:
- `verdict_id`
- `proof_object_hash`
- `kernel/version`
- budgets
- sweep outcomes summary

This is the “audit spine” that prevents story-driven progress claims.
