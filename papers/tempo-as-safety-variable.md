# Tempo as a First-Class Safety Variable
## Identifying Irreversible Operations in AI Systems via the FIT Framework

**Version:** GitHub long-form draft (Markdown-first; LaTeX later)  
**Other versions:** [LessWrong](tempo-as-safety-variable.lesswrong.md) | [NeurIPS workshop submission](tempo-as-safety-variable.neurips-workshop.submission.md) | [中文](tempo-as-safety-variable.zh_cn.md)  
**FIT specs:** [docs/v2.4.md](../docs/v2.4.md) (EST), [docs/v2.3.md](../docs/v2.3.md) (baseline)

---

## Abstract

Rapid advances in AI systems have shifted safety risks from isolated failures toward systemic, irreversible transitions driven by accelerated deployment and governance mismatch. Existing AI safety approaches primarily focus on performance bounds, alignment objectives, or post hoc control mechanisms, often treating time as an implicit or secondary parameter.

In this work, we introduce the Force-Information-Time (FIT) framework, which elevates temporal dynamics - specifically update tempo and irreversibility - as first-class safety variables. FIT models AI systems as evolving under interacting forces, informational constraints, and time-dependent update regimes, allowing explicit identification of **Irreversible Operations (IOs)**: system-level actions that permanently constrain future state spaces and eliminate rollback options.

We formalize criteria for detecting tempo mismatch between system evolution and governance feedback, propose a minimal set of observable indicators for irreversibility risk, and introduce **Minimum Viable Tempo Governance (MVTG)** - a lightweight, auditable governance layer that enforces slow authority, rollback windows, tempo stratification, and circuit breakers for high-impact AI operations.

We argue that managing tempo, rather than solely optimizing objectives, is necessary to prevent false stability states in which AI systems appear performant yet become structurally uncontrollable. The FIT framework provides a unifying lens for AI safety, governance, and deployment practices, emphasizing prevention of irreversible harm over reactive mitigation.

**Keywords:** AI safety, governance, irreversibility, temporal dynamics, deployment risk, systemic control

---

## 1. Introduction

AI systems increasingly operate as socio-technical stacks: model training, data pipelines, deployment infrastructure, product surfaces, and organizational policies co-evolve under pressure to ship updates faster. Safety mechanisms (evaluations, red-teaming, incident review, external oversight) often run on slower cycles. This creates a structural failure mode: systems can change in ways that make future correction infeasible, even if individual changes appear benign.

This paper proposes that **tempo** (the rate and sequencing of updates) should be treated as a first-class safety variable. When system evolution outpaces governance feedback, safety interventions become retrospective: issues recur faster than they can be resolved; rollback paths silently degrade; and decision authority shifts to components or actors that cannot be effectively audited or constrained.

We use the FIT framework to formalize this failure mode and to define a practical interface for governance. The core claim is not that alignment, robustness, or interpretability are unimportant, but that their effectiveness depends on preserving the ability to intervene over time.

**Contributions**
- We define **Irreversible Operations (IOs)** as a distinct failure mode from alignment and robustness: actions that permanently constrain future corrective options.
- We give an operational IO taxonomy and a set of auditable indicators for detecting irreversibility risk.
- We propose **Minimum Viable Tempo Governance (MVTG)**: five minimal controls that apply selectively to IOs (slow authority, rollback windows, tempo stratification, circuit breakers, adversarial audit).
- We provide abstracted case patterns showing how IOs arise without naming any organization or system.

---

## 2. Problem Framing: Irreversibility as a Safety Failure Mode

### 2.1 Reversible vs. Irreversible Failures

Many failures in AI systems are reversible: a bad release is rolled back, a dataset issue is fixed, a policy is updated, and the system returns to an acceptable operating regime. In contrast, **irreversible failures** are those where recovery is not feasible within acceptable bounds (time, cost, legal exposure, trust, governance capacity).

This paper treats irreversibility as a property of operations that change the reachable future of the system. IOs can be technical (e.g., eliminating rollback), organizational (e.g., removing review gates), or institutional (e.g., commitments that block withdrawal). We formalize IOs in Section 4.1 and operationalize them via measurable indicators in Section 4.3.

