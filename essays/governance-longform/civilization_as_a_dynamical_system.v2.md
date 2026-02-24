# Civilization as a Dynamical System

## Thresholds, Irreversibility, and the Mathematics of Coexistence

---

## Abstract

We construct a minimal three-variable ordinary differential equation system describing the co-evolution of extraction strategies, resource stocks, and governance bandwidth in a civilization. The model admits two structurally distinct thresholds: a transcritical bifurcation at which cooperation loses local stability to extraction, and a saddle-node bifurcation with hysteresis at which resource depletion becomes dynamically irreversible. We prove, via Lyapunov–LaSalle analysis, that a cooperation equilibrium is asymptotically stable whenever a barrier function $\Psi = P\gamma - dR$ remains positive on a forward-invariant operating domain, and we derive a closed-form upper bound on the maximum population scale $N_{\max}^\star$ that the domain can sustain. We extend the model to non-autonomous parameter drift (technology-induced shifts in extraction gain) and to two-civilization competitive coupling, showing that unilateral capability increases can destabilize both parties through a parameter-space prisoner's dilemma. The mathematics suggests that civilizational coexistence is not a moral aspiration but a parameter regime—one whose maintenance requires structural investment and whose loss triggers qualitatively irreversible dynamics.

---

## I. Structural Causality, Not Moral Causality

Civilizations rarely collapse in a single dramatic act. They drift, they tilt, they slide past a threshold that in retrospect looks obvious. Historians often narrate decline in moral vocabulary—corruption, decadence, greed—but moral language obscures structural causality. If we strip away intention and psychology and attend only to incentive gradients, a simpler and more unsettling mechanism appears: when extraction becomes more profitable at the margin than cooperation, extraction spreads. No villain is required, no conspiracy is needed—only differential payoff.

Turchin (2003) documents this pattern across dozens of historical polities: territorial overextension strains fiscal capacity, elite competition intensifies as surplus shrinks, and administrative costs escalate until the state can no longer maintain its governance infrastructure. Tainter (1988) frames the same dynamic as rising marginal costs of complexity. Scheffer et al. (2009) provide the mathematical vocabulary—critical transitions, early-warning signals, hysteresis—drawn from ecology but applicable wherever nonlinear feedbacks produce threshold behavior.

This essay attempts to synthesize these insights into the smallest dynamical system capable of expressing the tension between extraction and governance, and to show that the system's qualitative fate is determined by the sign of a single composite variable. The mathematical apparatus is deliberately minimal: a three-variable ODE system with replicator dynamics, logistic-Allee resource growth, and linear governance feedback. What it lacks in realism it gains in transparency—every conclusion can be traced to a specific parameter inequality, and every policy lever maps to a specific coefficient.

---

## II. A Minimal Three-Variable Model

### II.1 State Variables

We define three state variables:

- $x(t) \in [0, 1]$: the proportion of extraction strategies in the population.
- $R(t) \geq 0$: the resource stock—economic, ecological, or institutional.
- $\gamma(t) \geq 0$: governance bandwidth, a scalar proxy for the system's capacity to monitor, sanction, and coordinate.

### II.2 Dynamics

**Strategy selection** follows replicator dynamics, where the growth rate of extraction is proportional to its net marginal advantage:

$$
\dot{x} = x(1 - x)(dR - P\gamma)
$$

Here $d > 0$ is the marginal gain from extraction and $P > 0$ is the enforceability multiplier—the rate at which governance translates into effective deterrence. The composite variable

$$
\mu = dR - P\gamma
$$

determines the direction of strategic selection: if $\mu > 0$, extraction grows; if $\mu < 0$, extraction decays. The entire civilizational trajectory is governed by the sign of this single expression.

**Resource evolution** follows logistic growth with an Allee threshold, diminished by extraction:

$$
\dot{R} = rR\left(1 - \frac{R}{K}\right)\left(\frac{R}{A} - 1\right) - hxR
$$

The Allee term $\left(\frac{R}{A} - 1\right)$ is the critical modeling choice. When $R > A$, the resource regenerates; when $R < A$, regeneration collapses and the resource decays toward zero. The parameter $K$ is the carrying capacity, $r$ the intrinsic growth rate, $A$ the irreversibility threshold, and $h$ the destruction coefficient.

**Governance evolution** responds positively to resource abundance, negatively to system scale, and decays at a characteristic rate:

