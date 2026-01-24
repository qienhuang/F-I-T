
# Case 01 — Smartphones and the Attention System

## Scope & Claims Notice

This case illustrates how the FIT framework can be *applied* under a specific
interpretive lens and estimator choice.

It does NOT constitute proof, prediction, or universal validation.
The analysis is structural, not normative.

## System Snapshot
Modern smartphones form a closed-loop attention system combining devices,
apps, notifications, and behavioral feedback.
The system optimizes for engagement, not long-term human goals.

## FIT Variable Mapping
- F: Notifications, social feedback, novelty signals
- I: Habits, learned attention patterns, app usage routines
- T: Sub-second feedback loops, daily repetition
- C: Cognitive bandwidth, sleep, emotional regulation

## Boundary (what is in-scope)

In-scope system boundary (a minimal, auditable version):

- One user (or a defined cohort), one device, and a fixed set of apps + OS settings.
- Explicit intervention surface: notification policy, feed ranking knobs, app limits, and OS-level friction.

Out of scope: macro political economy, smartphone supply chain, and cultural narratives (not because they are unimportant, but because the boundary becomes non-auditable).

## Oracle (what counts as "better" under this boundary)

A usable case needs at least one measurable evaluation channel. Examples:

- Behavioral: unlock frequency, notification-response latency, session length distribution, night-time usage share.
- Self-report: perceived control, stress, sleep quality (as a survey instrument).
- Task performance: sustained-focus task scores (if you run a controlled study).

## Minimal estimator tuple (suggested)

Write down an explicit estimator tuple for your boundary:

`E = (S_t, B, {F_hat, C_hat, I_hat}, W)`

One workable choice for this case:

- `S_t` (state): rolling behavioral logs + current notification policy + current app set.
- `B` (boundary): the cohort definition, app set, OS settings, and the measurement protocol you will not change mid-study.
- `F_hat` (force proxy): notification arrival rate, notification "interruptiveness" (e.g., sound/vibration), and ranking/recency pressure.
- `C_hat` (constraint proxy): sleep debt proxy, time budget pressure, and subjective fatigue (kept as measured quantities, not moral labels).
- `I_hat` (information proxy): habit persistence (e.g., autocorrelation of unlock rate; stability of app-session composition).
- `W` (window): a fixed window for aggregation (e.g., 7-day rolling; plus a day/night split).

## Event definition (illustrative)

Define one event so the case is evaluable:

- Target event `E_entrench` (Phi3 entrenchment): sustained dominance of notification-triggered engagement.
- Example operationalization (choose your own thresholds and preregister them):
  - `notif_open_share_7d >= 0.70`, and
  - `unlock_rate_7d` is stable or increasing, and
  - night-time usage share is non-decreasing.

Do not treat this as a moral judgment; treat it as a regime label for analysis.

## Phase Map
Use Phi1/Phi2/Phi3 as a teaching shorthand (not a claim that any individual must progress this way).

Phi1 (Accumulation):
- Rapid habit formation
- High novelty, weak user-level governance

Phi2 (Crystallization):
- Stable compulsive usage patterns
- Predictable daily loops

Phi3 (Coordination):
- Behavior stabilized, hard to change
- System absorbs user intent rather than serving it

## PT-MSS Check
Look for (at least) three co-occurring signals:

- Force redistribution: notifications and ranking incentives dominate user intent.
- Information re-encoding: attention policy becomes implicit habit (not an explicit choice).
- Constraint reorganization: external obligations (sleep/work) are routed through the device, so attention is always available to the loop.

## Post-Phi3 Bifurcation

Stability of the loop does not imply user wellbeing.
Path A (Collapse):
- Burnout, reduced attention span, loss of agency

Path B (Hierarchical Transition):
- New Force: intentional constraints (design limits, OS-level control)
- New Information: reflective habits, delayed feedback
- Old constraints embedded, not removed

## Monitorability exercise (early warning, not moral judgment)

Treat "Phi3 entrenchment" as a target event and ask whether you can get usable alarms:

- Candidate score: ratio of notification-triggered opens to intentional opens; or growth rate of unlock frequency.
- Alarm criterion: can you set a threshold with a tolerable false-positive rate (FPR), or do you get an FPR floor (degenerate alarm)?

See: `docs/core/monitorability.md`.

## Minimal logging schema (practical)

If you want this case to be "hard" enough to support future demos, define a minimal log schema:

- `ts` (timestamp)
- `event_type` (`unlock`, `notif_received`, `notif_open`, `app_open`, `session_end`)
- `app_id`
- `trigger` (`notification`, `intentional`, `unknown`)
- `session_seconds`
- `is_night` (boolean; preregister your definition)

From this schema you can compute the core proxies above (unlock rate, notification share, session distributions) without overfitting to anecdotes.

## One falsifiable claim (pick exactly one; illustrative)

Example protocol claim (not asserted here):

> Under a fixed app set and a fixed cohort boundary, batching notifications to 3 delivery windows/day reduces unlock frequency by at least X% without increasing missed-critical-message rate beyond Y%.

## Takeaways
- Stability does not imply wellbeing.
- Escaping Phi3 requires structural intervention, not willpower alone.
- Attention systems are governance problems, not personal failures

---

*Further applied discussion exists in an external whitepaper [`Humane Attention Whitepaper`](https://github.com/qienhuang/humane-attention-whitepaper).*
