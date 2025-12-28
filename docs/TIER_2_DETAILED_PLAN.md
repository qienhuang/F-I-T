# Tier-2 Experiments: Detailed Status and Planning

**Date**: December 26, 2025  
**Current Status**: Tier-1 Complete (Conway + Langton), Tier-2 Not Yet Started  
**Timeline**: 3-9 months from now

---

## 🎯 What is Tier-2?

### Tier Structure Overview

**Tier-1** (✅ COMPLETE):
- **Systems**: Conway's GoL, Langton's Ant
- **Characteristics**: Fully deterministic, fully observable, simple rules
- **Purpose**: Establish baseline, validate core framework
- **Status**: 67% support rate (6/9 propositions)

**Tier-2** (📋 PLANNED):
- **Systems**: Ising model, simple RL environments, basic optimization
- **Characteristics**: Stochastic elements, clearer statistical mechanics connection
- **Purpose**: Test framework beyond toy automata, approach "real" systems
- **Timeline**: 3-9 months

**Tier-3** (🔮 FUTURE):
- **Systems**: Biological data, neural network training, economic systems
- **Characteristics**: Real-world complexity, noisy, high-dimensional
- **Purpose**: Demonstrate practical applicability
- **Timeline**: 6-18 months

---

## 📊 Tier-2 Specific Systems

### System 1: Ising Model ⭐ PRIORITY

**Why Ising?**
- Well-understood statistical mechanics model
- Known phase transition (critical temperature)
- Connects FIT to established physics
- Tests P13-P15 (critical phenomena)

**Implementation**:
```python
# 2D Ising model on lattice
- State S_t: spin configuration {+1, -1}^{N×N}
- Force F: ∇H (energy gradient)
- Constraint C: magnetization structure, correlation length
- Temperature T as control parameter
```

**Target Propositions**:
- **P13** (Critical slowing down): τ ∝ |T-T_c|^(-ν)
- **P14** (Scale-free fluctuations): Power-law near criticality
- **P15** (Universality classes): Ising exponents match FIT predictions
- **P2** (Constraint monotonicity): Test in equilibration
- **P4** (Plateau detection): Thermal equilibrium as plateau

**Expected Timeline**: 1-2 months
- 2 weeks: Implementation
- 2 weeks: Validation runs
- 2 weeks: Analysis and write-up

**Difficulty**: Medium
- Known reference values (exponents)
- Standard algorithms (Metropolis, Wolff)
- Clear success criteria

---

### System 2: Simple RL Environment (GridWorld Extended)

**Why RL?**
- Bridge to AI safety application
- Tests learning dynamics (not just physical evolution)
- Validates P1, P3, P11 in learning context

**Implementation**:
```python
# Enhanced GridWorld
- State S_t: policy parameters θ_t
- Force F: policy gradient ∇_θ J(θ)
- Constraint C: behavioral constraints, safe regions
- Information I: predictive accuracy
```

**Two Conditions**:
1. **Standard RL**: Minimal constraints
2. **Safety-constrained**: High C by design (action masking, penalties)

**Target Propositions**:
- **P1** (Nirvana persistence): Converged policies stay stable
- **P3** (Force decay): Gradient magnitude → 0 at convergence
- **P11** (Phase transition): Exploration → exploitation shift
- **P12** (Information bottleneck): Learning plateaus without new constraints
- **P18** (Timescale separation): Fast Q-updates vs slow policy change

**Expected Timeline**: 2-3 months
- 3 weeks: Environment design + safety variants
- 3 weeks: Training runs (many seeds)
- 2 weeks: Metrics implementation
- 2 weeks: Analysis

**Difficulty**: Medium-High
- Stochastic (need many runs)
- Estimator design non-trivial (θ-space vs behavior-space)
- No ground truth like Langton

---

### System 3: Continuous Optimization (Gradient Flows)

**Why Gradient Flows?**
- Tests continuous-time version
- Validates theoretical toy model (from fit_continuous_toy_paper.md)
- Cleanest mathematical setting

**Implementation**:
```python
# Gradient descent on known landscapes
- Rosenbrock function (banana-shaped valley)
- Rastrigin function (many local minima)
- Convex quadratic (baseline)
```

**Target Propositions**:
- **P2** (Constraint monotonicity): In strongly convex case
- **P3** (Force decay): ||∇f(x_t)||² decay
- **P5** (Recovery time): Perturbation response
- **Theoretical validation**: Compare to continuous theorems

**Expected Timeline**: 1 month
- 1 week: Implementation (simple)
- 1 week: Runs on multiple landscapes
- 2 weeks: Compare to theoretical predictions

**Difficulty**: Low-Medium
- Deterministic (or controlled noise)
- Mathematics well-understood
- Mainly validates continuous-time theory

---

### System 4: Flocking/Swarm Models (Optional)

**Why Flocking?**
- Tests multi-agent coordination
- Emergent collective behavior
- Different from single-agent systems

