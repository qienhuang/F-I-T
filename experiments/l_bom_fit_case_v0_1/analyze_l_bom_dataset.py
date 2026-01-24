from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class DatasetPaths:
    dataset_dir: Path
    count_json: Path
    ncount_json: Path
    countT_json: Path
    img_zip: Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_paths(dataset_dir: Path) -> DatasetPaths:
    dataset_dir = dataset_dir.resolve()
    count_json = dataset_dir / "count.json"
    ncount_json = dataset_dir / "ncount.json"
    countT_json = dataset_dir / "countT.json"
    img_zip = dataset_dir / "img.zip"
    missing = [p.name for p in [count_json, ncount_json, countT_json, img_zip] if not p.exists()]
    if missing:
        raise SystemExit(f"Missing files in dataset_dir: {missing}")
    return DatasetPaths(
        dataset_dir=dataset_dir,
        count_json=count_json,
        ncount_json=ncount_json,
        countT_json=countT_json,
        img_zip=img_zip,
    )


def as_vec4(x) -> List[float]:
    xs = list(x)
    if len(xs) != 4:
        raise ValueError(f"Expected 4-vector, got len={len(xs)}")
    return [float(v) for v in xs]


def normalize_vec(x: List[float], vmin: List[float], vmax: List[float]) -> List[float]:
    out = []
    for xi, lo, hi in zip(x, vmin, vmax):
        denom = (hi - lo) if (hi - lo) != 0 else 1.0
        out.append((xi - lo) / denom)
    return out


