# Next Validation Plan (post Route B)

Status: Route B for GoL is complete at v2.x closure level (`SUPPORTED_WITH_SCOPE_LIMITS`).

## Priority 2: Cross-system replication

### 2.1 Langton's Ant (recommended first)

Reason:
- Lower engineering overhead than Ising.
- Strong boundary story and existing FIT context.

Minimum deliverables:
- Same gate stack as GoL:
  - Q1 map existence
  - saturation gate
  - semigroup hard gate
- Matrix at least `2 schemes x 2 estimators`.
- Route-level verdict (`SUPPORTED` / `SUPPORTED_WITH_SCOPE_LIMITS` / `NONCLOSURE_OR_CHALLENGED` / `INCONCLUSIVE`).

### 2.2 Ising (second)

Reason:
- Stronger RG-traditional framing.
- Higher implementation and compute cost.

Minimum deliverables:
- Same hard-gate protocol for comparability.
- Explicit separation of finite-size effects vs saturation effects.

## Priority 3: Deferred (do not mix into this cycle)

- Fixed-point exponent claims
- Critical exponents
- v3 primitive changes

These are paper-2 / v3 topics and should stay out of current v2.x closure package.

