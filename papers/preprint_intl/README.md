# International preprint package (EN)

This folder is a platform-neutral, English-first submission package intended for international preprint venues (e.g., OSF Projects/Preprints, SSRN, personal sites, institutional repositories).

It is **not** tied to ChinaXiv. The ChinaXiv-specific, Chinese-first package remains at `papers/chinaxiv/`.

## Contents

- `metadata.en.yaml` - copy/paste metadata (title, abstract, keywords, links, statements)
- `cover_letter.en.md` - short cover letter template
- `checklist.en.md` - pre-submission checklist (incl. math rendering pitfalls)
- `tier2_predictions_register.en.md` - Tier-2 prediction register (A/B/C novelty filter + falsifiable templates)

## Recommended usage

1. Keep the canonical spec and evidence in the repo:
   - FIT v2.4 spec: https://github.com/qienhuang/F-I-T/blob/main/docs/v2.4.md
   - Zenodo archive: https://doi.org/10.5281/zenodo.18082325
2. Use `tier2_predictions_register.en.md` as the “scientific spine”:
   - Every Tier-2 case study must pass the A/B/C novelty filter.
   - Pre-register estimator choices and thresholds before looking at results.

