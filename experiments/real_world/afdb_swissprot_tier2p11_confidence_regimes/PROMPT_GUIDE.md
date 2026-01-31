# PROMPT_GUIDE — AFDB Swiss‑Prot Confidence Regimes (Tier2P11)

This case is designed so a non‑specialist can use an LLM tool (local CLI assistant) to:
1) stay disciplined about **EST boundary**,
2) generate analysis notebooks / small scripts,
3) narrate results without over‑claiming biology.

The prompts below assume you have run the pipeline and have `out/<run_id>/` artifacts.

---

## 0) Boundary discipline prompt (always first)

**Prompt:**

You are a scientific assistant helping with a FIT/EST case study.
You must treat the following as the locked boundary of the experiment:

- boundary_mode: <B0/B1/B2>
- AFDB release label: <...>
- sampling seed: <...>
- selection rule: deterministic hash order from coords_dir scan
- estimators and event definition: as in EST_PREREG.locked.yaml

You must refuse to interpret results if the coherence gate status is ESTIMATOR_UNSTABLE.
You must distinguish “signature” from “cause”.
Now read the prereg and the regime_report, and summarize: (a) what is in boundary, (b) what is out of scope, (c) whether coherence passed.

Inputs:
- out/<run_id>/EST_PREREG.locked.yaml
- out/<run_id>/regime_report.md

Outputs:
- a short boundary summary
- a yes/no for coherence, with reasons
- one sentence describing what it is safe to claim
- one sentence describing what is unsafe to claim

---

## 1) Artifact audit prompt (EST hygiene)

**Prompt:**

Audit the run manifest and boundary snapshot.
List every artifact produced and verify file existence.
If any file is missing, label the run SCOPE_LIMITED and explain why.

Inputs:
- out/<run_id>/run_manifest.json
- out/<run_id>/boundary_snapshot.json

---

## 2) “Hard data” analysis prompt (no storytelling yet)

**Prompt:**

Only compute and report descriptive statistics.
No hypotheses, no explanations.

Tasks:
- Read metrics_per_protein + metrics_per_bin
- Report summary stats for I1, C1 (and C2/C3 if present)
- Report bin counts vs length
- Identify candidate regime transition bins by largest negative dR over jump window

Inputs:
- out/<run_id>/metrics_per_protein.parquet (or .csv fallback)
- out/<run_id>/metrics_per_bin.parquet (or .csv fallback)

Output:
- bullet list, numbers only, with bin ids and length midpoints

---

## 3) “Boundary switch comparison” prompt (B0 vs B1 vs B2)

**Prompt:**

Compare runs that differ ONLY by boundary mode.

Rules:
- Do NOT pool runs.
- Treat each boundary mode as a different experiment.

Tasks:
- Align bins by bin_id across runs
- Compute how event_bin changes across boundaries
- If event exists in one boundary but not others, label BOUNDARY_DEPENDENT

Inputs:
- out/B0_*/metrics_per_bin.*
- out/B1_*/metrics_per_bin.*
- out/B2_*/metrics_per_bin.*

Output:
- a small table: boundary_mode, event_found, event_bin, coherence_status
- one paragraph interpreting boundary dependence in EST terms

---

## 4) Narrative prompt (LessWrong/Medium style, falsifiable checks)

**Prompt:**

Write a narrative report for this case following the pattern:

- Claim (bounded)
- What would falsify it
- What we measured (estimator tuple)
- What changed (event)
- What we refuse to conclude

Constraints:
- Only use facts present in the artifacts.
- Include the coherence gate outcome prominently.
- Treat “PAE/MSA added” as boundary change, not incremental improvement.

Inputs:
- README.md
- out/<run_id>/regime_report.md
- out/<run_id>/tradeoff_onepage.pdf (describe, don’t reproduce)
