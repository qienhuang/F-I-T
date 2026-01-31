from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd


def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: Path, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(p: Path, s: str):
    p.write_text(s, encoding="utf-8")


def _fmt(x):
    try:
        if x is None:
            return "NA"
        v = float(x)
        if v != v:
            return "NA"
        return f"{v:.4f}"
    except Exception:
        return "NA"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="out/<run_id> directory")
    args = ap.parse_args()
    rd = Path(args.run_dir)

    # Prefer robust tables (bilevel > policy-seed > baseline-only)
    robust_path = rd / "frontier_bilevel_robust_table.csv"
    if not robust_path.exists():
        robust_path = rd / "frontier_policy_robust_table.csv"
    if not robust_path.exists():
        robust_path = rd / "frontier_robust_table.csv"

    robust = pd.read_csv(robust_path)
    policy = pd.read_csv(rd / "policy_table.csv")
    merged = policy.merge(robust, on="policy", how="left", suffixes=("", "_rob"))

    templates = {
        "strong_allowed": (
            "Under the preregistered protocol and cost-aware low-FPR cap, {policy} robustly exceeds the random baseline band "
            "under the **bilevel two-key gate** (CVaR/expected shortfall gate **and** tail-min audit; both CI strictly positive)."
        ),
        "weak_cvar": (
            "Under the preregistered protocol and cost-aware low-FPR cap, {policy} shows a **directional advantage under the CVaR gate**, "
            "but does **not** meet the tail-min audit gate. Do not claim “outperforms random”."
        ),
        "weak_tail": (
            "Under the preregistered protocol and cost-aware low-FPR cap, {policy} shows a **directional advantage under the tail-min audit**, "
            "but does **not** meet the CVaR gate. Do not claim “outperforms random”."
        ),
        "none_safe": (
            "Under the preregistered protocol and cost-aware low-FPR cap, {policy} does not meet the preregistered two-key gate "
            "(CVaR + tail-min)."
        ),
        "forbidden_phrase": "Under the preregistered protocol, {policy} outperforms random.",
        "jump_phrase": "{policy} jump_type={jump_type} (delay={jump_delay_rounds}) under availability_delay_max_rounds={avail_max}.",
    }
    write_json(rd / "claims_templates.json", templates)

    ev = read_json(rd / "event_summary.json")
    avail_max = int(ev.get("availability_delay_max_rounds", 0) or 0)

    # Determine claim_level
    if "claim_level" not in merged.columns:
        # Best-effort reconstruction if table is older
        cvar_lo = merged.get("bilevel_cvar_gate_margin_ci_low", None)
        tail_lo = merged.get("bilevel_tail_min_margin_ci_low", None)
        if cvar_lo is not None and tail_lo is not None:
            pass_cvar = cvar_lo.astype(float) > 0
            pass_tail = tail_lo.astype(float) > 0
            merged["claim_level"] = "none"
            merged.loc[pass_cvar & pass_tail, "claim_level"] = "strong"
            merged.loc[pass_cvar & (~pass_tail), "claim_level"] = "weak_cvar_only"
            merged.loc[(~pass_cvar) & pass_tail, "claim_level"] = "weak_tail_only"
        else:
            merged["claim_level"] = "none"

    # Derive boolean allow flag (strong only)
    merged["claim_outperforms_random_allowed"] = merged["claim_level"].astype(str) == "strong"

    lines = []
    lines.append("# Claims Pack (v2.7)\n\n")
    lines.append("This file is generated. It constrains wording to what the preregistered two-key robustness gate allows.\n\n")

    lines.append("## Global rules\n\n")
    lines.append('- The phrase **"outperforms random"** is allowed **only** for policies with claim_level=`strong` (two-key gate passed).\n')
    lines.append('- For `weak_*` levels, you may say **"directional advantage"** but must state which gate is satisfied and which is not.\n')
    lines.append('- Prefer cap-aware language: **"under the preregistered protocol and low-FPR cap"**.\n\n')

    lines.append("## Allowed claims (per policy)\n\n")
    for _, r in merged.iterrows():
        pol = str(r["policy"])
        lvl = str(r.get("claim_level", "none"))

        jt = str(r.get("jump_type", "none"))
        jd = r.get("jump_delay_rounds", None)

        cvar_lo = r.get("bilevel_cvar_gate_margin_ci_low", None)
        tail_lo = r.get("bilevel_tail_min_margin_ci_low", None)
        two_key_lo = r.get("bilevel_two_key_min_ci_low", None)

        lines.append(f"### `{pol}`\n\n")

        if lvl == "strong":
            lines.append("- ✅ " + templates["strong_allowed"].format(policy=pol) + "\n")
        elif lvl == "weak_cvar_only":
            lines.append("- ⚠️ " + templates["weak_cvar"].format(policy=pol) + "\n")
        elif lvl == "weak_tail_only":
            lines.append("- ⚠️ " + templates["weak_tail"].format(policy=pol) + "\n")
        else:
            lines.append("- ⚠️ " + templates["none_safe"].format(policy=pol) + "\n")

        lines.append(f"- Gate audit: CVaR_ci_low={_fmt(cvar_lo)}, tail_min_ci_low={_fmt(tail_lo)}, two_key_min_ci_low={_fmt(two_key_lo)}\n")
        lines.append("- " + templates["jump_phrase"].format(policy=pol, jump_type=jt, jump_delay_rounds=jd, avail_max=avail_max) + "\n\n")

        lines.append("**Forbidden examples**\n\n")
        lines.append("- ❌ " + templates["forbidden_phrase"].format(policy=pol) + "\n\n")

    write_text(rd / "Claims.md", "".join(lines))
    print("Wrote:", rd / "Claims.md")


if __name__ == "__main__":
    main()
