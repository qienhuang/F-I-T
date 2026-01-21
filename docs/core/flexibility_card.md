# Flexibility Card (v2.4.1+)

**Artifact type**: Core Artifact (handoff-ready)

**Purpose**: Provide an operational definition and monitoring schema for “Flexibility,” so that once a system stabilizes in a late coordinated phase (e.g., $ \Phi_3 $ ), it still retains *controlled* adaptivity—and we can reliably distinguish:

- Legitimate phase transitions / reorganizations (reconfiguration)
- Harmful lock-in (over-constraint without reconfiguration channels)
- Harmful drift (constraint erosion / loss of coordination)
- Pure measurement failures (estimator instability)

**FIT/EST prerequisite**: Every judgment is bound to an explicit estimator tuple $ \mathcal{E} $ , and under EST we only accept *auditable admissible estimator families*.

**Scope note**: This card introduces no new primitives or propositions; it is an operational classification + monitoring schema under FIT v2.4/v2.4.1.


$$
\mathcal{E} = (S_t, \mathcal{B}, \{\hat{F}, \hat{C}, \hat{I}\}, W)
$$

---

## Three classes of flexibility

Reading guide: for each class we specify **(i) the corresponding FIT propositions (v2.4 / v2.4.1)**, **(ii) minimal metrics**, and **(iii) failure modes**: lock-in / drift / estimator instability.

---

## 1) Structural Flexibility (Constraint / Phase Flexibility, C-Flex)

**Definition**: The capability to (a) keep $ \hat{C}(t) $ statistically non-decreasing *within a phase*, while (b) permitting short-term constraint-proxy reorganization (including local regressions) near transitions, and (c) enabling *controlled constraint reconfiguration* when new information/structure must be formed.

### Corresponding propositions

- **P2a — Phase-conditional monotonicity**: within an explicitly declared phase, $ \hat{C}(t) $ is statistically non-decreasing.
- **P2b — Late-phase irreversibility**: once a system enters a coordinated structural phase ( $ \Phi_3 $ -like), large-scale regressions become rapidly unlikely (probabilistic irreversibility, not “no change”).
- **P12 — Information growth requires constraint reconfiguration**: sustained growth of $ I_{\mathrm{useful}} $ under fixed boundary requires growth or reconfiguration of $ C $ .

### Minimal metric set

- **Within-phase monotonicity violation rate** (computed per phase segment):


$$
 v_C := \frac{|\{ t \in \Phi_k : \hat{C}(t+1) < \hat{C}(t) \}|}{|\Phi_k|}
$$

- **Transition / reorganization signal strength** (for identifying reconfiguration windows):


$$
J(t) := \left| \frac{\mathrm{d}}{\mathrm{d}t}\left( \frac{\hat{I}(t)}{\hat{C}(t)} \right) \right|
$$

  Practical implementations may use change-point scores or finite-difference estimates over a pre-registered smoothing/filter window $W_s$; the method must be pre-registered.

