from __future__ import annotations
import argparse
from pathlib import Path

REQUIRED = ['PREREG.locked.yaml', 'dataset_snapshot.json', 'boundary_snapshot.json', 'model.joblib', 'eval_metrics.json', 'eval_report.md', 'tradeoff_onepage.pdf', 'run_manifest.json']

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    args = ap.parse_args()
    rd = Path(args.run_dir)
    if not rd.exists():
        raise SystemExit(f"run_dir does not exist: {rd}")
    missing = [f for f in REQUIRED if not (rd / f).exists()]
    if missing:
        raise SystemExit("Missing required artifacts:\n" + "\n".join(f"- {m}" for m in missing))
    print("OK: artifacts present for pae_proxy_alarm_smoke.")

if __name__ == "__main__":
    main()
