# Prereg Template (FIT/EST Session)

Copy/paste and fill the placeholders. Keep this file unchanged during Phase B.

## 0) Metadata

- Case ID:
- Date:
- Objective: (alarm / constrained exploration / benchmark / paper note)
- Public scope: (OK to publish artifacts? yes/no; what must be redacted?)

## 1) Boundary (locked for Phase B)

- In-scope system:
- In-scope data source(s):
- Data license/permission (real-world only):
- Time boundary / pinned release:
- Allowed variations:
- Forbidden changes:

## 2) Window + event definition (locked for Phase B)

- Time unit: (steps/checkpoints/requests/days)
- Cadence: (every K steps / every request / daily)
- Window length `W`:
- Primary event definition:
- Secondary event definition (optional):

## 3) Estimator tuple and estimator family (locked for Phase B)

- Estimator tuple:
  - `E_state`:
  - `E_constraint`:
  - `E_force`:
- Estimator family for robustness check (min 2):
  - Alt 1:
  - Alt 2:

## 4) Operating point (alarms only; locked for Phase B)

- Target FPR:
- Required reporting:
  - achieved FPR
  - `fpr_floor`
  - `feasible`
  - coverage
  - lead time

## 5) Phase split (A vs B)

- Phase A (definition selection; NOT evidence)
  - Seeds / runs:
  - What can be chosen here:
  - Output artifacts:

- Phase B (frozen evaluation; evidence)
  - Hold-out seeds / runs:
  - Locked items list:

## 6) Primary outcomes and failure semantics

- Primary outcome(s):
- Secondary outcome(s):

- Failure semantics (choose before running):
  - NON-EVALUABLE (event density too low):
  - NON-MONITORABLE (FPR floor too high / FPR not controllable):
  - WEAK BASELINE (feasible but low coverage at target FPR):
  - INCONCLUSIVE (missing contract items or missing artifacts):

## 7) Commands to reproduce (locked for Phase B)

- Environment setup:
- Run command(s):
- Summarize command(s):

## 8) Artifact contract (paths)

- Input manifest:
- Raw logs:
- Summary table(s):
- Figures:
- Run metadata (version/hash):

