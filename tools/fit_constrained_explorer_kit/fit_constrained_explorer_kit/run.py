from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict

import numpy as np

from .config import load_prereg, validate_prereg
from .domain_toy_bitstring import decode_cfg, is_feasible, oracle_reward, fingerprint_bits, summarize_constraints
from .search import propose
from .plot_onepager import plot_onepage
from .report import render_report


def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--run_id", default=None)
    args = ap.parse_args()

    cfg = load_prereg(args.prereg).raw
    validate_prereg(cfg)

    kit_dir = Path(__file__).resolve().parents[1]
    out_root = kit_dir / cfg.get("outputs", {}).get("out_root", "out")
    out_root.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # lock prereg
    _write_text(run_dir / "PREREG.locked.yaml", Path(args.prereg).read_text(encoding="utf-8"))

    dom = decode_cfg(cfg)

    max_evals = int(cfg["budget"]["oracle_evals_max"])
    batch_size = int(cfg["search"]["batch_size"])
    rounds = int(cfg["search"]["rounds"])
    init_random = int(cfg["search"]["init_random"])
    policies = list(cfg["search"]["policies"])

    evaluated_X: list[np.ndarray] = []
    evaluated_y: list[float] = []
    evaluated_fp: list[str] = []
    trace: list[dict] = []

    best = {"reward": float("-inf"), "fingerprint": None, "bits": None, "policy": None, "eval_index": None}

    def _eval_batch(X: np.ndarray, policy: str, start_idx: int) -> int:
        nonlocal best
        feas = is_feasible(dom, X)
        r = oracle_reward(dom, X)
        for i in range(X.shape[0]):
            if len(evaluated_y) >= max_evals:
                break
            fp = fingerprint_bits(X[i])
            evaluated_X.append(X[i].copy())
            evaluated_y.append(float(r[i]) if bool(feas[i]) else float("nan"))
            evaluated_fp.append(fp)

            reward_val = float(r[i]) if bool(feas[i]) else float("nan")
            if bool(feas[i]) and reward_val > float(best["reward"]):
                best = {
                    "reward": reward_val,
                    "fingerprint": fp,
                    "bits": X[i].astype(int).tolist(),
                    "policy": policy,
                    "eval_index": int(len(evaluated_y)),
                }

            trace.append(
                {
                    "eval_index": int(len(evaluated_y)),
                    "policy": policy,
                    "feasible": bool(feas[i]),
                    "reward": reward_val,
                    "fingerprint": fp,
                    "best_reward_so_far": float(best["reward"]),
                }
            )
        return len(evaluated_y)

    # init
    X0 = propose(
        policy="random",
        cfg=dom,
        batch_size=min(init_random, max_evals),
        rng_tag=dom.seed_string + "::init",
        evaluated_X=None,
        evaluated_y=None,
        policy_cfg=cfg["search"],
    ).X
    _eval_batch(X0, policy="init_random", start_idx=0)

    # rounds
    for r in range(1, rounds + 1):
        if len(evaluated_y) >= max_evals:
            break

        evX = np.stack(evaluated_X, axis=0)
        evy = np.asarray(evaluated_y, dtype=np.float64)
        # train surrogate only on feasible samples (toy semantics)
        ok = np.isfinite(evy)
        evX_ok = evX[ok]
        evy_ok = evy[ok]

        for policy in policies:
            if len(evaluated_y) >= max_evals:
                break
            pr = propose(
                policy=policy,
                cfg=dom,
                batch_size=min(batch_size, max_evals - len(evaluated_y)),
                rng_tag=dom.seed_string + f"::round{r}::{policy}",
                evaluated_X=evX_ok if len(evX_ok) else None,
                evaluated_y=evy_ok if len(evy_ok) else None,
                policy_cfg=cfg["search"],
            )
            _eval_batch(pr.X, policy=policy, start_idx=len(evaluated_y))

    _write_json(run_dir / "best_candidate.json", best)
    import pandas as pd

    pd.DataFrame(trace).to_csv(run_dir / "trace.csv", index=False)

    constraints = summarize_constraints(dom)
    summary = {
        "n_oracle_evals": int(len(evaluated_y)),
        "best_reward": float(best["reward"]),
        "best_policy": best.get("policy"),
        "feasible_rate": float(np.mean([1.0 if t["feasible"] else 0.0 for t in trace])) if trace else float("nan"),
    }
    _write_text(run_dir / "eval_report.md", render_report(run_id=run_id, cfg=cfg, best=best, constraints=constraints, summary=summary))

    plot_onepage(
        out_pdf=run_dir / "onepage.pdf",
        trace=trace,
        meta_footer=f"kit=fit_constrained_explorer_kit | case={cfg.get('preregistration', {}).get('case_id', 'UNKNOWN')} | budget={max_evals}",
    )

    _write_json(
        run_dir / "run_manifest.json",
        {
            "kit_id": cfg.get("preregistration", {}).get("kit_id", "fit_constrained_explorer_kit"),
            "case_id": cfg.get("preregistration", {}).get("case_id", "UNKNOWN"),
            "run_id": run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "artifacts": {
                "locked_prereg": "PREREG.locked.yaml",
                "trace": "trace.csv",
                "best": "best_candidate.json",
                "report": "eval_report.md",
                "onepage": "onepage.pdf",
            },
        },
    )

    print(f"Run complete. Outputs in: {run_dir}")


if __name__ == "__main__":
    main()

