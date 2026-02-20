# AGI Without and With FIT

## World Models, Spatial Intelligence, and the Missing System Discipline

**Author**: Qien Huang
**Version**: v1.0

---

## Introduction

The industry does not need FIT to move toward AGI.

World models, spatial intelligence, multimodal foundation models, embodied agents—these trajectories are already in motion. Capital is flowing, data pipelines are expanding, and benchmarks are evolving faster than the papers that introduce them. If FIT had never been written, the field would still advance. Nothing in this essay depends on denying that fact.

The question this essay addresses is different. It is not whether AGI research will progress, but whether that progress will be *structurally diagnosable*—whether, when a system fails, we will know why it failed; whether, when a system succeeds, we will know what made it succeed; and whether the lessons learned in one system will transfer to the next without starting from scratch.

The history of engineering suggests that these properties do not emerge automatically from capability growth. Aviation advanced rapidly in the first half of the twentieth century, but it was not until the adoption of systematic failure analysis—black boxes, standardized incident reports, root-cause decomposition—that the industry achieved the reliability levels we now take for granted. The airplanes were always getting faster. What changed was that crashes became *informative*.

FIT's role in AGI research is analogous. It does not propose new architectures or invent new loss functions. It proposes a structural decomposition language—Force, Information, Time, Constraint, State—that converts progress from empirical accumulation into system-level discipline: a discipline in which failures are as reusable as successes, and in which the diagnosis of a bottleneck tells you something about its nature, not just its location.

---

## 1. What Happens Without a Structural Discipline

To understand what FIT adds, it helps to consider what happens in its absence. Let us project three patterns that characterize current AGI development when no unifying structural framework is in place.

### The benchmark treadmill

Each subfield optimizes its own metric. Vision-language models chase zero-shot accuracy. 3D generation pursues perceptual realism. Robotics targets task success rates. Agent systems compete on tool-use benchmarks. Within each silo, progress is real and measurable. But integration across silos becomes an afterthought, because the metrics that drive progress in one domain say nothing about compatibility with another. A vision-language model that achieves state-of-the-art on image captioning may produce representations that are useless for robotic manipulation—not because the representations are bad, but because the benchmark that shaped them was indifferent to the constraints that manipulation requires.

The system grows in capability but not necessarily in coherence. And the gap between the two is invisible from within any single benchmark.

### Scaling as default strategy

The dominant improvement recipe remains straightforward: more data, larger models, better training recipes, more careful alignment tuning. When something goes wrong, the response is typically a patch—prompt engineering, guardrails, fine-tuning layers, auxiliary reward models. These patches often work. But they accumulate, and their interactions become opaque.

The deeper issue is epistemological. When a scaled-up model performs better, we know *that* it performs better before we understand *why*. Was the improvement due to more capacity, better data coverage, an accidental change in the constraint landscape of the loss function, or a phase transition in the model's internal representation? Without a structural vocabulary for distinguishing these possibilities, each success is a data point with no explanatory coordinates. The next scaling decision is informed by the outcome of the last one, but not by a causal model of what produced that outcome.

### Theoretical fragmentation

Partial theoretical lenses exist and are individually valuable. Control theory provides stability analysis and gain margins. Active inference reframes perception as uncertainty reduction through action. Minimum Description Length explains why abstraction emerges under compression pressure. Causal representation learning enables intervention-level reasoning. Hierarchical reinforcement learning operationalizes temporal abstraction. Calibration theory turns overconfidence into a measurable failure mode.

But these frameworks remain loosely coupled. A control theorist can tell you whether a system is stable. A causal learning researcher can tell you whether an intervention is identifiable. An MDL theorist can tell you whether a representation is compressed. What no single framework currently provides is a shared structural map that answers questions like: *which constraint regime triggered the capability emergence we observed? Was the bottleneck temporal or informational? Was the failure architectural or dynamical?* These cross-cutting questions fall between frameworks, and in the gaps between frameworks, expensive diagnostic work happens ad hoc.

---

## 2. Why World Models Matter

Before introducing FIT's contribution, it is worth understanding why world models represent a genuine structural advance, not merely a branding exercise.

Language models, for all their power, operate inside symbolic projection. They can generate text that describes a ball rolling off a table, but they do not maintain an internal state that tracks the ball's position, velocity, and contact forces as the sentence unfolds. The text is coherent at the linguistic level while being unconstrained at the physical level. This is why a language model can confidently describe a scenario that violates conservation of energy—the constraint that would catch that violation simply does not exist in the model's representational space.

World models change this. They introduce constraints that language alone does not impose: object permanence (things continue to exist when unobserved), geometric consistency (occluded surfaces have definite shapes), physical feasibility (proposed actions must respect dynamics), and counterfactual coherence (if you change one condition, the downstream consequences must update accordingly). Each of these is a constraint in the precise FIT sense—a reduction of the space of states the model is allowed to occupy.

