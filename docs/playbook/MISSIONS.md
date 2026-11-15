# Missions

```agent-room-state
lease_session: none
lease_generation: 2
phase: 1
room: 1
mission: M2
step: spec
pr: merged:3
cursor: 6898483510
counter: 0
intent: none
waiting_for_owner: no
status: running
mission_started: 2026-11-15T17:07:29Z
```

Owned by the lead. Only `room.py` edits the block above (`state set`, `state next`, `lease take`, `handoff`); edit the rest by hand and commit with `room.py state commit -m MSG`. `status` is running, paused, stopped or done; `mission_started` is the ISO-8601 UTC time the mission's spec was recorded.

## Phase 1

| Mission | Branch | Status | PR | Criteria |
| --- | --- | --- | --- | --- |
| M1 | `mission/M1-store-add-list` | merged | #2 (12d2b13) | P1-1 (also makes `main` green) |
| M2 | `mission/M2-done-remove` | merged | #3 (9ffe9a1) | P1-2 |
| M3 | `mission/M3-due-overdue` | planned | | P1-3 |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- A failed save prints `todo: cannot write <path>` and exits 1 (DESIGN Interfaces: errors start `todo: `, exit 1; cold M1 R1-3).
- L-2: `load` repairs a bad `next_id` to `max(stored ids)+1` (at least 1) rather than refusing the file; this keeps DESIGN's "IDs are never reused" without a new error message. A missing or non-integer `next_id` still reads as `todo: cannot read <path>` (existing shape check kept; M2-T2 question).
- For `done` and `remove`, a single argument is always the ID, including `-h`/`--help`, which give `todo: no item <arg>`; `todo -h`, `add -h` and `list -h` still show help (cold M2 R1-2; the earlier choice to keep `done -h` as help failed audit twice).
- Stored item IDs must be 1..MAX_ID (2**63-1) and `next_id` at most MAX_ID+1, else `todo: cannot read`; an `add` past MAX_ID prints `todo: cannot write <path>` (qodo PR #3 findings on negative and large IDs).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).

## Current mission

- none (M2 merged as 9ffe9a1; M3 next)

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |

### Parked questions

- none
