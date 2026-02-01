from __future__ import annotations

import argparse
import json
from pathlib import Path

from .prereg import load_prereg, prereg_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a minimal fail-windows note for audit")
    parser.add_argument("--prereg", required=True, help="Preregistration YAML")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parents[1]
    prereg = load_prereg(Path(args.prereg).resolve())
    paths = prereg_paths(prereg, workdir)

    if not paths.coherence_report_json.exists():
        # regimes step not run yet; write a placeholder.
        paths.fail_windows_md.parent.mkdir(parents=True, exist_ok=True)
        paths.fail_windows_md.write_text("# Fail windows\n\n(Not generated yet; run `python -m src.regimes`.)\n", encoding="utf-8")
        return

    report = json.loads(paths.coherence_report_json.read_text(encoding="utf-8"))
    verdict = report.get("verdict", "UNKNOWN")
    pass_gate = report.get("pass_gate", False)
    rho = report.get("rho_across_windows", None)
    thr = report.get("coherence_threshold_rho", None)

    if pass_gate:
        text = "# Fail windows\n\nNone. Coherence gate passed for the preregistered estimator family.\n"
    else:
        text = (
            "# Fail windows\n\n"
            "The v0.1 run uses a single coherence gate across windows.\n\n"
            f"- Verdict: `{verdict}`\n"
            f"- Observed rho: `{rho}`\n"
            f"- Threshold: `|rho| >= {thr}`\n\n"
            "Interpretation is disallowed under EST discipline.\n"
        )

    paths.fail_windows_md.parent.mkdir(parents=True, exist_ok=True)
    paths.fail_windows_md.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()

