# Missions

```agent-room-state
lease_session: 252beb84
lease_generation: 2
phase: 1
room: 1
mission: M2
step: build
pr: none
cursor: 6897870993
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
| M2 | `mission/M2-done-remove` | in progress | | P1-2 |
| M3 | `mission/M3-due-overdue` | planned | | P1-3 |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- A failed save prints `todo: cannot write <path>` and exits 1 (DESIGN Interfaces: errors start `todo: `, exit 1; cold M1 R1-3).
- L-2: `load` repairs a bad `next_id` to `max(stored ids)+1` (at least 1) rather than refusing the file; this keeps DESIGN's "IDs are never reused" without a new error message. A missing or non-integer `next_id` still reads as `todo: cannot read <path>` (existing shape check kept; M2-T2 question).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).

## Current mission

- **Mission:** M2, `mission/M2-done-remove`.
- **Scope:** Add the `done ID` and `remove ID` commands to `python3 -m todo`, as in DESIGN.md Interfaces. `list` hides done items unless `--all`, which shows `[x]`. IDs are never reused after a removal, including when the stored `next_id` is too low or invalid (L-2).
- **Criteria:**
  - P1-2 a: `done ID` prints `done <id>`, `list` hides it, `list --all` shows `[x]`; doing it twice is not an error (unittest in `tests/test_cli.py`).
  - P1-2 b: `remove ID` prints `removed <id>`; after removing the highest ID, the next `add` gets a new ID (unittest).
  - P1-2 c: an unknown ID (and a non-integer ID) prints `todo: no item <id>` and exits 1 for both commands (unittest).
- **Ledger items:** L-2 (`load` accepts a `next_id` not above every stored ID, or below 1).
- **Spec revision:** 45f27de060f74f758513aea77cd1487419202b10, pipeline main.
- **Tasks:**
  - T1 done/remove: `todo/cli.py`, `todo/store.py` if needed, `tests/test_cli.py`. Done when: P1-2 a–c unittests pass and the full suite is green.
  - T2 L-2: `todo/store.py`, `tests/test_store.py`. `load` never yields a `next_id` at or below a stored ID or below 1 (repair to `max(id)+1`, at least 1). Done when: a unittest with a hand-edited file (`next_id` 1 with item 3; `next_id` 0; missing) shows `add` hands out a fresh ID, and the full suite is green.

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |
| M2-T1 | builder a62f6a1ec7ed2c6ee (worktree) | 1 | merged cb5f417 |
| M2-T2 | builder a47810d72aee0e554 (worktree) | 1 | merged 3759fc6 |

### Parked questions

- none