$$
\dot{\gamma} = aR - bN - c\gamma
$$

The parameters $a$, $b$, $c > 0$ encode governance productivity, complexity friction, and maintenance cost respectively. The scale parameter $N$ is treated as exogenous—a proxy for population, institutional complexity, or network size.

### II.3 Positivity and Boundedness

**Proposition 1 (Invariance).** The set $\Omega = \{(x, R, \gamma) \mid 0 \leq x \leq 1,\ 0 \leq R \leq K,\ \gamma \geq 0\}$ is positively invariant under the flow.

*Proof sketch.* At $x = 0$ and $x = 1$, the factor $x(1-x) = 0$ ensures $\dot{x} = 0$. At $R = 0$, $\dot{R} = 0$. At $R = K$, $\dot{R} = -hxK \leq 0$. At $\gamma = 0$, we apply a projection: $\dot{\gamma} = \max(aR - bN - c\gamma,\ 0)$, enforcing the physical constraint that governance bandwidth cannot be negative. $\square$

### II.4 Modeling Assumptions and Scope

The replicator equation presupposes a well-mixed, infinitely large population with continuous-time imitation dynamics. These conditions are not strictly met in finite-population settings such as the cultural evolution experiments of Willis et al. (2026), where 512 agents interact over 200 discrete generations. The linear form of the governance equation is a simplifying choice; Ostrom's (1990) empirical work on common-pool resource institutions suggests that governance capacity depends nonlinearly on group size, resource characteristics, and institutional history. The Allee effect has strong empirical grounding in ecology—fisheries collapse, population viability thresholds—but its application to abstract resources such as institutional trust or financial stability should be understood as structural analogy rather than empirical derivation.

These caveats do not invalidate the model's qualitative insights, but they bound how literally its quantitative predictions should be taken. The model is a phase-portrait generator, not a forecasting tool.

---

## III. First Threshold: The Governance Barrier

### III.1 Cooperation Equilibrium

At high resource levels $R \approx K$ with zero extraction $x = 0$, the governance equation admits a steady state:

$$
\gamma^* = \frac{aK - bN}{c}
$$

This equilibrium exists (i.e., $\gamma^* > 0$) if and only if

$$
aK > bN
$$

The interpretation is direct: the resource-driven supply of governance ($aK$) must exceed the complexity-driven demand ($bN$). When scale $N$ grows without a commensurate increase in governance productivity $a$ or a reduction in complexity friction $b$, the governance steady state degrades.

### III.2 Transcritical Bifurcation

The cooperation equilibrium $E_C = (0, K, \gamma^*)$ is locally stable only if extraction is unprofitable there—that is, if $\mu(E_C) < 0$:

$$
dK - P\gamma^* = dK - P\frac{aK - bN}{c} < 0
$$

Solving the critical condition $\mu(E_C) = 0$ for $N$ yields the bifurcation threshold:

$$
N_{\text{flip}} = \frac{K(Pa - cd)}{Pb}
$$

Below $N_{\text{flip}}$, cooperation is stable. Above it, extraction becomes the attracting strategy. This is a standard transcritical bifurcation: the cooperation and extraction equilibria exchange stability as $N$ crosses the threshold.

The Jacobian at $E_C$ (derived in Appendix A) confirms the structure. At $x = 0$, the matrix is block-triangular with eigenvalue $\lambda_1 = dK - P\gamma^*$ governing the $x$-direction. The sign flip of $\lambda_1$ at $N = N_{\text{flip}}$ is the linearized signature of the transcritical bifurcation.

Crucially, this first threshold is consequential but not catastrophic. The resource base remains intact at $R \approx K$. A reform of governance institutions—an increase in $P$, a reduction in $d$, or a structural improvement in $a/c$—can restore $\mu < 0$ and return the system to cooperation.

### III.3 Empirical Parallel

The parallel to Willis et al.'s (2026) experimental findings is direct. In the Public Goods Game, cultural evolution reliably converges to exploitative equilibria—Claude Haiku's "Exploitative" prompt won 100 out of 100 simulations at both group sizes—but the game is repeatable and welfare can be restored by changing the selection environment. The PGG regime corresponds to the pre-Allee region of this model: extraction dominates, but resources have not yet crossed the irreversibility threshold.

---

## IV. Second Threshold: The Irreversibility Basin

### IV.1 Allee Structure

The resource growth function

