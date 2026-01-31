# Constraint Accumulation and Force Collapse in Strongly Convex Gradient Flows  
*A Continuous‑Time Toy Model in the FIT Framework*

**Status**: draft working note (not peer reviewed)  
**Intended use**: FIT v3.x roadmap – continuous‑time / classical toy paper

---

## Abstract

The Force–Information–Time (FIT) framework proposes five primitives—State, Time, Force, Constraint, and Information—as a minimal vocabulary for describing evolutionary dynamics in dissipative or optimizing systems. The existing FIT specifications (v2.1, v2.3) focus on discrete‑time and simulation‑centric settings (cellular automata, simple algorithms) and include a one‑dimensional continuous‑time toy model in which an explicit scalar “constraint” variable accumulates monotonically while the squared force decays in exact proportion to the remaining distance to a constraint plateau. This paper develops a slightly more realistic continuous‑time toy model: deterministic gradient flows in $ \mathbb{R}^d $ with strongly convex potentials.

We embed the FIT primitives into this gradient‑flow setting by taking the state as $ X_t \in \mathbb{R}^d $, time as $ t \in \mathbb{R}_{\ge 0} $, force as the drift $ F(X_t) = -\nabla V(X_t) $, and an effective constraint functional $ C(t) $ as an affine reparameterization of the energy gap $ E(t) = V(X_t) - V(x^\star) $, where $ x^\star $ is the unique minimizer of $ V $. Under standard smoothness and strong convexity assumptions, we prove two simple theorems. First, $ C(t) $ is differentiable, non‑decreasing, and converges exponentially fast to a finite plateau $ C_\infty $, providing a continuous‑time realization of FIT’s “constraint accumulation” pattern. Second, the squared force magnitude $ \|F(t)\|^2 = \|\nabla V(X_t)\|^2 $ decays exponentially to zero and is linearly sandwiched between constants times the remaining constraint gap $ C_\infty - C(t) $.

These results show that in a nontrivial continuous‑time system—gradient descent in a strongly convex landscape—one can define a FIT‑style constraint functional that genuinely accumulates and a FIT‑style force magnitude that genuinely collapses, with a clean linear coupling between them. The model ignores noise, nonconvexity, and information‑theoretic subtleties, but it secures a small patch of ground where key FIT slogans become theorems rather than aspirations, and it clarifies what kinds of inequalities future continuous‑time (stochastic, nonconvex, quantum) versions of FIT would need to establish.

---

## 1 Introduction

Continuous‑time gradient systems are among the simplest settings in which questions about relaxation, attractors, and late‑time structure can be phrased as theorems rather than metaphors. At the same time, most discussions of evolutionary or learning dynamics across domains—physics, biology, optimization, social systems—rely on heterogeneous vocabularies: loss vs. fitness vs. free energy vs. incentives, constraints vs. rules vs. norms, and so on. The Force–Information–Time (FIT) framework was proposed as a minimal, falsifiable vocabulary for talking about such dynamics at an explicitly chosen level of description, with five primitives (State, Time, Force, Constraint, Information), six framework principles, and eighteen propositions, plus operational estimators and toy testbeds in Conway’s Game of Life and Langton’s Ant.

The core FIT documents (v2.1 and v2.3) are discrete‑time and simulation‑centric. They show how to define effective constraints and forces on cellular automata or simple algorithms, how to estimate “force variance” and “constraint accumulation” operationally, and how to phrase propositions such as “low‑force‑variance attractors” and “critical slowing down” in a way that can be falsified in code. They also include a one‑dimensional continuous‑time toy model in which an explicitly defined scalar constraint variable accumulates monotonically and the squared force decays in exact proportion to the remaining distance to a constraint plateau. That toy model is deliberately simple: it serves as a sanity check that the FIT pattern “constraint accumulation ⇒ force collapse” is not internally inconsistent. It does not yet connect FIT to the standard analytical machinery of dynamical systems and gradient flows in $ \mathbb{R}^d $.

This paper takes the next step. We restrict attention to deterministic gradient flows with strongly convex potentials and show that, even in this modest but nontrivial continuous‑time setting, a FIT‑style picture—constraints accumulating toward a plateau while force magnitudes collapse—can be made precise as a pair of theorems. In doing so, we provide a first “continuous‑time FIT” case study that sits between the existing discrete‑time specification and the more ambitious v3.0 roadmap involving stochastic differential equations and quantum extensions.

### 1.1 Motivation: from discrete FIT to continuous gradient flows

The v2.1 “Review & Validation Edition” of FIT was designed primarily for community critique and falsification on discrete computational systems. It supplies: (i) the five primitives with suggested estimators; (ii) a dependency chain of six principles distinguishing definitional statements from empirical hypotheses; (iii) a solvable one‑dimensional toy model where an effective constraint integral grows monotonically and the squared force decays linearly in its remaining gap; and (iv) eighteen propositions bundled with test protocols for cellular automata. This discrete emphasis is deliberate: one can simulate millions of steps, compute force and constraint estimators directly, and search aggressively for counterexamples.

However, the kinds of systems that motivated FIT are not only discrete automata. Thermodynamic relaxations, classical potential flows, optimization dynamics in high‑dimensional parameter spaces, and many mean‑field models of learning are more naturally written as ordinary or stochastic differential equations. In these settings, notions like force, information, and constraint already have continuous‑time counterparts (drift fields, entropy or free‑energy functionals, Lyapunov functions), and there is a rich analytical literature on convergence rates, spectral gaps, and gradient flows.

If FIT is to be more than a language for cellular automata and toy algorithms, it should (at minimum) demonstrate that its central qualitative pattern—roughly, “effective constraints build up while net drift variability dies out”—can be instantiated and proved in some continuous‑time systems that are already well understood on their own terms. Conversely, if it fails even in these benign settings, that is strong evidence that several of FIT’s late‑time claims (for example, its Cluster A “low‑force‑variance attractor” propositions) are too broad or too loosely formulated.

Gradient flows with strongly convex potentials are an obvious first candidate. They are simple enough that energy decay and exponential convergence to a unique minimizer are classical results, but flexible enough to represent many dissipative systems and optimization dynamics. By characterizing these flows in FIT terms—mapping State, Time, Force, Information, and Constraint into a standard gradient system—we can ask sharply: is there a natural continuous‑time constraint functional that accumulates monotonically, and how tightly can we tie the decay of force magnitude to the remaining gap in that constraint?

### 1.2 Relation to the FIT framework

The present work is intentionally narrow in scope. It does not attempt to restate or extend the full FIT axiomatization. Instead, it treats FIT as a background program and asks a focused technical question inside that program:

> In deterministic gradient flows on $ \mathbb{R}^d $ with a strongly convex potential $ V $, can we define a constraint functional $ C(t) $ and a force magnitude $ F(t) $ so that:
> 1. $ C(t) $ accumulates monotonically towards a finite plateau $ C_\infty $; and  
> 2. $ \|F(t)\|^2 $ decays in a controlled way that is linearly tied to $ C_\infty - C(t) $?

In the FIT vocabulary, State is $ S(t) = X_t \in \mathbb{R}^d $, Time is $ t \in \mathbb{R}_{\ge 0} $, and Force is the drift $ F(X_t) = -\nabla V(X_t) $. Information, in a deterministic gradient flow with a unique attractor, is less central than in stochastic or ensemble settings, but one can still think of the energy gap $ V(X_t) - V(x^\star) $ as a primitive Lyapunov‑type functional encoding distinguishable structure: as the gap shrinks, the set of states compatible with a given energy band collapses. Constraint can then be defined from this gap—for example as a linearly rescaled complement $ C(t) = C_{\max} - (V(X_t) - V(x^\star)) $—or, more generally, via an appropriate Lyapunov functional.

