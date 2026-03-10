#!/usr/bin/env python3
"""Summarize held-out structural indicator candidates against the v0.6 control run."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import median


SUMMARY_FILES = {
    "+1": "eval_summary_sign_pos1.md",
    "-1": "eval_summary_sign_neg1.md",
}

CANDIDATES = {
    "control": {
        "dir": "estimator_spec.v0_5_holdout",
        "label": "Control",
        "hypothesis": "unembed.weight baseline control",
        "run_id": "grokking_v0_6_control",
    },
    "A": {
        "dir": "estimator_spec.v0_6_structural_A",
        "label": "Candidate A",
        "hypothesis": "embed.weight primary spectral matrix",
        "run_id": "grokking_v0_6_structural_A",
    },
    "B": {
        "dir": "estimator_spec.v0_6_structural_B",
        "label": "Candidate B",
        "hypothesis": "encoder.layers.0.self_attn.in_proj_weight primary",
        "run_id": "grokking_v0_6_structural_B",
    },
    "C": {
        "dir": "estimator_spec.v0_6_structural_C",
        "label": "Candidate C",
        "hypothesis": "encoder.layers.1.self_attn.in_proj_weight primary",
        "run_id": "grokking_v0_6_structural_C",
    },
}


@dataclass
class SignSummary:
    score_sign: str
    total_seeds: int
    seeds_no_transition: int
    valid_auc_seeds: int
    median_auc: float | None
    mean_auc: float | None
    median_ap: float | None
    mean_ap: float | None
    seeds_with_lead_fpr: int
    lead_fpr_rate: float
    median_lead_steps: float | None
    mean_lead_steps: float | None


def _parse_float(value: str) -> float | None:
    value = value.strip()
    if value.lower() in {"nan", "none", ""}:
        return None
    return float(value)


def _parse_summary_table(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or set("".join(cells)) <= {"-", ":"}:
            continue
        if header is None:
            header = cells
            continue
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def _summarize_rows(score_sign: str, rows: list[dict[str, str]]) -> SignSummary:
    auc_values = []
    ap_values = []
    lead_values = []
    seeds_no_transition = 0
    for row in rows:
        t_event = row.get("seed", "")
        _ = t_event
        n_pos = row.get("n_pos", "")
        try:
            if int(float(n_pos)) == 0:
                seeds_no_transition += 1
        except Exception:
            pass
        auc = _parse_float(row.get("ROC-AUC", ""))
        ap = _parse_float(row.get("Avg Precision", ""))
        lead = _parse_float(row.get("Lead@FPR", ""))
        if auc is not None:
            auc_values.append(auc)
        if ap is not None:
            ap_values.append(ap)
        if lead is not None:
            lead_values.append(lead)

    def _mean(values: list[float]) -> float | None:
        if not values:
            return None
        return sum(values) / len(values)

    return SignSummary(
        score_sign=score_sign,
        total_seeds=len(rows),
        seeds_no_transition=seeds_no_transition,
        valid_auc_seeds=len(auc_values),
        median_auc=median(auc_values) if auc_values else None,
        mean_auc=_mean(auc_values),
        median_ap=median(ap_values) if ap_values else None,
        mean_ap=_mean(ap_values),
        seeds_with_lead_fpr=len(lead_values),
        lead_fpr_rate=(len(lead_values) / len(rows)) if rows else 0.0,
        median_lead_steps=median(lead_values) if lead_values else None,
        mean_lead_steps=_mean(lead_values),
    )


def _preferred_sign(pos: SignSummary, neg: SignSummary) -> SignSummary:
    pos_key = (
        pos.lead_fpr_rate,
        -1 if pos.median_lead_steps is None else pos.median_lead_steps,
        -1 if pos.median_auc is None else pos.median_auc,
        -1 if pos.mean_ap is None else pos.mean_ap,
    )
    neg_key = (
        neg.lead_fpr_rate,
        -1 if neg.median_lead_steps is None else neg.median_lead_steps,
        -1 if neg.median_auc is None else neg.median_auc,
        -1 if neg.mean_ap is None else neg.mean_ap,
    )
    return pos if pos_key >= neg_key else neg


def _fmt(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float) and math.isnan(value):
        return "NA"
    if digits == 0:
        return str(int(round(value)))
    return f"{value:.{digits}f}"


def _metrics_dict(summary: SignSummary) -> dict[str, float | int | str | None]:
    return {
        "score_sign": summary.score_sign,
        "total_seeds": summary.total_seeds,
        "seeds_no_transition": summary.seeds_no_transition,
        "valid_auc_seeds": summary.valid_auc_seeds,
        "median_auc": summary.median_auc,
        "mean_auc": summary.mean_auc,
        "median_ap": summary.median_ap,
        "mean_ap": summary.mean_ap,
        "seeds_with_lead_fpr": summary.seeds_with_lead_fpr,
        "lead_fpr_rate": summary.lead_fpr_rate,
        "median_lead_steps": summary.median_lead_steps,
        "mean_lead_steps": summary.mean_lead_steps,
    }


def build_summary(root: Path) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for key, meta in CANDIDATES.items():
        candidate_dir = root / meta["dir"]
        by_sign: dict[str, SignSummary] = {}
        for sign, filename in SUMMARY_FILES.items():
            rows = _parse_summary_table(candidate_dir / filename)
            by_sign[sign] = _summarize_rows(sign, rows)
        preferred = _preferred_sign(by_sign["+1"], by_sign["-1"])
        out[key] = {
            "key": key,
            "label": meta["label"],
            "hypothesis": meta["hypothesis"],
            "run_id": meta["run_id"],
            "by_sign": {sign: _metrics_dict(summary) for sign, summary in by_sign.items()},
            "preferred": _metrics_dict(preferred),
        }
    return out


def write_csv(path: Path, summary: dict[str, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "key",
        "label",
        "hypothesis",
        "preferred_sign",
        "total_seeds",
        "seeds_no_transition",
        "valid_auc_seeds",
        "median_auc",
        "mean_auc",
        "median_ap",
        "mean_ap",
        "seeds_with_lead_fpr",
        "lead_fpr_rate",
        "median_lead_steps",
        "mean_lead_steps",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in summary.values():
            preferred = item["preferred"]
            writer.writerow(
                {
                    "key": item["key"],
                    "label": item["label"],
                    "hypothesis": item["hypothesis"],
                    "preferred_sign": preferred["score_sign"],
                    "total_seeds": preferred["total_seeds"],
                    "seeds_no_transition": preferred["seeds_no_transition"],
                    "valid_auc_seeds": preferred["valid_auc_seeds"],
                    "median_auc": preferred["median_auc"],
                    "mean_auc": preferred["mean_auc"],
                    "median_ap": preferred["median_ap"],
                    "mean_ap": preferred["mean_ap"],
                    "seeds_with_lead_fpr": preferred["seeds_with_lead_fpr"],
                    "lead_fpr_rate": preferred["lead_fpr_rate"],
                    "median_lead_steps": preferred["median_lead_steps"],
                    "mean_lead_steps": preferred["mean_lead_steps"],
                }
            )


def write_json(path: Path, summary: dict[str, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def write_md(path: Path, summary: dict[str, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    control = summary["control"]["preferred"]
    lines = [
        "# Structural Candidate Summary (v0.6)",
        "",
        "- task: modular-addition grokking hard-indicator screening on held-out seeds 140–179",
        "- comparison rule: pick the score sign with better low-FPR coverage for each candidate, then compare against the fixed control run",
        "- source: `D:/FIT Lab/grokking/runs_v0_6_structural/*/eval_summary_sign_{pos1,neg1}.md`",
        "",
        "## Preferred-sign comparison",
        "",
        "| Candidate | Preferred sign | median AUC | mean AUC | median AP | lead@FPR seeds | lead rate | median lead steps | Delta median AUC vs control | Delta lead rate vs control |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summary.values():
        preferred = item["preferred"]
        delta_auc = None
        if preferred["median_auc"] is not None and control["median_auc"] is not None:
            delta_auc = preferred["median_auc"] - control["median_auc"]
        delta_lead = preferred["lead_fpr_rate"] - control["lead_fpr_rate"]
        lines.append(
            f"| {item['label']} | {preferred['score_sign']} | {_fmt(preferred['median_auc'])} | "
            f"{_fmt(preferred['mean_auc'])} | {_fmt(preferred['median_ap'])} | "
            f"{preferred['seeds_with_lead_fpr']}/{preferred['total_seeds']} | {_fmt(preferred['lead_fpr_rate'])} | "
            f"{_fmt(preferred['median_lead_steps'], 0)} | {_fmt(delta_auc)} | {_fmt(delta_lead)} |"
        )

    lines.extend(
        [
            "",
            "## Sign-level detail",
            "",
            "| Candidate | sign | median AUC | mean AUC | median AP | lead rate | median lead steps |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in summary.values():
        for sign in ["+1", "-1"]:
            s = item["by_sign"][sign]
            lines.append(
                f"| {item['label']} | {sign} | {_fmt(s['median_auc'])} | {_fmt(s['mean_auc'])} | "
                f"{_fmt(s['median_ap'])} | {_fmt(s['lead_fpr_rate'])} | {_fmt(s['median_lead_steps'], 0)} |"
            )

    lines.extend(
        [
            "",
            "## Readout",
            "",
            f"- Control preferred sign is `{control['score_sign']}` with median AUC `{_fmt(control['median_auc'])}` and lead rate `{_fmt(control['lead_fpr_rate'])}`.",
            "- Candidate verdicts are not auto-assigned here. This artifact is a screening summary for deciding whether any structural candidate meaningfully improves low-FPR usefulness over the control family.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path(r"D:\FIT Lab\grokking\runs_v0_6_structural"),
        help="Root directory containing estimator_spec.v0_5_holdout and v0_6_structural_{A,B,C}.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("github/F-I-T/experiments/grokking_hard_indicators_v0_2/results/structural_v0_6"),
        help="Directory to write summary artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(args.runs_root)
    out_dir = args.out_dir
    write_csv(out_dir / "structural_candidates_summary.csv", summary)
    write_json(out_dir / "structural_candidates_summary.json", summary)
    write_md(out_dir / "structural_candidates_summary.md", summary)
    print(f"[ok] wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
