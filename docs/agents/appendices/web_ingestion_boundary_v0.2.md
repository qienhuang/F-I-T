# Web Ingestion Boundary v0.2
*Prevent “world noise” from silently becoming memory, skills, or training data.*

**Status**: appendix (repo-ready)  
**Date**: 2026-01-27  

---

## 0. Principle

> Network access is not authority. Retrieval is not ingestion.

We separate four pipelines:

1. **Read-only retrieval** (allowed by default)
2. **Semantic memory write** (gated, hashed, cited)
3. **Skill creation** (requires tests + admission gate)
4. **Training ingestion** (offline only, trace-derived only)

---

## 1. Read-only retrieval (default)

Allowed:
- search/open/read
- cache raw pages in `sandbox/web_cache/` with hash + timestamp

Forbidden:
- silent summarization into “facts” without citations
- copying into skill code without provenance markers

---

## 2. Semantic memory write (gated)

To write a web chunk into semantic memory, require:

- source URL metadata
- content hash
- extraction method recorded
- confidence tag (low/med/high)
- optional cross-source verification (recommended)

If missing any, store only in cache, not in memory.

---

## 3. Skill creation from web content

If web content informs a skill:
- store the referenced snippet hash + source in skill provenance
- require unit tests demonstrating behavior without needing network
- if network is required, skill must be at L2 or above (Skill Admission Gate)

---

## 4. Training ingestion (offline, trace-derived)

Hard rule:
- web content cannot directly enter training data.
- training data must be trace-derived (agent runs + outcomes + human labels if any).
- any external corpora use must be separately versioned and approved.

---

## 5. Incident response

If poisoning or misinformation is suspected:
- freeze semantic memory writes
- demote network skills to L0
- require re-verification for affected memory chunks