**Examples**:
- Vicsek model (alignment-based)
- Boids (Reynolds rules)
- Kuramoto oscillators (synchronization)

**Target Propositions**:
- **P11** (Phase transition): Disorder → order
- **P16** (Constraint hierarchy): Individual vs collective constraints
- **P17** (Dimensional collapse): Collective manifold dimension

**Expected Timeline**: 2-3 months (if pursued)

**Difficulty**: Medium-High
- Multi-agent complexity
- Estimator design unclear
- May defer to Tier-3

---

## 🎯 Tier-2 Priorities and Sequencing

### Recommended Order

**Phase 1** (Months 1-3): Core Physics
1. ✅ **Ising Model** first
   - Most important for credibility
   - Connects to established physics
   - Tests critical phenomena (P13-P15)

**Phase 2** (Months 4-6): AI/Learning
2. ✅ **GridWorld RL**
   - Validates AI safety direction
   - Tests in learning context
   - Prepares for AI safety paper submission

**Phase 3** (Months 7-9): Theory Validation
3. ✅ **Gradient Flows**
   - Validates continuous-time theory
   - Simplest mathematical setting
   - Connects to fit_continuous_toy_paper.md

**Optional** (If time/resources):
4. ⚪ Flocking models (defer if needed)

---

## 📋 Success Criteria for Tier-2

### Minimum Success (50% support)
- Ising: P13, P14 supported (critical phenomena)
- GridWorld: P1, P3 supported (learning dynamics)
- Gradient: P2, P3 supported (continuous theory)
- **Interpretation**: Framework extends beyond toy automata

### Good Success (70% support)
- Above + P15 (universality), P11 (transitions), P12 (bottleneck)
- **Interpretation**: Framework robust across system types

### Strong Success (>80% support)
- Most propositions supported across all three systems
- **Interpretation**: Framework has broad applicability

### Acceptable Outcomes
- **Partial failures OK**: As long as mechanistic explanations exist
- **Estimator refinement**: Expected, not failure
- **Scope limitations**: Document clearly

---

## 🛠️ Implementation Requirements

### Code Infrastructure Needed

**Ising Model**:
- `ising_model.py`: Monte Carlo implementation
- `ising_estimators.py`: C, F, I measurements
- `ising_validation.py`: Run propositions P13-P15

**GridWorld RL**:
- `gridworld_env.py`: Environment (already sketched in AI safety paper)
- `gridworld_agents.py`: Standard + safety-constrained
- `rl_estimators.py`: θ-space and behavior-space metrics
- `rl_validation.py`: Track P1, P3, P11, P12, P18

**Gradient Flows**:
- `gradient_landscapes.py`: Test functions
- `continuous_solver.py`: ODE/SDE integration
- `continuous_validation.py`: Compare to theorems

### Common Infrastructure
- **Proposition registry**: YAML format (already designed)
- **Plotting utilities**: Shared across systems
- **Report generation**: Unified format
- **Statistical testing**: Significance tests, confidence intervals

---

## 📊 Expected Outcomes by Proposition

Based on system characteristics:

| Proposition | Ising | GridWorld | Gradient | Overall Expectation |
|-------------|-------|-----------|----------|---------------------|
| P1 (Nirvana persist) | N/A | ✅ High | ✅ High | 2/2 support |
| P2 (Constraint monotone) | ✅ Medium | ⚠️ Medium | ✅ High | 2-3/3 support |
| P3 (Force decay) | ✅ High | ✅ High | ✅ High | 3/3 support |
| P4 (Plateau detect) | ✅ High | ⚠️ Medium | ✅ High | 2-3/3 support |
| P5 (Recovery time) | ⚠️ Medium | ✅ High | ✅ High | 2-3/3 support |
| P11 (Phase transition) | ✅ High | ✅ High | ⚠️ Low | 2/3 support |
| P12 (Info bottleneck) | N/A | ✅ High | N/A | 1/1 support |
| P13 (Critical slowing) | ✅ **Very High** | N/A | N/A | 1/1 support |
| P14 (Scale-free) | ✅ **Very High** | N/A | N/A | 1/1 support |
| P15 (Universality) | ✅ High | N/A | N/A | 1/1 support |
| P16 (Hierarchy) | ⚠️ Medium | ✅ Medium | ⚠️ Low | 1-2/3 support |
| P17 (Dimension collapse) | ⚠️ Medium | ✅ Medium | ✅ High | 2-3/3 support |
| P18 (Timescale sep) | ✅ High | ✅ High | ✅ High | 3/3 support |

**Predicted Tier-2 Overall**: 65-75% support (similar to Tier-1)

---

## ⚠️ Known Challenges

### Ising Model
- **Challenge**: Estimator design for C(t) in spin systems
- **Solution**: Use magnetization correlation length, susceptibility
- **Risk**: Low (well-studied system)

