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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="out/<run_id> directory")
    args = ap.parse_args()
    rd = Path(args.run_dir)

    
    # Prefer robust tables (v2.3 bilevel > v2.2 policy-seed > v2.0 baseline-only)
    robust_path = rd / "frontier_bilevel_robust_table.csv"
    if not robust_path.exists():
        robust_path = rd / "frontier_policy_robust_table.csv"
    if not robust_path.exists():
        robust_path = rd / "frontier_robust_table.csv"

    robust = pd.read_csv(robust_path)
    policy = pd.read_csv(rd / "policy_table.csv")

    merged = policy.merge(robust, on="policy", how="left", suffixes=("", "_rob"))

    templates = {
        "allowed_phrase": "Under the preregistered protocol and cost-aware low-FPR cap, {policy} robustly exceeds the random baseline band under the bilevel tail-margin gate (CI strictly positive).",
        "forbidden_phrase": "Under the preregistered protocol, {policy} outperforms random.",
        "safe_phrase": "Under the preregistered protocol and cost-aware low-FPR cap, {policy} does not show a statistically robust advantage over the random baseline band under the bilevel tail-margin gate (CI crosses zero or is undefined).",
        "jump_phrase": "{policy} jump_type={jump_type} (delay={jump_delay_rounds}) under availability_delay_max_rounds={avail_max}."
    }
    write_json(rd / "claims_templates.json", templates)

    ev = read_json(rd / "event_summary.json")
    avail_max = int(ev.get("availability_delay_max_rounds", 0) or 0)

    # identify allow flag column
    allow_col = "claim_outperforms_random_allowed"
    if allow_col not in merged.columns:
        # fallback: allow if dominance_margin_ci_low > 0
        if "dominance_margin_ci_low" in merged.columns:
            merged[allow_col] = merged["dominance_margin_ci_low"].astype(float) > 0
        else:
            merged[allow_col] = False

    lines = []
    lines.append("# Claims Pack (v2.1)\n\n")
    lines.append("This file is generated. It constrains wording to what the robustness gate allows.\n\n")
    lines.append("## Global rules\n\n")
    lines.append("- If the relevant margin CI low bound is `<= 0` (bilevel preferred), the phrase **\"outperforms random\"** is forbidden.\n")
    lines.append("- Prefer cap-aware language: **\"under the preregistered protocol and low-FPR cap\"**.\n\n")

    lines.append("## Allowed claims (per policy)\n\n")
    for _, r in merged.iterrows():
        pol = str(r["policy"])
        allowed = bool(r.get(allow_col, False))
        jt = str(r.get("jump_type", "none"))
        jd = r.get("jump_delay_rounds", None)

        lines.append(f"### `{pol}`\n\n")
        if allowed:
            lines.append("- ✅ " + templates["allowed_phrase"].format(policy=pol) + "\n")
        else:
            lines.append("- ⚠️ " + templates["safe_phrase"].format(policy=pol) + "\n")
        lines.append("- " + templates["jump_phrase"].format(policy=pol, jump_type=jt, jump_delay_rounds=jd, avail_max=avail_max) + "\n\n")

        lines.append("**Forbidden examples**\n\n")
        lines.append("- ❌ " + templates["forbidden_phrase"].format(policy=pol) + "\n\n")

    write_text(rd / "Claims.md", "".join(lines))
    print("Wrote:", rd / "Claims.md")


if __name__ == "__main__":
    main()