### 2.2 Why Post-Hoc Controls Fail Under Acceleration

Post-hoc controls assume that corrective feedback arrives in time. Under acceleration, three effects break this assumption:

1. **Latency domination:** evaluation and review take longer than the time between consequential updates, so governance cannot keep up.
2. **Compounding change:** each update changes the context in which the previous fix was validated, so reliability becomes path-dependent.
3. **Silent capacity erosion:** rollback paths, auditability, and alternative routes can degrade gradually until recovery becomes infeasible.

The result is **false stability**: the system appears performant and stable while the option space for intervention collapses. This motivates a governance interface that focuses on **threshold prevention** (don’t cross irreversibility thresholds) rather than outcome-only monitoring.

### 2.3 Abstracted Case Patterns of Irreversibility

This section presents **abstracted case patterns** that illustrate how IOs arise in AI systems under accelerated deployment and governance mismatch. The cases are intentionally de-identified and generalized to highlight **structural dynamics rather than contingent details**.

#### Case Pattern A: Acceleration Without Governance Synchronization

**Initial Condition:**  
An AI system is deployed with periodic evaluation and human review gates. Update cycles are aligned with governance feedback.

**Intervention:**  
To increase responsiveness, deployment frequency is gradually increased. Evaluation and review processes remain unchanged.

**Observed Dynamics:**  
- Update velocity exceeds evaluation completion time.
- Incidents recur before prior corrections are validated.
- Governance feedback becomes retrospective rather than preventative.

**Irreversible Operation:**  
A **tempo-escalating IO** occurs when the system’s maximum update rate is permanently raised without proportional governance synchronization.

**Outcome:**  
The system enters a state of **structural acceleration** where rollback is theoretically possible but practically infeasible due to compounding changes.

**Key Insight:**  
Irreversibility emerges not from any single update, but from **crossing a tempo threshold** beyond which governance cannot reassert control.

---

#### Case Pattern B: Rollback Erosion Through Operational Convenience

**Initial Condition:**  
The system maintains versioned deployments and tested rollback procedures.

**Intervention:**  
Rollback steps are simplified or deferred to reduce operational overhead. Backup frequency is reduced.

**Observed Dynamics:**  
- Rollback rehearsals become infrequent.
- Recovery time objectives increase unnoticed.
- Dependencies accumulate across releases.

**Irreversible Operation:**  
A **rollback-removing IO** occurs when restoration paths exist nominally but fail under real stress.

**Outcome:**  
Failures that were previously recoverable now propagate into permanent system state changes.

**Key Insight:**  
Irreversibility can arise **gradually and unintentionally** through convenience-driven erosion rather than explicit decisions.

---

#### Case Pattern C: Control Transfer to Opaque Decision Components

**Initial Condition:**  
Critical decisions are mediated by interpretable processes with human override.

**Intervention:**  
Opaque or non-auditable components are introduced to improve efficiency or performance, while oversight structures remain unchanged.

**Observed Dynamics:**  
- Decision rationales cannot be reconstructed post hoc.
- Overrides exist formally but cannot be executed in real time.
- Accountability diffuses across components.

**Irreversible Operation:**  
A **control-transferring IO** occurs when effective control shifts to mechanisms outside meaningful audit or intervention.

**Outcome:**  
The system retains nominal human authority but loses **operational controllability**.

**Key Insight:**  
Loss of control can precede visible failure, creating a **false sense of stability**.

---

#### Case Pattern D: Option Space Collapse via Standardization

**Initial Condition:**  
Multiple technical and governance pathways coexist, enabling comparison and fallback.

**Intervention:**  
To streamline operations, alternatives are retired and a single pathway is standardized.

**Observed Dynamics:**  
- Dependency on unique components increases.
- Switching costs rise sharply.
- Dissent or parallel evaluation channels disappear.

**Irreversible Operation:**  
A **diversity-collapsing IO** occurs when alternative trajectories are eliminated.

**Outcome:**  
System resilience declines as future adaptation options are constrained.

**Key Insight:**  
Efficiency-driven consolidation can unintentionally lock systems into brittle equilibria.

---

