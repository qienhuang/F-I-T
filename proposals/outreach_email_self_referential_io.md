# Outreach Email (Template): Self-Referential IO Controls (Two-Week Pilot)

This file contains short, copy/paste-ready email templates for reaching out to AI safety / release / assurance leads. It does **not** pitch a worldview. It pitches a low-friction pilot with auditable outputs.

All content is provided under CC BY 4.0 (consistent with the repo docs).

---

## Template A (short, plain)

**Subject:** Two-week pilot: governing self-eval, tool loops, and memory write-back (IO risk)

Hello [Name/Team],

I’m an independent researcher working on deployment safety failure modes that show up when systems gain **self-referential capabilities** (tool-use/planning loops, self-evaluation used as a gate, memory write-back, and policy self-modification).

The pattern I’m targeting is not “the model made a mistake”, but **loss of corrective capacity**: evaluation lags behind change velocity, rollback becomes impractical, and bypass paths quietly accumulate.

If this resonates, I’d like to propose a **two-week pilot** that produces auditable outputs:

1) A minimal dashboard: **Validation Lag (VL)**, **Rollback Drill Pass Rate (RDPR)**, **Gate Bypass Rate (GBR)**  
2) An **IO Register** for self-referential changes (5 copy/paste categories)  
3) One rollback (or purge) drill to verify feasibility (pass/fail both informative)

Pilot standard (IO-SR categories + gates + circuit breakers):  
`https://github.com/qienhuang/F-I-T/blob/main/docs/ai_safety/self_referential_io.md`

Pilot proposal (step-by-step):  
`https://github.com/qienhuang/F-I-T/blob/main/proposals/tempo-io-pilot.md`

If you can point me to the right owner for release governance / safety assurance, I can adapt the pilot to your existing process and keep it low-overhead.

Best regards,  
Qien Huang  
Independent Researcher  
Email: qienhuang@hotmail.com  
ORCID: https://orcid.org/0009-0003-7731-4294

---

## Template B (slightly more context, still short)

**Subject:** Self-eval gates and tool loops as irreversibility risks: low-friction pilot

Hello [Name/Team],

I’m reaching out with a small, engineering-first proposal. As systems gain tool-use loops, self-eval gates, and persistent memory, a common failure mode is that the system stays “performant” while becoming structurally harder to correct.

I’m using an “irreversible operation” lens: changes that permanently shrink the feasible option space for correction (because rollback/purge becomes hard, or governance feedback becomes retrospective).

The two-week pilot is intentionally minimal:

- **Metrics:** VL / RDPR / GBR (weekly trend snapshot is enough)
- **Register:** 5 IO categories specific to self-referential capabilities
- **Control:** apply a slow gate only to IO-class changes (routine iteration stays fast)
- **Reality check:** one rollback / purge drill

Reference standard and templates:  
`https://github.com/qienhuang/F-I-T/blob/main/docs/ai_safety/self_referential_io.md`

If you’d like, I can also share a toy demo notebook that shows the difference between “self-eval as gate” vs “independent evaluators + coherence gate” in a small controlled setup.

Best,  
Qien Huang

---

## Template C (follow-up after 5–7 days)

**Subject:** Follow-up: two-week IO pilot for self-eval/tool-loop changes

Hello [Name/Team],

Just following up in case this was buried. The ask remains small: a two-week pilot using VL/RDPR/GBR + an IO register for self-referential changes + a rollback/purge drill.

If you can share the right contact (release owner / safety assurance / evaluation owner), I’ll keep the pilot scoped to whatever you already track.

Links:  
`https://github.com/qienhuang/F-I-T/blob/main/docs/ai_safety/self_referential_io.md`  
`https://github.com/qienhuang/F-I-T/blob/main/proposals/tempo-io-pilot.md`

Best,  
Qien Huang