The shift from language models to world models is therefore not a shift from less data to more data. It is a shift from a weakly constrained representational space to a strongly constrained one. And in FIT's vocabulary, that distinction matters enormously, because capability emergence is often driven not by increasing information but by entering a new constraint regime.

Consider an analogy from the GoL experiments. A random initial configuration of cells has maximum informational variety but almost no structure. As the system evolves and cells freeze into still-lifes and oscillators, information (in the sense of entropy) decreases while constraint increases. The system becomes *less* informationally rich but *more* structurally organized. The transition from language models to world models may be analogous: the addition of physical constraints reduces the space of representational possibilities, and it is precisely this reduction that enables new capabilities—spatial reasoning, physical prediction, action planning—that were inaccessible in the unconstrained regime.

---

## 3. The Hidden Bottleneck

Multimodal training increases the information available to a model. World models increase the structural richness of its representations. But the hardest bottleneck emerging in current AGI research is neither model size nor data scale. It is temporal structure.

Consider what a genuinely intelligent embodied agent must do. It must maintain a consistent internal model across hundreds or thousands of interaction steps, each of which may update the model's beliefs, trigger actions, receive feedback, and revise plans. It must assign credit for outcomes to decisions made far in the past—the long-horizon credit assignment problem that reinforcement learning has struggled with for decades. It must recover gracefully from perturbations: unexpected obstacles, sensor noise, adversarial inputs. And it must do all of this in a closed loop, where delays between sensing and acting can destabilize the very feedback that the system depends on.

These are not information problems. They are time problems. The constraint is not "does the system have enough data?" but "can the system maintain coherence across a temporal sequence of state transitions, each of which is conditioned on all previous ones?"

Without a temporal lens, research drifts toward static evaluation. We test models on single-shot tasks, frozen environments, and prompt-based scoring. These evaluations capture a system's capacity at an instant but say nothing about its stability over time. A model that scores 95% on a spatial reasoning benchmark may collapse after ten steps of closed-loop interaction—not because it lacks spatial knowledge, but because it lacks the temporal discipline to maintain that knowledge under sequential updating.

This is one of the field's quietest structural gaps. It is quiet because benchmark-driven research has no natural way to measure it. You cannot score "temporal coherence" on a leaderboard. But it is the gap that will matter most as systems move from static inference to dynamic interaction.

---

## 4. Where FIT Enters

FIT does not provide a new neural architecture, and it does not replace any of the established theoretical frameworks mentioned above. Its contribution is at a different level: it provides a structural decomposition language that makes certain questions askable—and answerable—that would otherwise remain implicit.

### Force as diagnostic

The standard question in scaling research is: "Does scaling work?" FIT replaces this with a more structural question: "What kind of optimization pressure is shaping the system, and toward which attractor is it being driven?"

This is not a rhetorical substitution. Different forces shape systems in qualitatively different ways. Scaling the dataset drives the system toward the statistical regularities of the data distribution. Safety alignment drives it toward the boundaries of a constraint set defined by human preferences. Productization drives it toward the attractors of user engagement metrics. Each of these is a force in the FIT sense—a driver of state change—and they do not necessarily point in the same direction. A system simultaneously subject to scaling pressure, safety constraints, and engagement optimization is navigating a multi-force landscape, and its trajectory through that landscape is not determined by any single force alone.

The diagnostic value of this decomposition is that when a system behaves unexpectedly—when a safety-tuned model suddenly produces harmful outputs under a novel prompt, or when a scaled-up model loses a capability it previously had—FIT provides a vocabulary for asking: *which force dominated in this regime? Did the system cross a phase boundary where the relative strength of forces changed?* These questions do not guarantee answers, but they constrain the search space for diagnosis.

### Constraint as the real currency of capability

The conventional narrative about multimodal training is that it provides "more information." FIT offers a sharper interpretation: multimodal training adds cross-modal consistency constraints, and it is the constraints, not the information, that drive capability emergence.

Text alone permits many internally coherent but externally false narratives—a language model can describe a perpetual motion machine in grammatically perfect English. Adding visual grounding introduces geometric constraints. Adding physics simulation introduces dynamical constraints. Adding embodied interaction introduces action-feasibility constraints. Each new modality does not simply add data; it narrows the space of representations the model is allowed to occupy.

This perspective makes a specific prediction: capability jumps should correlate with the introduction of new constraint families, not merely with increases in data volume or model size. If a vision-language model suddenly acquires spatial reasoning ability, FIT predicts that the relevant change was the addition of a constraint (perhaps 3D consistency) rather than a quantitative increase in image-text pairs. This prediction is testable, though testing it requires the kind of controlled experimental design that benchmark-driven research rarely provides.

