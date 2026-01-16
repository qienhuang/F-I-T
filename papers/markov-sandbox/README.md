# FIT Markov Sandbox (Minimal Release v2)

This is a **minimal, publication-ready bundle** for the Markov-chain "provable specialization" of FIT.

## One-line claim (paper-grade wording)

Here is a provable specialization: along the lazy hardening path $P_{\alpha}=(1-\alpha)P+\alpha I$, the entropy rate $h(\alpha)$ tends to $0$ and the predictive mutual information $C(\alpha)=I(X_t;X_{t+1})$ tends to $H(\pi)$; under a simple **self-dominance** condition, $h(\alpha)$ is non-increasing and $C(\alpha)$ is non-decreasing in $\alpha$.

## Key figure (single glance)

![FIT Markov validation](fit_markov_validation.png)

## Minimal release artifacts

- Paper (short): `fit_markov_sandbox_short.md`
- Definitions + scope: `definitions.md`
- Repro code (core): `experiments.py`
- Key figure: `fit_markov_validation.png`

## Quick reproduce (1 command)

From this folder:

```bash
python plot_validation.py
```

Outputs:
- `fit_markov_validation.png`
- `fit_markov_validation_small.png`

## Notes (scope discipline)

- Do **not** claim unconditional monotonicity for all chains; monotonicity is stated only under explicit sufficient conditions.
- Treat "nirvana" as a **limit-regime descriptor** in this sandbox, not a universal terminal claim.
