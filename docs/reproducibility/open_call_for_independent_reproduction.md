---

# Open Call for Independent Reproduction

**FIT v2.4 - Tier-1 reproducibility invitation**

This is a public invitation to reproduce core Tier-1 results under fully declared estimator tuples and boundary conditions.

---

## Why this call exists

FIT proposes a level-aware, falsifiable language for late-time dynamics, with explicit estimator dependence.

Instead of asking for agreement, FIT asks for replication.

---

## What we are asking you to do

Attempt an independent reproduction of:

- Proposition P11: phase transition signatures in $I/C$
- Testbed: Langton's Ant

Follow a documented protocol and report the outcome (positive or negative) with artifacts.

---

## What counts as a valid contribution

Any of the following outcomes are valuable:

1. Successful reproduction under the declared estimator tuple
2. Partial reproduction with deviations documented
3. Failure to reproduce, provided:
   - estimator tuple is declared
   - boundary conditions are explicit
   - artifacts and run manifests are shared
4. Sensitivity findings (boundary choice, estimator choice, window size, thresholds)

Negative results are first-class scientific outcomes.

---

## How to participate

1. Follow the newcomer reproduction challenge (time box: ~60 minutes).
2. Run the experiment under declared conditions.
3. Collect artifacts:
   - run manifest / config
   - raw time series
   - plots or summaries
4. Report:
   - estimator tuple
   - boundary condition
   - outcome classification (`SUPPORTED` / `CHALLENGED` / etc.)
   - links to artifacts

Internal reference run (for sanity-checking):
- `docs/reproducibility/example_results/langton_ant_p11_golden_result.md`

---

## What happens to your result

- Results should be logged with attribution (issue, PR, or registry entry).
- There is no gatekeeping based on outcome.
- The goal is an auditable evidence trail.

---

## Final note

FIT does not ask you to believe it. It asks you to run it, document what happens, and make the result public.