### GridWorld RL
- **Challenge**: High variance, need many runs
- **Solution**: 50+ seeds, statistical significance tests
- **Risk**: Medium (stochastic)

### Gradient Flows
- **Challenge**: Gap between theory (convex) and practice (non-convex)
- **Solution**: Test both, document scope limits
- **Risk**: Low (theory well-developed)

### General
- **Estimator coherence (P10)**: Must validate for each new system
- **Time investment**: Each system = 1-3 months
- **Burnout risk**: Pace yourself, not all at once

---

## 🎓 Learning Goals

Tier-2 should teach us:

1. **Does FIT extend beyond cellular automata?**
   - Answer: Ising will tell us (physics credibility)

2. **Can FIT handle stochasticity?**
   - Answer: GridWorld RL will tell us

3. **Does continuous-time theory match practice?**
   - Answer: Gradient flows will tell us

4. **Are estimators transferable?**
   - Answer: If same C estimators work across systems

5. **What are the failure modes?**
   - Answer: Document all challenges for v3.0 improvements

---

## 📅 Realistic Timeline (Starting January 2026)

**Month 1-2** (Jan-Feb 2026): Ising Model
- Week 1-2: Implementation + basic validation
- Week 3-4: P13 (critical slowing) measurement
- Week 5-6: P14, P15 (universality)
- Week 7-8: Write-up + figures

**Month 3-4** (Mar-Apr 2026): GridWorld RL
- Week 1-3: Environment + agents
- Week 4-6: Training runs (many seeds)
- Week 7-8: P1, P3, P11 analysis
- Week 9-10: P12, P18 analysis
- Week 11-12: Write-up

**Month 5-6** (May-Jun 2026): Gradient Flows
- Week 1-2: Implementation
- Week 3-4: Validation runs
- Week 5-6: Theory comparison
- Week 7-8: Integration + summary

**Month 7-9** (Jul-Sep 2026): Synthesis
- Tier-2 summary paper
- Update FIT to v2.4 (if needed)
- Or: Begin v3.0-C (continuous-time)

---

## 💡 Strategic Considerations

### When to Start Tier-2?

**Not immediately**:
- Tier-1 results need to be published first
- Community feedback should inform Tier-2 design
- Let v2.3 "settle" for 2-3 months

**Ideal start time**: 
- After FIT v2.3 on arXiv/GitHub (1 month to settle)
- After initial community feedback (identify weak points)
- **Suggested**: February-March 2026

### Who Should Do It?

**Options**:
1. **You alone**: 9 months full timeline
2. **You + collaborators**: 6 months, better estimators
3. **Community**: Distribute systems, faster but coordination overhead

**Recommendation**: 
- Start Ising alone (establish pattern)
- Recruit collaborators for GridWorld (AI safety interest)
- Open-source gradient flows (easy for others to replicate)

### Integration with AI Safety Paper

**GridWorld RL results** can directly feed into AI safety paper:
- Use same environment
- Generate real data for Section 5 tables
- Validate T-theory predictions empirically

**Timeline alignment**:
- AI safety paper submission: March-April 2026 (NeurIPS)
- GridWorld Tier-2: March-April 2026
- **Perfect overlap**: Kill two birds with one stone

---

## 🎯 Current Recommendation

### Before Starting Tier-2

**Priority 1** (Next 2 weeks): 
- ✅ Publish FIT v2.3 (GitHub + LessWrong)

**Priority 2** (Weeks 3-4):
- ✅ Gather community feedback
- ✅ Identify which propositions people most want tested

**Priority 3** (Weeks 5-8):
- ✅ AI safety paper experiments (= GridWorld Tier-2)
- ✅ This doubles as both AI paper and Tier-2 validation

**Priority 4** (Month 3+):
- ✅ Ising model (if community feedback suggests)
- ✅ Or: Move to continuous-time FIT v3.0-C

### Don't Rush

- Tier-1 (67% support) is already strong
- Better to have solid Tier-1 + v2.3 published
- Than to have messy Tier-2 + nothing published

**Tier-2 can wait 2-3 months.** Focus on launch first.

---

## ✅ Summary

**What Tier-2 is**:
- Ising model, GridWorld RL, gradient flows
- 3-9 months of work
- Tests ~12 propositions in more "realistic" settings

**When to do it**:
- Not now (focus on v2.3 launch)
- Start February-March 2026
- Align GridWorld with AI safety paper

**Expected outcome**:
- 65-75% support (similar to Tier-1)
- Broader scope validation
- Either confirm framework or reveal scope limits

**Strategic value**:
- Ising: Physics credibility
- GridWorld: AI safety application
- Gradient: Theory validation

**Your immediate focus should be**: 
1. Publish v2.3 ✅
2. Write AI safety paper ✅  
3. Let Tier-2 come naturally as part of that work ✅

---

**Bottom line**: Tier-2 is planned and important, but **not urgent**. You have 2-3 months before needing to think about it seriously.

