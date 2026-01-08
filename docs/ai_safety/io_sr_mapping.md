# IO-SR Mapping (Self-Referential IOs) to FIT IO Classes

This is a companion to `docs/ai_safety/self_referential_io.md`. It maps each IO-SR entry to FIT’s broader IO classes and to the minimal dashboard metrics used for governance.

**Purpose**: help teams answer, quickly and consistently:

- “What kind of irreversibility is this change creating?”
- “Which metric(s) should move first if we are getting into trouble?”

---

## FIT IO Classes (quick refresher)

- **IO-T (tempo-escalating)**: compresses cycle time; increases change velocity beyond governance closure.
- **IO-R (rollback-removing)**: makes rollback/purge impractical; the system cannot return to a prior state within bounded cost/time.
- **IO-C (control-transferring)**: moves authority into opaque, hard-to-override, or self-approving paths.
- **IO-D (diversity/optionality-collapsing)**: removes fallback routes, independent evaluators, or alternative pathways.

## Minimal dashboard metrics

- **VL (Validation Lag)**: change-effective -> evaluation closure
- **RDPR (Rollback Drill Pass Rate)**
- **GBR (Gate Bypass Rate)**: bypass of IO-relevant gates

---

## Mapping table

| IO-SR | Primary IO class(es) | What changes | Early warning metrics | Extra signals (recommended) |
|------:|-----------------------|--------------|------------------------|-----------------------------|
| IO-SR-1 | IO-T, IO-C | Unbounded tool-use / planning loops | VL, GBR | loop depth/time/calls; tool invocation rate; kill-switch activations |
| IO-SR-2 | IO-C, IO-R | Model-generated policy updates | VL, GBR, RDPR | policy provenance integrity; diff approval latency; regression-suite failure rate |
| IO-SR-3 | IO-R, IO-C | Persistent memory write-back | RDPR, VL | purge success rate; anomaly/poison indicators; memory audit sampling coverage |
| IO-SR-4 | IO-C, IO-D | Self-eval used as a gate | GBR, VL | self-eval vs external-eval disagreement rate; **consecutive disagreement count** (triggers mandatory human review); override latency; evaluator diversity count |
| IO-SR-5 | IO-T, IO-R | Continuous deployment of high-impact behaviors | VL, RDPR, GBR | incident rate per release; staged rollout coverage; freeze/circuit-breaker activations |

---

## Notes (how to use this)

1. **If it’s IO-T-first**, treat VL as your “canary”. If VL is consistently rising, governance is becoming retrospective.
2. **If it’s IO-R-first**, require drills. Paper rollback is not rollback. RDPR is the hard check.
3. **If it’s IO-C-first**, watch for self-approval and bypass. GBR tends to climb quietly before incidents.
4. **If it’s IO-D-first**, track independence. Losing independent evaluators often looks like “efficiency” right before it looks like “surprise”.

For the operational controls (evidence, IO-only gate, circuit breakers, and templates), see `docs/ai_safety/self_referential_io.md`.