$$
G(R) = rR\left(1 - \frac{R}{K}\right)\left(\frac{R}{A} - 1\right)
$$

is a cubic with three roots at $R = 0$, $R = A$, and $R = K$. The middle root $R = A$ acts as a separatrix. For $R > A$, we have $G(R) > 0$ (net positive regeneration when extraction is absent); for $R < A$, we have $G(R) < 0$ (regeneration collapses). This is a saddle-node structure with hysteresis: once $R$ crosses $A$ from above, spontaneous recovery is dynamically suppressed, and the system enters a different basin of attraction.

### IV.2 Collapse Basin

When $R$ falls below $A$ and the extraction fraction is high, the resource dynamics satisfy

$$
\dot{R} \leq (\underline{g} - h)R < 0
$$

where $\underline{g} = \max_{R \in [0,A]} G(R)/R$ is the maximum per-capita regeneration rate in the sub-Allee region. If $\underline{g} < h$—that is, if regeneration cannot outpace extraction even at full capacity—the resource decays exponentially toward zero, dragging governance with it ($\dot{\gamma} \to -bN - c\gamma < 0$ when $R \to 0$) and locking in full extraction ($\dot{x} > 0$ when $\gamma \to 0$).

This chain is the mathematical expression of civilizational collapse:

$$
\text{Scale exceeds governance} \to \text{Extraction dominates} \to \text{Resources breach } A \to \text{Irreversible decay}
$$

### IV.3 Empirical Parallel

The CPR (Common Pool Resource) experiments in Willis et al. (2026) provide the sharpest empirical analogue. At group size 64, welfare efficiency drops to 5%—a single round of mutual defection depletes the shared resource so severely that the remaining 19 rounds are effectively forfeit. The CPR is a system trapped below its Allee threshold.

---

## V. Collapse as a Two-Stage Time Process

### V.1 Derivation Sketch

If at the boundary $R = A$, extraction still enjoys a positive net advantage,

$$
\mu(N) = dA - P\Gamma_{\max}(N) > 0
$$

where $\Gamma_{\max}(N) = \max\left(\gamma(0),\ \frac{aK - bN}{c}\right)$ is the best governance the system can muster, then collapse proceeds in two stages with distinct time scales.

**Stage 1: Strategy takeover.** The replicator equation $\dot{x} = x(1-x)\mu$ has the standard logistic solution. Starting from a small initial fraction $x(0) \ll 1$, extraction reaches dominance ($x \approx 1$) in time

$$
T_1 \approx \frac{1}{\mu}\ln\left(\frac{1 - x(0)}{x(0)}\right)
$$

which is logarithmic in the initial condition and inversely proportional to the net extraction advantage $\mu$.

**Stage 2: Resource depletion.** With $x \approx 1$, the resource equation reduces to $\dot{R} \approx G(R) - hR$. Near the Allee threshold, $G(R)$ is small relative to $hR$, so the dominant behavior is exponential decay: $R(t) \approx R_0 e^{-ht}$. The time for $R$ to reach $A$ from $R_0$ is

$$
T_2 \approx \frac{1}{h}\ln\left(\frac{R_0}{A}\right)
$$

### V.2 Collapse Time Upper Bound

Combining both stages yields:

$$
T^\star(N) \approx \frac{1}{\mu(N)}\left[1 + \ln\left(\frac{\mu(N)}{h}\ln\left(\frac{R_0}{A}\right) \cdot \frac{1 - x(0)}{x(0)}\right)\right] + \frac{1}{h}\ln\left(\frac{R_0}{A}\right)
$$

Both terms are logarithmic in the relevant ratios, so collapse—once $\mu > 0$—proceeds fast relative to civilizational planning horizons. Larger $N$ typically increases $\mu(N)$ by degrading governance bandwidth, which shortens collapse time. Scale amplifies instability, not because larger societies are morally weaker, but because the governance deficit $\mu$ grows with $N$.

---

## VI. Stability of the Cooperation Equilibrium: Lyapunov–LaSalle Analysis

The preceding sections establish qualitative dynamics through nullcline and bifurcation analysis. We now provide a rigorous stability result for the cooperation equilibrium using Lyapunov–LaSalle methods.

### VI.1 Barrier Function and Operating Domain

Define the barrier function

$$
\Psi(R, \gamma) = P\gamma - dR
$$

and the operating domain

