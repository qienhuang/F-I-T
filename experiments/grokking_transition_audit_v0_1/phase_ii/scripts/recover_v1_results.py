"""Parse the Phase-II v1.0 run.log and write per_seed_metrics.csv + summary.json."""
from __future__ import annotations
import re, csv, json
from pathlib import Path
import numpy as np

LOG = Path("D:/FIT Lab/github/F-I-T/experiments/grokking_transition_audit_v0_1/phase_ii/results/phase2_v1_0_run.log")
OUT = Path("D:/FIT Lab/github/F-I-T/experiments/grokking_transition_audit_v0_1/phase_ii/results/main_v1_0")
OUT.mkdir(parents=True, exist_ok=True)

# Tee-Object on Windows writes UTF-16 LE (with BOM) to log files.
try:
    log_raw = LOG.read_text(encoding="utf-16")
except UnicodeDecodeError:
    log_raw = LOG.read_text(encoding="utf-8", errors="replace")
# Tee-Object wraps long lines at ~80 chars with "\n " (newline + space).
# Collapse every such wrap into a single space so the regex sees one line.
log = re.sub(r"\n ", " ", log_raw)

# Parse per-run metric lines
DETAIL_RE = re.compile(
    r"\s+(grokked|pregrok)\s+seed=(\d+)\s+(gaussian_random|structured_rank1)"
    r"\s+scale=([\d.]+)%\s+p_seed=(\d+)\s+\|\s+"
    r"t50=([\d.]+)\s+t90=([\d.]+)\s+auc=([\d.]+)\s*\n?\s*unrecov=([\d.]+)",
    re.MULTILINE,
)
BASELINE_RE = re.compile(
    r"seed=(\d+)\s+group=(grokked|pregrok)\s+step=\d+\s+baseline_acc=([\d.]+)"
)

rows: list[dict] = []
for m in DETAIL_RE.finditer(log):
    rows.append({
        "seed": int(m.group(2)),
        "group": m.group(1),
        "matrix": "embed.weight",
        "perturb_type": m.group(3),
        "scale_rel": float(m.group(4)) / 100,
        "perturb_seed_idx": int(m.group(5)),
        "t50": float(m.group(6)),
        "t90": float(m.group(7)),
        "auc": float(m.group(8)),
        "unrecovered": float(m.group(9)),
        "baseline_acc": float("nan"),
    })

baselines: dict[tuple, float] = {}
for m in BASELINE_RE.finditer(log):
    baselines[(int(m.group(1)), m.group(2))] = float(m.group(3))

for r in rows:
    key = (r["seed"], r["group"])
    if key in baselines:
        r["baseline_acc"] = baselines[key]

print(f"Parsed {len(rows)} rows from log")
print(f"Seeds: {sorted({r['seed'] for r in rows})}")
print(f"Groups: {sorted({r['group'] for r in rows})}")

# Write CSV
csv_path = OUT / "per_seed_metrics.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows -> {csv_path}")

# Aggregate: per-seed median over all perturb conditions
grok = [r for r in rows if r["group"] == "grokked"]
pre  = [r for r in rows if r["group"] == "pregrok"]

def seed_median(rs: list[dict], key: str) -> list[float]:
    seeds = sorted({r["seed"] for r in rs})
    return [float(np.median([r[key] for r in rs if r["seed"] == s])) for s in seeds]

grok_t50 = seed_median(grok, "t50");  pre_t50 = seed_median(pre, "t50")
grok_t90 = seed_median(grok, "t90");  pre_t90 = seed_median(pre, "t90")
grok_auc = seed_median(grok, "auc");  pre_auc = seed_median(pre, "auc")
grok_unr = seed_median(grok, "unrecovered")
pre_unr  = seed_median(pre,  "unrecovered")

rng = np.random.default_rng(42)

def bci(vals: list[float], fn, n: int = 2000, ci: float = 0.95) -> list[float]:
    arr = np.asarray(vals)
    boots = [fn(rng.choice(arr, len(arr), replace=True)) for _ in range(n)]
    alpha = (1 - ci) / 2
    return [float(np.quantile(boots, alpha)), float(np.quantile(boots, 1 - alpha))]

# t50
med_grok_t50 = float(np.median(grok_t50))
med_pre_t50  = float(np.median(pre_t50))
t50_ratio = (med_pre_t50 + 1e-9) / (med_grok_t50 + 1e-9)
t50_dir = med_grok_t50 < med_pre_t50
t50_eff = t50_ratio >= 1.5

# t90
med_grok_t90 = float(np.median(grok_t90))
med_pre_t90  = float(np.median(pre_t90))
t90_ratio = (med_pre_t90 + 1e-9) / (med_grok_t90 + 1e-9)
t90_dir = med_grok_t90 < med_pre_t90
t90_eff = t90_ratio >= 1.5

# AUC
mean_grok_auc = float(np.mean(grok_auc))
mean_pre_auc  = float(np.mean(pre_auc))
auc_diff = mean_grok_auc - mean_pre_auc
auc_dir = auc_diff >= 0
auc_eff = auc_diff >= 0.10

# unrecovered@2000
mean_grok_unr = float(np.mean(grok_unr))
mean_pre_unr  = float(np.mean(pre_unr))
unr_diff_pp = (mean_pre_unr - mean_grok_unr) * 100
unr_dir = unr_diff_pp >= 0
unr_eff = unr_diff_pp >= 20

