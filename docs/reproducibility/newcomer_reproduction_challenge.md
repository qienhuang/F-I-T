---

# FIT Newcomer Reproduction Challenge

**60 minutes to reproduce a core FIT Tier-1 result**

Goal: reproduce a core proposition end-to-end and produce a concrete pass/fail record with artifacts.

---

## 0) What You Will Prove (and What You Will Not)

You will demonstrate:

- a FIT proposition can be reproduced end-to-end
- boundary conditions matter as constraints (a central FIT lesson)
- estimator tuples make claims auditable and falsifiable

You will NOT need:

- deep knowledge of FIT theory
- to derive new equations
- to invent new estimators

This is a reproducibility challenge, not a theory exam.

---

## 1) Target Result

Proposition: **P11 - Phase transition signatures in $I/C$**

Testbed: Langton's Ant

Expected contrast:

- Open boundary: chaotic motion -> "highway" regime, with a clear transition signature
- Periodic boundary: transition is suppressed (boundary introduces an artificial global constraint)

This contrast is the point of the challenge.

---

## 2) Prerequisites (5 minutes)

- Python >= 3.10
- Git

Clone:

```bash
git clone https://github.com/qienhuang/F-I-T.git
cd F-I-T
```

Install minimal deps if needed:

```bash
pip install numpy matplotlib pyyaml
```

---

## 3) Declared Estimator Tuple (Do Not Change)

Write down the estimator tuple you are using (copy this block into your report):

```yaml
system: "Langton's Ant"
boundary: "open"
F_hat: "displacement_alignment"
C_hat: "trajectory_R2"
I_hat: "grid_compression_proxy"
window_W: 104
```

If you change the tuple, you are running a different experiment. That's allowed, but it is no longer the reproduction challenge.

---

## 4) Step-by-Step Reproduction (40 minutes)

### Step 1 - Open Boundary Run (20 minutes)

Run the open-boundary implementation:

```bash
python experiments/v2_fixed/langton_open_final.py
```

What to look for:

- a transition around ~8,000-12,000 steps (approximate)
- a regime change from 2D wandering to near-linear displacement
- late-time stabilization (post-transition behavior looks qualitatively different)

Save:

- the console output
- any generated plot(s)
- any generated data files

If the script writes files, keep them together in a folder and do not edit them.

### Step 2 - Periodic Boundary Control (10 minutes)

Run the historical periodic version (expected to fail to show the highway):

```bash
python experiments/v1_initial/langton_fit_experiment.py
```

What to look for:

- no clear highway regime
- no comparable transition signature

### Step 3 - Artifacts Check (10 minutes)

You should be able to answer (in one paragraph):

- which boundary did you run?
- which estimator tuple did you use?
- did you observe the transition signature?

---

## 5) Report Your Result (Pass / Fail)

PASS (expected for open boundary):

- observable transition signature
- stable post-transition regime

FAIL (acceptable, but must be documented):

- no transition within the horizon
- numerical issues
- unclear or unstable metrics

Failure is not disqualifying; undocumented failure is.

---

## 6) Submit Your Result

Open a GitHub issue (or record a local entry) including:

- the estimator tuple (as YAML)
- boundary condition
- outcome classification: `SUPPORTED` or `CHALLENGED`
- artifacts (attach or link)
- one paragraph interpretation

If you ran both boundaries, include both outcomes.

Reference (internal example record):
- `docs/reproducibility/example_results/langton_ant_p11_golden_result.md`

---

## 7) Why This Matters

This challenge demonstrates three FIT commitments:

1. Level awareness: claims are meaningful only under declared estimators
2. Boundary as constraint: boundary choice changes reachable regimes
3. Falsifiability: outcomes can differ across scopes, and we record both