$$
\Omega_{\varepsilon, R_{\min}} = \left\{(x, R, \gamma) \in \Omega :\ R \geq R_{\min},\ \Psi(R, \gamma) \geq \varepsilon\right\}
$$

for parameters $\varepsilon > 0$ and $R_{\min} > 0$. Within this domain, extraction is uniformly unprofitable: $dR - P\gamma \leq -\varepsilon$, so $\dot{x} \leq -\varepsilon x(1-x) \leq 0$.

### VI.2 Forward Invariance

**Lemma 1 (Resource boundary).** If $r(1 - R_{\min}/K) \geq h$, then $R(t) \geq R_{\min}$ is forward invariant.

*Proof.* At $R = R_{\min}$, $\dot{R} = R_{\min}[r(1 - R_{\min}/K) - hx] \geq R_{\min}[r(1 - R_{\min}/K) - h] \geq 0$ under the stated condition (worst case $x = 1$). $\square$

**Lemma 2 (Barrier boundary).** Define

$$
A(R_{\min}) = Pa - cd - dr\left(1 - \frac{R_{\min}}{K}\right)
$$

If $A(R_{\min}) > 0$ and $A(R_{\min}) \cdot R_{\min} \geq PbN + c\varepsilon$, then $\Psi \geq \varepsilon$ is forward invariant on $\{R \geq R_{\min}\}$.

*Proof sketch.* On the boundary $\Psi = \varepsilon$, we compute $\dot{\Psi} = P\dot{\gamma} - d\dot{R}$, substitute the dynamics and the boundary relation $\gamma = (dR + \varepsilon)/P$, and bound from below using $R \geq R_{\min}$ and the worst case $x = 0$ (which minimizes the positive term $dhxR$). The resulting expression $\dot{\Psi}|_{\Psi=\varepsilon} \geq A(R_{\min})R - PbN - c\varepsilon \geq A(R_{\min})R_{\min} - PbN - c\varepsilon \geq 0$ ensures the barrier is not penetrated from inside. $\square$

### VI.3 Asymptotic Stability

**Theorem 1 (Cooperation stability under governance margin).** Suppose:

1. *Resource sustainability*: $r > h$, and $R_{\min} \leq K(1 - h/r)$.
2. *Governance efficiency threshold*: $A(R_{\min}) > 0$.
3. *Operating domain invariance*: $A(R_{\min}) \cdot R_{\min} \geq PbN + c\varepsilon$.

Then $\Omega_{\varepsilon, R_{\min}}$ is forward invariant, and for all initial conditions in this domain,

$$
x(t) \to 0, \quad R(t) \to K, \quad \gamma(t) \to \gamma^* = \frac{aK - bN}{c}
$$

*Proof sketch.* Forward invariance follows from Lemmas 1 and 2. Within the domain, $\dot{x} \leq -\varepsilon x(1-x)$ ensures $x(t) \to 0$ by comparison with the logistic equation. As $x \to 0$, the resource equation approaches $\dot{R} = rR(1 - R/K)(R/A - 1)$, which has $R = K$ as a stable equilibrium (given $R > A$, which is guaranteed by $R \geq R_{\min} > 0$). The governance equation is a stable linear system with input $R \to K$, yielding $\gamma \to \gamma^*$. By LaSalle's invariance principle, the only invariant set in $\{\dot{V} = 0\}$ for the Lyapunov candidate $V = \lambda x + \frac{1}{2}(R-K)^2 + \frac{\eta}{2}(\gamma - \gamma^*)^2$ is the singleton $\{(0, K, \gamma^*)\}$. $\square$

### VI.4 Maximum Sustainable Scale

The invariance conditions can be solved for the maximum population scale that the cooperation basin can sustain. Setting $R_{\min}^\star = K(1 - h/r)$ (the tightest feasible resource floor) yields:

$$
A(R_{\min}^\star) = Pa - cd - dh
$$

The hard existence condition for a non-empty cooperation basin is therefore:

$$
Pa > cd + dh \quad \text{and} \quad r > h
$$

The first inequality states that resource-to-governance conversion ($Pa$) must exceed the combined drag of governance decay times extraction gain ($cd$) and extraction-resource destruction ($dh$). The second states that natural regeneration must exceed maximum extraction intensity.

Under these conditions, the maximum sustainable scale is:

$$
N_{\max}^\star \approx \frac{(Pa - cd - dh) \cdot K(1 - h/r)}{Pb}
$$

