# FIT-Synth loop (FIT-Explorer v0.1)
*A constrained exploration loop: failure label -> admissible actuators -> prereg -> evaluation.*

---

## 0) Core loop

1. Generate candidate variants (Explore)
2. Diagnose failure label(s) on evaluation traces
3. Select actuators allowed by the Synthesis Playbook
4. Mutate candidate within allowed actuators (budgeted)
5. Lock (preregister) boundary + estimators + gates + stop conditions
6. Evaluate
7. Record:
   - feasible leaderboard
   - failure map (with diagnostics)
8. Repeat until budget exhaustion

---

## 1) Why this avoids Goodhart

- Boundary changes require a new preregistered candidate class.
- Every mutation is justified by a failure label + allowed actuator.
- Stop conditions prevent endless post-hoc "fixing".

