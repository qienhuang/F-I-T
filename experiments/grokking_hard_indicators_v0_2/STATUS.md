# Status (v0.2)

As of 2026-01-21, **v0.2/v0.2.1 are complete as a reproducible, held-out evaluation pipeline**, but they are **not yet a validated “hard indicator”** in the strong sense.

## What is “done” (strong claim we can make)

- **Protocol/pipeline success:** Explore -> Lock -> Evaluate works end-to-end on held-out seeds.
- **Evaluability fixed:** the primary event is **E1 (jump/regime shift)**, which yields dense events in Phase B (25/25 runs had an E1 under the current boundary), so Phase B is not “NaN / no-event” anymore.
- **Reproducibility materials exist:** this folder contains a runnable snapshot (`code/`) plus a locked-ish protocol draft.

## What is *not* done yet (claim we should not make)

- **Hard-indicator validation (strong):** the baseline remains **unstable across held-out seed blocks**:
  - In v0.2 eval seeds (`100–119`), `score_sign=-1` tends to improve ranking-style metrics (ROC-AUC / AP).
  - In v0.2.1 eval seeds (`120–139`), the alarm-style orientation (`score_sign=+1`) yields non-zero low-FPR coverage (but ranking metrics are weak on fresh seeds).
  This is not yet a clean “hard indicator verified” story.

## What can be published now (low-risk)

- A clean **v0.2 technical report / reproducibility note**:
  - the prereg-style evaluation setup;
  - why plateau events are often not evaluable;
  - why jump events improve evaluability;
  - baseline results reported honestly as modest/early signal.

## Where the results are recorded

- `RESULTS_v0.2_v0.2.1.md`
- `results/v0.3_A1_component_diagnosis.md`
- `results/v0.3_A2_fpr_tradeoff.md`
- `results/structural_v0_6/structural_candidates_summary.md`

## Structural candidate screen (v0.6, held-out seeds 140–179)

Structural follow-up runs are now complete on the shared held-out block:

- `control`: `unembed.weight`
- `A`: `embed.weight`
- `B`: `encoder.layers.0.self_attn.in_proj_weight`
- `C`: `encoder.layers.1.self_attn.in_proj_weight`

Readout from `results/structural_v0_6/structural_candidates_summary.md`:

- **Candidate A** is the strongest screen result:
  - preferred sign `+1`
  - median AUC `0.5874` vs control `0.4546`
  - lead@FPR coverage `30/40 = 0.75` vs control `17/40 = 0.425`
  - median lead `15250` steps vs control `11500`
- **Candidate C** is also positive but weaker than A on low-FPR usefulness:
  - preferred sign `+1`
  - median AUC `0.5969`
  - lead@FPR coverage `24/40 = 0.60`
  - median lead `14750` steps
- **Candidate B** does not improve the hard-indicator objective:
  - preferred sign `-1`
  - median AUC `0.3871`
  - lead@FPR coverage `12/40 = 0.30`

Current decision point:

- treat **A** as the primary structural candidate for the next locked run,
- keep **C** as a secondary comparison,
- drop **B** unless a different objective favors ranking over low-FPR alarm coverage.

## What to do next (v0.3 direction)

- Keep the “ranking vs alarm” objective distinction explicit, and decide which one is primary.
- Lock the next run around **Candidate A** (and optionally **C**) on fresh held-out seeds.
- Improve the estimator tuple (still preregistered): add 1–3 cheap-to-log indicators and re-evaluate on fresh held-out seeds.
- Keep Phase discipline strict: no threshold or model changes on eval seeds.
