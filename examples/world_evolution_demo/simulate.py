#!/usr/bin/env python3
"""
Toy world A1: Stochastic Majority Cellular Automaton
- binary grid with periodic boundary
- update rule: majority of Moore neighborhood (3x3) with noise p(t)
- schedule p(t) linearly increases from p0 to p1

Outputs traces as JSONL:
{
  "run_id": "...",
  "seed": 0,
  "t": 123,
  "p": 0.12,
  "density": 0.53,
  "magnetization": 0.06,
  "activity": 0.21
}

We store only macro observables for speed; you can extend to store micro state snapshots if needed.
"""
import argparse, json, time, math, random
from dataclasses import dataclass
from typing import List, Tuple

def torus_idx(i, n):
    return i % n

def majority_update(grid, p):
    n = len(grid)
    m = len(grid[0])
    new = [[0]*m for _ in range(n)]
    activity = 0
    for i in range(n):
        for j in range(m):
            # Moore neighborhood majority
            s = 0
            for di in (-1,0,1):
                for dj in (-1,0,1):
                    s += grid[torus_idx(i+di,n)][torus_idx(j+dj,m)]
            maj = 1 if s >= 5 else 0  # 9-neighbor majority
            # noise flip
            if random.random() < p:
                maj = 1 - maj
            new[i][j] = maj
            if new[i][j] != grid[i][j]:
                activity += 1
    return new, activity / (n*m)

def density(grid):
    n = len(grid); m=len(grid[0])
    return sum(sum(row) for row in grid)/(n*m)

def magnetization_from_density(d):
    # map density in [0,1] to |2d-1| in [0,1]
    return abs(2*d - 1)

def simulate_run(seed: int, grid_size: int, steps: int, p0: float, p1: float, init_p: float = 0.9):
    random.seed(seed)
    n = grid_size
    # init in an ordered state by default (high magnetization),
    # so a threshold-crossing event can occur later under the noise schedule.
    grid = [[1 if random.random() < init_p else 0 for _ in range(n)] for _ in range(n)]
    out = []
    for t in range(steps):
        p = p0 + (p1 - p0) * (t / max(1, steps-1))
        d = density(grid)
        m = magnetization_from_density(d)
        grid, act = majority_update(grid, p)
        out.append({"t": t, "p": p, "density": d, "magnetization": m, "activity": act})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output jsonl path")
    ap.add_argument("--runs", type=int, default=40)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--p0", type=float, default=0.02)
    ap.add_argument("--p1", type=float, default=0.45)
    ap.add_argument("--init_p", type=float, default=0.9, help="initial probability of 1s (bias toward an ordered state)")
    args = ap.parse_args()

    with open(args.out, "w", encoding="utf-8") as f:
        for r in range(args.runs):
            seed = args.seed0 + r
            run_id = f"run_{seed}"
            trace = simulate_run(seed, args.grid, args.steps, args.p0, args.p1, init_p=args.init_p)
            for row in trace:
                row.update({"run_id": run_id, "seed": seed})
                f.write(json.dumps(row) + "\n")

    print(f"Wrote traces to {args.out}")

if __name__ == "__main__":
    main()
