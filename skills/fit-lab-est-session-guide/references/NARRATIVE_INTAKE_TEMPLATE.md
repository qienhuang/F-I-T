# Stage 0 Narrative Intake (NOT EVIDENCE)

Use this when the user needs a readable overview before committing to the contract.
This output is explicitly exploratory and must end with "what to run next".

## Style choice

- Style A (default): Research memo (concise, technical, decision-oriented)
- Style B: Reader brief (more narrative, still ends with runnable next step)

## Input (ask for the minimum)

- 3-10 sentence case description
- Any available artifacts (paths to logs/plots/results) or "none yet"
- What counts as bad (failure/unsafe/irreversible)
- What counts as good (success/acceptable behavior)

## Output template

1) Case snapshot
   - What we know:
   - What we do not know:

2) Candidate boundary (draft)
   - In-scope:
   - Out-of-scope:
   - Real-world notes (license/time boundary if relevant):

3) Candidate event(s)
   - Event E1 (primary):
   - Event E2 (secondary, optional):

4) Candidate estimators (family, not a single metric)
   - Estimator A:
   - Estimator B:

5) Main failure modes to watch for
   - Non-evaluable (no events)
   - Non-monitorable (FPR floor too high / threshold not controllable)
   - Estimator-dependent (claim flips across estimator family)

6) Next runnable step (single engine)
   - Pick one toolkit:
   - Exact command(s):
   - Expected artifacts:

Hard rule: do not end with a grand conclusion.

