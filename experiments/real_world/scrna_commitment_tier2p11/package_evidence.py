from __future__ import annotations

import argparse
import json
import shutil
import time
import zipfile
from pathlib import Path


def _add_dir(zf: zipfile.ZipFile, root: Path, rel_prefix: str, allow_ext: set[str]) -> int:
    count = 0
    if not root.exists():
        return 0
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        if p.suffix.lower() not in allow_ext:
            continue
        arc = str(Path(rel_prefix) / p.relative_to(root))
        zf.write(p, arcname=arc)
        count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser(description="Package scRNA commitment evidence artifacts into a zip")
    ap.add_argument("--out", default=None, help="Output zip path (default: evidence_<ts>.zip)")
    ap.add_argument("--sanity_dir", default="outputs", help="Sanity outputs folder")
    ap.add_argument("--main_dir", default=None, help="Main outputs folder (optional)")
    ap.add_argument("--note", default="EVIDENCE_NOTE_TEMPLATE.md", help="Evidence note (md)")
    args = ap.parse_args()

    workdir = Path(__file__).resolve().parent
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = Path(args.out) if args.out else workdir / f"evidence_{ts}.zip"
    out = out if out.is_absolute() else (workdir / out)
    out.parent.mkdir(parents=True, exist_ok=True)

    allow_ext = {".yaml", ".yml", ".json", ".md", ".png", ".pdf", ".parquet", ".csv"}
    sanity = workdir / args.sanity_dir
    main_outputs = (workdir / args.main_dir) if args.main_dir else None
    note = workdir / args.note

    manifest: dict[str, object] = {"created": ts, "sanity_dir": str(sanity), "main_dir": str(main_outputs) if main_outputs else None}

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        n1 = _add_dir(zf, sanity, "sanity", allow_ext)
        manifest["sanity_files"] = n1

        if main_outputs:
            n2 = _add_dir(zf, main_outputs, "main", allow_ext)
            manifest["main_files"] = n2

        if note.exists():
            zf.write(note, arcname="EVIDENCE_NOTE.md")

        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    print(str(out))


if __name__ == "__main__":
    main()