The one‑dimensional continuous‑time toy model in FIT v2.1 essentially implements this pattern: it takes a scalar force $ F(t) $ obeying a linear relaxation ODE and defines a scalar constraint $ C(t) $ via the integral of $ F(t)^2 $, yielding a closed‑form relation $ F(t)^2 \propto C_\infty - C(t) $. The present paper can be seen as a higher‑dimensional and more conventional continuous‑time analogue in which the dynamics are those of a gradient flow $ \dot X_t = -\nabla V(X_t) $, the constraint functional is derived from the energy gap $ V(X_t) - V(x^\star) $, and the force magnitude is $ \|\nabla V(X_t)\|^2 $.

Within the broader FIT program, the theorems proved here contribute to two specific pieces:

* They provide a concrete continuous‑time realization of the late‑time constraint and force patterns associated with what FIT calls low‑force‑variance attractors or “nirvana states” in a nontrivial $ d $‑dimensional system, strengthening the case that the v2.x toy derivations are not artifacts of one‑dimensional linearity.  
* They offer a template for how future v3.x work might proceed in more difficult settings (stochastic Langevin dynamics, Markov semigroups, and eventually Lindbladian quantum systems): pick a well‑studied class, map FIT primitives onto standard objects, and prove one or two flagship theorems that explicitly realize constraint accumulation and force collapse in that class.

At the same time, the limitations of our setting—strong convexity, determinism, a single unique minimizer, and an essentially scalar notion of constraint—underscore that FIT cannot yet claim continuous‑time universality. In multiwell potentials, nonconvex landscapes, or noisy dynamics, constraint functionals become more subtle and the force need not vanish pointwise even at stationarity. We treat those cases as future work.

### 1.3 Contributions of this paper

Concretely, this paper makes three contributions, all within the narrowly defined class of deterministic gradient flows with strongly convex potentials:

1. **Continuous‑time embedding of FIT primitives.**  
   We give an explicit mapping from the FIT primitives to the gradient‑flow setting. State is $ X_t \in \mathbb{R}^d $, Time is $ t \in \mathbb{R}_{\ge 0} $, Force is the drift $ F(X_t) = -\nabla V(X_t) $, and we take Constraint to be a simple Lyapunov‑based functional of the form

   $$
   C(t) := C_{\max} - \bigl(V(X_t) - V(x^\star)\bigr),
   $$

   where $ x^\star $ is the unique minimizer of $ V $. This makes $ C(t) $ large when the system is energetically pinned near $ x^\star $ and small when it is energetically far away, aligning with the FIT interpretation of constraint as effective restriction of accessible states.

2. **Theorem 1: constraint accumulation with exponential convergence.**  
   Under standard smoothness and strong convexity assumptions on $ V $, we show that the energy gap $ E(t) := V(X_t) - V(x^\star) $ decays exponentially, and hence the constraint functional $ C(t) $ is differentiable, monotone increasing, and converges exponentially fast to a finite plateau $ C_\infty = C_{\max} $. In particular,

   $$
   \frac{d}{dt} C(t) = \|\nabla V(X_t)\|^2 \ge 0,
   $$

   and $ C_\infty - C(t) = E(t) \le E(0) e^{-2\lambda t} $ for some $ \lambda > 0 $. This gives a rigorous continuous‑time version of the statement “effective constraints accumulate towards a plateau as the system relaxes.”

3. **Theorem 2: force collapse tied to the constraint gap.**  
   We define the instantaneous force magnitude as $ \|F(t)\|^2 = \|\nabla V(X_t)\|^2 $ and show that, in the same setting, it both decays exponentially in time and is linearly sandwiched by the remaining constraint gap:

   $$
   2\lambda\bigl(C_\infty - C(t)\bigr) \;\le\; \|F(t)\|^2 \;\le\; 2L\bigl(C_\infty - C(t)\bigr),
   $$

   where $ \lambda $ and $ L $ are the strong convexity and smoothness constants of $ V $. Thus force collapse is not only qualitatively true (force goes to zero as the system converges) but quantitatively locked to the distance from the constraint plateau. In the one‑dimensional linear toy model of FIT v2.1, this relation appears as an exact equality; here it appears as two‑sided linear bounds with constants determined by the curvature of $ V $.

Taken together, these results show that in a nontrivial continuous‑time system—gradient descent in a strongly convex landscape—one can define a FIT‑style constraint functional that genuinely accumulates and a FIT‑style force magnitude that genuinely collapses, with a clean linear coupling between them. This does not prove any of the general FIT propositions in full generality, but it does supply a mathematically standard example where the FIT pattern is realized exactly, providing both reassurance that the pattern is not internally contradictory and a concrete anchor for future generalizations.

### 1.4 Scope, limitations, and paper organization

The scope of this paper is intentionally modest. We remain entirely within deterministic, strongly convex gradient flows in finite dimensions. We do not treat multiwell landscapes, nonconvex objectives, or stochastic forcing; we do not attempt to define or compute information functionals $ I(t) $ in the sense of entropy or mutual information; and we do not attempt to extend T‑theory (FIT’s subframework for tail dynamics and perturbation recovery) beyond a brief discussion. These omissions are by design. Our aim is to secure one small but clean patch of ground—a continuous‑time toy model with real theorems—before attempting to climb the more technically demanding hills outlined in the FIT v3 roadmap (SDEs, Markov semigroups, open quantum systems).

The paper is organized as follows. Section 2 defines the gradient‑flow model class and explains how the five FIT primitives are instantiated in this setting, including the choice of constraint functional and force magnitude. Section 3 states and sketches proofs for the two main results: a constraint accumulation theorem and a force‑collapse theorem, together with explicit inequalities connecting $ C(t) $ and $ \|F(t)\|^2 $. Section 4 discusses how these results map back onto FIT’s informal claims about constraint accumulation and low‑force‑variance attractors, highlights the limitations of our setting, and outlines how similar arguments might be adapted to noisy Langevin dynamics and more complex landscapes. Appendix A collects technical details and proof steps that are standard in the gradient‑flow literature but would otherwise interrupt the main line of argument.

---

## 2 Setup: Gradient Flows as a Continuous‑Time FIT Toy Model

In this section we fix the dynamical setting, specify the regularity assumptions on the potential function, and define the particular FIT primitives and observables that will be used in our two main results. The goal is not to propose the most general possible continuous‑time formulation of FIT, but to choose a simple, standard model class in which all quantities are unambiguous and existing gradient‑flow theory can be reused with minimal overhead.

### 2.1 Model class: deterministic gradient flow on $ \mathbb{R}^d $

We work throughout with a deterministic gradient flow in finite dimensions. Let

* the **state space** be $ \mathbb{R}^d $ with its usual Euclidean structure, and  
* the **state trajectory** be a differentiable map $ t \mapsto X_t \in \mathbb{R}^d $ for $ t \ge 0 $.

The dynamics are given by the ordinary differential equation

$$
\frac{dX_t}{dt} = -\nabla V(X_t), \qquad t \ge 0,
$$

where $ V : \mathbb{R}^d \to \mathbb{R} $ is a potential function satisfying the following standing assumptions.

**Assumption A1 (smoothness and strong convexity).**  
The potential $ V $ is twice continuously differentiable, and there exist constants $ 0 < \lambda \le L < \infty $ such that for all $ x, y \in \mathbb{R}^d $,

* **strong convexity**

  $$
  V(x) \;\ge\; V(y) + \langle \nabla V(y), x - y \rangle + \frac{\lambda}{2} \, \|x - y\|^2,
  $$

* **Lipschitz gradient**

  $$
  \|\nabla V(x) - \nabla V(y)\| \;\le\; L \, \|x - y\|.
  $$

