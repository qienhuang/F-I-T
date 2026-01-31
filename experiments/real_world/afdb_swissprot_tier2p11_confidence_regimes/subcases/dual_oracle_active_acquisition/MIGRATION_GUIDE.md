# Migration guide — moving from versioned subcases to the canonical subcase

This pack converges the repository layout to a **single canonical subcase**:

- `subcases/dual_oracle_active_acquisition/`

If your repo currently contains a versioned folder (e.g., `dual_oracle_active_acquisition_v2_8/`), use one of the following migration paths.

---

## Option A (recommended): replace the versioned folder with the canonical folder

1. Remove (or move to a git tag / release branch):

   - `subcases/dual_oracle_active_acquisition_v2_8/` (or the latest versioned folder you used)

2. Add the canonical folder from this pack:

   - `subcases/dual_oracle_active_acquisition/`

3. Run the smoke CI script:

```bash
cd experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes/subcases/dual_oracle_active_acquisition
bash scripts/ci_check.sh
```

4. Commit.

---

## Option B: keep the old folder but point tooling/docs to canonical

If you prefer not to delete the versioned folder:

- Keep the old folder in place, but treat it as **archived**.
- Update any references in docs or automation to point to:

  `subcases/dual_oracle_active_acquisition/`

---

## What to update if you had hard-coded paths

Common places where the versioned name might be hard-coded:

- CI scripts that `cd` into `dual_oracle_active_acquisition_v2_8`
- READMEs or notebooks referencing a versioned path
- any automation that expects `aggregate_v2_8.py` directly

Canonical entrypoints:

- `bash scripts/ci_check.sh`
- `python scripts/aggregate.py ...`  (wrapper around the latest stable aggregator)

---

## What NOT to change

Canonicalization does **not** change:

- boundary definitions
- estimator semantics
- event definitions (E_*)
- robustness and claims gate logic (functional core preserved from v2.8)

It only changes **repo ergonomics and naming**, plus messaging strings to avoid stale versions.
