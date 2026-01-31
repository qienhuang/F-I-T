from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--missing_pae_rate", type=float, default=0.25)
    ap.add_argument("--missing_msa_rate", type=float, default=0.25)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    n = int(args.n)
    ids = [f"SYN{idx:07d}" for idx in range(n)]
    length = rng.integers(80, 800, size=n)

    # B0 features (bounded, plausible)
    I2_mean_plddt = np.clip(rng.normal(72, 12, size=n), 0, 100)
    C1_low_conf_frac = np.clip(rng.beta(2, 8, size=n), 0, 1)
    I1_hi_conf_frac = np.clip(rng.beta(6, 2, size=n), 0, 1)
    # make hi+low not exceed 1 too much
    I1_hi_conf_frac = np.clip(I1_hi_conf_frac * (1 - 0.4*C1_low_conf_frac), 0, 1)

    # entropy proxy: higher when mixed, lower when extreme
    I3_plddt_entropy = np.clip(1.0 - np.abs(I1_hi_conf_frac - 0.5) - np.abs(C1_low_conf_frac - 0.5), 0, 1)

    # oracle fields with partial signal + noise
    # PAE offdiag tends to be higher with more low confidence, longer proteins, lower mean pLDDT
    base_pae = 0.8*C1_low_conf_frac + 0.0008*(length - 200) + 0.006*(70 - I2_mean_plddt)
    C2_pae_offdiag = np.clip(base_pae + rng.normal(0, 0.15, size=n), -0.5, 3.0)

    # MSA depth: tends to be larger when high confidence + moderate length, but noisy/heavy-tailed
    log_msa = 2.0 + 1.2*I1_hi_conf_frac - 0.0012*(length - 200) + rng.normal(0, 0.6, size=n)
    msa_depth = np.clip(np.exp(log_msa), 0, 1e6)

    # missingness (simulate boundary switch availability)
    miss_pae = rng.random(n) < float(args.missing_pae_rate)
    miss_msa = rng.random(n) < float(args.missing_msa_rate)
    C2_pae_offdiag = C2_pae_offdiag.astype(float)
    msa_depth = msa_depth.astype(float)
    C2_pae_offdiag[miss_pae] = np.nan
    msa_depth[miss_msa] = np.nan

    df = pd.DataFrame({
        "accession": ids,
        "length": length.astype(int),
        "I1_hi_conf_frac": I1_hi_conf_frac.astype(float),
        "I2_mean_plddt": I2_mean_plddt.astype(float),
        "I3_plddt_entropy": I3_plddt_entropy.astype(float),
        "C1_low_conf_frac": C1_low_conf_frac.astype(float),
        # oracle stores
        "C2_pae_offdiag": C2_pae_offdiag,
        "msa_depth": msa_depth,
    })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote: {out} (n={len(df)})")

if __name__ == "__main__":
    main()
