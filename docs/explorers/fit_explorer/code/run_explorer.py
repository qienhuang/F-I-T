#!/usr/bin/env python3
"""
FIT-Explorer Non-LLM Runner (v0.1)

- Random/budgeted exploration with multi-stage gating
- Produces reproducible artifacts:
  - run_log.jsonl
  - leaderboard.csv
  - failure_map.yaml (JSON-as-YAML; YAML 1.2 accepts JSON)
  - prereg/ (per-candidate prereg locks; JSON-as-YAML)

This file is intentionally a skeleton:
you must implement the domain-specific hooks for real evaluation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


def stable_id(prefix: str, payload: Dict[str, Any]) -> str:
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}:{h}"


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return default_config()

    ext = os.path.splitext(path)[1].lower()
    raw = _read_text(path)

    if ext == ".json":
        return json.loads(raw)

    if ext in (".yml", ".yaml"):
        try:
            import yaml  # type: ignore
        except Exception:
            raise SystemExit(
                f"YAML config requires PyYAML. Install it with: python -m pip install pyyaml\n"
                f"Config path: {path}"
            )
        return yaml.safe_load(raw) or {}

    # Best-effort: try JSON, then YAML if available.
    try:
        return json.loads(raw)
    except Exception:
        try:
            import yaml  # type: ignore
        except Exception:
            raise SystemExit(
                f"Unsupported config extension '{ext}'. Use .json or .yaml/.yml.\n"
                f"Config path: {path}"
            )
        return yaml.safe_load(raw) or {}


def write_jsonl(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        return
    keys = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def write_yaml_json(path: str, obj: Dict[str, Any]) -> None:
    """
    Write JSON to a .yaml file.
    YAML 1.2 is a superset of JSON, so this stays dependency-free.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


@dataclass
class Candidate:
    candidate_id: str
    kind: str  # "detector" | "agent_config"
    params: Dict[str, Any]
    boundary: Dict[str, Any]


@dataclass
class StageResult:
    stage: str
    label: str
    metrics: Dict[str, Any]


def propose_candidates(n: int, search_space: Dict[str, Any], boundary: Dict[str, Any]) -> List[Candidate]:
    out: List[Candidate] = []
    det = search_space.get("detector", {})
    families = det.get("families", [])
    windows = det.get("windows", [])
    smoothing = det.get("smoothing", [])
    calibration = det.get("calibration_methods", [])

    if not (families and windows and smoothing and calibration):
        raise SystemExit("Invalid config: search_space.detector must define families/windows/smoothing/calibration_methods")

    for _ in range(int(n)):
        params = {
            "family": random.choice(families),
            "window_W": random.choice(windows),
            "smoothing": random.choice(smoothing),
            "calibration": random.choice(calibration),
        }
        cid = stable_id("det", {"params": params, "boundary": boundary})
        out.append(Candidate(candidate_id=cid, kind="detector", params=params, boundary=boundary))
    return out


# ---- Domain hooks (TODO): implement for your setting ----


def evaluate_candidate_stage0(c: Candidate, config: Dict[str, Any]) -> StageResult:
    """
    Cheap pre-check. Replace with real diagnostics, e.g.:
    - effective negative support size
    - tie/cluster dominance
    - quick floor suspicion test
    """
    return StageResult(stage="S0", label="S0_PASS", metrics={"support_size_neg": None, "tie_dominance": None})


def evaluate_candidate_gate(c: Candidate, config: Dict[str, Any]) -> StageResult:
    """
    Hard gate. Replace with real metrics:
    - achieved vs target FPR table
    - floor detection
    """
    W = int(c.params.get("window_W", 0))
    if W <= 50:
        return StageResult(stage="S1", label="RANK_ONLY", metrics={"fpr_min": 0.44, "ok_targets": 0})
    return StageResult(stage="S1", label="GATE_PASS", metrics={"fpr_min": 0.08, "ok_targets": 2})


def evaluate_candidate_utility(c: Candidate, config: Dict[str, Any]) -> StageResult:
    """
    Utility + robustness. Replace with real utility, e.g.:
    - coverage@FPR
    - lead time distribution
    - seed stability
    """
    W = int(c.params.get("window_W", 0))
    coverage = min(0.60, max(0.05, (W / 400.0)))
    lead = int(50 + (W / 10))
    return StageResult(
        stage="S2", label="SUPPORTED_FOR_ALARM", metrics={"coverage@0.05": coverage, "lead_time_median": lead}
    )


def default_config() -> Dict[str, Any]:
    return {
        "budget": {"N0": 30, "eta0": 0.33, "eta1": 0.50},
        "search_space": {
            "detector": {
                "families": ["dynamics", "process", "judge", "hierarchical_convergence"],
                "windows": [50, 100, 200, 400],
                "smoothing": [0.0, 0.1, 0.2],
                "calibration_methods": ["quantile", "isotonic", "temperature"],
            }
        },
        "boundary": {
            "system": "grokking",
            "event": "E_jump",
            "negative_window": "t <= t* - delta_safe",
            "positive_window": "t* - H_pos <= t < t*",
        },
        "output_dir": "out/fit_explorer_run",
    }


