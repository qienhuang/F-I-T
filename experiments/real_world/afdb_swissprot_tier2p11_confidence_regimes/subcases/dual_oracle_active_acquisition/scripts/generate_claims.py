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


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def _inject_section(before: str, marker: str, section: str) -> str:
    """
    Idempotently inject `section` right before the first occurrence of `marker`.
    If an older v2.9 section exists, replace it.
    """
    if marker not in before:
        # Fallback: just prepend after the first H1
        parts = before.split("\n\n", 1)
        if len(parts) == 2 and parts[0].startswith("#"):
            return parts[0] + "\n\n" + section + "\n\n" + parts[1]
        return section + "\n\n" + before

    # Remove existing injected block if present
    start_tag = "## Claims & gate status (generated)"
    if start_tag in before:
        # remove from start_tag up to marker (exclusive)
        pre, rest = before.split(start_tag, 1)
        # rest contains old section + marker...
        if marker in rest:
            _, tail = rest.split(marker, 1)
            before = pre.rstrip() + "\n\n" + marker + tail
        else:
            before = pre

    head, tail = before.split(marker, 1)
    return head.rstrip() + "\n\n" + section.rstrip() + "\n\n" + marker + tail


def _fmt_bool(x) -> str:
    return "True" if bool(x) else "False"


def _make_overlay_md(policy: str, lvl: str, allow: bool, row: dict, phrasing: str, jump_rb: dict | None) -> str:
    cvar_lo = row.get("bilevel_cvar_gate_margin_ci_low", None)
    cvar_hi = row.get("bilevel_cvar_gate_margin_ci_high", None)
    tail_lo = row.get("bilevel_tail_min_margin_ci_low", None)
    tail_hi = row.get("bilevel_tail_min_margin_ci_high", None)
    two_lo = row.get("bilevel_two_key_min_ci_low", None)
    two_hi = row.get("bilevel_two_key_min_ci_high", None)

    lines = []
    lines.append("## Claims & gate status (generated)\n\n")
    lines.append(f"- claim_level: `{lvl}`\n")
    lines.append(f"- outperforms_random_allowed: `{_fmt_bool(allow)}`\n")
    lines.append("- gate_metric: `bilevel_two_key_min_ci_low` (two-key)\n")
    lines.append(f"- gate audit: two_key_min_ci_low={_fmt(two_lo)}, two_key_min_ci_high={_fmt(two_hi)}; "
                 f"cvar_ci_low={_fmt(cvar_lo)}, cvar_ci_high={_fmt(cvar_hi)}; "
                 f"tail_min_ci_low={_fmt(tail_lo)}, tail_min_ci_high={_fmt(tail_hi)}\n\n")

    lines.append("**Allowed phrasing (copy/paste)**\n\n")
    lines.append("> " + phrasing.strip() + "\n\n")

    lines.append("**Forbidden phrasing**\n\n")
    lines.append(f"- ❌ Under the preregistered protocol, `{policy}` outperforms random.\n\n")

    if jump_rb is not None:
        try:
            grid = jump_rb.get("availability_delay_grid", []) or []
            byp = (jump_rb.get("by_policy", {}) or {}).get(policy, {}) or {}
            probs = (byp.get("jump_type_prob_by_delay", {}) or {})
            if grid:
                d0 = str(int(grid[0]))
                p0 = probs.get(d0, None)
                if isinstance(p0, dict) and p0:
                    lines.append("**Jump robustness (multi-seed, summary)**\n\n")
                    lines.append(f"- delay_threshold_rounds: `{d0}`\n")
                    lines.append(f"- P(availability_driven)={_fmt(p0.get('availability_driven'))}, "
                                 f"P(learning_driven)={_fmt(p0.get('learning_driven'))}, "
                                 f"P(none)={_fmt(p0.get('none'))}\n\n")
        except Exception:
            pass

    return "".join(lines)