These are the standard assumptions for strongly convex, smooth optimization landscapes and ensure that:

1. there exists a unique minimizer $ x^\star \in \mathbb{R}^d $ with $ \nabla V(x^\star) = 0 $;  
2. for every initial condition $ X_0 \in \mathbb{R}^d $, the ODE has a unique global solution $ X_t $ for all $ t \ge 0 $;  
3. the trajectory converges to $ x^\star $ as $ t \to \infty $, with an exponential convergence rate in both state and energy gap.

We will not re‑prove the full convergence theory here; instead we will use the standard consequences of Assumption A1 as given facts and focus on their interpretation in FIT terms.

For later use we define the **energy gap** (or suboptimality) at time $ t $:

$$
E(t) := V(X_t) - V(x^\star) \;\ge\; 0.
$$

By construction $ E(t) $ measures how far the system is, in potential energy, from its unique equilibrium point $ x^\star $.

### 2.2 Equilibrium, late‑time behavior, and “nirvana”

In the conventional gradient‑flow literature, the equilibrium of the system is the minimizer $ x^\star $ of $ V $, and relaxation means $ X_t \to x^\star $ and $ E(t) \to 0 $ as $ t \to \infty $. Under Assumption A1, one can show that

$$
E(t) \;\le\; E(0) \, e^{-2\lambda t},
$$

i.e., the energy gap decays exponentially.

In the FIT vocabulary, the late‑time regime of interest is not merely “near the minimizer” but specifically the regime where:

* the **effective constraints** $ C(t) $ are close to a plateau $ C_\infty $, and  
* the **net drift** or **force magnitude** $ \|F(t)\| $ is small and exhibits low variability across time and across realizations.

This regime is what FIT refers to as a low‑force‑variance attractor or “nirvana state.” In a deterministic gradient flow with a unique minimizer and no noise, the natural candidate for such a state is simply the fixed point $ X_t \equiv x^\star $. Our goal is to choose:

* a constraint functional $ C(t) $ that monotonically approaches a finite plateau as $ X_t $ relaxes to $ x^\star $; and  
* a force magnitude $ \|F(t)\|^2 $ that both decays to zero and is linearly tied to how far $ C(t) $ is from its plateau.

The next subsection makes this mapping precise.

### 2.3 Embedding the FIT primitives

We now spell out how the five FIT primitives are instantiated in this toy model. The starting point is the discrete‑time specification in FIT v2.1/v2.3, where a generalized force is defined as a drift term $ \mathbb{E}[S_{t+1} - S_t \mid S_t] = \alpha F(S_t, t) $, constraints are effective restrictions on accessible state variability, and information is a scalar functional quantifying distinguishability or uncertainty.

In the present continuous‑time gradient‑flow setting we take:

* **State**

  $$
  S(t) := X_t \in \mathbb{R}^d.
  $$

  The state at time $ t $ is the position of the system in $ \mathbb{R}^d $.

* **Time**

  $$
  T := t \in \mathbb{R}_{\ge 0}.
  $$

  Time is a continuous, non‑negative index; all processes we consider are forward‑in‑time gradient flows starting from $ t = 0 $.

* **Force (generalized drift)**

  $$
  F(X_t) := -\nabla V(X_t).
  $$

  This is the deterministic drift in the ODE and plays exactly the role of force in the discrete FIT definition, with $ \dot X_t = F(X_t) $.

* **Information**

  In this deterministic single‑trajectory setting there is no nontrivial distribution over states unless we introduce randomness in the initial condition. For the purposes of this paper, information will therefore remain in the background. One can regard the energy gap $ E(t) $ as a proxy for distinguishable structure (it bounds the set of states compatible with a given energy level), or, in an ensemble picture, one could define an information functional based on the distribution of $ X_t $ across initial seeds. However, our main results do not depend on an explicit choice of $ I(t) $, and we will postpone detailed information‑theoretic definitions to future stochastic extensions.

* **Constraint (effective restriction)**

  We will define a scalar constraint functional $ C(t) $ derived from the energy gap $ E(t) $, chosen so that:

  1. $ C(t) $ is non‑decreasing in $ t $;  
  2. $ C(t) $ converges to a finite upper bound $ C_\infty $;  
  3. the difference $ C_\infty - C(t) $ is proportional to $ E(t) $; and  
  4. the squared force magnitude $ \|F(t)\|^2 $ can be bounded above and below by constants times $ C_\infty - C(t) $.

  These properties will make the relationship between constraint accumulation and force collapse transparent and will directly parallel the one‑dimensional toy model in FIT v2.1, where an explicit integral definition of $ C(t) $ yields an exact algebraic relation to $ F(t)^2 $.

The next subsection introduces the specific choice of $ C(t) $ we will use.

### 2.4 Constraint functional from the energy gap

Intuitively, in a strongly convex potential, being more constrained corresponds to being energetically closer to the unique minimizer: the lower the energy gap, the smaller the region of state space compatible with the current energy. This suggests defining constraint as a monotone transform of the energy gap.

We fix the initial energy gap

$$
E(0) := V(X_0) - V(x^\star),
$$

and define the **constraint functional** as

$$
C(t) := C_{\max} - E(t),
$$

where $ C_{\max} $ is a constant chosen so that $ C(0) = 0 $. A convenient choice is

$$
C_{\max} := E(0),
$$

which yields

$$
C(t) = E(0) - E(t).
$$

With this definition:

* at $ t = 0 $, $ C(0) = E(0) - E(0) = 0 $;  
* as $ t \to \infty $, $ E(t) \to 0 $ and thus

  $$
  C(t) \to C_\infty := E(0);
  $$

* the **constraint gap** (distance to plateau) is exactly the energy gap:

  $$
  C_\infty - C(t) = E(t).
  $$

This choice makes $ C(t) $ a simple affine reparameterization of $ E(t) $. The FIT interpretation is that as the system relaxes, more and more of the initial freedom encoded in $ E(0) $ is converted into effective constraints; once $ C(t) $ reaches $ C_\infty $, no energy gap remains and the system is fully pinned at the minimizer. Although this is a stylized notion of constraint, it matches the spirit of the one‑dimensional FIT toy model and is sufficient for our purposes: all of our results can be rephrased directly in terms of $ E(t) $ if one prefers to avoid the additional layer of vocabulary.

### 2.5 Force magnitude as a variance proxy

In the discrete FIT specification, propositions about low‑force‑variance attractors are phrased in terms of the variance of a generalized force across either time or an ensemble of trajectories. In the deterministic gradient‑flow toy model considered here, there is only a single trajectory and no randomness. Thus there is no nontrivial statistical variance; instead, the natural late‑time quantity of interest is the **squared force magnitude along the trajectory**:

$$
\Phi_F(t) := \|F(t)\|^2 = \|\nabla V(X_t)\|^2.
$$

This plays the role of a variance proxy: in a noisy or ensemble formulation, $ \mathbb{E}[\|F(X_t)\|^2] $ would be the second moment of the force, and its decay would correspond to force‑variance collapse. Here we simply track $ \Phi_F(t) $ as a scalar observable that must go to zero as the system converges to equilibrium.

Under Assumption A1, standard inequalities from convex optimization relate $ \Phi_F(t) $ to the energy gap $ E(t) $. In particular, strong convexity and smoothness imply the two‑sided bounds

$$
2\lambda \, E(t) \;\le\; \|\nabla V(X_t)\|^2 \;\le\; 2L \, E(t)
\qquad \text{for all } t \ge 0.
$$

Combined with the identity $ E(t) = C_\infty - C(t) $, this yields