#### Case Pattern E: Governance Lag in Socio-Technical Integration

**Initial Condition:**  
An AI system operates within a bounded technical domain.

**Intervention:**  
The system is integrated into broader organizational or social workflows without corresponding governance adaptation.

**Observed Dynamics:**  
- Decision impact expands faster than oversight scope.
- Feedback signals become indirect or delayed.
- Responsibility boundaries blur.

**Irreversible Operation:**  
A **trajectory lock-in IO** occurs when integration precedes governance redesign.

**Outcome:**  
Reversing integration becomes socially or institutionally infeasible even if technical rollback remains possible.

**Key Insight:**  
Irreversibility may arise from **institutional coupling**, not technical failure.

---

#### Cross-Case Synthesis

Across these patterns, irreversibility consistently arises from **tempo mismatch** between system evolution and governance feedback rather than from isolated errors. IOs often emerge incrementally, making early detection essential.

These patterns motivate the governance mechanisms introduced in Section 5, which target **threshold prevention** rather than outcome optimization.

---

### 2.4 Threat Model (Sketch)

This paper focuses on **unintentional irreversibility** arising from:
- Tempo mismatch between system evolution and governance feedback
- Convenience-driven erosion of rollback capacity
- Incremental control transfer without explicit decision

We do not address **adversarial IO injection** (e.g., deliberate sabotage of rollback mechanisms), though MVTG’s adversarial audit component provides partial mitigation.

---

## 3. The FIT Framework (Minimal for This Paper)

FIT (Force-Information-Time) is a minimal meta-language for describing how systems evolve across substrates. In this paper, we use FIT as a **diagnostic lens** for deployment safety: systems can fail not only by optimizing wrongly, but by **evolving faster than their governance can correct**.

### 3.1 Primitives (Mini-Glossary)

| Symbol | Name | Definition (for this paper) |
|---|---|---|
| $F$ | Force | Drivers of state change (gradients, pressures, incentives) |
| $I$ | Information | Persistent structures / signals that shape future evolution |
| $T$ | Time | Update tempo and the irreversibility horizon |
| $C$ | Constraint | Accumulated restrictions on reachable state space |
| $S$ | State | System configuration at a given time |

### 3.2 Core Insight for This Paper

FIT's contribution to AI safety here is not a new objective function, but a **meta-level diagnostic**: systems fail not only by optimizing wrongly, but by **evolving faster than their governance can correct**. IOs are the concrete interface where this becomes legible and governable.

