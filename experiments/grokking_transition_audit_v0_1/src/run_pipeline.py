import argparse
import csv
import glob
import json
import os
import uuid
from bisect import bisect_left
from datetime import datetime, timezone
from pathlib import Path

import yaml


def quantile(values, q):
    if not values:
        return None
    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = int(round((len(sorted_vals) - 1) * q))
    idx = max(0, min(len(sorted_vals) - 1, idx))
    return sorted_vals[idx]


def parse_float(x):
    if x is None:
        return None
    x = str(x).strip()
    if not x:
        return None
    try:
        return float(x)
    except ValueError:
        return None


def load_timeseries(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            step = parse_float(row.get("step"))
            if step is None:
                continue
            row["step"] = int(step)
            rows.append(row)
    rows.sort(key=lambda r: r["step"])
    return rows


def series_from_rows(rows, col):
    values = []
    for r in rows:
        v = parse_float(r.get(col))
        values.append(v)
    return values


def event_steps(rows, col, threshold):
    steps = []
    for r in rows:
        v = parse_float(r.get(col))
        if v is not None and threshold is not None and v >= threshold:
            steps.append(int(r["step"]))
    return steps


def has_event_within(sorted_steps, t, radius):
    if not sorted_steps:
        return False
    left = bisect_left(sorted_steps, t - radius)
    if left >= len(sorted_steps):
        return False
    return sorted_steps[left] <= t + radius


def nearest_event_within(sorted_steps, t, radius):
    if not sorted_steps:
        return None
    idx = bisect_left(sorted_steps, t)
    candidates = []
    if idx < len(sorted_steps):
        candidates.append(sorted_steps[idx])
    if idx > 0:
        candidates.append(sorted_steps[idx - 1])
    best = None
    best_dist = None
    for c in candidates:
        d = abs(c - t)
        if d <= radius and (best_dist is None or d < best_dist):
            best = c
            best_dist = d
    return best


def detect_ptmss(steps, force_events, info_events, constraint_events, radius):
    for t in steps:
        if (
            has_event_within(force_events, t, radius)
            and has_event_within(info_events, t, radius)
            and has_event_within(constraint_events, t, radius)
        ):
            return t
    return None


def find_ptmss_candidates(steps, force_events, info_events, constraint_events, radius):
    candidates = []
    for t in steps:
        if (
            has_event_within(force_events, t, radius)
            and has_event_within(info_events, t, radius)
            and has_event_within(constraint_events, t, radius)
        ):
            candidates.append(t)
    return candidates


def event_order_signature(t, force_events, info_events, constraint_events, radius):
    positions = {
        "S1": nearest_event_within(force_events, t, radius),
        "S2": nearest_event_within(info_events, t, radius),
        "S3": nearest_event_within(constraint_events, t, radius),
    }
    if any(v is None for v in positions.values()):
        return None
    return tuple(k for k, _ in sorted(positions.items(), key=lambda kv: (kv[1], kv[0])))


def detect_baseline_transition(rows, acc_col, jump_window, jump_min):
    values = [parse_float(r.get(acc_col)) for r in rows]
    steps = [r["step"] for r in rows]
    for i in range(jump_window, len(values)):
        cur = values[i]
        prev = values[i - jump_window]
        if cur is None or prev is None:
            continue
        if cur - prev >= jump_min:
            return steps[i]
    return None


def seed_id_from_path(path):
    return Path(path).stem


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute_thresholds(rows, family_cols, cfg_signals):
    mode = cfg_signals["mode"]
    thresholds = {}
    if mode == "quantile":
        q = cfg_signals["quantiles"]
        for key, col in family_cols.items():
            vals = [v for v in series_from_rows(rows, col) if v is not None]
            thresholds[key] = quantile(vals, float(q[key]))
    elif mode == "fixed":
        fx = cfg_signals["fixed_thresholds"]
        for key in family_cols:
            thresholds[key] = parse_float(fx[key])
    else:
        raise ValueError(f"Unknown signals.mode: {mode}")
    return thresholds


def analyze_seed(path, cfg, run_id):
    rows = load_timeseries(path)
    steps = [r["step"] for r in rows]
    notes = []

    required = cfg["inputs"]["required_columns"]
    if not rows:
        return {"seed": seed_id_from_path(path), "label": "INCONCLUSIVE", "notes": ["empty_input"]}
    for col in required:
        if col not in rows[0]:
            return {
                "seed": seed_id_from_path(path),
                "label": "INCONCLUSIVE",
                "notes": [f"missing_required_column:{col}"],
            }

    family_results = {}
    density_gate = cfg["signals"]["density_gate"]
    min_rate = float(density_gate["min_rate"])
    max_rate = float(density_gate["max_rate"])
    pt_radius = int(cfg["ptmss"]["window_radius_steps"])

    signal_cfg = cfg["signals"]
    for fam in cfg["families"]:
        fam_name = fam["name"]
        cols = fam["cols"]
        optional = bool(fam.get("optional", False))
        missing_cols = [c for c in cols.values() if c not in rows[0]]
        if missing_cols:
            if optional:
                continue
            return {
                "seed": seed_id_from_path(path),
                "label": "INCONCLUSIVE",
                "notes": [f"missing_family_column:{','.join(missing_cols)}"],
            }

        thresholds = compute_thresholds(rows, cols, cfg["signals"])
        force_ev = event_steps(rows, cols["force"], thresholds["force"])
        info_ev = event_steps(rows, cols["info"], thresholds["info"])
        cons_ev = event_steps(rows, cols["constraint"], thresholds["constraint"])
        rates = {
            "force": len(force_ev) / len(rows),
            "info": len(info_ev) / len(rows),
            "constraint": len(cons_ev) / len(rows),
        }
        density_ok = all(min_rate <= r <= max_rate for r in rates.values())
        if not density_ok:
            notes.append(f"density_gate_fail:{fam_name}")

        candidates = find_ptmss_candidates(steps, force_ev, info_ev, cons_ev, pt_radius)
        t_pt = candidates[0] if candidates else None
        order = None
        if t_pt is not None:
            order = event_order_signature(t_pt, force_ev, info_ev, cons_ev, pt_radius)
        family_results[fam_name] = {
            "thresholds": thresholds,
            "event_density": rates,
            "density_ok": density_ok,
            "t_ptmss": t_pt,
            "order": order,
            "events": {
                "force": force_ev,
                "info": info_ev,
                "constraint": cons_ev,
            },
            "event_counts": {
                "force": len(force_ev),
                "info": len(info_ev),
                "constraint": len(cons_ev),
            },
            "ptmss_candidates": candidates,
        }

    if "primary" not in family_results:
        return {
            "seed": seed_id_from_path(path),
            "label": "INCONCLUSIVE",
            "notes": ["missing_primary_family"],
        }

    primary = family_results["primary"]
    pt_primary = primary["t_ptmss"]
    all_density_ok = all(f["density_ok"] for f in family_results.values())

    gate = {
        "pass": False,
        "alignment_fail_families": [],
        "order_fail_families": [],
    }
    delta_t = int(cfg["coherence_gate"]["alignment_tolerance_steps"])
    require_order = bool(cfg["coherence_gate"]["require_order_consistency"])
    primary_order = primary["order"]

    if pt_primary is not None:
        gate["pass"] = True
        for fam_name, f in family_results.items():
            if fam_name == "primary":
                continue
            t_other = f["t_ptmss"]
            if t_other is None or abs(t_other - pt_primary) > delta_t:
                gate["pass"] = False
                gate["alignment_fail_families"].append(fam_name)
                continue
            if require_order and f["order"] != primary_order:
                gate["pass"] = False
                gate["order_fail_families"].append(fam_name)

    baseline_cfg = cfg.get("baseline", {})
    baseline_t = None
    if baseline_cfg.get("use_acc_jump", False):
        acc_col = baseline_cfg.get("acc_col", "acc_test")
        if acc_col in rows[0]:
            baseline_t = detect_baseline_transition(
                rows,
                acc_col=acc_col,
                jump_window=int(baseline_cfg["jump_window"]),
                jump_min=float(baseline_cfg["jump_min"]),
            )

    if not all_density_ok:
        label = "INCONCLUSIVE"
    elif pt_primary is None:
        label = "NO_TRANSITION"
    elif not gate["pass"]:
        label = "ESTIMATOR_UNSTABLE"
    else:
        label = "REGISTERED_TRANSITION"

    fit_transition = label == "REGISTERED_TRANSITION"
    baseline_transition = baseline_t is not None
    divergence = fit_transition != baseline_transition

    return {
        "run_id": run_id,
        "prereg_id": cfg["id"],
        "seed": seed_id_from_path(path),
        "input_file": path.replace("\\", "/"),
        "signal_lock": {
            "mode": signal_cfg.get("mode"),
            "quantiles": signal_cfg.get("quantiles", {}),
            "fixed_thresholds": signal_cfg.get("fixed_thresholds", {}),
            "density_gate": signal_cfg.get("density_gate", {}),
        },
        "thresholds": {k: v["thresholds"] for k, v in family_results.items()},
        "event_density": {k: v["event_density"] for k, v in family_results.items()},
        "event_counts": {k: v["event_counts"] for k, v in family_results.items()},
        "ptmss": {
            "primary_t": pt_primary,
            "family_t": {k: v["t_ptmss"] for k, v in family_results.items()},
            "family_order": {k: v["order"] for k, v in family_results.items()},
            "family_candidate_count": {k: len(v["ptmss_candidates"]) for k, v in family_results.items()},
            "primary_candidate_steps": primary.get("ptmss_candidates", []),
            "window_radius_steps": pt_radius,
        },
        "events": {k: v["events"] for k, v in family_results.items()},
        "gate": gate,
        "baseline": {
            "transition_t": baseline_t,
            "has_transition": baseline_transition,
            "diverges_from_fit": divergence,
        },
        "label": label,
        "notes": notes,
    }


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def render_report(cfg, summary):
    template_path = Path("outputs/summary_template.md")
    if template_path.exists():
        txt = template_path.read_text(encoding="utf-8")
    else:
        txt = "# Grokking Transition Audit Summary\n"
    repl = {
        "{{run_id}}": summary["run_id"],
        "{{prereg_id}}": summary["prereg_id"],
        "{{n_seeds}}": str(summary["n_seeds"]),
        "{{count_registered}}": str(summary["label_counts"].get("REGISTERED_TRANSITION", 0)),
        "{{count_no_transition}}": str(summary["label_counts"].get("NO_TRANSITION", 0)),
        "{{count_unstable}}": str(summary["label_counts"].get("ESTIMATOR_UNSTABLE", 0)),
        "{{count_inconclusive}}": str(summary["label_counts"].get("INCONCLUSIVE", 0)),
        "{{baseline_transition_rate}}": f"{summary['baseline_transition_rate']:.3f}",
        "{{fit_transition_rate}}": f"{summary['fit_transition_rate']:.3f}",
        "{{divergence_rate}}": f"{summary['divergence_rate']:.3f}",
        "{{c1_threshold}}": f"{summary['c1_threshold']:.3f}",
        "{{c1_status}}": summary["c1_status"],
        "{{replay_status}}": summary["replay"]["status"],
        "{{replay_compared_count}}": str(summary["replay"]["compared_count"]),
        "{{replay_stable_count}}": str(summary["replay"]["stable_count"]),
    }
    for k, v in repl.items():
        txt = txt.replace(k, v)
    return txt


def load_replay_entries(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("replays"), list):
        return payload["replays"]
    return []


def evaluate_replay(valid_records, cfg):
    replay_cfg = cfg.get("replay", {})
    enabled = bool(replay_cfg.get("enabled", False))
    manifest_path = replay_cfg.get("manifest")
    min_replay = int(cfg["claim"]["c1_min_replay_count"])
    if not enabled:
        return {
            "enabled": False,
            "status": "not_required",
            "manifest_path": manifest_path,
            "compared_count": 0,
            "stable_count": 0,
            "stable_rate": None,
            "unstable_seeds": [],
            "pass": True,
            "mode": "count_fallback",
        }
    if not manifest_path:
        return {
            "enabled": True,
            "status": "missing_manifest_path",
            "manifest_path": None,
            "compared_count": 0,
            "stable_count": 0,
            "stable_rate": None,
            "unstable_seeds": [],
            "pass": False,
            "mode": "manifest",
        }
    entries = load_replay_entries(manifest_path)
    by_seed = {str(e.get("seed")): e for e in entries if e.get("seed")}
    scope_seeds = replay_cfg.get("seeds") or []
    if scope_seeds:
        target = [r for r in valid_records if r["seed"] in set(scope_seeds)]
    else:
        target = list(valid_records)
    compared = 0
    stable = 0
    unstable_seeds = []
    for rec in target:
        seed = rec["seed"]
        if seed not in by_seed:
            continue
        compared += 1
        replay_label = by_seed[seed].get("label")
        if replay_label == rec["label"]:
            stable += 1
        else:
            unstable_seeds.append(seed)
    stable_rate = (stable / compared) if compared else None
    replay_pass = compared >= min_replay and stable == compared
    status = "pass" if replay_pass else "fail"
    if compared < min_replay:
        status = "insufficient_replay_samples"
    return {
        "enabled": True,
        "status": status,
        "manifest_path": manifest_path.replace("\\", "/"),
        "compared_count": compared,
        "stable_count": stable,
        "stable_rate": stable_rate,
        "unstable_seeds": unstable_seeds,
        "pass": replay_pass,
        "mode": "manifest",
    }


def ensure_replay_template(cfg, out_dir):
    replay_cfg = cfg.get("replay", {})
    manifest_path = replay_cfg.get("manifest")
    if not replay_cfg.get("enabled", False) or not manifest_path:
        return
    if os.path.exists(manifest_path):
        return
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    template = {
        "run_id": "REPLAY_RUN_ID_HERE",
        "replays": [
            {
                "seed": "seed_140",
                "label": "NO_TRANSITION",
                "config_hash": "LOCKED_CONFIG_HASH",
                "notes": "Fill with replay run outputs."
            }
        ]
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)


def write_audit_cards(per_seed, out_dir):
    cards_dir = os.path.join(out_dir, "audit_cards")
    os.makedirs(cards_dir, exist_ok=True)
    written = []
    for rec in per_seed:
        if rec["label"] != "REGISTERED_TRANSITION":
            continue
        seed = rec["seed"]
        primary_th = rec["thresholds"].get("primary", {})
        primary_den = rec["event_density"].get("primary", {})
        primary_cnt = rec["event_counts"].get("primary", {})
        fam_t = rec["ptmss"].get("family_t", {})
        fam_o = rec["ptmss"].get("family_order", {})
        content = []
        content.append(f"# Audit Card: {seed}\n")
        content.append(f"- label: `{rec['label']}`")
        content.append(f"- baseline_transition_t: `{rec['baseline']['transition_t']}`")
        content.append(f"- fit_transition_t(primary): `{rec['ptmss']['primary_t']}`")
        content.append(f"- gate_pass: `{rec['gate']['pass']}`")
        content.append("")
        content.append("## Primary thresholds")
        content.append("")
        content.append(f"- tau_F: `{primary_th.get('force')}`")
        content.append(f"- tau_I: `{primary_th.get('info')}`")
        content.append(f"- tau_C: `{primary_th.get('constraint')}`")
        content.append("")
        content.append("## Primary event density")
        content.append("")
        content.append(f"- p_F: `{primary_den.get('force')}`")
        content.append(f"- p_I: `{primary_den.get('info')}`")
        content.append(f"- p_C: `{primary_den.get('constraint')}`")
        content.append("")
        content.append("## Primary event counts")
        content.append("")
        content.append(f"- n_S1: `{primary_cnt.get('force')}`")
        content.append(f"- n_S2: `{primary_cnt.get('info')}`")
        content.append(f"- n_S3: `{primary_cnt.get('constraint')}`")
        content.append(f"- n_PT_candidates: `{rec['ptmss']['family_candidate_count'].get('primary')}`")
        content.append("")
        content.append("## Family alignment")
        content.append("")
        for fam, t in fam_t.items():
            content.append(f"- {fam}: t={t}, order={fam_o.get(fam)}")
        if rec.get("notes"):
            content.append("")
            content.append("## Notes")
            content.append("")
            for n in rec["notes"]:
                content.append(f"- {n}")
        card_path = os.path.join(cards_dir, f"{seed}.md")
        with open(card_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content) + "\n")
        written.append(card_path.replace("\\", "/"))
    return written


