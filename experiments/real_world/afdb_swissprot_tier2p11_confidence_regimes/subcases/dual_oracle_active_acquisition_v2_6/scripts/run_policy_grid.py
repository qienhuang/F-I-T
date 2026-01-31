from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
import yaml


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--seeds", default=None, help="comma-separated override seeds")
    ap.add_argument("--max_policies", type=int, default=None, help="limit number of policy_specs (for smoke/CI)")
    args = ap.parse_args()

    prereg = Path(args.prereg)
    cfg = yaml.safe_load(prereg.read_text(encoding="utf-8"))

    pol_cfg = (cfg.get("robustness", {}).get("policy", {}) or {})
    seeds = pol_cfg.get("seeds", [])
    if args.seeds:
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()]

    if not seeds:
        raise SystemExit("No robustness.policy.seeds found (or provided).")

    policy_specs = (cfg.get("acquisition", {}) or {}).get("policy_specs", [])
    if not isinstance(policy_specs, list) or not policy_specs:
        raise SystemExit("No acquisition.policy_specs found in prereg.")

    if args.max_policies is not None:
        policy_specs = policy_specs[: int(args.max_policies)]

    out_root = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "policy_seeds": seeds,
        "policy_specs_used": policy_specs,
        "runs": []
    }

    for s in seeds:
        run_id = f"POLICY_{int(s)}"
        tmp_cfg = dict(cfg)
        tmp_cfg["data"] = dict(tmp_cfg.get("data", {}))
        tmp_cfg["data"]["seed_string"] = f"{tmp_cfg['data'].get('seed_string','SEED')}_POLICY_{int(s)}"
        tmp_cfg["acquisition"] = dict(tmp_cfg.get("acquisition", {}))
        tmp_cfg["acquisition"]["policy_specs"] = policy_specs
        tmp_cfg["outputs"] = dict(tmp_cfg.get("outputs", {}))
        tmp_cfg["outputs"]["out_root"] = str(out_root)

        tmp_path = out_root / f"_tmp_prereg_policy_{int(s)}.yaml"
        tmp_path.write_text(yaml.safe_dump(tmp_cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")

        subprocess.check_call(["python", "-m", "src.run", "--prereg", str(tmp_path), "--run_id", run_id], cwd=str(prereg.parent))
        tmp_path.unlink(missing_ok=True)

        manifest["runs"].append({"seed": int(s), "run_id": run_id})

    (out_root / "policy_grid_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Policy grid complete: {out_root}")


if __name__ == "__main__":
    main()
