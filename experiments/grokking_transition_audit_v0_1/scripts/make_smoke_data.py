import csv
import os
import random
from pathlib import Path


def write_seed(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "step",
                "d_force",
                "d_info",
                "d_constraint",
                "d_force_alt",
                "d_info_alt",
                "d_constraint_alt",
                "acc_test",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)


def base_row(step):
    return {
        "step": step,
        "d_force": 0.05,
        "d_info": 0.05,
        "d_constraint": 0.05,
        "d_force_alt": 0.05,
        "d_info_alt": 0.05,
        "d_constraint_alt": 0.05,
        "acc_test": 0.35 + 0.001 * step,
    }


def make_registered(seed_idx):
    random.seed(1000 + seed_idx)
    rows = [base_row(s) for s in range(120)]
    for s in [58, 60, 62]:
        rows[s]["d_force"] = 0.9
    for s in [59, 60, 61]:
        rows[s]["d_info"] = 0.92
    for s in [60, 63]:
        rows[s]["d_constraint"] = 0.88
    for s in [60, 63]:
        rows[s]["d_force_alt"] = 0.87
    for s in [61, 63]:
        rows[s]["d_info_alt"] = 0.86
    for s in [62]:
        rows[s]["d_constraint_alt"] = 0.9
    for s in range(55, 80):
        rows[s]["acc_test"] += 0.12
    return rows


def make_no_transition(seed_idx):
    random.seed(2000 + seed_idx)
    rows = [base_row(s) for s in range(120)]
    for s in [30, 70]:
        rows[s]["d_force"] = 0.9
    for s in [45]:
        rows[s]["d_info"] = 0.85
    # constraint stays low; no co-window PT-MSS
    for s in [30, 70]:
        rows[s]["d_force_alt"] = 0.86
    for s in [45]:
        rows[s]["d_info_alt"] = 0.84
    return rows


def make_unstable(seed_idx):
    random.seed(3000 + seed_idx)
    rows = [base_row(s) for s in range(120)]
    for s in [48, 50, 52]:
        rows[s]["d_force"] = 0.89
    for s in [49, 51]:
        rows[s]["d_info"] = 0.9
    for s in [50]:
        rows[s]["d_constraint"] = 0.92

    # alt family is deliberately shifted far away => alignment fail
    for s in [90, 92]:
        rows[s]["d_force_alt"] = 0.9
    for s in [91]:
        rows[s]["d_info_alt"] = 0.9
    for s in [94]:
        rows[s]["d_constraint_alt"] = 0.9

    for s in range(48, 78):
        rows[s]["acc_test"] += 0.1
    return rows


def make_inconclusive(seed_idx):
    random.seed(4000 + seed_idx)
    rows = [base_row(s) for s in range(120)]
    # too many events -> density gate fail
    for s in range(15, 115):
        rows[s]["d_force"] = 0.95
        rows[s]["d_info"] = 0.95
        rows[s]["d_constraint"] = 0.95
        rows[s]["d_force_alt"] = 0.95
        rows[s]["d_info_alt"] = 0.95
        rows[s]["d_constraint_alt"] = 0.95
    return rows


def main():
    out_dir = Path("data/smoke")
    out_dir.mkdir(parents=True, exist_ok=True)

    generator_plan = [
        ("registered", make_registered, 4),
        ("no_transition", make_no_transition, 4),
        ("unstable", make_unstable, 2),
        ("inconclusive", make_inconclusive, 2),
    ]

    written = 0
    for tag, fn, n in generator_plan:
        for i in range(n):
            seed = f"{tag}_seed_{i:02d}"
            path = out_dir / f"{seed}.csv"
            write_seed(path, fn(i))
            written += 1

    print(f"wrote {written} smoke seed files to {out_dir}")


if __name__ == "__main__":
    main()