$$
2\lambda\bigl(C_\infty - C(t)\bigr)
\;\le\;
\Phi_F(t)
\;\le\;
2L\bigl(C_\infty - C(t)\bigr),
$$

exhibiting a linear sandwiching of the force magnitude by the constraint gap. This relationship is the continuous‑time, multi‑dimensional analogue of the exact proportionality $ F(t)^2 \propto C_\infty - C(t) $ in the one‑dimensional toy model of FIT v2.1. The formal statement and proof sketch of this bound will appear as part of Theorem 2 in Section 3.

### 2.6 Summary of assumptions and objects

For clarity, we summarize the objects and assumptions that will be used in the rest of the paper.

* **State trajectory**

  $$
  X_t \in \mathbb{R}^d, \qquad t \ge 0,
  $$

  evolving according to the gradient flow

  $$
  \dot X_t = -\nabla V(X_t).
  $$

* **Potential**

  $ V : \mathbb{R}^d \to \mathbb{R} $ is twice continuously differentiable, $ \lambda $‑strongly convex, and has $ L $‑Lipschitz gradient.

* **Equilibrium**

  Unique minimizer $ x^\star $ with $ \nabla V(x^\star) = 0 $.

* **Energy gap**

  $$
  E(t) := V(X_t) - V(x^\star) \ge 0.
  $$

* **Force**

  $$
  F(t) := -\nabla V(X_t), \qquad \Phi_F(t) := \|F(t)\|^2.
  $$

* **Constraint**

  $$
  C(t) := E(0) - E(t), \qquad C_\infty := E(0),
  $$

  so that $ C_\infty - C(t) = E(t) $.

Under these definitions, the qualitative FIT claims we aim to realize can be phrased as:

1. **Constraint accumulation**: $ C(t) $ increases monotonically and converges exponentially to $ C_\infty $.  
2. **Force collapse**: $ \Phi_F(t) $ decays exponentially to zero and is linearly tied to the remaining constraint gap $ C_\infty - C(t) $.

Section 3 will state these properties as Theorem 1 and Theorem 2 and provide proof sketches based on standard gradient‑flow inequalities.

---

## 3 Main Results

We now state and sketch proofs of the two main results. Both are formulated in the deterministic gradient‑flow setting of Section 2 under Assumption A1. The first theorem shows that the constraint functional defined from the energy gap accumulates monotonically and converges exponentially to a finite plateau. The second theorem shows that the squared force magnitude decays exponentially and is linearly tied to the remaining constraint gap. Taken together, these establish a continuous‑time realization of the “constraint accumulation ⇒ force collapse” pattern highlighted in the FIT toy model.

Throughout this section we use the notation introduced in Section 2: the state trajectory satisfies

$$
\dot X_t = -\nabla V(X_t),
$$

with unique minimizer $ x^\star $, energy gap

$$
E(t) := V(X_t) - V(x^\star),
$$

constraint functional

$$
C(t) := E(0) - E(t),
\qquad
C_\infty := E(0),
$$

so that $ C_\infty - C(t) = E(t) $, and force

$$
F(t) := -\nabla V(X_t),
\qquad
\Phi_F(t) := \|F(t)\|^2 = \|\nabla V(X_t)\|^2.
$$

### 3.1 Theorem 1: constraint accumulation and exponential convergence

#### 3.1.1 Statement

Informally, Theorem 1 states that in a strongly convex potential, the chosen constraint functional $ C(t) $ accumulates monotonically and converges exponentially fast to its plateau $ C_\infty $. Equivalently, the energy gap $ E(t) $ decays exponentially. This is the continuous‑time analogue of effective constraint accumulation in the one‑dimensional FIT toy model.

We first record a standard inequality from convex optimization.

**Lemma 1 (Gradient–suboptimality bounds).**  
Under Assumption A1, for all $ x \in \mathbb{R}^d $,

$$
2\lambda \bigl(V(x) - V(x^\star)\bigr)
\;\le\;
\|\nabla V(x)\|^2
\;\le\;
2L \bigl(V(x) - V(x^\star)\bigr),
$$

where $ \lambda > 0 $ is the strong convexity parameter and $ L \ge \lambda $ is the gradient Lipschitz constant.

The proof is standard and follows from the combination of strong convexity and smoothness; we use it as a black box.

We can now state the main result of this subsection.

**Theorem 1 (Constraint accumulation in gradient flows).**  
Let $ X_t $ evolve according to

$$
\dot X_t = -\nabla V(X_t),
$$

with $ V $ satisfying Assumption A1 and constraint functional $ C(t) $ defined as above. Then:

1. $ C(t) $ is differentiable and non‑decreasing in $ t $, with

   $$
   \frac{d}{dt} C(t)
   = \|\nabla V(X_t)\|^2
   \;\ge\; 0
   \quad \text{for all } t \ge 0;
   $$

2. $ C(t) $ converges exponentially fast to its plateau $ C_\infty = E(0) $, and the constraint gap obeys

   $$
   C_\infty - C(t) = E(t) \;\le\; E(0) \, e^{-2\lambda t}
   \quad \text{for all } t \ge 0.
   $$

In particular, constraint accumulation is not only monotone but also exponentially fast in this toy setting.

#### 3.1.2 Proof sketch

The proof uses only the chain rule and Lemma 1.

**Step 1: differentiate the energy along the flow.**  
By the chain rule,

$$
\frac{d}{dt} E(t)
= \frac{d}{dt} \bigl(V(X_t) - V(x^\star)\bigr)
= \langle \nabla V(X_t), \dot X_t \rangle.
$$

Substituting $ \dot X_t = -\nabla V(X_t) $ yields

$$
\frac{d}{dt} E(t)
= -\|\nabla V(X_t)\|^2
\;\le\; 0.
$$

Thus $ E(t) $ is non‑increasing in $ t $.

By definition $ C(t) = E(0) - E(t) $, so

$$
\frac{d}{dt} C(t)
= -\frac{d}{dt} E(t)
= \|\nabla V(X_t)\|^2
\;\ge\; 0,
$$

showing that $ C(t) $ is non‑decreasing and proving the first part of the theorem.

**Step 2: use strong convexity to obtain an exponential rate.**  
From Lemma 1, for every $ t \ge 0 $,

$$
\|\nabla V(X_t)\|^2
\;\ge\;
2\lambda \bigl(V(X_t) - V(x^\star)\bigr)
= 2\lambda E(t).
$$

Combining this with the energy derivative,

$$
\frac{d}{dt} E(t)
= -\|\nabla V(X_t)\|^2
\;\le\;
-2\lambda E(t).
$$

This scalar differential inequality can be solved using Grönwall’s lemma, giving

$$
E(t) \;\le\; E(0) \, e^{-2\lambda t}.
$$

Recalling $ C_\infty - C(t) = E(t) $, we obtain

$$
C_\infty - C(t)
\;\le\;
E(0) \, e^{-2\lambda t},
$$

i.e., $ C(t) $ converges exponentially fast to $ C_\infty $. This completes the proof sketch.

∎

From the FIT perspective, Theorem 1 shows that in this gradient‑flow toy model one can define a constraint functional that behaves exactly as the framework informally requires: it is monotone in late time and approaches a finite plateau, rather than diverging unboundedly.

---

### 3.2 Theorem 2: force collapse and linear coupling to the constraint gap

#### 3.2.1 Statement

The second result concerns the decay of the squared force magnitude

$$
\Phi_F(t) := \|F(t)\|^2 = \|\nabla V(X_t)\|^2,
$$

and its relationship to the remaining constraint gap $ C_\infty - C(t) = E(t) $. Informally, Theorem 2 states that in the same gradient‑flow setting, the force magnitude collapses exponentially to zero and is linearly bounded above and below by the constraint gap. This mirrors the exact proportionality $ F(t)^2 \propto C_\infty - C(t) $ in the one‑dimensional FIT toy ODE, but with dimension‑ and potential‑dependent constants.

