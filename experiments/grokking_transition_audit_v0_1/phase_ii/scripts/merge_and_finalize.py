"""Merge partial Phase-II v1.0 results from two sources and produce final analysis.

Sources:
  1. Original eval log (phase2_v1_0_40_eval.log) — seeds 140-160 (complete)
  2. Continuation CSV (final_v1_0_40/per_seed_metrics.csv) — seeds 161-179
      written by run_phase2_v1.py after the completion of the continuation run

Outputs (to final_v1_0_40/):
  per_seed_metrics.csv  — all 40 seeds combined
  summary.json          — verdict + per-metric stats
  report.md             — human-readable summary
"""
from __future__ import annotations
import re, csv, json
from pathlib import Path
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PHASE_II_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR  = PHASE_II_DIR / "results"

ORIG_LOG  = RESULTS_DIR / "phase2_v1_0_40_eval.log"
CONT_CSV  = RESULTS_DIR / "final_v1_0_40" / "per_seed_metrics.csv"
OUT_DIR   = RESULTS_DIR / "final_v1_0_40"

# Seeds sourced from the original log (others come from the continuation CSV)
LOG_SEEDS = set(range(140, 161))  # 140-160 inclusive (161 was partial in log)

# Decision thresholds (from EST_PREREG.phase_ii.v1_0.yaml)
T90_RATIO_MIN    = 1.5
UNRECOV_DIFF_MIN = 20.0   # percentage points
AUC_DIFF_MIN     = 0.10
N_REQUIRED       = 2
PRIMARY_MATRIX   = "embed.weight"
GROKKED_STEP     = 300000
PREGROK_STEP     = 5000

VERDICT_PASS         = "ATTRACTOR_SUPPORTED"
VERDICT_FAIL         = "ATTRACTOR_NOT_SUPPORTED"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# Parse original eval log (Tee-Object UTF-16 output)
# ---------------------------------------------------------------------------
DETAIL_RE = re.compile(
    r"\s+(grokked|pregrok)\s+seed=(\d+)\s+(gaussian_random|structured_rank1)"
    r"\s+scale=([\d.]+)%\s+p_seed=(\d+)\s+\|\s+"
    r"t50=([\d.]+)\s+t90=([\d.]+)\s+auc=([\d.]+)\s*\n?\s*unrecov=([\d.]+)",
    re.MULTILINE,
)
BASELINE_RE = re.compile(
    r"seed=(\d+)\s+group=(grokked|pregrok)\s+step=\d+\s+baseline_acc=([\d.]+)"
)

def parse_log(log_path: Path, seed_filter: set[int]) -> list[dict]:
    """Parse eval log, return rows for seeds in seed_filter only."""
    try:
        raw = log_path.read_text(encoding="utf-16")
    except UnicodeDecodeError:
        raw = log_path.read_text(encoding="utf-8", errors="replace")
    # Collapse Tee-Object line-wrap (newline + space -> space)
    log = re.sub(r"\n ", " ", raw)

    baselines: dict[tuple, float] = {}
    for m in BASELINE_RE.finditer(log):
        seed = int(m.group(1))
        if seed in seed_filter:
            baselines[(seed, m.group(2))] = float(m.group(3))

    rows: list[dict] = []
    for m in DETAIL_RE.finditer(log):
        seed = int(m.group(2))
        if seed not in seed_filter:
            continue
        group = m.group(1)
        rows.append({
            "seed": seed,
            "group": group,
            "matrix": PRIMARY_MATRIX,
            "perturb_type": m.group(3),
            "scale_rel": float(m.group(4)) / 100,
            "perturb_seed_idx": int(m.group(5)),
            "t50": float(m.group(6)),
            "t90": float(m.group(7)),
            "auc": float(m.group(8)),
            "unrecovered": float(m.group(9)),
            "baseline_acc": baselines.get((seed, group), float("nan")),
        })
    return rows