metrics = {
    "t50": {
        "grokked_median": med_grok_t50, "pregrok_median": med_pre_t50,
        "grokked_ci95": bci(grok_t50, np.median),
        "pregrok_ci95":  bci(pre_t50,  np.median),
        "ratio_pregrok_over_grokked": t50_ratio,
        "direction_ok": t50_dir, "effect_ok": t50_eff,
        "separating": t50_dir and t50_eff,
    },
    "t90": {
        "grokked_median": med_grok_t90, "pregrok_median": med_pre_t90,
        "grokked_ci95": bci(grok_t90, np.median),
        "pregrok_ci95":  bci(pre_t90,  np.median),
        "ratio_pregrok_over_grokked": t90_ratio,
        "direction_ok": t90_dir, "effect_ok": t90_eff,
        "separating": t90_dir and t90_eff,
    },
    "auc": {
        "grokked_mean": mean_grok_auc, "pregrok_mean": mean_pre_auc,
        "grokked_ci95": bci(grok_auc, np.mean),
        "pregrok_ci95":  bci(pre_auc,  np.mean),
        "diff_grokked_minus_pregrok": auc_diff,
        "direction_ok": auc_dir, "effect_ok": auc_eff,
        "separating": auc_dir and auc_eff,
    },
    "unrecovered_2000": {
        "grokked_pct": mean_grok_unr * 100, "pregrok_pct": mean_pre_unr * 100,
        "grokked_ci95": [x * 100 for x in bci(grok_unr, np.mean)],
        "pregrok_ci95":  [x * 100 for x in bci(pre_unr,  np.mean)],
        "diff_pregrok_minus_grokked_pp": unr_diff_pp,
        "direction_ok": unr_dir, "effect_ok": unr_eff,
        "separating": unr_dir and unr_eff,
    },
}

n_sep = sum(1 for m in metrics.values() if m["separating"])
if n_sep >= 2:
    verdict = "ATTRACTOR_SUPPORTED"
elif n_sep == 0:
    verdict = "ATTRACTOR_NOT_SUPPORTED"
else:
    verdict = "INCONCLUSIVE"

summary = {
    "phase2_id": "GROKKING_TRANSITION_AUDIT_PHASE_II_V1_0",
    "version": "1.0",
    "n_seeds": len({r["seed"] for r in rows}),
    "n_grokked": len({r["seed"] for r in grok}),
    "n_pregrok":  len({r["seed"] for r in pre}),
    "grokked_step": 300000,
    "pregrok_step": 5000,
    "recover_steps": 2000,
    "primary_matrix": "embed.weight",
    "metrics": metrics,
    "n_separating": n_sep,
    "n_required": 2,
    "verdict": verdict,
}
with (OUT / "summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

# Report
REPORT_LINES = [
    "# Phase-II v1.0 Attractor Stability Report",
    "",
    f"## Verdict: **{verdict}** ({n_sep}/2 metrics required)",
    "",
    "## Setup",
    f"- Grokked: step_300000 ({len({r['seed'] for r in grok})} seeds)",
    f"- Pre-grok: step_5000 ({len({r['seed'] for r in pre})} seeds)",
    "- Design: within-seed matched (same 10 seeds, different checkpoint)",
    "- Primary matrix: `embed.weight`",
    "- Perturbations: Gaussian + rank-1, scales 0.5/1/2/5% of ||W||_F",
    "- Recovery horizon: 2000 steps",
    "",
    "## Metrics (primary matrix, all scales/perturb types aggregated)",
    "",
    "| Metric | Grokked | Pre-grok | Effect | Min required | Pass |",
    "|---|---:|---:|---:|---:|:---:|",
    f"| t50 (steps) | {med_grok_t50:.0f} | {med_pre_t50:.0f} | {t50_ratio:.1f}x | >=1.5x | {'PASS' if t50_dir and t50_eff else 'fail'} |",
    f"| t90 (steps) | {med_grok_t90:.0f} | {med_pre_t90:.0f} | {t90_ratio:.1f}x | >=1.5x | {'PASS' if t90_dir and t90_eff else 'fail'} |",
    f"| AUC [0,2000] | {mean_grok_auc:.3f} | {mean_pre_auc:.3f} | delta={auc_diff:.3f} | >=0.10 | {'PASS' if auc_dir and auc_eff else 'fail'} |",
    f"| Unrecov@2000 (%) | {mean_grok_unr*100:.1f}% | {mean_pre_unr*100:.1f}% | delta={unr_diff_pp:.1f}pp | >=20pp | {'PASS' if unr_dir and unr_eff else 'fail'} |",
    "",
    f"## Files",
    f"- `{csv_path}`",
    f"- `{OUT / 'summary.json'}`",
]
with (OUT / "report.md").open("w", encoding="utf-8") as f:
    f.write("\n".join(REPORT_LINES) + "\n")

print()
print("=" * 60)
print(f"VERDICT: {verdict}  ({n_sep}/2 metrics required)")
for name, m in metrics.items():
    g = m.get("grokked_median", m.get("grokked_mean", 0))
    p = m.get("pregrok_median", m.get("pregrok_mean", 0))
    sep_str = "PASS" if m["separating"] else "fail"
    print(f"  {name:22s}: grokked={g:.1f}  pregrok={p:.1f}  -> {sep_str}")
print("=" * 60)