def coerce_config(config: Dict[str, Any], out_dir_override: Optional[str]) -> Dict[str, Any]:
    cfg = dict(config or {})

    cfg.setdefault("budget", {})
    cfg["budget"].setdefault("N0", 30)
    cfg["budget"].setdefault("eta0", 0.33)
    cfg["budget"].setdefault("eta1", 0.50)

    cfg.setdefault("search_space", {})
    cfg.setdefault("boundary", {})
    cfg.setdefault("output_dir", "out/fit_explorer_run")

    if out_dir_override:
        cfg["output_dir"] = out_dir_override

    return cfg


def write_prereg_lock(out_dir: str, c: Candidate, config: Dict[str, Any]) -> None:
    prereg_dir = os.path.join(out_dir, "prereg")
    path = os.path.join(prereg_dir, f"{c.candidate_id.replace(':', '_')}.yaml")
    lock = {
        "prereg": {
            "date_locked": time.strftime("%Y-%m-%d"),
            "candidate_id": c.candidate_id,
            "scope": config.get("boundary", {}).get("system", "unknown"),
        },
        "boundary": c.boundary,
        "candidate": {"kind": c.kind, "params": c.params},
        "gates": {"monitorability": {"fpr_targets": [0.01, 0.05, 0.10], "eps": 0.01, "floor_max": 0.20, "min_targets_ok": 2}},
        "notes": "Auto-generated prereg lock (skeleton).",
    }
    write_yaml_json(path, lock)


def main() -> None:
    ap = argparse.ArgumentParser(description="FIT-Explorer non-LLM runner (skeleton).")
    ap.add_argument("--config", default=None, help="Path to config (.yaml/.yml/.json).")
    ap.add_argument("--out_dir", default=None, help="Override output_dir from config.")
    ap.add_argument("--seed", type=int, default=0, help="Random seed for exploration.")
    args = ap.parse_args()

    random.seed(int(args.seed))

    config = coerce_config(load_config(args.config), args.out_dir)
    out_dir = str(config["output_dir"])
    os.makedirs(out_dir, exist_ok=True)

    # Write resolved config for provenance.
    write_yaml_json(os.path.join(out_dir, "resolved_config.yaml"), config)

    log_path = os.path.join(out_dir, "run_log.jsonl")
    leaderboard_path = os.path.join(out_dir, "leaderboard.csv")
    failure_map_path = os.path.join(out_dir, "failure_map.yaml")

    # ---- Explore ----
    cands = propose_candidates(config["budget"]["N0"], config["search_space"], config["boundary"])

    # Stage S0
    s0: List[Candidate] = []
    for c in cands:
        r0 = evaluate_candidate_stage0(c, config)
        write_jsonl(log_path, {"t": time.time(), "candidate": asdict(c), "result": asdict(r0)})
        if r0.label == "S0_PASS":
            s0.append(c)

    keep0 = max(1, int(len(s0) * float(config["budget"]["eta0"])))
    if len(s0) > keep0:
        s0 = random.sample(s0, keep0)

    # Stage S1 (gate)
    s1_pass: List[Candidate] = []
    for c in s0:
        write_prereg_lock(out_dir, c, config)
        r1 = evaluate_candidate_gate(c, config)
        write_jsonl(log_path, {"t": time.time(), "candidate": asdict(c), "result": asdict(r1)})
        if r1.label == "GATE_PASS":
            s1_pass.append(c)

    keep1 = max(1, int(len(s1_pass) * float(config["budget"]["eta1"])))
    if len(s1_pass) > keep1:
        s1_pass = random.sample(s1_pass, keep1)

    # Stage S2 (utility)
    leaderboard_rows: List[Dict[str, Any]] = []
    for c in s1_pass:
        r2 = evaluate_candidate_utility(c, config)
        write_jsonl(log_path, {"t": time.time(), "candidate": asdict(c), "result": asdict(r2)})
        leaderboard_rows.append(
            {
                "candidate_id": c.candidate_id,
                "family": c.params.get("family"),
                "window_W": c.params.get("window_W"),
                "smoothing": c.params.get("smoothing"),
                "calibration": c.params.get("calibration"),
                "label": r2.label,
                **r2.metrics,
            }
        )

    leaderboard_rows.sort(key=lambda x: (x.get("coverage@0.05", 0), x.get("lead_time_median", 0)), reverse=True)
    write_csv(leaderboard_path, leaderboard_rows)

    # Failure map (very small, placeholder): counts by label and by family.
    label_counts: Dict[str, int] = {}
    family_counts: Dict[str, Dict[str, int]] = {}
    for row in leaderboard_rows:
        label = str(row.get("label", "UNKNOWN"))
        fam = str(row.get("family", "UNKNOWN"))
        label_counts[label] = label_counts.get(label, 0) + 1
        family_counts.setdefault(fam, {})
        family_counts[fam][label] = family_counts[fam].get(label, 0) + 1

    write_yaml_json(
        failure_map_path,
        {
            "schema_version": "v0.1",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": "Placeholder failure map (counts only). Replace with a real failure map model.",
            "label_counts": label_counts,
            "family_x_label": family_counts,
        },
    )

    print(f"Done. Wrote:\n- {log_path}\n- {leaderboard_path}\n- {failure_map_path}\n- {os.path.join(out_dir, 'prereg')}{os.sep}")


if __name__ == "__main__":
    main()

