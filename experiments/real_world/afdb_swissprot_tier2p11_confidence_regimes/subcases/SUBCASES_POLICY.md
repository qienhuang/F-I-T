# Subcases policy — canonical naming

This repository uses a **canonical subcase naming** policy for long‑lived case packs.

Canonical subcases in this case family:

- `pae_proxy_alarm/`  (Track A: proxy alarm / monitorability gate)
- `msa_deficit_proxy/` (Track B: proxy estimator for a B2‑only channel)
- `dual_oracle_active_acquisition/` (Track C: active boundary acquisition + robust claims)

Historical pack evolution should be preserved via **git tags / releases** and/or per‑subcase release notes (when provided), rather than proliferating directories like `*_v0_1/`, `*_v2_8/`, etc.

Migration note:

- This repo may still contain older `*_vX_Y/` directories from earlier iterations.
- Treat those as **legacy snapshots**. For reading, running, or citing, prefer the canonical folders listed above.
- New improvements should land in the canonical folders, with changes recorded in `RELEASE_NOTES.md` (and tags/releases as needed).

Related:

- Suite entrypoint: `../suite_v3_0/` (v3.1) (one‑click smoke + learning order)

Rationale:

- Avoid near‑duplicate subcase folders that drift over time.
- Make “the path a reader should run” unambiguous.
- Preserve evolution through release notes and version control.
