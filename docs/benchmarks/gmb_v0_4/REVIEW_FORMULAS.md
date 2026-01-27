# GMB v0.4 Formula Review

**Reviewer**: Claude (Opus 4.5)
**Date**: 2026-01-27
**Scope**: All markdown files in `docs/benchmarks/gmb_v0_4/`
**Status**: ✅ **ALL ISSUES FIXED** (2026-01-27)

---

## Summary

| File | Issues | Severity | Status |
|------|--------|----------|--------|
| `gmb_v0.4_spec.md` | 2 formulas with escaped underscores | Minor | ✅ Fixed |
| `monitorability_boundary_toy_theorem.md` | Uses `\[...\]` syntax (may not render on GitHub) | Minor | ✅ Fixed |
| `gmb_v0.4_addendum_hrm_indicator_family.md` | **Double backslashes throughout** | **Critical** | ✅ Fixed |

---

## 1. gmb_v0.4_spec.md

### Issue: Escaped underscores in math mode (Lines 120-128)

**Current** (may not render correctly):
```latex
$$
|f\_{\mathrm{hat}} - f| \le \epsilon
$$

$$
\min_{f \in F} f\_{\mathrm{hat}} \le f\_{\mathrm{floor\_max}}
$$
```

**Fixed**:
```latex
$$
|\hat{f} - f| \le \epsilon
$$

$$
\min_{f \in F} \hat{f} \le f_{\text{floor\_max}}
$$
```

**Notes**:
- Inside `$$...$$`, underscores don't need escaping
- `\hat{f}` is more standard than `f_{\mathrm{hat}}`
- Use `\text{}` for multi-word subscripts with underscores

---

## 2. monitorability_boundary_toy_theorem.md

### Issue: Uses `\[...\]` and `\(...\)` syntax

GitHub-flavored Markdown prefers:
- `$$...$$` for display math
- `$...$` for inline math

**Current** (Lines 27-35):
```latex
\[
a(t) = \mathbf{1}[s(t) \ge \tau]
\]

\[
\mathrm{FPR}(\tau) := \Pr(a(t)=1 \mid y(t)=0).
\]
```

**Fixed**:
```latex
$$
a(t) = \mathbf{1}[s(t) \ge \tau]
$$

$$
\mathrm{FPR}(\tau) := \Pr(a(t)=1 \mid y(t)=0).
$$
```

**Inline math** (e.g., Line 22):
- Current: `\(y(t) \in \{0,1\}\)`
- Fixed: `$y(t) \in \{0,1\}$`

---

## 3. gmb_v0.4_addendum_hrm_indicator_family.md (CRITICAL)

### Issue: Double backslashes `\\` instead of single `\`

This is a **critical rendering bug**. In LaTeX, `\\` is a line break, not an escape sequence.

**Current** (Line 77):
```latex
$$
\\tau_L(k;\\epsilon) := \\min\\{ j : r_L(k,j) \\le \\epsilon \\}
$$
```

This renders as garbage or broken math.

**Fixed**:
```latex
$$
\tau_L(k;\epsilon) := \min\{ j : r_L(k,j) \le \epsilon \}
$$
```

### Full list of affected lines:

| Line | Current | Fixed |
|------|---------|-------|
| 77 | `\\tau_L`, `\\epsilon`, `\\min`, `\\le` | `\tau_L`, `\epsilon`, `\min`, `\le` |
| 87-88 | `\\tau_L` | `\tau_L` |
| 97 | `\\Delta r(k)` | `\Delta r(k)` |
| 102-103 | `\\Delta r(k)`, `\\ge`, `\\theta` | `\Delta r(k)`, `\ge`, `\theta` |
| 113-117 | `g(\\cdot)`, all operators | `g(\cdot)`, etc. |
| 125 | `\\lambda_i` | `\lambda_i` |
| 128 | `\\sum_i` | `\sum_i` |
| 139 | `\\rho_{PR}`, `\\frac` | `\rho_{PR}`, `\frac` |
| 162-164 | `\\mathcal{F}`, `\\epsilon`, `f_{\\mathrm{...}}` | `\mathcal{F}`, `\epsilon`, `f_{\mathrm{...}}` |

---

## Recommended Fix Script (Python)

```python
import re
from pathlib import Path

def fix_double_backslash(content: str) -> str:
    """Fix double backslashes inside $$ blocks."""
    # Pattern: find $$ blocks and replace \\ with \ (except \\\\)
    def fix_block(match):
        block = match.group(0)
        # Replace \\ followed by a letter (LaTeX command) with single \
        fixed = re.sub(r'\\\\([a-zA-Z])', r'\\\1', block)
        return fixed

    return re.sub(r'\$\$.*?\$\$', fix_block, content, flags=re.DOTALL)

# Apply to addendum file
path = Path('docs/benchmarks/gmb_v0_4/gmb_v0.4_addendum_hrm_indicator_family.md')
content = path.read_text(encoding='utf-8')
fixed = fix_double_backslash(content)
path.write_text(fixed, encoding='utf-8')
```

---

## Other files (no issues)

- `README.md` — No formulas, clean
- `V0_5_RUNBOOK.md` — No formulas, clean
- `results/README.md` — No formulas, clean
- `gmb_prereg_v0.4.yaml` — No formulas, clean
- `gmb_results_v0.4.yaml` — No formulas, clean

---

## Content review (non-formula)

All files are **well-structured** and **repo-ready**:

- Clear four-layer evaluation architecture (A/B/C/D)
- Explicit failure semantics (`RANK_ONLY`, `ESTIMATOR_UNSTABLE`, etc.)
- V0_5_RUNBOOK provides step-by-step reproducibility
- Real example run (`run_grokking_v0_3_A2_tradeoff`) demonstrates the benchmark

---

## Fixes Applied (2026-01-27)

All issues have been corrected:

1. **gmb_v0.4_spec.md**: Changed `f\_{\mathrm{hat}}` → `\hat{f}` and `f\_{\mathrm{floor\_max}}` → `f_{\text{floor\_max}}`

2. **monitorability_boundary_toy_theorem.md**: Converted all `\(...\)` → `$...$` and `\[...\]` → `$$...$$`

3. **gmb_v0.4_addendum_hrm_indicator_family.md**: Fixed all double backslashes (`\\tau` → `\tau`, etc.) and converted inline code with backslashes to proper `$...$` math

---

*Review ends.*