This is a closed-form expression in terms of observable institutional and ecological parameters. Each factor has a specific policy interpretation: increasing governance productivity $a$, increasing enforceability $P$, reducing extraction gain $d$, reducing governance friction $c$, reducing resource destruction $h$, or increasing regeneration rate $r$ all expand the maximum sustainable scale.

---

## VII. Intelligence as a Gain Multiplier

If strategic search improves—through better technology, faster computation, financial innovation, or artificial intelligence—agents discover extraction strategies more rapidly. In the model, this corresponds to an increase in the effective speed at which the replicator dynamics operate: the population approaches the equilibrium dictated by $\text{sign}(\mu)$ faster.

The implication is structurally clean: intelligence is a gain multiplier on selection speed, not a moral variable. When $\mu < 0$, intelligence accelerates convergence to cooperation—better governance tools, faster institutional feedback, more effective coordination. When $\mu > 0$, intelligence accelerates convergence to extraction and collapse—faster arbitrage discovery, more effective exploitation, quicker evasion of governance.

Willis et al.'s (2026) finding that high-capability reasoning models produce both the most effective cooperative and the most effective exploitative strategies is exactly this dual-use character expressed in an experimental setting. Claude 3.5 Sonnet generated the strategy with the highest individual payoff in the CPR game (Exploitative) and also the strategy with the highest collective welfare when universally adopted (Collective). Intelligence amplifies whichever regime the system is in; it does not determine which regime prevails.

---

## VIII. Prevention versus Recovery: Two Control Regimes

### VIII.1 Preventive Control

Maintaining $\mu \leq 0$ along the entire trajectory requires $P\gamma \geq dR + \varepsilon$. The required external governance input is:

$$
u_\gamma \geq c\frac{dK + \varepsilon}{P} - aA + bN
$$

Under this condition, $\dot{x} \leq -\varepsilon x(1-x)$ and extraction decays exponentially. The cost scales linearly with $N$—demanding but tractable.

### VIII.2 Recovery Control

When $R < A$, natural regeneration is negative. Recovery requires a sustained resource injection $u_R$ exceeding the maximum deficit:

$$
\bar{u}_R > m = \max_{R \in [0, A]} \left(-G(R)\right)
$$

The recovery time is bounded by:

$$
T_{\text{rec}} \leq \frac{A - R(0)}{\bar{u}_R - m}
$$

### VIII.3 The Asymmetry

Prevention cost is linear in $N$ and proportional to the safety margin $\varepsilon$. Recovery cost has a hard threshold $m$ below which no investment suffices. A civilization that underinvests in prevention by a small margin pays a linear penalty; a civilization that allows $R$ to cross $A$ faces a qualitatively different problem that may exceed its resource budget entirely.

In the FIT framework's terminology, this corresponds to the concept of Recoverability: the bounded-resource feasibility of reconstructing a target structural state from the current state. When $R > A$, recoverability is high. When $R < A$, it drops discontinuously, and the system may be practically irrecoverable under any realistic budget.

---

## IX. Non-Autonomous Extension: Moving Bifurcations

### IX.1 Parameter Drift

In a technologically dynamic environment, the model parameters are not constant. Let

$$
d = d(t), \quad P = P(t), \quad h = h(t)
$$

The system becomes non-autonomous, and the bifurcation thresholds become moving targets:

$$
N_{\text{flip}}(t) = \frac{K(P(t)a - cd(t))}{P(t)b}
$$

If AI and technology increase $d(t)$ at rate $\alpha > 0$ while governance adaptation lags, then $dN_{\text{flip}}/dt < 0$: the stable operating envelope shrinks even at fixed population $N$.

### IX.2 The Drift-Speed Inequality

Differentiating $\mu(t) = d(t)R - P(t)\gamma$ with respect to time:

$$
\dot{\mu} = \dot{d}R + d\dot{R} - \dot{P}\gamma - P\dot{\gamma}
$$

A necessary condition for sustained stability ($\mu \leq 0$) is that governance adaptation outpaces capability drift:

$$
\dot{P}\gamma + P\dot{\gamma} > \dot{d}R + d\dot{R}
$$

When this inequality is violated, $\mu$ eventually turns positive regardless of the current margin. The civilizational safety condition is therefore not merely $\mu < 0$ at a point in time, but $\dot{\mu} < 0$: governance must be gaining ground, not merely holding position.

