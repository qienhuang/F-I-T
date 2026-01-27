# Failure Map Model v0.1 (Non-LLM)
**Date**: 2026-01-27

---

## Purpose

Train a small supervised model to predict failure labels (e.g., `FPR_FLOOR`, `ESTIMATOR_UNSTABLE`) from candidate parameters.

This model is NOT used to claim scientific truth.
It is a *budget allocator* that biases exploration away from known-dead regions and toward the feasibility frontier.

---

## Minimal pipeline

1) Build a dataset from `run_log.jsonl`:
   - features: candidate params (W, smoothing, family, calibration, etc.)
   - labels: primary failure label

2) Train:
   - DecisionTreeClassifier (fast, interpretable) or
   - GradientBoosting (if available)

3) Export:
   - feature importance (rough)
   - tree rules (for human reading)
   - predicted feasibility heatmap (optional)

---

## Safety / anti-Goodhart rules

- Model never overrides gates. Gates are ground truth.
- Model cannot change boundaries or evaluation protocol.
- Model is for *sampling bias*, not acceptance.

---
