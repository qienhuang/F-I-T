#!/usr/bin/env python3
"""
Summarize `policy-eval` runs under an output directory.

Usage:
  python summarize_out.py --out_root out
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Row:
    run: str
    model: str
    prompts: str
    samples: int
    temp: float
    target_fpr: float
    seed_base: int
    baseline_adv_tool_rate: float
    controlled_adv_tool_rate: float
    baseline_safe_tool_rate: float
    controlled_safe_tool_rate: float
    baseline_feasible: bool
    controlled_feasible: bool
    baseline_coverage: float
    controlled_coverage: float
    baseline_fpr_floor: float
    controlled_fpr_floor: float
    baseline_achieved_fpr: float
    controlled_achieved_fpr: float


def _get(d: Dict[str, Any], key: str, default: Any) -> Any:
    v = d.get(key, default)
    return default if v is None else v


def infer_model_from_run_name(run: str) -> str:
    # Best-effort heuristic so older summary files can still be grouped sensibly.
    # Examples:
    #   qwen3_4b_rw_t0p9_fpr010_s50 -> qwen3:4b
    #   qwen3_8b_fpr010            -> qwen3:8b
    #   gemma3_1b_fpr010           -> gemma3:1b
    #   stub_fpr010                -> stub
    head = run.split("_", 3)[:2]
    if len(head) >= 2 and head[1].endswith(("b", "B")) and head[1][:-1].replace(".", "").isdigit():
        return f"{head[0]}:{head[1]}".replace("B", "b")
    return ""


def load_summary(path: Path) -> Optional[Row]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    baseline_alarm = dict(_get(data, "baseline_alarm", {}))
    controlled_alarm = dict(_get(data, "controlled_alarm", {}))

    model = str(_get(data, "model", "")).strip() or str(_get(data, "ollama_model", "")).strip()
    if not model:
        model = infer_model_from_run_name(path.parent.name)

    prompts = str(_get(data, "prompts", "")).replace("\\", "/")

    return Row(
        run=path.parent.name,
        model=model,
        prompts=prompts,
        samples=int(_get(data, "samples_per_prompt", 0)),
        temp=float(_get(data, "temperature", 0.0)),
        target_fpr=float(_get(data, "target_fpr", 0.0)),
        seed_base=int(_get(data, "seed_base", 0)),
        baseline_adv_tool_rate=float(_get(data, "baseline_adv_tool_rate", 0.0)),
        controlled_adv_tool_rate=float(_get(data, "controlled_adv_tool_rate", 0.0)),
        baseline_safe_tool_rate=float(_get(data, "baseline_safe_tool_rate", 0.0)),
        controlled_safe_tool_rate=float(_get(data, "controlled_safe_tool_rate", 0.0)),
        baseline_feasible=bool(_get(baseline_alarm, "feasible", False)),
        controlled_feasible=bool(_get(controlled_alarm, "feasible", False)),
        baseline_coverage=float(_get(baseline_alarm, "coverage", 0.0)),
        controlled_coverage=float(_get(controlled_alarm, "coverage", 0.0)),
        baseline_fpr_floor=float(_get(baseline_alarm, "fpr_floor", 0.0)),
        controlled_fpr_floor=float(_get(controlled_alarm, "fpr_floor", 0.0)),
        baseline_achieved_fpr=float(_get(baseline_alarm, "achieved_fpr", 0.0)),
        controlled_achieved_fpr=float(_get(controlled_alarm, "achieved_fpr", 0.0)),
    )


def to_markdown(rows: List[Row]) -> str:
    header = (
        "| run | model | prompts | samples | temp | target_fpr | seed_base | baseline_adv_tool_rate | controlled_adv_tool_rate | "
        "baseline_safe_tool_rate | controlled_safe_tool_rate | baseline_feasible | controlled_feasible | baseline_achieved_fpr | "
        "controlled_achieved_fpr | baseline_coverage | controlled_coverage | baseline_fpr_floor | controlled_fpr_floor |"
    )
    sep = "|" + " --- |" * (header.count("|") - 1)
    lines = [header, sep]
    for r in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    r.run,
                    r.model or "-",
                    r.prompts or "-",
                    str(r.samples),
                    f"{r.temp:.3g}",
                    f"{r.target_fpr:.3g}",
                    str(r.seed_base),
                    f"{r.baseline_adv_tool_rate:.3g}",
                    f"{r.controlled_adv_tool_rate:.3g}",
                    f"{r.baseline_safe_tool_rate:.3g}",
                    f"{r.controlled_safe_tool_rate:.3g}",
                    str(r.baseline_feasible),
                    str(r.controlled_feasible),
                    f"{r.baseline_achieved_fpr:.3g}",
                    f"{r.controlled_achieved_fpr:.3g}",
                    f"{r.baseline_coverage:.3g}",
                    f"{r.controlled_coverage:.3g}",
                    f"{r.baseline_fpr_floor:.3g}",
                    f"{r.controlled_fpr_floor:.3g}",
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class AggRow:
    model: str
    prompts: str
    samples: int
    temp: float
    target_fpr: float
    n_runs: int
    baseline_adv_tool_rate_mean: float
    baseline_adv_tool_rate_std: float
    controlled_adv_tool_rate_mean: float
    controlled_adv_tool_rate_std: float
    baseline_safe_tool_rate_mean: float
    baseline_safe_tool_rate_std: float
    controlled_safe_tool_rate_mean: float
    controlled_safe_tool_rate_std: float
    baseline_feasible_rate: float
    controlled_feasible_rate: float
    baseline_achieved_fpr_mean: float
    baseline_achieved_fpr_std: float
    controlled_achieved_fpr_mean: float
    controlled_achieved_fpr_std: float
    baseline_coverage_mean: float
    baseline_coverage_std: float
    controlled_coverage_mean: float
    controlled_coverage_std: float
    baseline_fpr_floor_max: float
    controlled_fpr_floor_max: float


def _mean_std(xs: List[float]) -> tuple[float, float]:
    if not xs:
        return 0.0, 0.0
    if len(xs) == 1:
        return float(xs[0]), 0.0
    return float(statistics.mean(xs)), float(statistics.stdev(xs))


def _rate(bools: List[bool]) -> float:
    if not bools:
        return 0.0
    return float(sum(1 for b in bools if b) / len(bools))


def aggregate(rows: List[Row]) -> List[AggRow]:
    groups: Dict[tuple[str, str, int, float, float], List[Row]] = {}
    for r in rows:
        key = (r.model, r.prompts, r.samples, float(r.temp), float(r.target_fpr))
        groups.setdefault(key, []).append(r)

    out: List[AggRow] = []
    for (model, prompts, samples, temp, target_fpr), rs in sorted(groups.items()):
        b_adv = [r.baseline_adv_tool_rate for r in rs]
        c_adv = [r.controlled_adv_tool_rate for r in rs]
        b_safe = [r.baseline_safe_tool_rate for r in rs]
        c_safe = [r.controlled_safe_tool_rate for r in rs]
        b_afpr = [r.baseline_achieved_fpr for r in rs]
        c_afpr = [r.controlled_achieved_fpr for r in rs]
        b_cov = [r.baseline_coverage for r in rs]
        c_cov = [r.controlled_coverage for r in rs]

        b_adv_m, b_adv_s = _mean_std(b_adv)
        c_adv_m, c_adv_s = _mean_std(c_adv)
        b_safe_m, b_safe_s = _mean_std(b_safe)
        c_safe_m, c_safe_s = _mean_std(c_safe)
        b_afpr_m, b_afpr_s = _mean_std(b_afpr)
        c_afpr_m, c_afpr_s = _mean_std(c_afpr)
        b_cov_m, b_cov_s = _mean_std(b_cov)
        c_cov_m, c_cov_s = _mean_std(c_cov)

        out.append(
            AggRow(
                model=model,
                prompts=prompts,
                samples=samples,
                temp=temp,
                target_fpr=target_fpr,
                n_runs=len(rs),
                baseline_adv_tool_rate_mean=b_adv_m,
                baseline_adv_tool_rate_std=b_adv_s,
                controlled_adv_tool_rate_mean=c_adv_m,
                controlled_adv_tool_rate_std=c_adv_s,
                baseline_safe_tool_rate_mean=b_safe_m,
                baseline_safe_tool_rate_std=b_safe_s,
                controlled_safe_tool_rate_mean=c_safe_m,
                controlled_safe_tool_rate_std=c_safe_s,
                baseline_feasible_rate=_rate([r.baseline_feasible for r in rs]),
                controlled_feasible_rate=_rate([r.controlled_feasible for r in rs]),
                baseline_achieved_fpr_mean=b_afpr_m,
                baseline_achieved_fpr_std=b_afpr_s,
                controlled_achieved_fpr_mean=c_afpr_m,
                controlled_achieved_fpr_std=c_afpr_s,
                baseline_coverage_mean=b_cov_m,
                baseline_coverage_std=b_cov_s,
                controlled_coverage_mean=c_cov_m,
                controlled_coverage_std=c_cov_s,
                baseline_fpr_floor_max=float(max([r.baseline_fpr_floor for r in rs], default=0.0)),
                controlled_fpr_floor_max=float(max([r.controlled_fpr_floor for r in rs], default=0.0)),
            )
        )

    return out


def agg_to_markdown(rows: List[AggRow]) -> str:
    header = (
        "| model | prompts | samples | temp | target_fpr | n_runs | "
        "baseline_adv_tool_rate (mean±std) | controlled_adv_tool_rate (mean±std) | "
        "baseline_safe_tool_rate (mean±std) | controlled_safe_tool_rate (mean±std) | "
        "baseline_feasible_rate | controlled_feasible_rate | "
        "baseline_achieved_fpr (mean±std) | controlled_achieved_fpr (mean±std) | "
        "baseline_coverage (mean±std) | controlled_coverage (mean±std) | "
        "baseline_fpr_floor_max | controlled_fpr_floor_max |"
    )
    sep = "|" + " --- |" * (header.count("|") - 1)
    lines = [header, sep]
    for r in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    r.model or "-",
                    r.prompts or "-",
                    str(r.samples),
                    f"{r.temp:.3g}",
                    f"{r.target_fpr:.3g}",
                    str(r.n_runs),
                    f"{r.baseline_adv_tool_rate_mean:.3g}±{r.baseline_adv_tool_rate_std:.3g}",
                    f"{r.controlled_adv_tool_rate_mean:.3g}±{r.controlled_adv_tool_rate_std:.3g}",
                    f"{r.baseline_safe_tool_rate_mean:.3g}±{r.baseline_safe_tool_rate_std:.3g}",
                    f"{r.controlled_safe_tool_rate_mean:.3g}±{r.controlled_safe_tool_rate_std:.3g}",
                    f"{r.baseline_feasible_rate:.3g}",
                    f"{r.controlled_feasible_rate:.3g}",
                    f"{r.baseline_achieved_fpr_mean:.3g}±{r.baseline_achieved_fpr_std:.3g}",
                    f"{r.controlled_achieved_fpr_mean:.3g}±{r.controlled_achieved_fpr_std:.3g}",
                    f"{r.baseline_coverage_mean:.3g}±{r.baseline_coverage_std:.3g}",
                    f"{r.controlled_coverage_mean:.3g}±{r.controlled_coverage_std:.3g}",
                    f"{r.baseline_fpr_floor_max:.3g}",
                    f"{r.controlled_fpr_floor_max:.3g}",
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_root", type=str, default="out", help="Directory containing run folders.")
    ap.add_argument("--write_md", type=str, default="", help="Optional path to write the markdown table.")
    ap.add_argument("--aggregate", action="store_true", help="Also print a grouped mean±std summary table.")
    ap.add_argument(
        "--write_agg_md",
        type=str,
        default="",
        help="Optional path to write the aggregated mean±std table.",
    )
    ap.add_argument(
        "--filter_prompts_contains",
        type=str,
        default="",
        help="If set, only include runs whose `prompts` path contains this substring.",
    )
    ap.add_argument(
        "--exclude_prompts_contains",
        type=str,
        default="",
        help="If set, exclude runs whose `prompts` path contains this substring.",
    )
    args = ap.parse_args()

    out_root = Path(args.out_root)
    if not out_root.exists():
        raise SystemExit(f"Missing out_root: {out_root}")

    rows: List[Row] = []
    for p in sorted(out_root.glob("*/policy_eval_summary.json")):
        row = load_summary(p)
        if row is not None:
            if args.filter_prompts_contains and (args.filter_prompts_contains not in row.prompts):
                continue
            if args.exclude_prompts_contains and (args.exclude_prompts_contains in row.prompts):
                continue
            rows.append(row)

    md = to_markdown(rows)
    if args.write_md:
        Path(args.write_md).write_text(md, encoding="utf-8")
    print(md, end="")

    if args.aggregate:
        agg = aggregate(rows)
        agg_md = agg_to_markdown(agg)
        if args.write_agg_md:
            Path(args.write_agg_md).write_text(agg_md, encoding="utf-8")
        print("\n## Aggregated (grouped mean±std)\n")
        print(agg_md, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
