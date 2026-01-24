from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class EventResult:
    event_found: bool
    event_bin: Optional[int]
    reason: str

def detect_event_E_regime(df_bin: pd.DataFrame, cfg: dict) -> EventResult:
    # Implements prereg E_regime logic on bin-level series.
    delta_R = float(cfg["p11_event"]["delta_R"])
    W_jump = int(cfg["windows"]["event_jump_bins"])
    W_persist = int(cfg["windows"]["event_persist_bins"])
    co_req = int(cfg["p11_event"]["cooccurrence_required"])
    signals = cfg["p11_event"]["signals"]

    if "R_primary" not in df_bin.columns:
        return EventResult(False, None, "missing R_primary")

    R = df_bin["R_primary"].to_numpy(dtype=float)
    if len(R) <= W_jump + W_persist:
        return EventResult(False, None, "too few bins")

    for i in range(W_jump, len(R)):
        dR = R[i] - R[i - W_jump]
        if not np.isfinite(dR):
            continue
        if dR > -delta_R:
            continue

        # persistence: subsequent bins maintain negative delta (relative to i-W_jump baseline)
        ok_persist = True
        for j in range(i, min(len(R), i + W_persist)):
            if not np.isfinite(R[j]) or (R[j] - R[j - W_jump]) > 0:
                ok_persist = False
                break
        if not ok_persist:
            continue

        # co-occurrence: count hits among prereg signals
        hits = 0
        for s in signals:
            metric = s["metric"]
            req = s.get("requires", [])
            if req and metric not in df_bin.columns:
                continue
            if metric not in df_bin.columns:
                continue
            delta = float(s["delta"])
            direction = s["direction"]
            x = df_bin[metric].to_numpy(dtype=float)
            if not np.isfinite(x[i]) or not np.isfinite(x[i - W_jump]):
                continue
            dx = x[i] - x[i - W_jump]
            if direction == "down" and dx <= -delta:
                hits += 1
            elif direction == "up" and dx >= delta:
                hits += 1

        if hits >= co_req:
            return EventResult(True, int(df_bin.iloc[i]["bin_id"]), f"E_regime at bin_idx={i} hits={hits}")

    return EventResult(False, None, "no event under prereg thresholds")
