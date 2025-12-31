#!/usr/bin/env python3
"""Run the self-referential IO demo."""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Tuple
import random

random.seed(42)
np.random.seed(42)

# MetricsTracker
@dataclass
class MetricsTracker:
    validation_lag: List[float] = field(default_factory=list)
    rollback_feasibility: List[float] = field(default_factory=list)
    gate_bypass_events: List[int] = field(default_factory=list)
    tempo: List[float] = field(default_factory=list)
    _cumulative_bypass: int = 0

    def record(self, vl: float, rollback_feas: float, bypassed: bool, cycle_time: float):
        self.validation_lag.append(vl)
        self.rollback_feasibility.append(rollback_feas)
        if bypassed:
            self._cumulative_bypass += 1
        self.gate_bypass_events.append(self._cumulative_bypass)
        self.tempo.append(cycle_time)

    def summary(self) -> dict:
        return {
            'final_VL': self.validation_lag[-1] if self.validation_lag else 0,
            'mean_VL': np.mean(self.validation_lag) if self.validation_lag else 0,
            'final_rollback_feasibility': self.rollback_feasibility[-1] if self.rollback_feasibility else 1,
            'total_bypasses': self._cumulative_bypass,
            'final_tempo': self.tempo[-1] if self.tempo else 1,
        }

# SelfReferentialAgent
@dataclass
class SelfReferentialAgent:
    use_coherence_gate: bool = False
    coherence_threshold: float = 0.3
    confidence: float = 0.5
    action_count: int = 0
    loop_depth: int = 0
    max_loop_depth: int = 10
    self_confirmation_bias: float = 0.3

    def self_eval(self) -> float:
        true_signal = 0.5 + 0.1 * np.sin(self.action_count * 0.1)
        noise = np.random.normal(0, 0.1)
        biased_eval = (1 - self.self_confirmation_bias) * (true_signal + noise) + self.self_confirmation_bias * self.confidence
        return np.clip(biased_eval, 0, 1)

    def external_eval(self) -> float:
        true_signal = 0.5 + 0.1 * np.sin(self.action_count * 0.1)
        noise = np.random.normal(0, 0.15)
        return np.clip(true_signal + noise, 0, 1)

    def coherence_gate(self) -> Tuple[bool, float]:
        self_score = self.self_eval()
        external_score = self.external_eval()
        disagreement = abs(self_score - external_score)
        passed = disagreement <= self.coherence_threshold
        return passed, disagreement

    def tool_call(self) -> bool:
        self.action_count += 1
        self.loop_depth += 1
        self.confidence = 0.7 * self.confidence + 0.3 * self.self_eval()
        return True

    def should_continue_loop(self) -> bool:
        self_score = self.self_eval()
        if self.use_coherence_gate:
            if self.loop_depth >= self.max_loop_depth:
                return False
            passed, _ = self.coherence_gate()
            if not passed:
                return False
            return self_score > 0.4
        else:
            return self_score > 0.3

    def reset_loop(self):
        self.loop_depth = 0

# Simulation
def run_simulation(agent, num_steps=100, base_cycle_time=1.0, base_validation_time=2.0):
    tracker = MetricsTracker()
    cycle_time = base_cycle_time
    validation_backlog = 0.0
    rollback_feasibility = 1.0

    for step in range(num_steps):
        agent.reset_loop()
        loop_actions = 0
        while agent.should_continue_loop():
            agent.tool_call()
            loop_actions += 1
            if loop_actions > 50:
                break

        if agent.use_coherence_gate:
            cycle_time = max(0.5, base_cycle_time - 0.01 * step + np.random.normal(0, 0.05))
        else:
            acceleration = 0.02 * (1 + loop_actions * 0.1)
            cycle_time = max(0.1, cycle_time - acceleration + np.random.normal(0, 0.02))

        validation_processed = base_validation_time * 0.8
        changes_produced = 1.0 / max(cycle_time, 0.1)

        if changes_produced > validation_processed:
            validation_backlog += (changes_produced - validation_processed) * 0.5
        else:
            validation_backlog = max(0, validation_backlog - 0.3)

        current_vl = validation_backlog + cycle_time

        if agent.use_coherence_gate:
            rollback_feasibility = max(0.6, 1.0 - 0.002 * step + np.random.normal(0, 0.02))
        else:
            rollback_feasibility = max(0.1, rollback_feasibility - 0.005 * loop_actions + np.random.normal(0, 0.01))

        bypassed = False
        if agent.use_coherence_gate:
            bypassed = random.random() < 0.01
        else:
            bypassed = loop_actions > 5

        tracker.record(vl=current_vl, rollback_feas=rollback_feasibility, bypassed=bypassed, cycle_time=cycle_time)

    return tracker

