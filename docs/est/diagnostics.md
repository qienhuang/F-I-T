# EST Diagnostics: Decision Procedure for Measurement Outcomes

**Status**: v0.2 (aligned with FIT v2.4 EST)  
**Purpose**: A conservative, auditable decision procedure for labeling outcomes of FIT/EST evaluations.  
**Epistemic stance (Route A)**: FIT does not claim observer-independent truth. FIT claims *invariants across admissible estimator families* under explicitly declared scope/boundary conditions.

**Note (Windows PowerShell 5.1)**: If you see garbled punctuation when printing this file (e.g., `ƒ?`), it is usually a UTF-8 decoding/display issue. View with `Get-Content -Encoding UTF8 docs/est/diagnostics.md` or use PowerShell 7 (`pwsh`).

---

## 0. Labels (what you may claim)

| Label | Meaning | When to use | Next action |
|---|---|---|---|
| `EXPLORATORY_ONLY` | Not preregistered evidence | Any post-hoc estimator choice, threshold choice, or scope boundary | Iterate, then preregister a new run |
| `ESTIMATOR_UNSTABLE` | Measurement failure | Coherence gate fails for the task type | Fix estimators / logging / windowing; do not interpret |
| `SCOPE_LIMITED` | Boundary sensitivity | Coherence passes, but conclusion flips across reasonable scope variants | Report scope conditions explicitly; narrow claims |
| `INCONCLUSIVE` | Insufficient signal/power | Coherence passes, scope fixed, but too few events / too wide uncertainty | Collect more data or change prereg design |
| `SUPPORTED` | Evidence consistent with proposition | Coherence passes; scope fixed; supported across prereg estimator family | Report as supported *within scope* |
| `CHALLENGED` | Negative evidence (not decisive) | Coherence passes; scope fixed; failure in primary estimator but not robustly across family | Report as challenged; refine scope or estimators |
| `FALSIFIED` | Strong disconfirmation | Coherence passes; scope fixed; consistent failure across prereg admissible family | Revise proposition or declare scope invalid |

**Hard rule**: You must not label `SUPPORTED/CHALLENGED/INCONCLUSIVE/FALSIFIED` unless the run is preregistered and locked.

---

## 1. Required inputs

Before applying this procedure, you must have:

- **Task type**: `ordinal` / `metric` / `topological`
- **Preregistration**: a locked `prereg.yaml` (or equivalent) with:
  - scope boundary definition (system boundary, time boundary, inclusion rules)
  - estimator family declaration (primary + alternatives)
  - coherence gate thresholds
  - success/failure criteria
- **Run artifacts**: raw logs + computed metrics + plots + `run_diagnostics.md`

---

## 2. Decision procedure (text, not a diagram)

### Step 0 — Preregistration check

If any of the following are true, label **`EXPLORATORY_ONLY`** and stop:

- thresholds were tuned after seeing results
- estimator definitions changed after seeing results
- scope/boundary was moved after seeing results (e.g., trimming “bad tail” post-hoc)
- only a subset of declared estimators was reported

### Step 1 — Coherence gate (task-typed)

If the coherence gate fails, label **`ESTIMATOR_UNSTABLE`** and stop.

**Ordinal tasks** (trend/monotonicity):

$$
\operatorname{median}_{i<j}\ \rho\_{\text{rank}}(\hat{C}_i,\hat{C}_j) \ge \rho_{\min}
$$

Recommended default: $\rho_{\min} \in [0.5,0.7]$ (must be preregistered).

**Metric tasks** (threshold / critical point):

- rank coherence passes (necessary), and
- threshold event alignment: $|t^*_i - t^*_j| \le \Delta t_{\max}$ (preregistered), and
- calibrated residual error $\le \epsilon$ (preregistered)

**Topological tasks** (regimes / phase transitions):

- regime count/order consistent within tolerance, and
- change-points within tolerance (preregistered), and optionally:
- TDA / barcode similarity if used (preregistered)

### Step 2 — Scope sensitivity check

Run the same analysis under preregistered *scope variants* (if any), or a declared “scope family”:

- boundary variants (e.g., created-date boundary vs closed-date boundary)
- window variants (e.g., $W=7$ vs $W=14$ if preregistered)
- representation variants (if within declared equivalence class)

If the final conclusion changes across reasonable variants, label **`SCOPE_LIMITED`**.

### Step 3 — Signal sufficiency check

If the proposition requires events (e.g., threshold crossings) but the run yields too few events for meaningful inference, label **`INCONCLUSIVE`**.

Typical prereg examples:

- `n_event < n_min` (e.g., fewer than 10 sustained events)
- confidence intervals too wide / non-identifiable parameters
- effect size below prereg minimum

### Step 4 — Outcome and robustness over estimator family

Compute the result under the entire preregistered admissible estimator family $\mathfrak{E}$.

Define a pass rate:

$$
\text{pass\_rate} := \frac{|\{\mathcal{E}\in\mathfrak{E}: P[\mathcal{E}] \text{ supported}\}|}{|\mathfrak{E}|}
$$

Recommended interpretation (must be preregistered if used as a rule):

- **High** pass rate (e.g., $\ge 0.8$) → `SUPPORTED`
- **Low** pass rate (e.g., $\le 0.2$) → `FALSIFIED`
- **Intermediate** → `CHALLENGED`

---

## 3. Reporting schema (YAML)

Use this minimal schema to ensure auditability:

```yaml
diagnostics:
  label: ESTIMATOR_UNSTABLE | SCOPE_LIMITED | INCONCLUSIVE | SUPPORTED | CHALLENGED | FALSIFIED | EXPLORATORY_ONLY

  prereg:
    locked: true
    prereg_path: "path/to/prereg.yaml"
    scope_boundary: "created_date in 2024; agency=HPD; ..."
    task_type: ordinal | metric | topological

  coherence_gate:
    passed: true
    metric: "spearman_rho"
    value: 0.234
    threshold: 0.2
    notes: ""

  scope_sensitivity:
    variants_tested:
      - "created_date boundary"
      - "closed_date boundary"
    conclusion_varies: false
    notes: ""

  robustness:
    estimator_family_size: 3
    pass_rate: 0.67
    failures_cluster: "boundary=periodic"

  known_limitations:
    - "n_event=0 within in-scope boundary (cannot test H1)"
    - "single-seed run (coherence incomplete)"
```

---

## 4. Practical notes

- **Negative results are assets**: `ESTIMATOR_UNSTABLE`, `SCOPE_LIMITED`, and `INCONCLUSIVE` should be published as first-class outcomes.
- **Do not overclaim**: the strongest safe claim is always “within declared scope and admissible estimator family.”
- **Prefer “fix the measurement” over “fix the story”**: if coherence fails, the correct action is estimator repair, not narrative repair.
