# AGI Engineering Path

## What Happens Without FIT — and How to Make Progress Auditable

**Author**: Qien Huang
**Version**: v1.0
**Companion to**: "AGI Without and With FIT: World Models, Spatial Intelligence, and the Missing System Discipline"

---

## Executive Summary

World models and spatial intelligence are pushing AGI from language simulation toward embodied, closed-loop systems. This transition is already underway. But without a structural engineering discipline, the field risks producing systems that are powerful yet poorly diagnosable—systems whose failures are patched rather than understood, and whose successes cannot be reliably reproduced in new domains.

This document translates the FIT framework into a practical engineering interpretation: not a new architecture, but a system-level measurement discipline for closed-loop AGI. It specifies four concrete instruments—loop stability metrics, constraint engineering protocols, optimization pressure diagnostics, and a structured failure taxonomy—and shows how they can be applied to existing systems without architectural modification.

---

## 1. The Engineering Reality

A modern AGI pipeline has a recognizable shape. A multimodal foundation model receives inputs from multiple modalities—text, vision, possibly 3D or audio. A planner or tool-use layer translates the model's outputs into action proposals. Those actions are executed in an environment (simulated or physical), and feedback from the environment flows back to update the model's beliefs, reward signals, or fine-tuning data. The loop then repeats.

Most current evaluation of these pipelines focuses on quantities that can be measured at a single step: task success rate, output quality, per-step reward, cost per token, inference latency. These are useful metrics, and they have driven genuine progress. But they share a common limitation: they are *static*. They evaluate the system at an instant, not over time. They tell you whether the system produced the right answer on this step, but not whether it will continue to produce right answers over the next hundred steps, or whether it can recover from an unexpected perturbation, or whether a slow drift in its internal representations will eventually destabilize its behavior.

This is not a theoretical concern. Any engineer who has worked with control systems recognizes the pattern: a system that performs well on step-by-step tests can fail catastrophically in closed-loop operation, because the feedback dynamics that govern long-horizon behavior are invisible to single-step evaluation. The gap between "performs well on benchmarks" and "remains stable under continuous operation" is exactly the gap that loop metrics are designed to measure.

---

## 2. The Default Trajectory

Without a structural discipline for loop-level evaluation, the field tends toward three patterns that are individually rational but collectively insufficient.

The first is recipe optimization. Models get larger, pretraining mixtures get better, alignment procedures get more sophisticated, tool integrations multiply. Each improvement is validated against benchmarks, and performance curves trend upward. But when something goes wrong—when a model that worked well at one scale fails at the next, or when an alignment intervention produces an unexpected side effect—the diagnostic vocabulary is limited to "try a different recipe." The system improves steadily, but the understanding of *why* it improves (or fails) lags behind.

The second is patch-based stability. When instability surfaces—hallucinations, inconsistent behavior across modalities, cascading errors in multi-step reasoning—the response is typically additive: add a guardrail, add a heuristic check, add a refusal policy, add a fallback prompt. Each patch addresses a specific failure mode, and the stack of patches accumulates over time. The result is a system whose stability is layered rather than structural. It works, until it encounters a failure mode that falls between the patches—and when it does, the diagnosis is expensive because the interaction effects between patches are poorly understood.

The third is fragmented evaluation. The vision team optimizes vision metrics. The robotics team optimizes manipulation success rates. The agent team optimizes tool-use benchmarks. Each team is competent within its domain, but system-level coherence—whether the vision representations support manipulation, whether the agent's plans are consistent with the world model's physics—is rarely measured explicitly. Integration testing exists, but it is typically an afterthought rather than a first-class engineering practice.

These three patterns are not pathological. They are the natural result of a field that has powerful subsystems and weak system-level measurement. The gap is not in capability but in diagnostics.

---

## 3. The Missing Layer: Loop Metrics

If AGI is a dynamical system—and any closed-loop agent operating over time is, by definition, a dynamical system—then it must be evaluated with dynamical metrics. Below is a minimal set, organized around the FIT primitive of Time.

### Uncertainty reduction rate