**Theorem 2 (Force collapse and linear coupling to constraint gap).**  
Under the same assumptions and definitions as Theorem 1:

1. The squared force magnitude decays exponentially,

   $$
   \Phi_F(t) = \|\nabla V(X_t)\|^2
   \;\le\;
   2L \, E(0) \, e^{-2\lambda t}
   \quad \text{for all } t \ge 0;
   $$

2. For all $ t \ge 0 $, the force magnitude is linearly sandwiched by the constraint gap,

   $$
   2\lambda \bigl(C_\infty - C(t)\bigr)
   \;\le\;
   \Phi_F(t)
   \;\le\;
   2L \bigl(C_\infty - C(t)\bigr),
   $$

   where $ \lambda $ and $ L $ are the strong convexity and smoothness constants of $ V $, and $ C_\infty - C(t) = E(t) $.

In particular, as constraints approach their plateau ( $ C(t) \to C_\infty $ ), the force magnitude collapses to zero in such a way that $ \Phi_F(t) $ and $ C_\infty - C(t) $ are proportional up to universal constants determined by the curvature of $ V $.

#### 3.2.2 Proof sketch

Again the argument relies only on Lemma 1 and the energy decay from Theorem 1.

**Step 1: exponential collapse of force magnitude.**  
From the upper bound in Lemma 1 we have, for all $ t \ge 0 $,

$$
\|\nabla V(X_t)\|^2
\;\le\;
2L \bigl(V(X_t) - V(x^\star)\bigr)
= 2L \, E(t).
$$

Combining this with the exponential decay of $ E(t) $ from Theorem 1 yields

$$
\Phi_F(t)
= \|\nabla V(X_t)\|^2
\;\le\;
2L \, E(t)
\;\le\;
2L \, E(0) \, e^{-2\lambda t},
$$

which shows that the squared force magnitude decays at least as fast as $ e^{-2\lambda t} $, establishing the first claim.

**Step 2: linear sandwiching by the constraint gap.**  
Using the two‑sided bounds from Lemma 1,

$$
2\lambda E(t)
\;\le\;
\|\nabla V(X_t)\|^2
\;\le\;
2L E(t),
$$

and substituting $ E(t) = C_\infty - C(t) $, we obtain, for all $ t \ge 0 $,

$$
2\lambda \bigl(C_\infty - C(t)\bigr)
\;\le\;
\Phi_F(t)
\;\le\;
2L \bigl(C_\infty - C(t)\bigr).
$$

This shows that the squared force magnitude is trapped between two straight lines as a function of the constraint gap, with slopes $ 2\lambda $ and $ 2L $. In particular, near equilibrium we have

$$
\Phi_F(t) \asymp C_\infty - C(t),
$$

in the sense that both go to zero at comparable rates up to fixed multiplicative constants, completing the proof sketch.

∎

From the FIT point of view, Theorem 2 realizes a central desideratum: as constraints accumulate and approach their plateau, the force magnitude does not merely happen to shrink—it is quantitatively tied to the remaining gap in constraints. In the one‑dimensional FIT toy model this relationship is an exact identity; here it appears as a two‑sided inequality controlled by the geometry of the potential $ V $.

---

### 3.3 Comparison with the one‑dimensional FIT toy model

The original FIT v2.1/v2.3 documents include a one‑dimensional continuous‑time toy model in which the state $ x(t) $ relaxes linearly toward a fixed point $ x^\star $, the force is defined as $ F(t) = x(t) - x^\star $, and an effective constraint variable $ C(t) $ is defined as an integral of $ F(t)^2 $. Solving the ODE yields a closed‑form relationship of the form

$$
F(t)^2 = \kappa \bigl(C_\infty - C(t)\bigr)
$$

for a system‑dependent constant $ \kappa > 0 $, so that the squared force is exactly proportional to the remaining constraint gap.

The gradient‑flow toy model analyzed here differs in three ways:

1. **Dimensionality and geometry.**  
   We work in $ \mathbb{R}^d $ with potentially complex level sets of $ V $, rather than in a one‑dimensional scalar system. This introduces directional structure and allows for anisotropic curvature, captured by the parameters $ \lambda $ and $ L $.

2. **Constraint definition.**  
   Instead of defining $ C(t) $ as an integral of $ F(t)^2 $ along the trajectory, we define it as an affine reparameterization of the energy gap $ E(t) $. This matches the intuition that being more constrained means being energetically closer to the unique minimizer $ x^\star $ in a strongly convex potential.

3. **Nature of the coupling.**  
   The relationship between force magnitude and constraint gap is no longer an exact scalar identity, but a pair of linear inequalities

   $$
   2\lambda\bigl(C_\infty - C(t)\bigr)
   \;\le\;
   \|F(t)\|^2
   \;\le\;
   2L\bigl(C_\infty - C(t)\bigr),
   $$

   with constants determined by the curvature of $ V $. In other words, $ \|F(t)\|^2 $ and $ C_\infty - C(t) $ are proportional up to multiplicative constants, rather than exactly equal.

Despite these differences, the qualitative FIT pattern is the same:

* there exists a scalar constraint functional $ C(t) $ that is non‑decreasing in time and converges to a plateau;  
* the squared force magnitude $ \|F(t)\|^2 $ decays to zero and is tightly coupled to the remaining distance $ C_\infty - C(t) $;  
* both quantities exhibit exponential convergence in this toy setting.

Thus the continuous‑time gradient‑flow model supports FIT’s claim that constraint accumulation and force collapse is not an artifact of one‑dimensional linearity, but a structural feature of a well‑studied class of dissipative systems.

---

## 4 Discussion and Outlook

We close by interpreting Theorems 1–2 in FIT terms, highlighting what they do and do not establish for the broader framework, and outlining the most natural directions for extension: stochastic Langevin dynamics, T‑theory for continuous time, and quantum analogues. We also discuss limitations of the present toy model and how those limitations inform the design of future v3.x work.

### 4.1 What Theorems 1–2 buy for the FIT program

The FIT framework proposes a family of late‑time patterns for low‑force‑variance attractors or nirvana states. Informally, these patterns can be summarized as:

1. Effective constraints accumulate over time and approach a plateau in many stationary, dissipative, or optimizing regimes.  
2. As this plateau is approached, the variance of generalized forces collapses, so that the system’s dynamics become increasingly quiescent.  
3. Near such attractors, information and constraints exhibit characteristic scaling relations and often coexist with phase‑transition signatures.

The continuous‑time gradient‑flow toy model analyzed here does not address all of these patterns, but it does elevate two of them from conjectural status to theorems in a specific, well‑understood dynamical class:

* **Constraint accumulation.**  
  Theorem 1 shows that in a strongly convex gradient flow, one can define a scalar constraint functional $ C(t) $ via an affine reparameterization of the energy gap such that $ C(t) $ is non‑decreasing and converges exponentially to a plateau $ C_\infty $. This directly realizes the late‑time “constraint non‑decrease” behavior that FIT informally expects in many dissipative regimes, at least in this narrow class.

* **Force collapse.**  
  Theorem 2 shows that the squared force magnitude $ \Phi_F(t) = \|\nabla V(X_t)\|^2 $ decays exponentially and is linearly sandwiched by the constraint gap $ C_\infty - C(t) $. This provides a precise version of force‑variance collapse near nirvana: as effective constraints saturate, the drift field vanishes in norm in a way tightly coupled to the remaining constraint gap.

In the discrete v2.1/v2.3 toy model, an explicitly defined constraint integral yields an exact identity

$$
F(t)^2 = \kappa\bigl(C_\infty - C(t)\bigr),
$$

