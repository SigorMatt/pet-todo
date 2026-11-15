# Missions

```agent-room-state
lease_session: 635a4978
lease_generation: 1
phase: 1
room: 1
mission: M1
step: spec
pr: merged:2
cursor: 6897870993
counter: 0
intent: none
waiting_for_owner: no
status: running
mission_started: 2026-11-15T16:27:57Z
```

Owned by the lead. Only `room.py` edits the block above (`state set`, `state next`, `lease take`, `handoff`); edit the rest by hand and commit with `room.py state commit -m MSG`. `status` is running, paused, stopped or done; `mission_started` is the ISO-8601 UTC time the mission's spec was recorded.

## Phase 1

| Mission | Branch | Status | PR | Criteria |
| --- | --- | --- | --- | --- |
| M1 | `mission/M1-store-add-list` | merged | #2 (12d2b13) | P1-1 (also makes `main` green) |
| M2 | `mission/M2-done-remove` | planned | | P1-2 |
| M3 | `mission/M3-due-overdue` | planned | | P1-3 |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- A failed save prints `todo: cannot write <path>` and exits 1 (DESIGN Interfaces: errors start `todo: `, exit 1; cold M1 R1-3).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).

## Current mission

- none (M1 merged as 12d2b13; M2 next)

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |

### Parked questions

- none
