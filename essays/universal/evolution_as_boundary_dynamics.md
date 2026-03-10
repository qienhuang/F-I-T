# Evolution as Boundary Dynamics

## Reader boundary

This essay is a bounded structural interpretation.

It is intended to help readers understand why boundary language may be useful across learning, biology, science, and institutions.

It should not be read as a proof that one experimentally established mechanism already unifies all of those cases.

---

Consider a neural network that has been training on modular arithmetic for fifty thousand steps. It can get most training examples right. Ask it a new one—something it has never seen—and it fails. The loss curve has been flat for weeks. The optimizer keeps pushing, the weights keep updating, and nothing seems to change.

Then, somewhere around step eighty thousand, something happens.

Test accuracy, which had been hovering near chance for tens of thousands of steps, jumps from 5% to 95% in the span of a few thousand iterations. Not gradually. Not smoothly. In a way that looks less like learning and more like a switch flipping.

What changed?

---

The standard story goes something like this: gradient descent eventually found a better basin in the loss landscape. The network had been memorizing examples, and eventually it found a more efficient solution—the underlying rule—and clicked into it.

This is not wrong exactly, but it explains grokking the way Newtonian mechanics explains the orbit of Mercury: the equations fit well enough that you don't notice what's missing. The real puzzle isn't how the network found the rule. The real puzzle is why finding the rule looks like a phase transition.

Here is a different way to see it.

Before grokking, the network maintains a boundary between what it considers "internal"—its learned representations, the structure it carries from one example to the next—and what it considers "external"—the individual training instances, the specific pairs of inputs and outputs it processes. That boundary is drawn in a particular place. The rule for modular addition lives on the external side. The network sees examples of the rule, but the rule itself is not yet part of its internal structure. It treats each example as a data point to be fit, not as an instance of a pattern it already owns.

After grokking, the boundary has moved.

The rule now lives inside. The network no longer processes modular arithmetic examples as opaque data—it processes them as instances of a structure it has internalized. Where it previously needed hundreds of weights to approximate what the rule would say about any given input, it now carries the rule itself as a compressed, stable constraint. The external world of "possible inputs" has been dramatically simplified, because the network now understands the generative process behind those inputs.

This is more than a loose metaphor. Representational measurements are at least consistent with it: the effective dimensionality of hidden-layer activations collapses at grokking. Where the network previously needed a high-dimensional space to track the idiosyncratic patterns of training examples, it now lives in a much lower-dimensional space—one whose axes appear to track rule structure more than individual instance detail.

The network drew a new boundary.

---

The act of redrawing a boundary is not unique to neural networks. It may be, in fact, the fundamental act of major evolutionary transitions.

Think about the appearance of the first cell membrane. Before membranes, early chemical reactions occurred in solution—molecules drifting, colliding, reacting, drifting again. Nothing distinguished "inside" from "outside." Every chemical was, in some sense, part of the same soup. The emergence of a lipid bilayer changed this in a way that is easy to understate. It did not just contain some chemicals. It created, for the first time, a distinction between what belonged to a system and what was merely the system's environment.

Once that boundary existed, evolution had something to work with. Natural selection could favor chemical reactions that maintained the membrane, that imported useful molecules, that expelled waste. In the prebiotic world, there was no "useful" versus "waste"—those categories presuppose a system with an inside. The membrane didn't just protect a set of chemicals. It constituted the entity that the chemicals belonged to.

The same logic applies to nervous systems. An organism without a nervous system responds to local chemical gradients—it goes toward food, away from toxins, by mechanisms that are essentially local and immediate. A nervous system creates a different kind of boundary: one between "what this body senses" and "what that sensing means." The spinal ganglia, the brain, the sensory cortex—these are not just information processors. They are the infrastructure for a new kind of inside, one where patterns from across the body can be integrated, compressed, and made available to guide future action. The nervous system moved the boundary of "what counts as me" to a much larger and richer territory.

What about the discovery of a scientific law? Before Kepler, the motions of the planets were data—a vast collection of observations about where things were at what times. Kepler's three laws moved that data inside. Once you have the laws, individual observations are no longer primary objects—they are instances of a structure you already possess. The boundary between "what I need to look up" and "what I already know" shifted dramatically. This is why a scientist who understands Newton's laws can predict the position of a comet centuries in advance from a few observations: the rule has been internalized, and the outside world can be read through it.