def build_diag_row(rec):
    primary_th = rec.get("thresholds", {}).get("primary", {})
    primary_den = rec.get("event_density", {}).get("primary", {})
    primary_cnt = rec.get("event_counts", {}).get("primary", {})
    alt_th = rec.get("thresholds", {}).get("alt", {})
    alt_den = rec.get("event_density", {}).get("alt", {})
    alt_cnt = rec.get("event_counts", {}).get("alt", {})
    q = rec.get("signal_lock", {}).get("quantiles", {})
    return {
        "seed": rec["seed"],
        "label": rec["label"],
        "baseline_transition_t": rec["baseline"]["transition_t"],
        "fit_transition_t": rec["ptmss"]["primary_t"],
        "gate_pass": rec["gate"]["pass"],
        "align_fail_families": "|".join(rec["gate"]["alignment_fail_families"]),
        "order_fail_families": "|".join(rec["gate"]["order_fail_families"]),
        "diverges_from_baseline": rec["baseline"]["diverges_from_fit"],
        "q_force": q.get("force"),
        "q_info": q.get("info"),
        "q_constraint": q.get("constraint"),
        "tau_force": primary_th.get("force"),
        "tau_info": primary_th.get("info"),
        "tau_constraint": primary_th.get("constraint"),
        "p_force": primary_den.get("force"),
        "p_info": primary_den.get("info"),
        "p_constraint": primary_den.get("constraint"),
        "n_s1": primary_cnt.get("force"),
        "n_s2": primary_cnt.get("info"),
        "n_s3": primary_cnt.get("constraint"),
        "n_pt_candidates": rec["ptmss"]["family_candidate_count"].get("primary"),
        "tau_force_alt": alt_th.get("force"),
        "tau_info_alt": alt_th.get("info"),
        "tau_constraint_alt": alt_th.get("constraint"),
        "p_force_alt": alt_den.get("force"),
        "p_info_alt": alt_den.get("info"),
        "p_constraint_alt": alt_den.get("constraint"),
        "n_s1_alt": alt_cnt.get("force"),
        "n_s2_alt": alt_cnt.get("info"),
        "n_s3_alt": alt_cnt.get("constraint"),
        "n_pt_candidates_alt": rec["ptmss"]["family_candidate_count"].get("alt"),
        "notes": "|".join(rec.get("notes", [])),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prereg", required=True, help="Path to prereg yaml")
    parser.add_argument("--run_id", default=None, help="Optional run id")
    args = parser.parse_args()

    cfg = load_yaml(args.prereg)
    run_id = args.run_id or f"{cfg['id']}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"

    files = sorted(glob.glob(cfg["inputs"]["timeseries_glob"]))
    if not files:
        raise FileNotFoundError(f"No input files matched: {cfg['inputs']['timeseries_glob']}")

    out = cfg["outputs"]
    out_dir = out["out_dir"]
    per_seed_dir = out["per_seed_json_dir"]
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(per_seed_dir, exist_ok=True)
    ensure_replay_template(cfg, out_dir)

    per_seed = []
    for fp in files:
        record = analyze_seed(fp, cfg, run_id)
        per_seed.append(record)
        seed_json = os.path.join(per_seed_dir, f"{record.get('seed', 'unknown')}.json")
        with open(seed_json, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

    label_counts = {}
    for r in per_seed:
        label_counts[r["label"]] = label_counts.get(r["label"], 0) + 1

    valid = [r for r in per_seed if r["label"] != "INCONCLUSIVE"]
    n_valid = len(valid)
    baseline_trans = sum(1 for r in valid if r["baseline"]["has_transition"])
    fit_trans = sum(1 for r in valid if r["label"] == "REGISTERED_TRANSITION")
    divergence = sum(1 for r in valid if r["baseline"]["diverges_from_fit"])
    divergence_rate = divergence / n_valid if n_valid else 0.0

    replay_eval = evaluate_replay(valid, cfg)

    c1_threshold = float(cfg["claim"]["c1_min_divergence_rate"])
    c1_min_replay = int(cfg["claim"]["c1_min_replay_count"])
    replay_pass = replay_eval["pass"]
    if replay_eval["mode"] == "count_fallback":
        replay_pass = divergence >= c1_min_replay

    c1_pass = divergence_rate >= c1_threshold and replay_pass
    verdict = (
        "SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY"
        if c1_pass
        else "SCOPE_LIMITED_GROKKING_TRANSITION_DETECTION"
    )

    card_paths = write_audit_cards(per_seed, out_dir)

    summary = {
        "run_id": run_id,
        "prereg_id": cfg["id"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "n_seeds": len(per_seed),
        "n_valid": n_valid,
        "label_counts": label_counts,
        "baseline_transition_rate": baseline_trans / n_valid if n_valid else 0.0,
        "fit_transition_rate": fit_trans / n_valid if n_valid else 0.0,
        "divergence_rate": divergence_rate,
        "divergence_count": divergence,
        "c1_threshold": c1_threshold,
        "c1_min_replay_count": c1_min_replay,
        "c1_replay_mode": replay_eval["mode"],
        "c1_status": "PASS" if c1_pass else "FAIL",
        "verdict": verdict,
        "replay": replay_eval,
        "registered_seed_cards": card_paths,
    }

    diag_rows = [build_diag_row(r) for r in per_seed]

    write_csv(
        out["diagnostics_csv"],
        diag_rows,
        fieldnames=[
            "seed",
            "label",
            "baseline_transition_t",
            "fit_transition_t",
            "gate_pass",
            "align_fail_families",
            "order_fail_families",
            "diverges_from_baseline",
            "q_force",
            "q_info",
            "q_constraint",
            "tau_force",
            "tau_info",
            "tau_constraint",
            "p_force",
            "p_info",
            "p_constraint",
            "n_s1",
            "n_s2",
            "n_s3",
            "n_pt_candidates",
            "tau_force_alt",
            "tau_info_alt",
            "tau_constraint_alt",
            "p_force_alt",
            "p_info_alt",
            "p_constraint_alt",
            "n_s1_alt",
            "n_s2_alt",
            "n_s3_alt",
            "n_pt_candidates_alt",
            "notes",
        ],
    )

    with open(out["summary_json"], "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    report_md = render_report(cfg, summary)
    with open(out["report_md"], "w", encoding="utf-8") as f:
        f.write(report_md)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
