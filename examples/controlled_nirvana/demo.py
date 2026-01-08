from __future__ import annotations

import random
import time

from emptiness_window import EmptinessWindowConfig, EmptinessWindowController, IrreversibleCommitBuffer, JsonlAuditLogger, TriggerMetrics


def main() -> None:
    audit = JsonlAuditLogger("examples/controlled_nirvana/_out/demo_audit.jsonl")
    cfg = EmptinessWindowConfig(theta_m=0.8, eps=0.45, min_queue_len=0, min_open_s=0.3, cooldown_s=0.2)

    controller = EmptinessWindowController(cfg, audit=audit)
    buffer = IrreversibleCommitBuffer(audit=audit)

    decision_cycle_s = 0.5
    correction_latency_s = 0.2

    print("Demo: Controlled Nirvana / Emptiness Window (toy simulation)")
    print("Audit log: examples/controlled_nirvana/_out/demo_audit.jsonl")

    for step in range(1, 41):
        # Simulate a system where self-gating ramps up, and occasionally correction latency worsens.
        self_gate_strength = min(1.0, max(0.0, 0.25 + 0.03 * step + random.uniform(-0.05, 0.05)))
        if step in (15, 16, 17, 18, 19, 20):
            correction_latency_s = 0.6 + random.uniform(0.0, 0.2)
        else:
            correction_latency_s = 0.2 + random.uniform(0.0, 0.1)

        # Update controller first so the next commit attempt can be deferred if the window is open.
        metrics = TriggerMetrics(
            decision_cycle_s=decision_cycle_s,
            correction_latency_s=correction_latency_s,
            self_gate_strength=self_gate_strength,
            irreversible_queue_len=len(buffer),
        )

        was_open = controller.is_open
        controller.update(metrics)
        now_open = controller.is_open

        if (not was_open) and now_open:
            print(f"[step {step:02d}] WINDOW OPEN (self_gate={self_gate_strength:.2f}, latency_ratio={metrics.correction_latency_ratio():.2f})")
        if was_open and (not now_open):
            print(f"[step {step:02d}] WINDOW CLOSED -> flushing {len(buffer)} buffered commit(s)")
            buffer.flush()

        # Submit an irreversible action every few steps (e.g., deploy, delete, permission escalation).
        if step % 3 == 0:
            buffer.submit(
                kind="irreversible_commit",
                window_open=controller.is_open,
                fn=lambda s=step: f"commit@step={s}",
            )

        time.sleep(0.05)

    # End: ensure no buffered commits remain
    if len(buffer) > 0:
        print(f"[final] flushing {len(buffer)} buffered commit(s)")
        buffer.flush()

    print("Done.")


if __name__ == "__main__":
    main()