### IX.3 Delayed Bifurcation

In slow-fast systems where parameters drift gradually past a critical value, a well-known phenomenon occurs: the system remains near the now-unstable equilibrium for a transient period before rapidly departing. This *delayed loss of stability* means that conventional monitoring—which checks whether the system appears stable—can fail to detect that the bifurcation boundary has already been crossed. The system looks stable; it is not.

This has precise historical analogues: financial markets that appear healthy on the eve of a crash, empires that expand vigorously before fiscal collapse, ecosystems that maintain output peaks just before a tipping point. In each case, the parameter drift has moved the bifurcation boundary past the system's current state, but the transition has not yet manifested in observable variables.

---

## X. Multi-Civilization Coupling

### X.1 Minimal Coupled Model

Consider two civilizations $(x_1, R_1, \gamma_1)$ and $(x_2, R_2, \gamma_2)$ coupled through three channels:

**Resource coupling** (trade and spillovers):

$$
\dot{R}_i = G(R_i) - h x_i R_i + \beta(R_j - R_i)
$$

where $\beta > 0$ represents resource flow between systems. A declining neighbor drags down its partner.

**Technology diffusion** (extraction capability spreads):

$$
d_i(t) = d_0 + \alpha_i t + \kappa(d_j - d_i)
$$

where $\kappa > 0$ is the diffusion rate. If one civilization develops higher extraction capability, competitive pressure forces the other to follow.

**Security competition** (governance diversion):

$$
\dot{\gamma}_i = aR_i - bN_i - c\gamma_i - s x_j
$$

where $s > 0$ captures the governance cost imposed by a neighbor's extraction. When civilization $j$ extracts more aggressively, civilization $i$ must divert governance resources to defense, reducing effective internal enforcement.

### X.2 Synchronized Destabilization

When technology diffusion is strong ($\kappa$ large), extraction capabilities converge: $d_1 \approx d_2$. Both civilizations then face similar composite variables $\mu_i$, and if $d$ rises sufficiently, both cross the transcritical threshold near-simultaneously. The result is a *synchronized phase transition*—not because one civilization corrupted the other morally, but because the parameter $d$ propagated through competitive coupling.

When resource coupling $\beta$ is significant, the problem worsens: if one civilization's resources breach $A$, the resulting outflow drags its partner's resources toward the same threshold. This is *coupled hysteresis*—a cascade of irreversibility.

### X.3 A Parameter-Space Prisoner's Dilemma

The coupling structure reveals that multi-civilization dynamics involve a prisoner's dilemma not in strategy space but in parameter space. Each civilization, acting individually, has an incentive to increase $d$ (competitive advantage through better extraction technology). But when both do so, the global composite variable $\mu_{\text{global}}$ rises, pushing the entire coupled system toward instability. The Nash equilibrium of unilateral capability races is collectively destabilizing.

The escape from this dilemma requires coordinated constraints on the coupling parameters: limiting the diffusion of extraction-enhancing capabilities ($\kappa$), building circuit-breakers into resource coupling ($\beta$ with threshold cutoffs), and reducing the security externality ($s$) through verifiable agreements. These are not moral recommendations but stability conditions—the parameter inequalities that keep the coupled system in the coexistence basin.

---

## XI. Coexistence as Institutional Engineering

### XI.1 The Stability Conditions

Long-term civilizational coexistence corresponds to a parameter regime:

$$
\mu \leq 0 \quad \text{and} \quad R \gg A
$$

These two inequalities translate into four structural levers, each with specific institutional content:

**Reducing $d$ (extraction rent).** This corresponds to anti-monopoly enforcement, externality pricing, financial transparency requirements, and the elimination of regulatory arbitrage channels. The goal is not to suppress economic activity but to close the gap between private extraction returns and social cooperation returns.

**Increasing $P$ (enforceability).** This requires auditable governance interfaces, credible third-party verification, unified anti-corruption frameworks, and technology-enabled compliance (verifiable computation, traceable ledgers). The key insight from the model is that coexistence does not require shared values—it requires shared auditable interfaces.

**Improving $a/c$ (governance efficiency).** The model shows that the critical ratio is not the absolute level of governance but the efficiency with which resources convert to governance bandwidth relative to maintenance costs. Coexistence may require more efficient states, not necessarily more powerful ones.

