# Search Spaces for FIT-Math Explorer (v0.1)
**Date**: 2026-01-27

This document defines what “method space” means for mathematical discovery.

---

## 1. Representation space (effective variables / invariants)

These are candidates for $g(x)$ or structure maps that compress complexity.

Examples:
- global order parameters (density, magnetization)
- multi-scale statistics (block variance/entropy across scales)
- correlation proxies (lag-1 AC, agreement rate)
- spectral low-frequency dominance

In mathematics proper, analogs include:
- invariants (rank, dimension, homology)
- normal forms (canonical representations)
- equivalence relations that preserve the goal

---

## 2. Lemma space

Candidates for intermediate statements that:
- shorten proof depth,
- reduce branching,
- increase reuse.

In the explorer, represent lemmas as structured templates:
- preconditions
- conclusion schema
- tactic proof skeleton (optional)

---

## 3. Strategy space (proof plans)

A proof plan is a graph of transformations/tactics:
- rewrite normalization
- induction structure
- decomposition into subgoals
- refutation via counterexample search (when applicable)

---

## 4. Composite candidates

The most realistic unit is a pipeline:
- representation  + lemma library  + strategy policy  + budgets  + gates

This matches FIT-Explorer’s “pipeline” mindset.

---

## 5. YAML schema pointers

See:
- `docs/explorers/fit_explorer/search_space/fit_math_search_space_v0.1.yaml`
