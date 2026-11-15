# Missions

```agent-room-state
lease_session: 635a4978
lease_generation: 1
phase: 1
room: 1
mission: none
step: spec
pr: none
cursor: none
counter: 0
intent: none
waiting_for_owner: no
status: running
mission_started: none
```

Owned by the lead. Only `room.py` edits the block above (`state set`, `state next`, `lease take`, `handoff`); edit the rest by hand and commit with `room.py state commit -m MSG`. `status` is running, paused, stopped or done; `mission_started` is the ISO-8601 UTC time the mission's spec was recorded.

## Phase 1

| Mission | Branch | Status | PR | Criteria |
| --- | --- | --- | --- | --- |
| M1 | `mission/M1-store-add-list` | planned | | P1-1 (also makes `main` green) |
| M2 | `mission/M2-done-remove` | planned | | P1-2 |
| M3 | `mission/M3-due-overdue` | planned | | P1-3 |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).

## Current mission

- **Spec revision:** <state-branch commit of PLAYBOOK.md and DESIGN.md>, pipeline <version>
- **Recorded step:** spec | build | cold round n | PR #n | Qodo round n | gate | waiting for owner
- **Ledger items:** none

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |

### Parked questions

- none