def l2(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def pearson_r(xs: List[float], ys: List[float]) -> Optional[float]:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return float(cov / math.sqrt(vx * vy))


def quantiles(xs: List[float], ps: Iterable[float]) -> Dict[str, float]:
    xs = sorted(float(x) for x in xs)
    if not xs:
        return {}
    out: Dict[str, float] = {}
    n = len(xs)
    for p in ps:
        p = float(p)
        if p <= 0:
            out[str(p)] = xs[0]
            continue
        if p >= 1:
            out[str(p)] = xs[-1]
            continue
        k = int(round(p * (n - 1)))
        k = max(0, min(n - 1, k))
        out[str(p)] = xs[k]
    return out


def read_voxel_from_zip(z: zipfile.ZipFile, idx: int) -> bytes:
    name = f"img/{idx}voxel"
    return z.read(name)


def occupancy_fraction(voxel_bytes: bytes) -> float:
    if not voxel_bytes:
        return 0.0
    # Treat any nonzero as solid.
    solid = sum(1 for b in voxel_bytes if b != 0)
    return float(solid / len(voxel_bytes))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", type=str, required=True)
    ap.add_argument("--out_dir", type=str, default="out")
    ap.add_argument("--sample_voxels", type=int, default=200)
    ap.add_argument("--radii", type=str, default="0.02,0.05,0.10,0.20")
    args = ap.parse_args()

    paths = ensure_paths(Path(args.dataset_dir))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    count = load_json(paths.count_json)  # id -> [d0,d1,d2,d3]
    ncount = load_json(paths.ncount_json)  # id -> normalized vec, plus min/max/targets
    countT = load_json(paths.countT_json)  # often a columnar transpose (C1..C4 -> list of floats)

    vmin = as_vec4(ncount["min"]) if "min" in ncount else None
    vmax = as_vec4(ncount["max"]) if "max" in ncount else None

    ids = [int(k) for k in count.keys() if str(k).isdigit()]
    ids.sort()

    # Basic stats on raw values
    raw_cols = [[], [], [], []]
    for k in ids:
        vec = as_vec4(count[str(k)])
        for i in range(4):
            raw_cols[i].append(vec[i])

    summary: Dict[str, object] = {
        "n_samples_count_json": len(ids),
        "raw_quantiles": {f"d{i}": quantiles(raw_cols[i], [0.0, 0.1, 0.5, 0.9, 1.0]) for i in range(4)},
        "has_minmax": bool(vmin and vmax),
        "targets": {},
        "coverage_by_target": {},
        "nearest_by_target": {},
        "voxel_checks": {},
    }

    # Target coverage / nearest neighbor in normalized space (using ncount min/max)
    radii = [float(x.strip()) for x in str(args.radii).split(",") if x.strip()]
    if vmin and vmax:
        norm_vectors: Dict[int, List[float]] = {}
        for k in ids:
            norm_vectors[k] = normalize_vec(as_vec4(count[str(k)]), vmin=vmin, vmax=vmax)

        # Targets are not consistently stored across releases. Prefer explicit 4-vectors in ncount, e.g. "C4".
        targets_raw: Dict[str, List[float]] = {}
        for k, v in ncount.items():
            if isinstance(k, str) and k.startswith("C") and isinstance(v, list) and len(v) == 4:
                targets_raw[k] = as_vec4(v)

        for name, t_raw_vec in targets_raw.items():
            t_norm = normalize_vec(t_raw_vec, vmin=vmin, vmax=vmax)

            best_k = None
            best_d = None
            for k in ids:
                d = l2(norm_vectors[k], t_norm)
                if best_d is None or d < best_d:
                    best_d = d
                    best_k = k

            summary["targets"][name] = {"raw": t_raw_vec, "norm": t_norm}
            summary["nearest_by_target"][name] = {
                "id": int(best_k) if best_k is not None else None,
                "l2_norm": float(best_d) if best_d is not None else None,
                "raw": as_vec4(count[str(best_k)]) if best_k is not None else None,
            }

            cov = {}
            for r in radii:
                n_in = sum(1 for k in ids if l2(norm_vectors[k], t_norm) <= r)
                cov[str(r)] = {"n": int(n_in), "frac": float(n_in / max(1, len(ids)))}
            summary["coverage_by_target"][name] = cov

    # Voxel sanity: correlate occupancy with d3 (the 4th scalar)
    sample_n = max(0, int(args.sample_voxels))
    if sample_n > 0:
        rng = random.Random(1337)
        sample_ids = ids[:] if sample_n >= len(ids) else rng.sample(ids, k=sample_n)
        xs: List[float] = []
        ys: List[float] = []

        with zipfile.ZipFile(paths.img_zip, "r") as z:
            for k in sample_ids:
                vb = read_voxel_from_zip(z, idx=k)
                occ = occupancy_fraction(vb)
                xs.append(occ)
                ys.append(float(as_vec4(count[str(k)])[3]))

        summary["voxel_checks"] = {
            "n_samples": int(len(xs)),
            "occ_fraction_quantiles": quantiles(xs, [0.0, 0.1, 0.5, 0.9, 1.0]),
            "d3_quantiles": quantiles(ys, [0.0, 0.1, 0.5, 0.9, 1.0]),
            "pearson_r_occ_vs_d3": pearson_r(xs, ys),
            "note": "occ_fraction uses nonzero voxel bytes as solid. Compare against d3 to infer whether d3 is porosity/volume fraction-like.",
        }

    # Write outputs
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# L-BOM Dataset Quick Report (local)")
    lines.append("")
    lines.append(f"- dataset_dir: `{str(paths.dataset_dir)}`")
    lines.append(f"- n_samples (count.json): `{len(ids)}`")
    lines.append(f"- voxel payload: `img.zip` with `img/<id>voxel` entries (expected size ~ 32^3 bytes)")
    lines.append("")
    lines.append("## Raw quantiles (count.json)")
    for i in range(4):
        q = summary["raw_quantiles"][f"d{i}"]  # type: ignore[index]
        lines.append(f"- d{i}: {q}")
    lines.append("")
    if summary["targets"]:
        lines.append("## Named vectors (from ncount.json) and nearest samples")
        lines.append("Note: some releases store example/reference vectors under keys like `C4`; they may be samples rather than design targets.")
        for name in sorted(summary["targets"].keys()):  # type: ignore[union-attr]
            t = summary["targets"][name]  # type: ignore[index]
            nn = summary["nearest_by_target"][name]  # type: ignore[index]
            lines.append(f"- {name}: raw={t['raw']} nearest_id={nn['id']} l2_norm={nn['l2_norm']}")
    lines.append("")
    if summary["coverage_by_target"]:
        lines.append("## Local density around named vectors (normalized L2 radii)")
        for name in sorted(summary["coverage_by_target"].keys()):  # type: ignore[union-attr]
            cov = summary["coverage_by_target"][name]  # type: ignore[index]
            lines.append(f"- {name}: {cov}")
    lines.append("")
    if summary["voxel_checks"]:
        lines.append("## Voxel sanity checks (sample)")
        vc = summary["voxel_checks"]  # type: ignore[assignment]
        lines.append(f"- n_samples: {vc['n_samples']}")
        lines.append(f"- pearson_r(occ_fraction, d3): {vc['pearson_r_occ_vs_d3']}")
        lines.append(f"- occ_fraction_quantiles: {vc['occ_fraction_quantiles']}")
        lines.append(f"- d3_quantiles: {vc['d3_quantiles']}")
        lines.append(f"- note: {vc['note']}")
    lines.append("")
    lines.append("## Next steps (FIT lens)")
    lines.append("- Treat `count.json` as a static phase catalog; to study loop dynamics you need a time-indexed trace (AL iterations).")
    lines.append("- If you can reconstruct the AL iteration trace from the full training pipeline, replace this static report with a time-indexed `cov(t)` and preregister E_jump per `docs/cases/CASE_05_Computational_Phase_Transition_Pitch.md`.")

    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote: {out_dir / 'report.md'}")
    print(f"Wrote: {out_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