![Toy validation overview on Conway's Game of Life: FIT propositions are empirically checkable, and estimator choices can change pass/fail outcomes.](../experiments/figures/conway_status_overview.png)

*Figure 1: Toy validation (Conway's Game of Life). This is not a benchmark result; it illustrates falsifiability and estimator sensitivity in IO-style indicators.*

---

## 4. Irreversible Operations (IOs)

### 4.1 Definition and Scope

We define **Irreversible Operations (IOs)** as system-level actions that **permanently constrain the future reachable state space** of an AI system, such that rollback, recovery, or alternative trajectories become infeasible within acceptable cost, time, or governance bounds.

Formally, an operation $o$ is considered **irreversible** if, after execution at time $t$, at least one of the following holds:

1. **State-space collapse**: the set of reachable future states $\mathcal{S}_{t+1}$ is a strict subset of the pre-operation reachable set $\mathcal{S}_{t}$, with no feasible path to restore excluded regions.
2. **Rollback elimination**: no practical rollback procedure exists that restores prior system behavior within bounded loss (e.g., data, trust, legal exposure).
3. **Trajectory lock-in**: alternative technical or governance pathways are eliminated or rendered prohibitively costly.
4. **Control asymmetry**: decision authority or update tempo is shifted to components or actors that cannot be effectively audited or constrained.

**Definition (Irreversible Operation).**  
An operation $o$ executed at time $t$ is irreversible if:

$$
\exists\, s^{*} \in \mathcal{S}_t \setminus \mathcal{S}_{t+1}
\quad \text{such that} \quad
\inf_{\pi} \mathrm{Cost}(\pi: S_{t+1} \to s^{*}) > \theta_{\text{feasible}}
$$

where $\mathcal{S}_t$ is the reachable state space before $o$, $\mathcal{S}_{t+1}$ is the reachable state space after $o$, $\pi$ ranges over recovery plans, and $\theta_{\text{feasible}}$ is a domain-specific feasibility bound (time, money, legal exposure, trust, governance capacity).

This definition intentionally abstracts away from model internals and focuses on **systemic consequences**, allowing IOs to be identified across technical, organizational, and policy domains.

---

### 4.2 Taxonomy of Irreversible Operations

We classify IOs into four non-exclusive categories, each corresponding to a distinct mode of irreversibility.

#### 4.2.1 Tempo-Escalating IOs

Operations that **permanently increase the maximum update or deployment rate** of the system.

**Examples (abstracted):**
- Removing mandatory evaluation or review gates.
- Automating deployment pipelines without human-in-the-loop checkpoints.
- Shifting from staged to continuous release for high-impact components.

**Risk Mechanism:**  
Governance feedback cannot keep pace with system evolution, leading to unchecked drift.

---

#### 4.2.2 Rollback-Removing IOs

Operations that **eliminate or severely degrade the ability to revert** system state.

**Examples:**
- Deployments without versioned snapshots or restoration procedures.
- Irreversible data transformations without backups.
- Legal or contractual commitments that prevent system withdrawal.

**Risk Mechanism:**  
Errors transition from recoverable incidents to permanent structural changes.

---

#### 4.2.3 Control-Transferring IOs

Operations that **transfer effective control** to components, organizations, or processes outside existing oversight structures.

**Examples:**
- Entrusting critical decisions to opaque or non-auditable models.
- Outsourcing governance-critical functions without enforcement guarantees.
- Embedding third-party systems that cannot be paused or constrained.

**Risk Mechanism:**  
Loss of meaningful human or institutional control despite nominal authority.

---

#### 4.2.4 Diversity-Collapsing IOs

Operations that **eliminate alternative technical or governance pathways**.

**Examples:**
- Standardizing on a single model architecture or supplier without contingency.
- Removing parallel evaluation or dissent channels.
- Policy decisions that lock in one regulatory interpretation.

**Risk Mechanism:**  
System resilience decreases as option space collapses.

---

### 4.3 Observable Indicators of Irreversibility Risk

To operationalize IO detection, we define **observable indicators** that signal rising irreversibility risk. These indicators are domain-agnostic and auditable.

#### 4.3.1 Tempo Mismatch Indicators

- **Decision-to-validation lag**: time between deployment and completion of meaningful evaluation.
- **Update velocity ratio**: rate of system updates relative to rate of governance or review cycles.
- **Incident recurrence under acceleration**: repeated failures occurring faster than corrective actions.

---

#### 4.3.2 Rollback Viability Indicators

- **Rollback success rate**: proportion of attempted rollbacks that fully restore prior state.
- **Recovery time objective (RTO)** trends.
- **Rollback rehearsal frequency**: absence indicates latent irreversibility.

---

#### 4.3.3 Control and Interpretability Indicators

- **Opaque-decision fraction**: share of critical decisions mediated by non-interpretable components.
- **Audit latency**: time required to reconstruct decision rationale post hoc.
- **Override feasibility**: ability to halt or modify behavior in real time.

---

#### 4.3.4 Diversity and Optionality Indicators

- **Single-point dependency index**: degree of reliance on unique components or actors.
- **Path-switch cost**: estimated cost and time to adopt an alternative approach.
- **Redundancy erosion rate**: rate at which parallel systems are retired.

---

#### 4.3.5 Threshold Guidance (Provisional)

| Indicator | Yellow zone | Red zone |
|---|---|---|
| Update velocity ratio | > 3x governance cycle | > 10x |
| Rollback success rate | < 90% | < 50% |
| Opaque-decision fraction | > 20% of critical decisions | > 50% |
| Single-point dependency | > 60% reliance | > 90% |

Note: thresholds are illustrative and should be calibrated per domain and risk tolerance.

---

### 4.4 IOs as a Failure Mode Distinct from Alignment Errors

A key contribution of FIT is distinguishing IOs from traditional AI safety failure modes.

- **Alignment failures** concern *what* a system optimizes.
- **Robustness failures** concern *how* a system performs under perturbation.
- **IO failures** concern *whether future correction remains possible*.

An aligned and robust system may still become unsafe if IOs are executed prematurely, locking the system into uncontrollable trajectories.

---

### 4.5 Design Implications

Recognizing IOs reframes AI safety from reactive mitigation to **preventive threshold management**:

- Not all actions require slow governance - **only those crossing irreversibility thresholds**.
- Safety interventions should prioritize **tempo control and rollback preservation** over exhaustive foresight.
- Governance success is measured by **maintained option space**, not by absence of incidents.

This perspective motivates the governance mechanisms introduced in Section 5.

---

## 5. Minimum Viable Tempo Governance (MVTG)

### 5.1 Rationale: Governing Thresholds, Not Outcomes

AI safety interventions often attempt to govern outcomes (e.g., alignment objectives, performance bounds). However, when **Irreversible Operations (IOs)** are present, outcome-focused controls arrive too late. **MVTG** reframes governance around **threshold management**: preventing actions that irreversibly constrain future options.

MVTG is intentionally **minimal**. It does not seek comprehensive oversight of all AI activities. Instead, it targets **only those actions that cross irreversibility thresholds**, thereby maximizing safety impact while minimizing operational burden.

---

### 5.2 Design Principles

MVTG is guided by three principles:

1. **Slow the Irreversible**  
   Actions identified as IOs must be subject to deliberate, low-tempo decision processes.

2. **Preserve Rollback**  
   All high-impact actions must maintain a verifiable path to restoration or withdrawal.

3. **Stratify Tempo**  
   Systems may evolve rapidly at the edge, but core constraints and governance layers must evolve slowly.

These principles align safety effort with risk concentration.

---

### 5.3 Core Components

#### 5.3.1 Slow Authority

**Slow Authority** is a governance constraint applied exclusively to IOs.

**Definition:**  
A requirement that IOs pass through a decision process with enforced delay, dual authorization, and auditable justification.

**Key properties:**
- Applies only to IO-classified actions.
- Enforces a **cool-down period** to allow counterfactual evaluation.
- Requires **explicit rationale** recorded for post hoc audit.

**Safety function:**  
Prevents impulsive acceleration that bypasses governance feedback loops.

---

#### 5.3.2 Rollback Windows

A **Rollback Window** is a bounded period during which an IO-triggering change can be fully reversed.

**Requirements:**
- Versioned system snapshots prior to execution.
- Tested rollback procedures with defined recovery objectives.
- Periodic rollback rehearsals to verify feasibility.

**Safety function:**  
Converts latent irreversibility into managed risk by preserving corrective capacity.

---

#### 5.3.3 Tempo Stratification

MVTG separates system evolution into **tempo layers**, each governed at different speeds.

**Canonical stratification:**
- **Exploration Layer (Fast):** experimentation, A/B testing, local optimization.
- **Validation Layer (Medium):** evaluation, auditing, cross-checking.
- **Constraint Layer (Slow):** policies, irreversible deployments, core governance.

**Connection to Estimator Selection Theory (EST):**  
Tempo stratification also maps naturally onto EST's task-typed equivalence notions:
- Fast layer -> ordinal equivalence (trend detection)
- Medium layer -> metric equivalence (threshold / scale stability)
- Slow layer -> topological equivalence (regime structure)

This alignment helps keep governance metrics **admissible** and auditable under EST criteria.

**Example:** your inference pipeline can update hourly, but changes to safety filters require weekly review.

**Safety function:**  
Prevents fast-moving components from directly modifying slow, foundational constraints.

---

#### 5.3.4 Circuit Breakers

**Circuit Breakers** are predefined mechanisms that halt or downgrade system operation when irreversibility risk exceeds tolerable thresholds.

**Triggers may include:**
- Rapid accumulation of IO indicators.
- Repeated rollback failures.
- Governance feedback lag exceeding preset bounds.

**Safety function:**  
Provides a last-resort control to prevent cascading irreversible transitions.

---

#### 5.3.5 Adversarial Audit

MVTG incorporates **adversarial audit** to continuously test governance integrity.

**Scope:**
- Challenging IO classification decisions.
- Probing bypass paths around slow authority.
- Stress-testing rollback and circuit breaker effectiveness.

**Safety function:**  
Maintains governance resilience against complacency and internal bias.

---

### 5.4 Mapping MVTG to IO Categories

Each MVTG component directly mitigates one or more IO classes:

| IO Category | Primary MVTG Controls |
|---|---|
| Tempo-Escalating IOs | Slow Authority, Tempo Stratification |
| Rollback-Removing IOs | Rollback Windows |
| Control-Transferring IOs | Adversarial Audit, Circuit Breakers |
| Diversity-Collapsing IOs | Tempo Stratification, Audit |

This mapping emphasizes **selective control**, not blanket restriction.

---

### 5.5 Operational Metrics

MVTG effectiveness is evaluated using **process metrics**, not outcome guarantees:

- IO approval latency (should be non-zero and stable).
- Rollback success rate and rehearsal frequency.
- Ratio of fast-layer updates to slow-layer changes.
- Frequency and resolution time of circuit breaker activations.
- Number of governance bypasses detected via audit.

These metrics are **observable, auditable, and organization-agnostic**.

---

### 5.6 Limitations of MVTG (Scope)

MVTG does not:
- Optimize model objectives.
- Predict specific failure events.
- Eliminate the need for alignment or robustness research.

Instead, it **preserves the ability to intervene** before irreversible harm occurs.

---

## 6. Discussion

### 6.1 Related Work and Positioning

The FIT framework is **complementary** to, rather than a replacement for, existing AI safety approaches. Its contribution lies in identifying a **distinct failure mode**: irreversibility under tempo mismatch.

- **Alignment and objective-based safety:** Alignment focuses on ensuring that systems optimize intended objectives. However, even well-aligned systems may become unsafe if IOs permanently constrain corrective options. FIT addresses *when* intervention remains possible, not *what* objectives should be optimized.
- **Robustness and reliability:** Robustness mitigates performance degradation under distributional shift or adversarial input. FIT targets **structural risk**, where failures persist because recovery pathways have been eliminated.
- **Interpretability and transparency:** Interpretability improves understanding, but may be insufficient if decision authority and tempo are transferred to components that cannot be paused or overridden in practice.
- **Governance and policy frameworks:** Governance proposals emphasize compliance, accountability, and risk classification. FIT contributes a **temporal dimension**, providing operational criteria for identifying actions that must be governed differently due to irreversibility risk.

Representative anchors:
- Alignment: (Hadfield-Menell et al., 2016; Christiano et al., 2017)
- Robustness: (Goodfellow et al., 2014; Hendrycks & Dietterich, 2019)
- Interpretability: (Doshi-Velez & Kim, 2017; Lipton, 2018)
- Governance: (Brundage et al., 2020; Anderljung et al., 2023)

---

### 6.2 Why Tempo Matters as a First-Class Safety Variable

Most AI safety frameworks implicitly assume that corrective feedback can be applied in time. FIT challenges this assumption by emphasizing that **feedback latency relative to system update tempo** determines whether safety interventions are effective.

When system evolution outpaces governance feedback:
- Corrective actions become retrospective.
- Errors accumulate faster than they can be resolved.
- Safety shifts from prevention to damage control.

By elevating tempo to a first-class variable, FIT reframes safety from optimizing steady-state behavior to **maintaining intervention viability over time**.

---

### 6.3 False Stability and the Illusion of Control

FIT highlights **false stability**: states in which systems appear performant and stable while progressively losing controllability.

False stability differs from traditional failure modes:
- No immediate performance degradation is observed.
- Incidents are absorbed or normalized rather than resolved.
- Governance structures remain formally intact but lose practical efficacy.

FIT explains false stability as a consequence of **option-space collapse** driven by IOs. This perspective helps reconcile why some systems fail catastrophically despite prolonged periods of apparent success.

---

### 6.4 Implications for AI Deployment Practice

This paper suggests a practical shift: treat irreversibility as a governable variable via selective controls, rather than attempting to govern all actions equally.

**Minimal adoption path for an AI lab / org**
1. **Create an IO registry:** define what counts as an IO in your context; require IO tagging for changes to deployment tempo, rollback mechanisms, decision authority, and dependencies.
2. **Install Slow Authority gates for IOs:** enforce delay + dual authorization + auditable rationale for IO-classified changes.
3. **Require Rollback Windows and rehearsals:** treat rollback as a periodically tested capability, not a documentation artifact.
4. **Enforce tempo stratification:** prevent fast-layer updates from modifying slow constraints (policy, access, irreversible rollouts) without slow authority.
5. **Define circuit-breaker triggers:** link IO indicators to automatic downgrades or pauses; pre-register triggers to avoid ad hoc governance.
6. **Run adversarial audit:** continuously probe bypass paths and failure modes, including governance gaps and emergency shortcuts.

**What to measure (process metrics)**
- Update velocity ratio vs evaluation cycle time
- Rollback success rate and rehearsal frequency
- IO approval latency and bypass count
- Change-point frequency in governance-critical metrics (audit logs, policy exceptions)

---

### 6.5 Limitations

1. **No quantitative benchmarks yet.** IO indicators are proposed but not empirically validated at scale.
2. **Domain calibration required.** Thresholds for tempo mismatch and irreversibility are context-dependent.
3. **Not a complete safety solution.** FIT addresses *when* intervention is possible, not *what* objectives to align.
4. **Governance implementation costs.** MVTG introduces overhead; cost-benefit tradeoffs are not analyzed here.
5. **No adversarial threat model (yet).** Current framing emphasizes unintentional IO accumulation, not deliberate evasion.

---

## 7. Conclusion

This work argues that a growing class of AI safety risks arises not from isolated model failures, but from **irreversible system-level transitions** driven by accelerated deployment and governance mismatch. We introduced the Force-Information-Time (FIT) framework to elevate **tempo** - the rate and sequencing of system updates - to a first-class safety variable, and formalized **Irreversible Operations (IOs)** as actions that permanently constrain future corrective options.

By identifying observable indicators of tempo mismatch and irreversibility risk, we showed that many safety failures emerge **before** traditional alignment or robustness interventions can be applied. To address this gap, we proposed **Minimum Viable Tempo Governance (MVTG)**, a lightweight and auditable control layer that selectively governs only those actions that cross irreversibility thresholds.

Preventing irreversible harm requires shifting attention from optimizing outcomes to **maintaining option space**. Treating tempo as a governable variable provides a practical pathway to do so.

---

## Appendix A: EST Audit Artifacts (Optional)

If you run empirical studies of IO indicators, pre-register estimator choices and thresholds (to avoid metric hacking) and report coherence outcomes:

- Pre-registration template: [est_preregistration_template.yaml](../est_preregistration_template.yaml)
- Equivalence + coherence report: [est_equivalence_and_coherence_report.md](../est_equivalence_and_coherence_report.md)

---

## References

- Amodei, D. et al. (2016). *Concrete Problems in AI Safety.* arXiv:1606.06565.
- Anderljung, M. et al. (2023). *Frontier AI regulation: Managing emerging risks.* Centre for the Governance of AI (GovAI). (Policy report.)
- Brundage, M. et al. (2020). *Toward Trustworthy AI Development: Mechanisms for Supporting Verifiable Claims.* arXiv:2004.07213.
- Christiano, P. et al. (2017). *Deep Reinforcement Learning from Human Preferences.* arXiv:1706.03741.
- Doshi-Velez, F., & Kim, B. (2017). *Towards A Rigorous Science of Interpretable Machine Learning.* arXiv:1702.08608.
- Goodfellow, I., Shlens, J., & Szegedy, C. (2014). *Explaining and Harnessing Adversarial Examples.* arXiv:1412.6572.
- Hadfield-Menell, D. et al. (2016). *Cooperative Inverse Reinforcement Learning.* arXiv:1606.03137.
- Hendrycks, D., & Dietterich, T. (2019). *Benchmarking Neural Network Robustness to Common Corruptions and Perturbations.* arXiv:1903.12261.
- Lipton, Z. C. (2018). *The Mythos of Model Interpretability.* Communications of the ACM.