**Maintaining $R/A$ (resilience buffer).** Civilizations must never operate close to the irreversibility threshold. This translates to ecological red lines, financial capital requirements, social safety nets, and conflict de-escalation mechanisms—structural buffers that keep the system far from the basin boundary.

### XI.2 A Compact Coexistence Condition

At the resource floor $R = A$, the coexistence condition becomes:

$$
P\Gamma_{\max}(N) \geq dA
$$

where $\Gamma_{\max}(N) = \max(\gamma(0),\ (aK - bN)/c)$. As $N$ grows, maintaining coexistence requires proportionally stronger $P$ or higher $a/c$. This is not a cultural judgment; it is a scaling law.

---

## XII. Conclusion

Civilizations do not endure because they are virtuous. They endure because the parameter regime $\mu \leq 0$, $R \gg A$ is maintained—because extraction stops being marginally profitable relative to the governance deterrent. Collapse is not fate but parameter drift: a slow erosion of the governance-to-extraction ratio until the system crosses first the transcritical threshold $N_{\text{flip}}$ (reversible) and then, if uncorrected, the Allee threshold $A$ (irreversible). Coexistence is not utopia but a stability basin—one that requires sustained structural investment and that becomes catastrophically expensive to recover once exited.

The mathematics is deliberately minimal. A three-variable ODE system cannot capture the richness of historical civilizations. But it captures the structural logic that connects incentive gradients to phase transitions, and phase transitions to irreversibility. It provides closed-form expressions—$N_{\text{flip}}$, $N_{\max}^\star$, $T^\star(N)$—that translate qualitative intuitions into quantitative thresholds. And it suggests that the most consequential question a civilization faces is not "how do we become better?" but "which side of $\mu = 0$ are we on, how fast is $\mu$ drifting, and how far are we from $R = A$?"

---

## Appendix A: Jacobian at the Cooperation Equilibrium

At $E_C = (0, K, \gamma^*)$, the Jacobian of the system is:

$$
J(E_C) = \begin{pmatrix} dK - P\gamma^* & 0 & 0 \\ -hK & -r & 0 \\ 0 & a & -c \end{pmatrix}
$$

The eigenvalues are $\lambda_1 = dK - P\gamma^*$, $\lambda_2 = -r$, and $\lambda_3 = -c$. Since $r, c > 0$, the $(R, \gamma)$ subsystem is always locally stable. The cooperation equilibrium $E_C$ is locally asymptotically stable if and only if $\lambda_1 < 0$, i.e., $dK < P\gamma^*$, which is equivalent to $N < N_{\text{flip}}$.

---

## Appendix B: Phase Portrait and Bifurcation Diagrams

The following diagrams illustrate the system's qualitative behavior under slow-manifold reduction $\gamma \approx \gamma^*(R, N) = (aR - bN)/c$.

### B.1 Phase Portrait in $(x, R)$ Plane

**Regime I: Stable Cooperation** ($N < N_{\text{flip}}$, $\mu < 0$)

```
R
^
|
K ●─────────────── High-resource stable (x→0, R→K)
|      ↗  ↗  ↗
|    ↗  ↗  ↗
|  ↗  ↗  ↗
A ×─────────────── Saddle (separatrix)
|  ↘  ↘
|    ↘
0 ●─────────────── Collapse attractor
+─────────────────→ x
0                 1
```

All trajectories above $A$ converge to $(0, K)$. The saddle at $R = A$ separates the cooperation and collapse basins.

**Regime II: Zero-Sum Competition** ($N > N_{\text{flip}}$, $\mu > 0$, $R > A$)

```
R
^
|
K ○─────────────── High-resource (unstable in x-direction)
|        ↘
|          ↘
|            ● Mixed equilibrium (x>0)
A ×───────────────
|
0 ●───────────────
+─────────────────→ x
0                 1
```

The cooperation point loses stability; extraction grows. Resources remain above $A$ but are declining.

**Regime III: Irreversible Collapse** ($R < A$)

```
R
^
|
|  (high-R attractor has vanished)
|
A ──────────────── (no longer a separatrix — it's been crossed)
|    ↘  ↘  ↘
|      ↘  ↘
0 ●─────────────── All trajectories converge here
+─────────────────→ x
0                 1
```

### B.2 Bifurcation Diagram ($N$ as control parameter)