Over a sequence of interaction cycles, does the system's uncertainty about the world decrease? The measurement is straightforward:

$$\Delta H = H_t - H_{t+1}$$

where $H_t$ is the system's uncertainty (however operationalized—entropy of belief state, variance of predictions, calibration error) at cycle $t$. In a well-functioning system, $\Delta H$ should be predominantly positive: each interaction should, on average, reduce uncertainty. If $\Delta H$ fluctuates around zero or turns negative, the system is not learning from its interactions—it is either stagnating or actively losing information.

This metric is the temporal analog of FIT's constraint accumulation ($\mathcal{L}4$). In the GoL experiments, constraint increased monotonically as the system settled into stable configurations. In an AGI system, the analogous signature would be monotonic uncertainty reduction over interaction cycles—a signal that the system is converging toward a stable internal model rather than drifting.

### Recovery time

After a perturbation—an unexpected observation, an adversarial input, a sensor failure—how many interaction steps does the system require to return within $\varepsilon$ of its stable operating regime?

$$T_{\text{recover}} = \min\{k : \|s_{t+k} - s^*\| < \varepsilon\}$$

where $s^*$ is the stable-regime state and $s_{t+k}$ is the state $k$ steps after the perturbation. Short recovery time indicates dynamical robustness; long or infinite recovery time indicates fragility. In control theory, this is closely related to the concept of settling time. In FIT vocabulary, it measures the system's ability to re-accumulate constraint after a disruption.

### Drift accumulation

Over long horizons, do the system's internal states remain close to their expected trajectories, or do they slowly diverge?

$$D_t = \|s_t - \hat{s}_t\|$$

where $\hat{s}_t$ is the expected state at time $t$ given the system's dynamics and initial conditions. Slow drift is insidious because it is invisible to per-step evaluation—each individual step may look fine while the cumulative deviation grows. Monitoring drift accumulation is the temporal analog of monitoring a ship's heading: a one-degree error is negligible on any given minute but catastrophic over a transatlantic crossing.

### Loop delay sensitivity

Artificially increase the delay between the system's observation and its action (or between its action and the environment's feedback). Measure how steeply performance degrades as a function of the added delay. A system that collapses under small delays is operating near the edge of its stability margin—a situation that may be tolerable in a controlled lab but dangerous in deployment, where latencies are variable and unpredictable.

---

## 4. Constraint Engineering

The conventional approach to improving an AI system's capabilities is to give it more data. The constraint engineering approach, informed by FIT, is different: instead of increasing the volume of information, increase the stringency of the constraints the system must satisfy.

### Cross-modal consistency

When a system operates across multiple modalities—text, vision, 3D geometry, physical action—each modality imposes its own constraints. Text requires semantic coherence. Vision requires geometric consistency. 3D requires physical plausibility. Action requires dynamical feasibility. Cross-modal consistency testing asks whether these constraints are simultaneously satisfied: does the object the system describes in text match the object it perceives in vision? Does the 3D model it constructs respect the geometry visible in the image? Does the action it proposes respect the physics implied by its world model?

Failures in cross-modal consistency come in several flavors. Semantic drift occurs when the system's linguistic description gradually diverges from its perceptual state. Spatial incoherence occurs when the 3D geometry is internally contradictory. Physical violation occurs when the proposed action violates conservation laws or contact constraints. Each of these is a different kind of constraint failure, and distinguishing them matters for diagnosis: semantic drift points to a representation alignment problem, spatial incoherence points to a geometric reasoning problem, and physical violation points to a dynamics modeling problem. Treating all three as generic "errors" loses diagnostic information.

### Counterfactual consistency

Apply an intervention to the world model: remove an object, change a parameter, apply a force. Then ask whether the downstream consequences are consistent with the intervention. If you remove a supporting column from a simulated building, does the roof collapse? If you increase gravity, do falling objects accelerate faster? Counterfactual consistency tests the system's causal model, not just its observational statistics. A system that passes observational benchmarks but fails counterfactual tests has learned correlations, not causes—and in deployment, it will fail whenever the environment deviates from the training distribution.

### Edit stability