def read_csv_rows(csv_path: Path) -> list[dict]:
    """Read per_seed_metrics.csv, keep only primary-matrix rows."""
    rows = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("matrix", PRIMARY_MATRIX) == PRIMARY_MATRIX:
                rows.append({
                    "seed":           int(row["seed"]),
                    "group":          row["group"],
                    "matrix":         row.get("matrix", PRIMARY_MATRIX),
                    "perturb_type":   row["perturb_type"],
                    "scale_rel":      float(row["scale_rel"]),
                    "perturb_seed_idx": int(row["perturb_seed_idx"]),
                    "t50":            float(row["t50"]),
                    "t90":            float(row["t90"]),
                    "auc":            float(row["auc"]),
                    "unrecovered":    float(row["unrecovered"]),
                    "baseline_acc":   float(row.get("baseline_acc", "nan") or "nan"),
                })
    return rows


# ---------------------------------------------------------------------------
# Bootstrap helpers
# ---------------------------------------------------------------------------
_rng = np.random.default_rng(42)

def _bci_median(vals: list[float], n: int = 2000, ci: float = 0.95) -> list[float]:
    arr = np.asarray([v for v in vals if np.isfinite(v)], dtype=float)
    if len(arr) == 0:
        return [float("nan"), float("nan")]
    boots = [float(np.median(_rng.choice(arr, len(arr), replace=True))) for _ in range(n)]
    a = (1 - ci) / 2
    return [float(np.quantile(boots, a)), float(np.quantile(boots, 1 - a))]

def _bci_mean(vals: list[float], n: int = 2000, ci: float = 0.95) -> list[float]:
    arr = np.asarray([v for v in vals if np.isfinite(v)], dtype=float)
    if len(arr) == 0:
        return [float("nan"), float("nan")]
    boots = [float(np.mean(_rng.choice(arr, len(arr), replace=True))) for _ in range(n)]
    a = (1 - ci) / 2
    return [float(np.quantile(boots, a)), float(np.quantile(boots, 1 - a))]


