#!/usr/bin/env python3
"""
FIT Markov Sandbox - Numerical Validation

Demonstrates constraint accumulation via lazy hardening in finite Markov chains.

Key quantities:
- h(alpha): entropy rate (information production)
- C(alpha): mutual information (constraint)
- SLEM: second largest eigenvalue magnitude (mixing time proxy)

Usage:
    python experiments.py
    python experiments.py --n 30 --seed 42 --alpha_max 0.99
"""

from typing import Tuple, Optional
import numpy as np
from numpy.typing import NDArray


def row_normalize(A: NDArray[np.floating]) -> NDArray[np.floating]:
    """Normalize rows to sum to 1 (row-stochastic)."""
    A = np.clip(A, 1e-12, None)
    return A / A.sum(axis=1, keepdims=True)


def make_random_ergodic_P(n: int, seed: int = 0) -> NDArray[np.floating]:
    """
    Generate a random ergodic (irreducible, aperiodic) transition matrix.

    Args:
        n: Number of states
        seed: Random seed for reproducibility

    Returns:
        nxn row-stochastic transition matrix
    """
    rng = np.random.default_rng(seed)
    A = rng.random((n, n))
    P = row_normalize(A)
    # Ensure aperiodicity by adding self-loops
    P = 0.95 * P + 0.05 * np.eye(n)
    return row_normalize(P)


def stationary_dist(
    P: NDArray[np.floating],
    tol: float = 1e-12,
    max_iter: int = 200000
) -> NDArray[np.floating]:
    """
    Compute stationary distribution via power iteration.

    Args:
        P: Row-stochastic transition matrix
        tol: Convergence tolerance (L1 norm)
        max_iter: Maximum iterations

    Returns:
        Stationary distribution pi satisfying pi P = pi
    """
    n = P.shape[0]
    pi = np.ones(n) / n
    for _ in range(max_iter):
        pi_next = pi @ P
        if np.linalg.norm(pi_next - pi, 1) < tol:
            return pi_next
        pi = pi_next
    return pi


def entropy(p: NDArray[np.floating]) -> float:
    """
    Compute Shannon entropy H(p) = -sum_i p_i log(p_i).

    Args:
        p: Probability distribution

    Returns:
        Entropy in nats (natural log)
    """
    p = np.clip(p, 1e-15, 1.0)
    return float(-np.sum(p * np.log(p)))


def entropy_rate(P: NDArray[np.floating], pi: NDArray[np.floating]) -> float:
    """
    Compute entropy rate h = sum_i pi(i) H(P(i,.)).

    This measures the average uncertainty generated per transition.

    Args:
        P: Transition matrix
        pi: Stationary distribution

    Returns:
        Entropy rate in nats
    """
    return float(np.sum([pi[i] * entropy(P[i, :]) for i in range(P.shape[0])]))


def mutual_info_one_step(P: NDArray[np.floating], pi: NDArray[np.floating]) -> float:
    """
    Compute one-step mutual information I(X_t; X_{t+1}).

    Under stationarity: I(X;Y) = H(Y) - H(Y|X) = H(pi) - h

    Args:
        P: Transition matrix
        pi: Stationary distribution

    Returns:
        Mutual information (constraint measure) in nats
    """
    h_cond = entropy_rate(P, pi)
    h_marg = entropy(pi)
    return float(h_marg - h_cond)


def slem(P: NDArray[np.floating]) -> float:
    """
    Compute Second Largest Eigenvalue Magnitude (SLEM).

    SLEM is a proxy for mixing time: as SLEM -> 1, mixing slows.

    Args:
        P: Transition matrix

    Returns:
        |lambda_2| where lambda_2 is the second largest eigenvalue
    """
    vals = np.linalg.eigvals(P.T)
    mags = np.sort(np.abs(vals))[::-1]
    return float(mags[1])


def run_sweep(
    n: int = 20,
    seed: int = 0,
    alphas: Optional[NDArray[np.floating]] = None
) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
    """
    Sweep over hardening parameter alpha and compute FIT quantities.

    The lazy hardening family is: P_alpha = (1-alpha) P + alpha I

    Args:
        n: Number of states
        seed: Random seed
        alphas: Array of alpha values (default: linspace(0, 0.99, 50))

    Returns:
        Tuple of:
        - data: Array with columns [alpha, h(alpha), C(alpha), SLEM(alpha)]
        - P: The base transition matrix
    """
    if alphas is None:
        alphas = np.linspace(0.0, 0.99, 50)

    P = make_random_ergodic_P(n, seed=seed)
    I = np.eye(n)
    out = []

    # Proposition 1 (stationary invariance under lazy hardening) holds, so we can
    # reuse the base stationary distribution for all alpha.
    pi = stationary_dist(P)

    for a in alphas:
        # Lazy hardening: P_alpha = (1-alpha) P + alpha I
        Pa = (1 - a) * P + a * I
        h = entropy_rate(Pa, pi)
        C = mutual_info_one_step(Pa, pi)
        lam2 = slem(Pa)
        out.append((a, h, C, lam2))

    return np.array(out), P


def main():
    """Run validation and print summary."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FIT Markov Sandbox - Numerical Validation"
    )
    parser.add_argument("--n", type=int, default=30, help="Number of states")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--alpha_max", type=float, default=0.99, help="Max alpha")
    parser.add_argument("--n_points", type=int, default=50, help="Number of alpha points")
    args = parser.parse_args()

    alphas = np.linspace(0.0, args.alpha_max, args.n_points)
    data, P = run_sweep(n=args.n, seed=args.seed, alphas=alphas)

    # Print header
    print(f"FIT Markov Sandbox Validation (n={args.n}, seed={args.seed})")
    print("=" * 50)
    print(f"{'alpha':>8}  {'h(alpha)':>10}  {'C(alpha)':>10}  {'SLEM':>8}")
    print("-" * 50)

    # Print every 10th row
    for row in data[::10]:
        print(f"{row[0]:>8.2f}  {row[1]:>10.4f}  {row[2]:>10.4f}  {row[3]:>8.4f}")

    # Summary
    print("-" * 50)
    print(f"h reduction: {(1 - data[-1,1]/data[0,1])*100:.1f}%")
    print(f"C increase:  {data[-1,2]/data[0,2]:.1f}x")
    print(f"SLEM at alpha=0.99: {data[-1,3]:.4f}")


if __name__ == "__main__":
    main()
