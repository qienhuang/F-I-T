from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

def _parse_pdb_bfactors(pdb_text: str) -> Dict[int, float]:
    # Parse PDB and return per-residue pLDDT extracted from B-factor.
    # We use CA atoms when available; fallback to median across atoms in residue.
    by_res: Dict[int, List[float]] = {}
    ca_by_res: Dict[int, float] = {}
    for line in pdb_text.splitlines():
        if not (line.startswith("ATOM") or line.startswith("HETATM")):
            continue
        if len(line) < 66:
            continue
        atom_name = line[12:16].strip()
        try:
            resseq = int(line[22:26].strip())
        except Exception:
            continue
        try:
            b = float(line[60:66].strip())
        except Exception:
            continue
        by_res.setdefault(resseq, []).append(b)
        if atom_name == "CA":
            ca_by_res[resseq] = b
    out: Dict[int, float] = {}
    for resseq, vals in by_res.items():
        out[resseq] = ca_by_res.get(resseq, float(np.median(vals)))
    return out

def _tokenize_cif_value(tok: str) -> str:
    if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
        return tok[1:-1]
    return tok

def _parse_mmcif_atom_site(lines: List[str]) -> Tuple[List[str], List[List[str]]]:
    # Minimal mmCIF loop parser for AFDB coordinate files.
    # Finds a loop_ with _atom_site.* keys, then reads row tokens.
    keys: List[str] = []
    rows: List[List[str]] = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == "loop_":
            j = i + 1
            klist: List[str] = []
            while j < n and lines[j].lstrip().startswith("_atom_site."):
                klist.append(lines[j].strip())
                j += 1
            if not klist:
                i += 1
                continue
            keys = klist
            cur_tokens: List[str] = []
            while j < n:
                line = lines[j].strip()
                if not line:
                    j += 1
                    continue
                if line == "loop_" or (line.startswith("_") and not cur_tokens):
                    break
                toks = [_tokenize_cif_value(t) for t in line.split()]
                cur_tokens.extend(toks)
                while len(cur_tokens) >= len(keys):
                    row = cur_tokens[:len(keys)]
                    rows.append(row)
                    cur_tokens = cur_tokens[len(keys):]
                j += 1
            return keys, rows
        i += 1
    return [], []

def _parse_cif_bfactors(cif_text: str) -> Dict[int, float]:
    # Parse mmCIF and return per-residue pLDDT from _atom_site.B_iso_or_equiv.
    # Use CA atoms when available; fallback to median across atoms in residue.
    lines = cif_text.splitlines()
    keys, rows = _parse_mmcif_atom_site(lines)
    if not keys:
        raise ValueError("mmCIF: could not find _atom_site loop.")

    def idx(name: str) -> int:
        try:
            return keys.index(name)
        except ValueError:
            return -1

    i_b = idx("_atom_site.B_iso_or_equiv")
    i_atom = idx("_atom_site.label_atom_id")
    i_auth = idx("_atom_site.auth_seq_id")
    i_label = idx("_atom_site.label_seq_id")

    if i_b < 0 or i_atom < 0:
        raise ValueError("mmCIF: missing required atom_site columns (B_iso_or_equiv / label_atom_id).")

    seq_idx = i_auth if i_auth >= 0 else i_label
    if seq_idx < 0:
        raise ValueError("mmCIF: missing seq id (auth_seq_id or label_seq_id).")

    by_res: Dict[int, List[float]] = {}
    ca_by_res: Dict[int, float] = {}
    for r in rows:
        try:
            resseq = int(r[seq_idx])
        except Exception:
            continue
        atom = r[i_atom]
        try:
            b = float(r[i_b])
        except Exception:
            continue
        by_res.setdefault(resseq, []).append(b)
        if atom == "CA":
            ca_by_res[resseq] = b

    out: Dict[int, float] = {}
    for resseq, vals in by_res.items():
        out[resseq] = ca_by_res.get(resseq, float(np.median(vals)))
    return out

def load_plddt_from_coords(path: str | Path) -> Tuple[np.ndarray, int]:
    # Load per-residue pLDDT array from AFDB coordinate file (.cif or .pdb).
    p = Path(path)
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix.lower() == ".pdb":
        m = _parse_pdb_bfactors(txt)
    else:
        m = _parse_cif_bfactors(txt)

    if not m:
        raise ValueError(f"No residues parsed from: {p.name}")

    keys = sorted(m.keys())
    start, end = keys[0], keys[-1]
    arr = np.full((end - start + 1,), np.nan, dtype=float)
    for k, v in m.items():
        arr[k - start] = v

    if np.isnan(arr).any():
        med = float(np.nanmedian(arr))
        arr = np.where(np.isnan(arr), med, arr)

    return arr, int(arr.shape[0])