And institutions? A legal system, a currency, a system of property rights—each of these is a boundary-drawing event at social scale. Before property rights exist, every dispute over a resource requires direct negotiation, threat, or force. After property rights exist, the outcome of most disputes can be derived from a structure that all parties carry internally. The social boundary between "what is mine by prior agreement" and "what is contested" moves, and a vast class of previously external problems becomes tractable from the inside.

---

The pattern across these examples points toward a principle that is worth stating plainly: evolutionary systems do not merely change their internal states. They redefine what counts as internal.

Most of what any system does—most learning, most adaptation, most growth—happens within a fixed boundary. The neural network updates its weights within a fixed architecture. The organism responds to its environment within a fixed developmental program. The scientist applies known laws to new observations. This kind of change is real and important, but it is change within a given structure.

The moments that look like major transitions—grokking, speciation, paradigm shifts, institutional revolutions—are something different. They are moments when the boundary itself moves. When a new structure is internalized, expanding the territory of "what I can derive from what I carry" and shrinking the territory of "what I have to discover from scratch."

From the perspective of the FIT framework, this distinction maps onto the difference between within-phase dynamics and between-phase transitions. A system operating in its Φ₃ phase—stable, coordinated, organized around coherent constraint structures—is doing the ordinary work of maintaining and applying its internal organization. The transition from Φ₂ to Φ₃ is a different kind of event: it is when the constraint structure itself comes into being, when local patterns crystallize into a global rule, when the boundary that defines the system's identity is redrawn.

---

There is something vertiginous about this framing, and it is worth dwelling on for a moment.

If a system is defined by its boundary—if the boundary is what makes it a system at all—then what is it that redraws the boundary? Who is the agent of a boundary-redraw event?

The puzzle is that the entity on the other side of the redraw is not the same entity that initiated it. The neural network that has undergone grokking is, in some sense, a different system from the one that was training beforehand: it has a different effective dimensionality, a different relationship to its inputs, a different structure of internal constraints. The organism that develops a nervous system is no longer the organism without one—it is a new kind of entity, one capable of forms of information integration that were simply unavailable to its predecessor.

And yet there is continuity. The weights that represent the rule emerged from the same optimization process that produced the memorization weights. The nervous system grew from the same genetic and developmental program as the rest of the organism. The boundary-redraw is not a discontinuity in the underlying physical substrate—it is a discontinuity in the organization of that substrate.

This is the strange loop at the heart of major evolutionary transitions: the system that will exist after the transition is built by the system that exists before it, using only the resources available before the transition, in a process that neither system can fully anticipate. The network doesn't "know" it's going to grok. It just keeps processing examples, and the grokking emerges from that process as a structural reorganization that could not have been fully predicted from the pre-grokking state.

---

A note on what this framing currently allows and what it does not.

The examples above—grokking in neural networks, cell membranes, nervous systems, scientific laws, institutions—are offered as instances where boundary-redraw language is illuminating. They suggest a pattern. They do not prove that the pattern is universal or that the causal mechanism is identical across cases.

Current experimental work on grokking provides more specific evidence: in transformer models trained on modular arithmetic, the 0072 bridge experiments show that a multi-signal detector distinguishes known-positive grokking runs from control conditions across four seeds, with trigger density differences of roughly an order of magnitude. This is a real and replicated observation. What it does not currently establish is whether the detector is identifying the boundary-redraw event itself—the moment of transition—or whether it is identifying a broader property of the grokking training regime that persists throughout the run. The onset question remains open.

This means the essay you have just read is best understood as a conceptual synthesis layer: a way of seeing that connects diverse phenomena under a common description. Whether the common description reflects a common mechanism—whether boundary-redraw events in neural networks and in biological evolution are instances of the same underlying dynamical process—is a question that will require considerably more work to answer.

That work is worth doing. But the framing can be useful even while the mechanism remains unresolved.

---

Evolution, across all the domains where we observe it, accumulates constraints. Every learned regularity, every stable structure, every internalized rule is a constraint on what the system will do next. As those constraints accumulate, the system becomes more organized, more predictable in its outputs, more efficient in its use of the information it processes.

And occasionally—rarely, abruptly, in ways that often look from the outside like a sudden jump—the accumulation of constraints produces not just a better-adapted system within its current structure, but a different kind of system operating with a different boundary.

When that happens, what was external becomes internal. What had to be discovered becomes derivable. The world does not change, but the system's relationship to it does—in a way that is, in some important sense, irreversible.

This is what it looks like when a system becomes capable of something it was not capable of before. Not a smoother fit to existing data, but a new kind of understanding: one that lives on the inside.
