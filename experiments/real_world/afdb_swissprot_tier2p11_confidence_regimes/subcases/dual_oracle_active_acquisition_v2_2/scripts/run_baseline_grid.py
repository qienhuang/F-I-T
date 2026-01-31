from __future__ import annotations
import argparse
import subprocess
from pathlib import Path
import yaml


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--policy", default=None, help="baseline family policy; default from prereg robustness.baseline.family_policy")
    args = ap.parse_args()

    prereg = Path(args.prereg)
    cfg = yaml.safe_load(prereg.read_text(encoding="utf-8"))
    seeds = (cfg.get("robustness", {}).get("baseline", {}) or {}).get("seeds", [])
    if not seeds:
        raise SystemExit("No robustness.baseline.seeds in prereg.")
    policy = args.policy or (cfg.get("robustness", {}).get("baseline", {}) or {}).get("family_policy", "random_hash__random_hash")

    out_root = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    for s in seeds:
        run_id = f"BASE_{int(s)}"
        tmp_cfg = dict(cfg)
        tmp_cfg["data"] = dict(tmp_cfg.get("data", {}))
        tmp_cfg["data"]["seed_string"] = f"{tmp_cfg['data'].get('seed_string','SEED')}_BASE_{int(s)}"
        tmp_cfg["acquisition"] = dict(tmp_cfg.get("acquisition", {}))
        tmp_cfg["acquisition"]["policy_specs"] = [policy]
        tmp_cfg["outputs"] = dict(tmp_cfg.get("outputs", {}))
        tmp_cfg["outputs"]["out_root"] = str(out_root)

        tmp_path = out_root / f"_tmp_prereg_{int(s)}.yaml"
        tmp_path.write_text(yaml.safe_dump(tmp_cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")

        subprocess.check_call(["python", "-m", "src.run", "--prereg", str(tmp_path), "--run_id", run_id], cwd=str(prereg.parent))
        tmp_path.unlink(missing_ok=True)

    print(f"Baseline grid complete: {out_root}")


if __name__ == "__main__":
    main()