Modify one aspect of the world state and measure whether unrelated aspects remain unchanged. If you change the color of an object, does its mass stay the same? If you move a wall, do distant objects remain in place? Edit stability tests the system's ability to localize changes—to update the relevant parts of its world model without corrupting the irrelevant parts. This is a particularly stringent test because it requires the system to maintain a modular representation in which different aspects of the world are independently adjustable.

---

## 5. Optimization Pressure Diagnostics

Every training procedure applies optimization pressure, and that pressure is not neutral. A system trained primarily on next-token prediction is driven toward the statistical regularities of its training corpus. A system trained with RLHF is driven toward human preference patterns. A system trained with safety constraints is driven away from certain output regions. Each of these pressures shapes the system's internal representations and behavior in specific ways, and the interactions between pressures can produce unexpected effects.

Two diagnostic tools make this pressure landscape more visible. The first is constraint activation mapping: tracking which constraints most frequently trigger loss during training. If safety constraints are activated ten times more often than accuracy constraints, the system is spending most of its optimization budget on avoiding forbidden outputs rather than improving correct ones—a tradeoff that may or may not be desirable, but should at least be visible. The second is phase transition detection: monitoring for sudden, discontinuous changes in system behavior—jumps in planning depth, collapses in consistency, abrupt changes in recovery time. In the GoL experiments, such transitions correspond to the onset of constraint accumulation; in an AI system, they may correspond to the emergence (or collapse) of capabilities.

---

## 6. Closed-Loop Evaluation Protocol

The metrics and diagnostics described above can be integrated into a reproducible evaluation protocol. The protocol has four stages, each of which can be implemented independently.

The first stage is environment definition. Before running any evaluation, specify the state space (what configurations the environment can be in), the action space (what the system can do), the observable space (what the system can see), and the intervention capability (what perturbations the evaluator can apply). These specifications serve the same role as boundary conditions in a physics experiment: they define the scope within which the evaluation results are valid.

