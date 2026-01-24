from __future__ import annotations
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_onepage(df_bin: pd.DataFrame, run_dir: Path, cfg: dict, event_bin: Optional[int]) -> Path:
    bin_width = int(cfg["axis"]["bin_width_aa"])
    min_len = int(cfg["boundary"]["selection"]["filters"]["min_length"])

    x = min_len + (df_bin["bin_id"].to_numpy(dtype=float) + 0.5) * bin_width

    # Choose C_primary series column
    if "C_primary" in df_bin.columns:
        c_primary = df_bin["C_primary"].to_numpy(dtype=float)
    else:
        c_primary = df_bin["C1_low_conf_frac"].to_numpy(dtype=float)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    # Panel A
    axA.plot(x, df_bin["I1_hi_conf_frac"].to_numpy(dtype=float), label="I1_hi_conf_frac")
    if "I2_mean_plddt" in df_bin.columns:
        axA.plot(x, df_bin["I2_mean_plddt"].to_numpy(dtype=float) / 100.0, label="I2_mean_plddt/100")
    axA.set_title("(A) Information vs length")
    axA.set_xlabel("length bin midpoint (aa)")
    axA.set_ylabel("I_hat")
    axA.legend()

    # Panel B
    axB.plot(x, df_bin["C1_low_conf_frac"].to_numpy(dtype=float), label="C1_low_conf_frac")
    if "C2_pae_offdiag_norm" in df_bin.columns:
        axB.plot(x, df_bin["C2_pae_offdiag_norm"].to_numpy(dtype=float), label="C2_pae_offdiag_norm")
    if "C3_msa_deficit_norm" in df_bin.columns:
        axB.plot(x, df_bin["C3_msa_deficit_norm"].to_numpy(dtype=float), label="C3_msa_deficit_norm")
    if "C_primary" in df_bin.columns:
        axB.plot(x, df_bin["C_primary"].to_numpy(dtype=float), label="C_primary", linewidth=2)
    axB.set_title("(B) Constraint proxies (boundary-sensitive)")
    axB.set_xlabel("length bin midpoint (aa)")
    axB.set_ylabel("C_hat")
    axB.legend()

    # Panel C
    axC.plot(x, df_bin["R_primary"].to_numpy(dtype=float), label="R_primary")
    axC.set_title("(C) Regime score + event")
    axC.set_xlabel("length bin midpoint (aa)")
    axC.set_ylabel("R")
    if event_bin is not None:
        x0 = min_len + (float(event_bin) + 0.5) * bin_width
        axC.axvline(x0)
        axC.text(x0, np.nanmax(df_bin["R_primary"].to_numpy(dtype=float)), "E_regime", rotation=90, va="top")
    axC.legend()

    # Panel D
    idx = np.arange(len(df_bin))
    sizes = np.maximum(df_bin["bin_n"].to_numpy(dtype=float) / 50.0, 10.0)
    sc = axD.scatter(c_primary, df_bin["I1_hi_conf_frac"].to_numpy(dtype=float), c=idx, s=sizes)
    axD.set_title("(D) Trade-off geometry")
    axD.set_xlabel("C_primary (or C1 in B0)")
    axD.set_ylabel("I1_hi_conf_frac")
    fig.colorbar(sc, ax=axD, label="bin index")

    boundary_mode = cfg["boundary"]["boundary_mode"]
    rel = cfg["boundary"]["afdb_release_version"]
    N = int(cfg["boundary"]["selection"]["sampler"]["target_n_valid"])
    footer = f"case=afdb_swissprot_tier2p11_confidence_regimes | boundary={boundary_mode} | release={rel} | N~{N} | bin_w={bin_width} | smooth={cfg['windows']['smoothing_bins']}"
    fig.suptitle(footer, y=0.98)
    fig.tight_layout()

    out = run_dir / "tradeoff_onepage.pdf"
    fig.savefig(out)
    plt.close(fig)
    return out