```
R*
^
|  ●━━━━━━━━━━━━━━━━━━━━━━━  Stable cooperation (R* = K)
|                         ╲
|                          ╲  Transcritical
|                           ×  N_flip
|                          ╱
|  ●━━━━━━━━━━━━━━━━━━━━━╱   Extraction equilibrium
|
|
A ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄  Irreversibility threshold
|
0 ●━━━━━━━━━━━━━━━━━━━━━━━  Collapse attractor
+━━━━━━━━━━━━━━━━━━━━━━━━━→ N
              N_flip
```

### B.3 Hysteresis Loop

```
R*
^
|      ●━━━━━━━━━━━━━━━╮  High state
|                       ┃  (forward path: increasing N)
|                       ┃
|                       ↓  Saddle-node collapse
A ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
|  ↑  Recovery requires  ┃
|  ┃  injection > m      ┃
|  ╰━━━━━━━━━━━━━━━━━━━━╯  Low state
|      (reverse path: decreasing N alone does NOT restore R)
+━━━━━━━━━━━━━━━━━━━━━━━━━→ Control parameter
```

The forward and reverse paths differ: reaching $R < A$ and then reducing $N$ back to its original value does not restore $R > A$. Recovery requires active resource injection exceeding the threshold $m$.

### B.4 Causal Chain

```
Scale N ↑  →  Governance γ* ↓  →  μ flips sign (+)
                                        ↓
                                Extraction x ↑
                                        ↓
                                Resource R ↓ toward A
                                        ↓
                              Saddle-node collision
                                        ↓
                              Irreversible basin (R → 0)
```

### B.5 Collapse Time versus Scale

```
T*(N)
^
|╲
| ╲
|  ╲
|   ╲
|    ╲
|     ╲
|      ╲
|       ╲━━━━━━━━━━━
+━━━━━━━━━━━━━━━━━━━→ N
  N_flip
```

For $N > N_{\text{flip}}$, the collapse time upper bound $T^\star(N)$ decreases as $N$ increases—larger systems collapse faster.

---

## Appendix C: Parameter Glossary

| Symbol | Name | Interpretation | Policy Lever |
|:---|:---|:---|:---|
| $x$ | Extraction fraction | Proportion using extractive strategies | — (endogenous) |
| $R$ | Resource stock | Economic, ecological, or institutional capital | Resilience investment |
| $\gamma$ | Governance bandwidth | Monitoring + enforcement + coordination capacity | Institutional design |
| $d$ | Extraction gain | Marginal return to exploitation | Anti-monopoly, externality pricing |
| $P$ | Enforceability | Governance-to-deterrence multiplier | Rule of law, auditability |
| $h$ | Destruction coefficient | Resource damage per unit extraction | Environmental regulation |
| $a$ | Governance productivity | Resource-to-governance conversion rate | Administrative efficiency |
| $b$ | Complexity friction | Scale-to-governance cost | Decentralization, subsidiarity |
| $c$ | Governance decay | Maintenance/depreciation rate | Anti-corruption, institutional renewal |
| $r$ | Regeneration rate | Intrinsic resource growth | Ecological restoration, R&D |
| $K$ | Carrying capacity | Maximum sustainable resource level | Technological frontier |
| $A$ | Allee threshold | Irreversibility boundary | Safety buffers, red lines |
| $N$ | System scale | Population, complexity, network size | — (exogenous) |
| $\mu$ | Composite variable | $dR - P\gamma$; sign determines regime | All of the above |

---

## References

Willis, R., Zhao, J., Du, Y., & Leibo, J. Z. (2026). Evaluating Collective Behaviour of Hundreds of LLM Agents. *arXiv preprint arXiv:2602.16662v1*.

Ostrom, E. (1990). *Governing the Commons: The Evolution of Institutions for Collective Action*. Cambridge University Press.

Ostrom, E., Walker, J., & Gardner, R. (1992). Covenants with and without a Sword: Self-Governance Is Possible. *American Political Science Review*, 86(2), 404–417.

Turchin, P. (2003). *Historical Dynamics: Why States Rise and Fall*. Princeton University Press.

Tainter, J. A. (1988). *The Collapse of Complex Societies*. Cambridge University Press.

Scheffer, M. et al. (2009). Early-warning signals for critical transitions. *Nature*, 461, 53–59.

Hofbauer, J. & Sigmund, K. (1998). *Evolutionary Games and Population Dynamics*. Cambridge University Press.