which is used to illustrate the internal consistency of the slogan “constraint accumulation ⇒ force‑variance collapse.” The results here show that in a more conventional continuous‑time, $ d $‑dimensional setting, one can recover the same qualitative pattern, now backed by standard convex‑analysis inequalities rather than a hand‑designed scalar ODE. The relationship is no longer an exact equality but a two‑sided bound

$$
2\lambda\bigl(C_\infty - C(t)\bigr)
\;\le\;
\|F(t)\|^2
\;\le\;
2L\bigl(C_\infty - C(t)\bigr)
$$

with constants determined by the curvature of $ V $. This is exactly the right kind of dependence: the geometry of the landscape controls how tightly force magnitude is pinned to the distance from the constraint plateau.

Within a FIT proposition registry, one natural way to register these results is:

* mark a constraint accumulation proposition as **“Theorem (continuous, deterministic, strongly convex gradient flows)”** under a continuous‑time classical column, while leaving it as “Hypothesis / Empirical” in other columns (e.g., noisy, nonconvex, discrete rule‑based systems);  
* mark a force‑variance decay proposition as **“Theorem (continuous, deterministic, strongly convex gradient flows)”** with explicit exponential decay and linear coupling to $ C_\infty - C(t) $ in this class, again leaving other classes open.

### 4.2 Limitations of the gradient‑flow toy model

The simplicity and analytical tractability of the present model come at a cost. Several important aspects of FIT’s intended scope are deliberately set aside.

**Determinism and absence of noise.**  
We work with a purely deterministic ODE $ \dot X_t = -\nabla V(X_t) $. Many systems of interest to FIT—thermodynamic relaxations, stochastic learning processes, ecological dynamics—are better modeled by stochastic differential equations, Markov processes, or other noisy dynamics, where fluctuations persist even at stationarity. In such systems one should not expect the drift or force to vanish pointwise; instead, one needs to work with variance or Dirichlet‑form‑like functionals over distributions. The deterministic toy model ignores this entire layer.

**Strong convexity and unique minimizer.**  
Assumption A1 requires $ V $ to be strongly convex with a single minimizer $ x^\star $. This excludes:

* multiwell landscapes and multi‑attractor structures, which are central to FIT’s multi‑nirvana and basin‑of‑attraction propositions;  
* nonconvex optimization landscapes with saddle points and flat directions, which are common in modern machine learning;  
* critical phenomena associated with bifurcations or qualitative changes in the set of attractors.

In other words, the model is tailored to a regime with a single, globally stable nirvana, and it cannot express the richer attractor geometries that motivate much of FIT’s T‑theory.

**Constraint definition via energy only.**  
We defined constraint as an affine function of the energy gap,

$$
C(t) = E(0) - E(t),
$$

so that $ C_\infty - C(t) = E(t) $. This is mathematically convenient and captures one intuitive sense in which the system becomes more constrained as it approaches the minimum of $ V $, but it is not the only or necessarily the most physically meaningful choice. In the broader FIT program, constraints are operationally defined in terms of reduced variability, intrinsic dimension, frozen fractions, or compression of trajectory windows. The energy‑based $ C(t) $ used here is a stylized proxy; showing that it correlates well with those more operational estimators in interesting systems remains an open task.

**Information left implicit.**  
Although information is one of the five FIT primitives, and the v2.1/v2.3 documents emphasize information–constraint tradeoffs (Cluster B propositions), the current paper does not define or use an explicit information functional $ I(t) $. In principle, one could define $ I(t) $ via an ensemble of initial conditions (for example, entropy of $ X_t $ over random seeds) or via functionals of $ X_t $ relative to the minimizer. For the deterministic single‑trajectory toy model, however, that machinery would add complexity without changing the main results about $ C(t) $ and $ \|F(t)\|^2 $. We therefore leave information‑theoretic extensions to future work.

These limitations are not defects so much as scope choices: the goal of this paper is to secure one small patch of ground where FIT‑style claims become theorems, not to pretend that this patch already covers the landscape that FIT cares about.

### 4.3 Towards stochastic and ensemble versions: Langevin and Markov semigroups

The obvious next step beyond deterministic gradient flows is to re‑introduce noise, either via Brownian motion (overdamped Langevin dynamics) or more general Markov generators. In that setting, the natural objects are:

* the law $ \mu_t $ of the process $ X_t $;  
* a stationary or equilibrium distribution $ \mu_\infty $ (when it exists);  
* functionals such as relative entropy $ D(\mu_t \Vert \mu_\infty) $ and Fisher information or Dirichlet forms;  
* spectral gaps or log‑Sobolev constants controlling rates of convergence.

Overdamped Langevin dynamics can be written as

$$
dX_t = -\nabla V(X_t)\,dt + \sqrt{2\beta^{-1}}\,dW_t,
$$

with Gibbs equilibrium $ \mu_\infty \propto e^{-\beta V} $. For such systems, classical results show that, under appropriate convexity and regularity assumptions, the free energy or relative entropy

$$
I(t) := D(\mu_t \Vert \mu_\infty)
$$

is a Lyapunov functional satisfying an entropy‑dissipation relation

$$
\frac{d}{dt} I(t) = -\mathcal{I}(\mu_t) \le -2\kappa\,I(t),
$$

where $ \mathcal{I} $ is a Fisher‑information‑type functional and $ \kappa > 0 $ is a spectral‑gap or log‑Sobolev constant. This yields exponential decay $ I(t) \le I(0) e^{-2\kappa t} $, which naturally suggests defining a constraint functional

$$
C_{\mathrm{rel}}(t) := C_{\max} - I(t)
$$

that accumulates monotonically. In other words, the same pattern “Lyapunov functional decreases ⇒ corresponding constraint increases” reappears, but now at the level of distributions on state space rather than single trajectories.

From a FIT perspective, the stochastic setting is attractive because it allows:

* a genuinely distributional definition of information $ I(t) $;  
* a probabilistic notion of force variance based on variance of the generator or drift with respect to $ \mu_t $;  
* a clean interface to T‑theory in terms of hitting times and quasi‑stationary distributions.

However, making the analogue of Theorem 2 precise in this setting—relating a force‑like functional to the gap $ C_\infty - C(t) $ in a clean inequality—requires more substantial functional‑analytic machinery. It would likely proceed via:

1. bounding force‑related quadratic forms in terms of entropy or $ L^2 $ distances to equilibrium;  
2. using differential inequalities for $ I(t) $ to control those forms;  
3. showing that the resulting bounds can be rewritten in terms of an appropriately defined $ C(t) $.

The present deterministic results should be understood as a “zeroth‑order” rehearsal for that more technical work: they demonstrate the pattern in the simplest setting and clarify which inequalities one should aim to prove in the noisy case.

### 4.4 Continuous‑time T‑theory: nirvana basins and recovery

T‑theory, introduced in later FIT drafts, is a subframework focused on tail dynamics: how systems behave near the edges of their attractors, how they respond to perturbations, and how recovery times and exit probabilities scale with constraint levels. Although this paper does not develop T‑theory in detail, it is useful to sketch how the gradient‑flow toy model could support a continuous‑time T‑theory.

In the deterministic setting considered here, the basin of nirvana is simply the basin of attraction of the unique minimizer $ x^\star $, and the recovery time from a perturbation is the time it takes $ X_t $ to return to a small neighborhood of $ x^\star $ after being displaced. Under strong convexity, these recovery times are uniformly bounded and decay exponentially with the size of the neighborhood, so there is little interesting T‑theoretic structure.

In stochastic or multiwell settings, however, the picture becomes richer. One can define:

