#!/usr/bin/env python3
"""
Fit a simple failure-map model from results/run_log.jsonl.

This is a helper for sampling bias; it never overrides gates.
"""
import os, json
from collections import Counter, defaultdict

def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: 
                continue
            rows.append(json.loads(line))
    return rows

def main():
    log_path = os.path.join("results", "run_log.jsonl")
    if not os.path.exists(log_path):
        print("Missing results/run_log.jsonl")
        return

    rows = load_jsonl(log_path)
    # Build simple counts by param buckets
    by_family = Counter()
    by_window = Counter()
    labels = Counter()

    for r in rows:
        cand = r.get("candidate", {})
        params = cand.get("params", {})
        res = r.get("result", {})
        label = res.get("label")
        if label:
            labels[label] += 1
        fam = params.get("family")
        w = params.get("window_W")
        if fam:
            by_family[(fam, label)] += 1
        if w is not None:
            by_window[(w, label)] += 1

    print("Label counts:", dict(labels))
    print("Family x label (top):", by_family.most_common(10))
    print("Window x label (top):", by_window.most_common(10))

    # Optional: if sklearn is available, fit a tree classifier
    try:
        from sklearn.tree import DecisionTreeClassifier
        import numpy as np

        X, y = [], []
        fam_map = {}
        def fam_id(f):
            if f not in fam_map:
                fam_map[f] = len(fam_map)
            return fam_map[f]

        # Use only gate stage S1 labels as a proxy feasibility target
        for r in rows:
            res = r.get("result", {})
            if res.get("stage") != "S1":
                continue
            label = res.get("label")
            cand = r.get("candidate", {})
            params = cand.get("params", {})
            X.append([fam_id(params.get("family","")), float(params.get("window_W",0)), float(params.get("smoothing",0.0))])
            y.append(1 if label == "GATE_PASS" else 0)

        if len(set(y)) >= 2 and len(y) >= 10:
            clf = DecisionTreeClassifier(max_depth=3, random_state=0)
            clf.fit(np.array(X), np.array(y))
            print("Tree trained. Feature importances:", clf.feature_importances_)
            print("fam_map:", fam_map)
        else:
            print("Not enough data to fit a classifier (need both classes and >=10 samples).")
    except Exception as e:
        print("sklearn not available or failed:", str(e))

if __name__ == "__main__":
    main()