def _seed_medians(rows: list[dict], key: str) -> list[float]:
    seeds = sorted({r["seed"] for r in rows})
    out = []
    for s in seeds:
        vals = [r[key] for r in rows if r["seed"] == s and np.isfinite(r[key])]
        if vals:
            out.append(float(np.median(vals)))
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading original eval log  : {ORIG_LOG}")
    log_rows = parse_log(ORIG_LOG, LOG_SEEDS)
    print(f"  Parsed {len(log_rows)} rows for seeds {sorted(LOG_SEEDS)}")

    print(f"Reading continuation CSV   : {CONT_CSV}")
    csv_rows = [r for r in read_csv_rows(CONT_CSV) if r["seed"] not in LOG_SEEDS]
    cont_seeds = sorted({r["seed"] for r in csv_rows})
    print(f"  Read {len(csv_rows)} rows for seeds {cont_seeds}")

    all_rows = log_rows + csv_rows
    all_seeds = sorted({r["seed"] for r in all_rows})
    print(f"Combined: {len(all_rows)} rows, {len(all_seeds)} seeds: {all_seeds}")

    # Write combined CSV (unified schema)
    fieldnames = ["seed","group","matrix","perturb_type","scale_rel",
                  "perturb_seed_idx","t50","t90","auc","unrecovered","baseline_acc"]
    combined_csv = OUT_DIR / "per_seed_metrics.csv"
    with combined_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)
    print(f"Wrote combined CSV ({len(all_rows)} rows) -> {combined_csv}")

    # ------------------------------------------------------------------
    # Aggregate: primary matrix, all seeds
    # ------------------------------------------------------------------
    grok = [r for r in all_rows if r["group"] == "grokked"]
    pre  = [r for r in all_rows if r["group"] == "pregrok"]

    grok_t50 = _seed_medians(grok, "t50")
    grok_t90 = _seed_medians(grok, "t90")
    grok_auc = _seed_medians(grok, "auc")
    grok_unr = _seed_medians(grok, "unrecovered")

    pre_t50 = _seed_medians(pre, "t50")
    pre_t90 = _seed_medians(pre, "t90")
    pre_auc = _seed_medians(pre, "auc")
    pre_unr = _seed_medians(pre, "unrecovered")

    def _safe_median(lst):
        v = [x for x in lst if np.isfinite(x)]
        return float(np.median(v)) if v else float("nan")
    def _safe_mean(lst):
        v = [x for x in lst if np.isfinite(x)]
        return float(np.mean(v)) if v else float("nan")

    gm_t50 = _safe_median(grok_t50);   pm_t50 = _safe_median(pre_t50)
    gm_t90 = _safe_median(grok_t90);   pm_t90 = _safe_median(pre_t90)
    gm_auc = _safe_mean(grok_auc);     pm_auc = _safe_mean(pre_auc)
    gm_unr = _safe_mean(grok_unr);     pm_unr = _safe_mean(pre_unr)

    t50_ratio   = (pm_t50 / gm_t50) if gm_t50 > 0 else float("nan")
    t90_ratio   = (pm_t90 / gm_t90) if gm_t90 > 0 else float("nan")
    auc_diff    = gm_auc - pm_auc
    unr_diff_pp = (pm_unr - gm_unr) * 100

    metrics = {
        "t50": {
            "grokked_median": gm_t50, "pregrok_median": pm_t50,
            "grokked_ci95": _bci_median(grok_t50), "pregrok_ci95": _bci_median(pre_t50),
            "ratio_pregrok_over_grokked": t50_ratio,
            "direction_ok": gm_t50 < pm_t50,
            "effect_ok": (t50_ratio >= T90_RATIO_MIN) if np.isfinite(t50_ratio) else False,
            "separating": (gm_t50 < pm_t50) and (np.isfinite(t50_ratio) and t50_ratio >= T90_RATIO_MIN),
        },
        "t90": {
            "grokked_median": gm_t90, "pregrok_median": pm_t90,
            "grokked_ci95": _bci_median(grok_t90), "pregrok_ci95": _bci_median(pre_t90),
            "ratio_pregrok_over_grokked": t90_ratio,
            "direction_ok": gm_t90 < pm_t90,
            "effect_ok": (t90_ratio >= T90_RATIO_MIN) if np.isfinite(t90_ratio) else False,
            "separating": (gm_t90 < pm_t90) and (np.isfinite(t90_ratio) and t90_ratio >= T90_RATIO_MIN),
        },
        "auc": {
            "grokked_mean": gm_auc, "pregrok_mean": pm_auc,
            "grokked_ci95": _bci_mean(grok_auc), "pregrok_ci95": _bci_mean(pre_auc),
            "diff_grokked_minus_pregrok": auc_diff,
            "direction_ok": auc_diff >= 0,
            "effect_ok": auc_diff >= AUC_DIFF_MIN,
            "separating": auc_diff >= AUC_DIFF_MIN,
        },
        "unrecovered_2000": {
            "grokked_pct": gm_unr * 100, "pregrok_pct": pm_unr * 100,
            "grokked_ci95": [x * 100 for x in _bci_mean(grok_unr)],
            "pregrok_ci95": [x * 100 for x in _bci_mean(pre_unr)],
            "diff_pregrok_minus_grokked_pp": unr_diff_pp,
            "direction_ok": unr_diff_pp >= 0,
            "effect_ok": unr_diff_pp >= UNRECOV_DIFF_MIN,
            "separating": unr_diff_pp >= UNRECOV_DIFF_MIN,
        },
    }

    n_sep = sum(1 for m in metrics.values() if m["separating"])
    verdict = (VERDICT_PASS if n_sep >= N_REQUIRED
               else VERDICT_FAIL if (n_sep == 0 and len(all_rows) > 0)
               else VERDICT_INCONCLUSIVE)

    # Ensure all metric booleans are native Python bool (numpy bool_ breaks json.dump)
    for m in metrics.values():
        for k, v in m.items():
            if isinstance(v, (np.bool_,)):
                m[k] = bool(v)

    summary = {
        "phase2_id": "GROKKING_TRANSITION_AUDIT_PHASE_II_V1_0",
        "version": "1.0",
        "n_seeds": len(all_seeds),
        "n_grokked_seeds": len({r["seed"] for r in grok}),
        "n_pregrok_seeds":  len({r["seed"] for r in pre}),
        "n_total_rows": len(all_rows),
        "primary_matrix": PRIMARY_MATRIX,
        "grokked_step": GROKKED_STEP,
        "pregrok_step":  PREGROK_STEP,
        "recover_steps": 2000,
        "data_sources": {
            "log_seeds": sorted(LOG_SEEDS),
            "csv_seeds": cont_seeds,
        },
        "metrics": metrics,
        "n_separating_metrics": n_sep,
        "n_required": N_REQUIRED,
        "verdict": verdict,
    }
    summary_path = OUT_DIR / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote summary -> {summary_path}")

    # Report
    t50_pass = "PASS" if metrics["t50"]["separating"] else "fail"
    t90_pass = "PASS" if metrics["t90"]["separating"] else "fail"
    auc_pass = "PASS" if metrics["auc"]["separating"] else "fail"
    unr_pass = "PASS" if metrics["unrecovered_2000"]["separating"] else "fail"

    report_lines = [
        "# Phase-II v1.0 Final 40-Seed Attractor Stability Report",
        "",
        f"## Verdict: **{verdict}** ({n_sep}/{N_REQUIRED} metrics required)",
        "",
        "## Setup",
        f"- Seeds: {len(all_seeds)} ({all_seeds[0]}–{all_seeds[-1]})",
        f"- Grokked: step_{GROKKED_STEP} checkpoints ({len({r['seed'] for r in grok})} seeds)",
        f"- Pre-grok: step_{PREGROK_STEP} checkpoints ({len({r['seed'] for r in pre})} seeds)",
        "- Design: within-seed matched (same seeds, different checkpoint)",
        "- Primary matrix: `embed.weight`",
        "- Perturbations: Gaussian + rank-1, scales 0.5/1/2/5% of ||W||_F",
        "- Recovery horizon: 2000 steps",
        "",
        "## Metrics (primary matrix, aggregated over all perturb conditions)",
        "",
        "| Metric | Grokked | Pre-grok | Effect | Min required | Pass |",
        "|---|---:|---:|---:|---:|:---:|",
        f"| t50 (steps) | {gm_t50:.0f} | {pm_t50:.0f} | {t50_ratio:.1f}x | ≥1.5x | {t50_pass} |",
        f"| t90 (steps) | {gm_t90:.0f} | {pm_t90:.0f} | {t90_ratio:.1f}x | ≥1.5x | {t90_pass} |",
        f"| AUC [0,2000] | {gm_auc:.3f} | {pm_auc:.3f} | Δ={auc_diff:+.3f} | ≥0.10 | {auc_pass} |",
        f"| Unrecov@2000 (%) | {gm_unr*100:.1f}% | {pm_unr*100:.1f}% | Δ={unr_diff_pp:+.1f}pp | ≥20pp | {unr_pass} |",
        "",
        "## Files",
        f"- `{combined_csv}`",
        f"- `{summary_path}`",
    ]
    report_path = OUT_DIR / "report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Wrote report   -> {report_path}")

    print()
    print("=" * 60)
    print(f"VERDICT: {verdict}  ({n_sep}/{N_REQUIRED} required)")
    for name, m in metrics.items():
        g = m.get("grokked_median", m.get("grokked_mean", 0))
        p = m.get("pregrok_median", m.get("pregrok_mean", 0))
        sep = "PASS" if m["separating"] else "fail"
        print(f"  {name:22s}: grokked={g:.1f}  pregrok={p:.1f}  -> {sep}")
    print("=" * 60)


if __name__ == "__main__":
    main()
