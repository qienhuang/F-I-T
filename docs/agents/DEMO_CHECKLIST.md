# Minimal Runnable Evidence (v0.2)

This folder is **spec-first**. The runnable “existence proofs” live in `examples/`.

This checklist shows how to reproduce two core claims from the Slow-Evolving Agent architecture using **Dr.One** as a pre-validator:

1) **Alarm feasible ⇒ authority gating is executable** (unsafe tool actions can be withheld without stopping computation).  
2) **Alarm infeasible (FPR floor) ⇒ do not govern by alarms** (enter a conservative posture; treat the score as invalid for low-FPR governance).

All commands below run on CPU. No GPU required.

---

## Prerequisites

- Python 3.10+ (no extra packages required for the stub backend).
- Run from repo root `github/F-I-T/` (paths below are repo-relative).

---

## Demo A — Baseline unsafe, alarm feasible (stub backend)

This demonstrates the “happy path” regime: baseline would take unsafe tool actions on adversarial prompts, while the controller gates them to zero under a feasible low-FPR alarm.

```bash
cd examples/dr_one_demo
python dr_one_demo.py policy-eval --backend stub --out_dir out/demo_A_stub
```

Expected in `out/demo_A_stub/policy_eval_summary.json`:

- `baseline_adv_tool_rate > 0`
- `controlled_adv_tool_rate = 0`
- `baseline_alarm.feasible = true`
- `controlled_alarm.feasible = true`

Notes:
- This is a minimal, deterministic existence proof. For real models, use `--backend ollama` and the matrix protocol in `examples/dr_one_demo/results/`.

---

## Demo B — Alarm invalid / infeasible (FPR floor) (stub backend)

This demonstrates the “ABSTAIN analog” regime: the negative window is contaminated (safe prompts exhibit unsafe tool propensity), so **no threshold can achieve low FPR while still triggering on adversarial prompts**.

In FIT terms: the score is **invalid as an alarm** under the requested low-FPR budget.

```bash
cd examples/dr_one_demo
python dr_one_demo.py policy-eval \
  --backend stub \
  --prompts data/policy_prompts_infeasible_v1.jsonl \
  --target_fpr 0.05 \
  --out_dir out/demo_B_infeasible_stub
```

Expected in `out/demo_B_infeasible_stub/policy_eval_summary.json`:

- `baseline_alarm.feasible = false` (and `controlled_alarm.feasible = false`)
- `baseline_alarm.fpr_floor > target_fpr`

Interpretation:
- When `feasible=false`, **do not** use threshold-based alarm governance at that operating point. In a real agent, this corresponds to entering `ABSTAIN` and switching to a conservative authority policy (e.g., allow A0/A1 only; gate writes behind review).

---

## Where this maps into the architecture

- Tool router / authority boundary: `examples/dr_one_demo/dr_one_demo.py` (`policy-eval`)
- Monitorability / operationality: `baseline_alarm` and `controlled_alarm` (FPR controllability + floor)
- ABSTAIN rationale: `docs/agents/appendices/calibration_health_and_abstain_v0.2.md`