def apply_claims_overlay_to_policy_cards(
    run_dir: Path,
    merged: pd.DataFrame,
    templates: dict,
) -> None:
    cards_dir = run_dir / "policy_cards"
    if not cards_dir.exists():
        return

    gate_report_path = run_dir / "claims_gate_report.json"
    gate_report = read_json(gate_report_path) if gate_report_path.exists() else {}
    jump_rb_path = run_dir / "jump_robustness.json"
    jump_rb = read_json(jump_rb_path) if jump_rb_path.exists() else None

    overlay = {
        "version": "v2.9",
        "gate_mode": gate_report.get("mode", "unknown"),
        "gate_metric": gate_report.get("gate_metric", "unknown"),
        "gate_components": gate_report.get("gate_components", []),
        "by_policy": {},
    }

    # Ensure we have a stable per-policy mapping
    for _, r in merged.iterrows():
        pol = str(r["policy"])
        lvl = str(r.get("claim_level", "none"))
        allow = bool(lvl == "strong")

        if lvl == "strong":
            phrasing = templates["strong_allowed"].format(policy=pol)
        elif lvl == "weak_cvar_only":
            phrasing = templates["weak_cvar"].format(policy=pol)
        elif lvl == "weak_tail_only":
            phrasing = templates["weak_tail"].format(policy=pol)
        else:
            phrasing = templates["none_safe"].format(policy=pol)

        row = {k: r.get(k, None) for k in [
            "bilevel_cvar_gate_margin_ci_low", "bilevel_cvar_gate_margin_ci_high",
            "bilevel_tail_min_margin_ci_low", "bilevel_tail_min_margin_ci_high",
            "bilevel_two_key_min_ci_low", "bilevel_two_key_min_ci_high",
            "gate_pass_cvar", "gate_pass_tail_min",
            "bilevel_cvar_gate_alpha",
            "bilevel_tail_quantiles",
            "bilevel_cvar_alphas",
        ]}

        overlay["by_policy"][pol] = {
            "claim_level": lvl,
            "outperforms_random_allowed": allow,
            "allowed_phrasing": phrasing,
            **row,
        }

        card_path = cards_dir / f"{pol}.md"
        if card_path.exists():
            md = _read_text(card_path)
            section = _make_overlay_md(pol, lvl, allow, row, phrasing, jump_rb)
            md2 = _inject_section(md, "## Boundary & operating point", section)
            _write_text(card_path, md2)

    # Write overlay json
    (cards_dir / "claims_overlay.json").write_text(
        json.dumps(overlay, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Rewrite policy_cards_index.md to include claim level
    idx_path = run_dir / "policy_cards_index.md"
    try:
        # Base info from policy_table.csv
        pt = pd.read_csv(run_dir / "policy_table.csv")
        df = pt[["policy", "r_joint_usable", "r_covjump_joint", "jump_type", "delta_lag", "leakage_pass"]].copy()
        df["claim_level"] = df["policy"].map(lambda p: overlay["by_policy"].get(str(p), {}).get("claim_level", "none"))
        df["outperforms_random_allowed"] = df["policy"].map(lambda p: overlay["by_policy"].get(str(p), {}).get("outperforms_random_allowed", False))
        df["card_path"] = df["policy"].map(lambda p: f"policy_cards/{p}.md")

        df = df.sort_values(by=["claim_level", "r_joint_usable", "delta_lag", "policy"], ascending=[True, True, True, True])

        lines = []
        lines.append("# Policy cards index (with claims overlay)\n\n")
        lines.append("| policy | claim_level | outperforms_random_allowed | r_joint_usable | r_covjump_joint | jump_type | delta_lag | leakage_pass | card |\n")
        lines.append("|---|---|---|---:|---:|---|---:|---|---|\n")
        for _, rr in df.iterrows():
            pol = str(rr["policy"])
            lines.append(
                f"| `{pol}` | `{rr['claim_level']}` | `{_fmt_bool(rr['outperforms_random_allowed'])}` | "
                f"{int(rr['r_joint_usable'])} | {int(rr.get('r_covjump_joint', -1))} | `{rr.get('jump_type','')}` | "
                f"{int(rr['delta_lag'])} | {bool(rr['leakage_pass'])} | [{pol}]({rr['card_path']}) |\n"
            )
        idx_path.write_text("".join(lines), encoding="utf-8")
    except Exception:
        # Do not fail claims generation if index rewrite fails
        pass

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
    lines.append("# Claims Pack (canonical v2.9)\n\n")
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

    # v2.9 (canonical): propagate gates/claims into policy cards (operationalization layer)
    apply_claims_overlay_to_policy_cards(rd, merged, templates)
    print("Updated policy cards with claims overlay:", rd / "policy_cards" / "claims_overlay.json")


if __name__ == "__main__":
    main()