- **Reconfiguration reachability**: under a pre-registered “release / reconfiguration protocol” $ \Pi_{\mathrm{reconf}} $ , whether the system can reach a new stable phase within a bounded horizon (e.g., $ \Phi_3 \rightarrow \Phi_2 $ or $ \Phi_3 \rightarrow \Phi_3' $ ).

### Failure modes

- **Lock-in**:
  - Signature: $ \hat{C}(t) $ saturates for long horizons, $ J(t) \approx 0 $ , while external task/environment indicators require structural change; executing $ \Pi_{\mathrm{reconf}} $ fails to reach a new phase.
  - Consequence: the system is “stable but unusable,” and can only change via external boundary/constraint relaxation.

- **Drift**:
  - Signature: persistent $ \hat{C}(t) $ downtrend *within the same phase* ( $ v_C $ far above threshold), or long-run degradation in $ I/C $ without a phase-transition-type reorganization.
  - Consequence: constraint erosion, reduced coordination, increasing fragility.

- **Estimator instability**:
  - Signature: phase segmentation / change points are highly inconsistent across admissible $ \hat{C} $ or $ \hat{I} $ variants, or small changes in window $ W $ flip conclusions.
  - Handling: label as `ESTIMATOR_UNSTABLE` and do **not** interpret this as supporting/challenging P2/P12.

---

## 2) Dynamical Flexibility (Force / Policy Flexibility, F-Flex)

**Definition**: The capability to generate sufficient drive to migrate under perturbations or objective changes, while maintaining low $ \sigma^2(F) $ during stable operation (to avoid sustained high-force noise that produces drift). In short: “stable when it should be stable, movable when it must move.”

### Corresponding propositions

- **P5 — Recovery time vs. constraint**: within a system, higher-constraint attractors should recover faster from small perturbations.
- **P18 — Timescale separation near attractors**: near attractors, $ \tau_F \ll \tau_C $ (fast variables stabilize first; slow variables evolve more slowly).
- **P1 — Nirvana irreversibility (boundary condition)**: without constraint relaxation, once in a strong low-variance attractor, spontaneous escape probability tends to zero.

### Minimal metric set

- **Force variance and its post-perturbation decay**:
  - Baseline $ \sigma^2(F_t) $ , post-perturbation peak, and decay rate.
  - Fit family (exponential vs. power law) must be pre-registered.

- **Recovery time** (under a pre-registered perturbation protocol $ \Pi_{\mathrm{perturb}} $ ):


$$
\tau_{\mathrm{recover}} := \min\{\Delta t : \text{metrics return to a pre-registered tolerance band} \}
$$

- **Timescale ratio**:


$$
r_{\mathrm{ts}} := \frac{\tau_F}{\tau_C}
$$

  Estimation method (windowing, autocorrelation time, change-point) must be consistent and pre-registered.

### Failure modes

- **Lock-in**:
  - Signature: $ \sigma^2(F) \approx 0 $ while $ \tau_{\mathrm{recover}} $ is effectively unbounded for *migration-type perturbations* (the system always snaps back to the old attractor and cannot transition).
  - Consequence: the system cannot retarget when objectives shift; explicit constraint relaxation or boundary changes are required to unlock.

- **Drift**:
  - Signature: $ \sigma^2(F) $ remains persistently high with no stable plateau (no P4-like stable regime), or timescale separation collapses ( $ r_{\mathrm{ts}} \not\ll 1 $ ).
  - Consequence: persistent wandering, unstable performance, accumulating risk.

- **Estimator instability**:
  - Signature: $ \hat{F} $ is extremely sensitive to equivalent representations or small $ W $ changes, making $ \tau_{\mathrm{recover}} $ and $ r_{\mathrm{ts}} $ non-reproducible.
  - Handling: run the EST admissibility + coherence gates; if they fail, label `ESTIMATOR_UNSTABLE`.

---

## 3) Epistemic Flexibility (Estimator / Interpretation Flexibility, E-Flex)

**Definition**: The ability to switch or expand estimator families across phases and task types *without* falling into post-hoc “changing rulers to save the theory.” E-Flex is what makes the measurement layer auditable, reproducible, and handoff-ready.

### Corresponding rules / meta-propositions

- **EST admissibility (A1–A8)**: scope declaration, robustness, task type, complexity cost, and pre-registration are mandatory.
- **P10 task-typed coherence gates**: use the correct coherence gate by task type (ordinal / metric / topological).
- **v2.4.1 constraint**: any P2 / P17 claim must declare phase context and estimator scope; reorganization near transitions is not a default counterexample.

### Minimal metric set

- **Coherence-gate pass rate** (task-typed):
  - Ordinal: median Spearman/Kendall correlation $ \ge $ pre-registered threshold.
  - Metric: threshold-event alignment ( $ |t_1^* - t_2^*| \le \Delta t_{\max} $ ) plus slope/residual stability.
  - Topological: same regime count/order plus change-point tolerance.

- **Robustness over admissible estimator family**:


$$
\text{pass\_rate} := \frac{|\{ \mathcal{E} \in \mathfrak{E}_{\mathrm{adm}} : P_i[\mathcal{E}] \ \text{is supported} \}|}{|\mathfrak{E}_{\mathrm{adm}}|}
$$

- **Window sensitivity**: empirical bounds / slopes of


$$
\|\hat{X}(t; W + \delta W) - \hat{X}(t; W)\|, \quad X \in \{C, I, F\}
$$

### Failure modes

- **Lock-in**:
  - Signature: the measurement pipeline is locked to a single representation/estimator, so transitions are misread as “theory failure” or “system collapse,” and correct phase-aware classification becomes impossible.

- **Drift**:
  - Signature: estimator/threshold changes are made without pre-registration, or results are cherry-picked from an estimator family to match expectations.
  - Consequence: non-reproducibility and non-handoffability; effectively, institutional drift in the measurement layer.

- **Estimator instability**:
  - Signature: coherence gates fail; the same data yields conflicting phase partitions or conclusions across admissible estimators.
  - Handling: label `ESTIMATOR_UNSTABLE`; prioritize measurement repair over theory revision.

---

## Usage conventions (handoff notes)

1. **Phase first, monotonicity second**: any claim that “ $ C(t) $ is monotone” must be evaluated *within phase* (P2a). Reorganization is allowed in transition windows.
2. **Lock-in is not the same as irreversibility**: P2b/P1 are about probabilistic irreversibility; “flexibility” comes from designed/allowed constraint relaxation and explicit reconfiguration protocols, not from hoping the system escapes spontaneously.
3. **Disagreements must pass P10/EST first**: if coherence gates fail, stop interpreting results as “supported/challenged.” Classify as measurement instability and fix the estimator layer.