### Time as the deepest diagnostic layer

This is where FIT becomes most distinctive. Instead of asking "Did performance improve?", FIT asks a battery of temporal questions. Did uncertainty decrease over interaction cycles? Is the system converging toward a stable attractor, or oscillating? What is the recovery time after a perturbation? Does the delay between sensing and acting destabilize the feedback loop?

These questions are not philosophical. They are measurable—in principle and, increasingly, in practice. The GoL experiments provide a small-scale demonstration: constraint accumulation ($\mathcal{L}4$) can be tracked over time, its rate of change measured, its cross-scale consistency tested. In an AI system, the analogous measurements would track the evolution of internal representations over sequential interactions, measuring whether the system's "constraint" (however operationalized) increases, stabilizes, or collapses.

Without such temporal metrics, we mistake a single good response for dynamical robustness. A model that produces a correct answer on one turn may be in a fragile state that will collapse on the next perturbation. Static benchmarks cannot detect this fragility. Temporal diagnostics can.

---

## 5. Honest Scope

Let us be precise about what FIT can and cannot do.

FIT cannot guarantee AGI, provide architectural blueprints, or replace empirical experimentation. In early capability regimes—where the system is far from any attractor and the dynamics are dominated by simple gradient descent—FIT's structural vocabulary adds relatively little to what standard optimization theory already provides. The force is the gradient, the constraint is the loss landscape, and the time structure is the training schedule. These are already well understood without FIT.

FIT's value increases as systems become more dynamical. In closed-loop embodied agents, where multiple forces interact, constraints accumulate nonlinearly, and temporal coherence is the binding bottleneck, the standard optimization vocabulary runs out. "The loss went down" is no longer a sufficient diagnosis when the system is simultaneously learning, acting, receiving feedback, updating its world model, and managing safety constraints across time. In that regime, FIT's decomposition into Force (what drives change), Information (what constrains the space), and Time (what governs the sequence) provides a diagnostic framework that is absent from any single existing theory.

The honest assessment is therefore regime-dependent. For static, single-shot models, FIT is a modest conceptual overlay. For dynamic, closed-loop, multi-constraint systems, it may be the difference between diagnosable engineering and trial-and-error scaling.

---

## 6. The Strategic Reframe

The deepest difference between AGI research with and without a structural discipline is not technical. It is strategic.

Without such a discipline, AGI progress looks like capability stacking: add vision, add language, add tools, add embodiment, add reasoning, and hope that the combination produces intelligence. Each addition is motivated by a benchmark gap, and success is measured by closing that gap. The implicit theory is that intelligence is the sum of capabilities.

With a structural discipline, AGI progress becomes something different—what we might call *constraint engineering*: the deliberate design of constraint regimes that push systems into more stable, more coherent phases of behavior. This is not a vague aspiration. It is a specific methodological stance. In the same way that a materials scientist does not simply mix elements and hope for useful alloys, but instead maps phase diagrams and identifies the temperature-pressure regimes where desired crystal structures form, a constraint engineer would map the landscape of possible constraint combinations and identify the regimes where desired capabilities emerge as stable attractors.

The GoL experiments offer a miniature illustration. The transition from random initial conditions to stable still-lifes is not the result of adding capabilities to the cells—the cells' rules never change. It is the result of constraint accumulation: the progressive elimination of unstable configurations until only dynamically stable structures remain. The "intelligence" of the final configuration (if we may use the word loosely) is not something added from outside. It is what remains after sufficient constraint has been applied.

Whether this analogy extends to AGI is an open question. But the methodological difference is clear: capability stacking asks "what can we add?", while constraint engineering asks "what constraint regime produces the phase of behavior we want?" The second question is harder to answer, but it is also more likely to produce results that transfer across systems—because the answer is structural, not substrate-specific.

---

## Conclusion

World models will advance. Spatial intelligence will expand. Embodied agents will become more capable. These trajectories are driven by capital, compute, and competitive pressure, none of which depend on the existence of any particular theoretical framework.

But whether this trajectory produces a collection of impressive subsystems or a structurally coherent path toward stable AGI depends on whether the field adopts a system-level discipline—a shared vocabulary for diagnosing why systems succeed, why they fail, and what connects success in one domain to success in another.

FIT is not necessary for AGI to emerge. It may, however, be necessary for AGI progress to remain intelligible, auditable, and transferable. In the long-horizon engineering of systems that will shape civilization, intelligibility may matter more than raw speed. The question is not whether we can build powerful AI without understanding what we are building. We probably can. The question is whether we should.
