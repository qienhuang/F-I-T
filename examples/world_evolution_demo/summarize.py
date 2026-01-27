#!/usr/bin/env python3
"""
Summarize a search_run directory: prints top candidates and failure label counts.
"""
import argparse, os, csv, json
from collections import Counter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", required=True)
    args = ap.parse_args()

    lb = os.path.join(args.indir, "leaderboard_feasible.csv")
    fm = os.path.join(args.indir, "failure_map.yaml")

    if os.path.exists(lb):
        with open(lb, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        print("Top feasible candidates (up to 10):")
        for r in rows[:10]:
            print(r)
    else:
        print("No feasible leaderboard found.")

    if os.path.exists(fm):
        data = json.loads(open(fm, "r", encoding="utf-8").read())
        c = {e["label"]: e["count"] for e in data.get("entries", [])}
        print("Failure label counts:", c)
    else:
        print("No failure_map.yaml found.")

if __name__ == "__main__":
    main()