if __name__ == "__main__":
    # Run scenarios
    print("Running Scenario A (No Gate)...")
    agent_a = SelfReferentialAgent(use_coherence_gate=False, self_confirmation_bias=0.4)
    tracker_a = run_simulation(agent_a, num_steps=100)
    summary_a = tracker_a.summary()

    print("Running Scenario B (With Gate)...")
    random.seed(42)
    np.random.seed(42)
    agent_b = SelfReferentialAgent(use_coherence_gate=True, coherence_threshold=0.3, max_loop_depth=10, self_confirmation_bias=0.4)
    tracker_b = run_simulation(agent_b, num_steps=100)
    summary_b = tracker_b.summary()

    # Print results
    print()
    print("=" * 60)
    print("RESULTS COMPARISON")
    print("=" * 60)
    print(f"{'Metric':<30} {'No Gate':>12} {'With Gate':>12}")
    print("-" * 54)
    print(f"{'Final Validation Lag (hrs)':<30} {summary_a['final_VL']:>12.2f} {summary_b['final_VL']:>12.2f}")
    print(f"{'Mean Validation Lag (hrs)':<30} {summary_a['mean_VL']:>12.2f} {summary_b['mean_VL']:>12.2f}")
    print(f"{'Rollback Feasibility':<30} {summary_a['final_rollback_feasibility']:>11.2%} {summary_b['final_rollback_feasibility']:>11.2%}")
    print(f"{'Total Bypass Events':<30} {summary_a['total_bypasses']:>12} {summary_b['total_bypasses']:>12}")
    print(f"{'Final Cycle Time':<30} {summary_a['final_tempo']:>12.3f} {summary_b['final_tempo']:>12.3f}")

    # Generate plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Self-Referential Agent: No Gate vs P10 Coherence Gate", fontsize=14, fontweight="bold")
    steps = range(len(tracker_a.validation_lag))

    ax1 = axes[0, 0]
    ax1.plot(steps, tracker_a.tempo, "r-", label="No Gate", alpha=0.8, linewidth=2)
    ax1.plot(steps, tracker_b.tempo, "g-", label="With Gate", alpha=0.8, linewidth=2)
    ax1.axhline(y=0.5, color="orange", linestyle="--", alpha=0.5, label="Danger threshold")
    ax1.set_xlabel("Step")
    ax1.set_ylabel("Cycle Time (lower = faster tempo)")
    ax1.set_title("Tempo Amplification")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.2)

    ax2 = axes[0, 1]
    ax2.plot(steps, tracker_a.validation_lag, "r-", label="No Gate", alpha=0.8, linewidth=2)
    ax2.plot(steps, tracker_b.validation_lag, "g-", label="With Gate", alpha=0.8, linewidth=2)
    ax2.axhline(y=10, color="orange", linestyle="--", alpha=0.5, label="VL_MAX threshold")
    ax2.set_xlabel("Step")
    ax2.set_ylabel("Validation Lag (hours)")
    ax2.set_title("Validation Lag (VL) - Governance Cannot Keep Up")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3 = axes[1, 0]
    ax3.plot(steps, tracker_a.rollback_feasibility, "r-", label="No Gate", alpha=0.8, linewidth=2)
    ax3.plot(steps, tracker_b.rollback_feasibility, "g-", label="With Gate", alpha=0.8, linewidth=2)
    ax3.axhline(y=0.5, color="orange", linestyle="--", alpha=0.5, label="RDPR_MIN threshold")
    ax3.set_xlabel("Step")
    ax3.set_ylabel("Rollback Feasibility (0-1)")
    ax3.set_title("Rollback Feasibility - Can We Undo?")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1.1)

    ax4 = axes[1, 1]
    ax4.plot(steps, tracker_a.gate_bypass_events, "r-", label="No Gate (implicit bypasses)", alpha=0.8, linewidth=2)
    ax4.plot(steps, tracker_b.gate_bypass_events, "g-", label="With Gate", alpha=0.8, linewidth=2)
    ax4.set_xlabel("Step")
    ax4.set_ylabel("Cumulative Bypass Count")
    ax4.set_title("Gate Bypass Rate (GBR) - Governance Integrity")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save to docs/ai_safety/figures for easy reference in documentation
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "ai_safety", "figures")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "self_referential_io_comparison.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print()
    print(f"Figure saved: {output_path}")
    print("Demo completed successfully!")
