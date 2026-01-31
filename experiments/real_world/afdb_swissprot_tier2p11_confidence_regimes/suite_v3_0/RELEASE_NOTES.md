# Suite release notes — AFDB Non‑LLM Small‑Models Suite

## v3.1 — Environment convergence + developer ergonomics

Additions:

- `requirements.all.txt`: convenience union of the three subcase requirements for single-env installs.
- `Makefile`: canonical developer targets (`make smoke`, `make pae`, `make msa`, `make dual`, `make clean`).
- `PROMPT_GUIDE.md`: suite-level LLM/coding assistant discipline (PREREG-first, boundary-safe, gate-compliant claims).

No changes to estimator semantics or boundary definitions.

## v3.0 — Initial suite pack

- Bundled three canonical subcases (PAE proxy alarm, MSA deficit proxy, dual-oracle active acquisition).
- Added suite one-click smoke runner: `suite_ci_check.sh`.
- Canonicalized subcase folder names (no version suffix).