* a **nirvana region** $ \mathcal{N}_\varepsilon := \{ x : \Phi_F(x) < \varepsilon,\, C(x) > C_\ast \} $ where both force magnitude and constraint gap are small;  
* **exit times** $ \tau_{\mathrm{exit}} := \inf\{ t > 0 : X_t \notin \mathcal{N}_\varepsilon \} $ from this region;  
* **recovery times** $ \tau_{\mathrm{rec}}(x) := \mathbb{E}_x[\inf\{ t > 0 : X_t \in \mathcal{N}_\varepsilon \}] $ from perturbed initial conditions $ x $.

Continuous‑time T‑theory would then ask, for example:

* how $ \mathbb{E}[\tau_{\mathrm{rec}}] $ depends on the constraint level $ C $;  
* how sensitive $ \tau_{\mathrm{exit}} $ is to exogenous perturbations of the potential or noise;  
* whether increasing $ C $ within a basin systematically shortens recovery times and lengthens exit times, echoing FIT propositions about perturbation recovery and robustness.

In gradient‑flow systems with small noise, these questions connect to classical results on Kramers’ escape times and large deviations: deeper and sharper wells typically yield larger expected exit times and faster recovery within wells. Translating those results into FIT language would create a concrete, continuous‑time realization of T‑theory’s core intuitions: more constrained attractors are easier to recover and harder to escape.

The deterministic gradient‑flow toy model in this paper does not yet do that; it simply puts in place the basic $ C(t) $ and $ \Phi_F(t) $ structure on which a continuous‑time T‑theory could build.

### 4.5 Outlook: from classical gradient flows to quantum FIT

Beyond stochastic classical dynamics, the FIT roadmap envisions a quantum layer, in which the primitives are re‑expressed in terms of density matrices, quantum channels, and Lindblad generators. The analogy with the present work is clear:

* State becomes a density operator $ \rho(t) $;  
* Force becomes a generator $ \mathcal{L}[\rho] $ of Lindblad type;  
* Information becomes von Neumann entropy or quantum relative entropy;  
* Constraints become rank, support, decoherence functionals, or relative‑entropy distances to fixed points.

In such a setting, a quantum gradient flow would be replaced by a quantum Markov semigroup with a unique fixed point $ \rho_\infty $. There, too, one can often show exponential convergence of $ D(\rho(t)\Vert \rho_\infty) $ and decay of certain dissipative functionals, suggesting that quantum analogues of Theorems 1–2 may be available for suitably simple models (for example, qubit dephasing or amplitude damping). The deterministic convex gradient flow studied here can thus be viewed as a classical warm‑up for that more ambitious quantum program.

From a practical standpoint, the main contributions of this paper to the v3 roadmap are:

1. It provides a concrete example of how to embed FIT primitives into a standard continuous‑time dynamical system in a way that makes constraint accumulation and force collapse provable.  
2. It identifies the specific analytical levers—Lyapunov functionals, gradient–suboptimality bounds, spectral gaps, log‑Sobolev inequalities—that future continuous‑time FIT work is likely to require.  
3. It suggests a pattern of development: start with a simple but nontrivial class (deterministic strongly convex flows), prove FIT‑style theorems there, then incrementally generalize to noisy, nonconvex, and quantum settings.

### 4.6 Summary

The deterministic gradient‑flow toy model analyzed here is intentionally modest: it covers only one corner of the space that FIT hopes to describe, and it deliberately glosses over noise, nonconvexity, and information‑theoretic nuance. Within that corner, however, it shows that the central qualitative FIT pattern—effective constraint accumulation towards a plateau coupled with collapse of force magnitude, tightly linked by a simple functional relationship—can be made into a theorem rather than an aspiration.

In particular:

* there exists a scalar constraint functional $ C(t) $ that is non‑decreasing and converges exponentially to a finite plateau;  
* the squared force magnitude $ \|F(t)\|^2 $ decays exponentially and is linearly pinned between constants times the constraint gap $ C_\infty - C(t) $;  
* both behaviors follow from standard convexity and smoothness assumptions, without any FIT‑specific machinery beyond the relabeling of existing analytical objects.

This is enough to justify, at least in this setting, treating certain late‑time FIT propositions not merely as empirical hypotheses but as theorems under clearly stated dynamical assumptions. It does not, by itself, establish broader universality claims, nor does it address the many regimes where those assumptions fail. But it provides a clean anchor point for the continuous‑time side of the FIT program: a baseline model where the slogans are true, the constants are computable, and the gap to more realistic systems is precisely visible.

The main work going forward is to see how far this structure extends: first to stochastic gradient flows and Markov semigroups, then to multiwell and nonconvex landscapes, and eventually to quantum open systems. At each step, the same question should be asked in the same style: given a well‑understood dynamical class and a concrete embedding of the FIT primitives, which of the FIT propositions can we prove, which survive empirically, and which must be revised or abandoned?

---

## Appendix A Proofs of Theorem 1 and Theorem 2

### A.1 Preliminaries

We recall the setting from Section 2. Let $ V : \mathbb{R}^d \to \mathbb{R} $ be a twice continuously differentiable potential satisfying Assumption A1: there exist constants $ 0 < \lambda \le L < \infty $ such that, for all $ x, y \in \mathbb{R}^d $, we have

* **strong convexity**

  $$
  V(x) \;\ge\; V(y) + \langle \nabla V(y), x - y \rangle + \frac{\lambda}{2} \, \|x - y\|^2,
  $$

* **Lipschitz gradient**

  $$
  \|\nabla V(x) - \nabla V(y)\| \;\le\; L \, \|x - y\|.
  $$

There is then a unique minimizer $ x^\star $ with $ \nabla V(x^\star) = 0 $, and the gradient flow

$$
\dot X_t = -\nabla V(X_t)
$$

is well posed for all $ t \ge 0 $ and converges to $ x^\star $.

We define the **energy gap**

$$
E(t) := V(X_t) - V(x^\star) \;\ge\; 0,
$$

the **constraint functional**

$$
C(t) := E(0) - E(t),
\qquad
C_\infty := E(0),
$$

and the **force** and its squared magnitude

$$
F(t) := -\nabla V(X_t),
\qquad
\Phi_F(t) := \|F(t)\|^2 = \|\nabla V(X_t)\|^2.
$$

Thus

$$
C_\infty - C(t) = E(t)
$$

for all $ t \ge 0 $.

The proofs of Theorem 1 and Theorem 2 rely on a standard inequality relating the gradient norm to the energy gap.

**Lemma A.1 (Gradient–suboptimality bounds).**  
Under Assumption A1, for all $ x \in \mathbb{R}^d $ we have

$$
2\lambda \bigl(V(x) - V(x^\star)\bigr)
\;\le\;
\|\nabla V(x)\|^2
\;\le\;
2L \bigl(V(x) - V(x^\star)\bigr).
$$

*Proof.* We sketch the argument, which is standard in convex optimization.

1. From strong convexity, taking $ y = x^\star $ and using $ \nabla V(x^\star) = 0 $,

   $$
   V(x) - V(x^\star)
   \;\ge\;
   \frac{\lambda}{2} \, \|x - x^\star\|^2.
   $$

2. From the inequality

   $$
   \langle \nabla V(x) - \nabla V(x^\star), x - x^\star \rangle
   \;\ge\;
   \lambda \, \|x - x^\star\|^2,
   $$

   and $ \nabla V(x^\star) = 0 $, we obtain

   $$
   \langle \nabla V(x), x - x^\star \rangle
   \;\ge\;
   \lambda \, \|x - x^\star\|^2.
   $$

   By Cauchy–Schwarz,

   $$
   \|\nabla V(x)\| \, \|x - x^\star\|
   \;\ge\;
   \langle \nabla V(x), x - x^\star \rangle
   \;\ge\;
   \lambda \, \|x - x^\star\|^2,
   $$

   hence $ \|\nabla V(x)\| \ge \lambda \, \|x - x^\star\| $.

