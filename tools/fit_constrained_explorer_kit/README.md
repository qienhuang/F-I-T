# FIT Constrained Explorer Kit (non-LLM path exploration)

This kit targets a different need than `tools/fit_proxy_alarm_kit`:

- **Proxy alarm kit**: monitorability under explicit low-FPR constraints.
- **Constrained explorer kit (this)**: given **constraints** and a **large design space**, do **budgeted path exploration** and return the best feasible candidates, plus an auditable trace.

It matches the three-layer discipline discussed in `discussions/reading_notes/FIT通用非LLM小模型/discussion-01.md`:

- **Layer 0 (locked prereg)**: search space, constraints, objective/oracle, budget, and success criteria.
- **Layer 1 (deterministic engine)**: candidate generation + constraint checks + oracle calls + surrogate training + artifacts.
- **Layer 2 (LLM assistant)**: optional; generates prereg drafts or writes reports, but never changes Layer 0/1 logic.

This is conceptually similar to BioArc (NAS over architecture space with constraints + evaluation budgets).

## Quickstart (smoke)

```bash
pip install -r requirements.txt
python -m fit_constrained_explorer_kit.run --prereg PREREG.fixture.yaml --run_id fixture
```

Outputs (example):

- `out/fixture/PREREG.locked.yaml`
- `out/fixture/trace.csv`
- `out/fixture/best_candidate.json`
- `out/fixture/onepage.pdf`

## What you change for a real BioArc-like case

Replace the toy domain with a real **domain adapter** that defines:

- **Candidate encoding** (architecture / sequence / topology).
- **Constraint check** (hard feasibility gate; cheap).
- **Oracle evaluation** (expensive: train+val score, simulator, wetlab proxy).
- Optional: **surrogate features** for faster search (embeddings, hand-crafted stats).

Then keep the loop the same: exploration policies allocate the oracle budget, while outputs remain fully auditable.