The second stage is loop execution. Run $N$ episodes, each consisting of a repeated cycle: observe, plan, act, update beliefs, repeat. The number of episodes and the length of each episode should be sufficient to observe both transient behavior (the system's initial adaptation) and steady-state behavior (its long-run stability). Recording only aggregate success rates across episodes misses the temporal structure within each episode, which is often where the most diagnostic information lies.

The third stage is recording. For each episode, record the full temporal trajectory of at least five quantities: the uncertainty trajectory ($H_t$ over time), constraint violations (which constraints were violated and when), recovery time after each perturbation, cumulative risk (how much irreversible action the system has taken), and resource consumption (compute, memory, wall-clock time). These trajectories, not their averages, are the primary data product.

The fourth stage is failure classification. When the system fails, the failure should be categorized by its structural type, not just its surface symptom. The minimal taxonomy distinguishes four types: informational failures (the system lacked the data to make a correct decision), temporal failures (the system had the information but its loop dynamics were unstable), constraint conflicts (two constraints imposed contradictory requirements), and optimization misalignment (the training objective pushed the system away from the desired behavior). This classification is valuable because different failure types require different interventions: informational failures call for better data, temporal failures call for loop stabilization, constraint conflicts call for constraint redesign, and optimization misalignment calls for objective revision.

---

## 7. Constraint Atlas

The metrics, diagnostics, and protocol described above can be organized into a progressive map of capability regimes. Each regime is defined by the constraints it imposes, and the expected behavioral signatures that emerge when those constraints are satisfied.

| Regime | Constraint introduced | Expected behavioral signature |
|---|---|---|
| R1 | Static consistency | Accurate single-frame reconstruction |
| R2 | Cross-modal agreement | Reduced hallucination across modalities |
| R3 | Action feedback | Closed-loop error correction |
| R4 | Long-horizon memory | Stable multi-step planning |
| R5 | Risk budget | Bounded irreversible action |

The table reads as a progression: each regime adds a constraint on top of all previous ones, and the expected behavior emerges only when the new constraint is satisfied in the context of the existing ones. A system that achieves R3 (closed-loop correction) without R2 (cross-modal agreement) may correct its actions based on internally inconsistent feedback—a form of stability that is worse than instability, because it converges to the wrong attractor with confidence.

AGI progression, in this view, is not a smooth curve of increasing capability. It is a sequence of constraint regimes, each of which represents a qualitative phase of behavior. Tracking which regimes a system has crossed—and which it has not—provides a more informative progress metric than any single benchmark score.

---

## 8. Risk Engineering

World models give systems the ability to simulate consequences before acting. This is a powerful capability, but it also increases the system's potential for irreversible action—because a system that can predict consequences can also plan actions with large-scale effects. Risk engineering adds three instruments to bound this potential.

The first is a risk budget: an explicit upper bound on the probability that the system takes an irreversible action in any given episode. The budget is set by the deployer, not by the system, and the system's behavior is evaluated against it. This is analogous to a financial risk budget (Value at Risk) that limits a trader's maximum exposure regardless of the expected return.

The second is the uncertainty declaration rate: how often does the system say "I do not know"? Calibration—the alignment between a system's confidence and its actual accuracy—is a well-studied problem, but it is rarely treated as a first-class evaluation metric in AGI benchmarks. A system that is wrong and knows it is wrong is safer than a system that is wrong and confident, because the former can trigger a fallback while the latter will act on its error.

The third is fail-safe recovery: the existence and reliability of a defined fallback state. When the system detects that it is outside its competence boundary—either through uncertainty thresholds or constraint violation counts—can it return to a safe baseline? The restoration success rate (how often the fallback actually works) is a critical metric that is almost never reported in current evaluations.

---

## 9. Implementation Path

These instruments can be adopted incrementally, without requiring architectural changes to existing systems.

The first phase is diagnostic: add loop metrics (uncertainty reduction rate, recovery time, drift accumulation, delay sensitivity) to an existing closed-loop agent. This requires only logging and post-hoc analysis—no changes to the agent's architecture, training, or deployment. The goal is to establish a baseline: what does the system's temporal behavior actually look like, measured with dynamical metrics rather than static benchmarks?

The second phase is taxonomic: document the failure modes observed in the diagnostic phase into a structured constraint atlas. Each failure is classified by type (informational, temporal, constraint conflict, optimization misalignment) and mapped to the constraint regime where it occurs. The atlas becomes a reusable diagnostic resource: when a new failure is observed, the atlas tells you which previously seen failures it resembles and what interventions have worked in the past.

The third phase is experimental: introduce one new constraint regime at a time—add cross-modal consistency testing, then counterfactual consistency, then edit stability—and measure whether each addition produces a detectable phase change in the system's behavior. This is the constraint engineering approach: not adding capabilities, but adding constraints and observing which constraints push the system into qualitatively different behavioral regimes.

The fourth phase is risk integration: add explicit risk budget evaluation, uncertainty declaration monitoring, and fail-safe recovery testing. This phase transforms the system from a capability demonstrator into a deployable engineering artifact with defined safety margins.

Each phase builds on the previous one. None requires waiting for the others to be complete. And none requires any change to the underlying model architecture—only to the measurement and evaluation infrastructure that surrounds it.

---

## Conclusion

AGI will likely emerge from the convergence of multimodal foundation models, world simulation, and closed-loop planning. The technical building blocks are largely in place, and they will continue to improve regardless of whether any particular theoretical framework is adopted.

But there is a difference between building blocks and buildings. The difference is engineering discipline—the practice of measuring not just whether the system works, but *how* it works, *when* it fails, *why* it fails, and whether the lessons from one failure transfer to the next system.

This document proposes a minimal version of that discipline: measure loops, engineer constraints, track phase transitions, audit failures. These four imperatives are not specific to FIT. They are specific to the challenge of building dynamical systems that must remain stable, coherent, and safe over extended operation. Whether the vocabulary comes from FIT, from control theory, from systems engineering, or from some framework not yet written matters less than whether the vocabulary exists at all.

What matters is that AGI engineering makes the transition from capability stacking to system stability design. The systems we are building are too consequential for their failures to remain unintelligible.