3. Combining the two bounds on $ \|x - x^\star\| $ yields

   $$
   V(x) - V(x^\star)
   \;\le\;
   \frac{1}{2\lambda} \, \|\nabla V(x)\|^2
   \quad \Longleftrightarrow \quad
   \|\nabla V(x)\|^2 \;\ge\; 2\lambda \bigl(V(x) - V(x^\star)\bigr),
   $$

   which is the lower bound.

4. The upper bound follows from $ L $‑smoothness and standard arguments: for an $ L $‑smooth and $ \lambda $‑strongly convex function,

   $$
   V(x) - V(x^\star)
   \;\ge\;
   \frac{1}{2L} \, \|\nabla V(x)\|^2,
   $$

   which is equivalent to

   $$
   \|\nabla V(x)\|^2
   \;\le\;
   2L \bigl(V(x) - V(x^\star)\bigr).
   $$

This establishes the claimed two‑sided inequality.  ∎

---

### A.2 Proof of Theorem 1 (Constraint accumulation)

We restate the theorem for convenience.

**Theorem 1 (Constraint accumulation in gradient flows).**  
Let $ X_t $ solve

$$
\dot X_t = -\nabla V(X_t)
$$

with $ V $ satisfying Assumption A1, and let $ C(t) $ be defined as above. Then:

1. $ C(t) $ is differentiable and non‑decreasing, with

   $$
   \frac{d}{dt} C(t)
   =
   \|\nabla V(X_t)\|^2
   \;\ge\;
   0
   \quad \text{for all } t \ge 0;
   $$

2. $ C(t) $ converges exponentially to $ C_\infty = E(0) $, and

   $$
   C_\infty - C(t)
   =
   E(t)
   \;\le\;
   E(0) \, e^{-2\lambda t}
   \quad \text{for all } t \ge 0.
   $$

*Proof.*  

**Step 1: monotonicity of $ C(t) $.**  
By definition,

$$
E(t) = V(X_t) - V(x^\star).
$$

Using the chain rule, we differentiate $ E(t) $ along the trajectory $ t \mapsto X_t $:

$$
\frac{d}{dt} E(t)
=
\bigl\langle \nabla V(X_t), \dot X_t \bigr\rangle.
$$

Substituting the gradient flow equation $ \dot X_t = -\nabla V(X_t) $ gives

$$
\frac{d}{dt} E(t)
=
- \|\nabla V(X_t)\|^2
\;\le\;
0.
$$

Thus $ E(t) $ is non‑increasing in $ t $. Since

$$
C(t)
=
E(0) - E(t),
$$

we immediately obtain

$$
\frac{d}{dt} C(t)
=
- \frac{d}{dt} E(t)
=
\|\nabla V(X_t)\|^2
\;\ge\;
0.
$$

This proves that $ C(t) $ is differentiable and non‑decreasing for all $ t \ge 0 $.

**Step 2: exponential convergence of the constraint gap.**  
From Lemma A.1 applied at $ x = X_t $, we have

$$
\|\nabla V(X_t)\|^2
\;\ge\;
2\lambda \bigl(V(X_t) - V(x^\star)\bigr)
=
2\lambda E(t).
$$

Combining this with the expression for $ \frac{d}{dt} E(t) $ yields

$$
\frac{d}{dt} E(t)
=
- \|\nabla V(X_t)\|^2
\;\le\;
- 2\lambda E(t).
$$

This is a scalar differential inequality of Grönwall type. Writing it as

$$
\frac{d}{dt} \bigl(\log E(t)\bigr)
\;\le\;
- 2\lambda
$$

for all $ t $ with $ E(t) > 0 $, and integrating from $ 0 $ to $ t $, we obtain

$$
\log E(t) - \log E(0)
\;\le\;
- 2\lambda t,
$$

whence

$$
E(t)
\;\le\;
E(0) \, e^{-2\lambda t}
\quad \text{for all } t \ge 0.
$$

Finally, since $ C_\infty - C(t) = E(t) $, we conclude

$$
C_\infty - C(t)
\;\le\;
E(0) \, e^{-2\lambda t},
$$

which is the claimed exponential convergence of $ C(t) $ to $ C_\infty $.  ∎

---

### A.3 Proof of Theorem 2 (Force collapse and coupling to the constraint gap)

We again restate the theorem.

**Theorem 2 (Force collapse and linear coupling to constraint gap).**  
Under the assumptions and definitions above:

1. The squared force magnitude decays exponentially:

   $$
   \Phi_F(t)
   =
   \|\nabla V(X_t)\|^2
   \;\le\;
   2L \, E(0) \, e^{-2\lambda t}
   \quad \text{for all } t \ge 0;
   $$

2. For all $ t \ge 0 $, the squared force magnitude is linearly sandwiched by the constraint gap:

   $$
   2\lambda \bigl(C_\infty - C(t)\bigr)
   \;\le\;
   \Phi_F(t)
   \;\le\;
   2L \bigl(C_\infty - C(t)\bigr).
   $$

*Proof.*  

**Step 1: exponential decay of $ \Phi_F(t) $.**  
By the upper bound in Lemma A.1, for every $ t \ge 0 $,

$$
\|\nabla V(X_t)\|^2
\;\le\;
2L \bigl(V(X_t) - V(x^\star)\bigr)
=
2L \, E(t).
$$

Using the estimate from Theorem 1,

$$
E(t)
\;\le\;
E(0) \, e^{-2\lambda t},
$$

we obtain

$$
\Phi_F(t)
=
\|\nabla V(X_t)\|^2
\;\le\;
2L \, E(t)
\;\le\;
2L \, E(0) \, e^{-2\lambda t},
$$

which proves the exponential decay of $ \Phi_F(t) $.

**Step 2: linear sandwiching by the constraint gap.**  
From Lemma A.1 we have, for each $ t \ge 0 $,

$$
2\lambda E(t)
\;\le\;
\|\nabla V(X_t)\|^2
\;\le\;
2L E(t).
$$

Using $ E(t) = C_\infty - C(t) $, this becomes

$$
2\lambda \bigl(C_\infty - C(t)\bigr)
\;\le\;
\Phi_F(t)
\;\le\;
2L \bigl(C_\infty - C(t)\bigr),
$$

which is exactly the claimed linear sandwich between squared force magnitude and the remaining constraint gap.  ∎

In particular, near the plateau $ C_\infty $, both sides of the inequality go to zero together, and one has

$$
\Phi_F(t)
\;\asymp\;
C_\infty - C(t)
\quad \text{as } t \to \infty,
$$

in the sense of equivalence up to constant factors $ 2\lambda $ and $ 2L $. This is the multi‑dimensional continuous‑time analogue of the exact scalar relation

$$
F(t)^2 = \kappa \bigl(C_\infty - C(t)\bigr)
$$

that appears in the one‑dimensional FIT toy model in v2.1.

---

### A.4 Remarks on stochastic extensions (informal)

Although the present appendix focuses on deterministic gradient flows, the overall strategy—identify a Lyapunov functional, define constraint as a monotone transform of that functional, and bound suitable force quantities in terms of its gap—extends naturally to stochastic dynamics such as overdamped Langevin SDEs and Markov semigroups. In those settings, however, one works with distributions $ \mu_t $ and functionals like relative entropy and Dirichlet forms rather than single‑trajectory quantities. Making the analogues of Theorem 1 and Theorem 2 fully rigorous in that context requires tools such as spectral gaps and log‑Sobolev inequalities, and is deferred to future work in the continuous‑time branch of the FIT program.

