# Missions

```agent-room-state
lease_session: 5d8b80b8
lease_generation: 3
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
| M3 | `mission/M3-due-overdue` | in progress | | P1-3 |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- A failed save prints `todo: cannot write <path>` and exits 1 (DESIGN Interfaces: errors start `todo: `, exit 1; cold M1 R1-3).
- L-2: `load` repairs a bad `next_id` to `max(stored ids)+1` (at least 1) rather than refusing the file; this keeps DESIGN's "IDs are never reused" without a new error message. A missing or non-integer `next_id` still reads as `todo: cannot read <path>` (existing shape check kept; M2-T2 question).
- For `done` and `remove`, a single argument is always the ID, including `-h`/`--help`, which give `todo: no item <arg>`; `todo -h`, `add -h` and `list -h` still show help (cold M2 R1-2; the earlier choice to keep `done -h` as help failed audit twice).
- Stored item IDs must be 1..MAX_ID (2**63-1) and `next_id` at most MAX_ID+1, else `todo: cannot read`; an `add` past MAX_ID prints `todo: cannot write <path>` (qodo PR #3 findings on negative and large IDs).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).

## Current mission

- **Mission:** M3, `mission/M3-due-overdue`.
- **Scope:** Add due dates to items: `add TEXT --due YYYY-MM-DD` stores an ISO date, and `list` shows ` (due YYYY-MM-DD)` after the text. Add `list --overdue`, which shows only open items whose due date is before today, with today injected through a `today` parameter of `cli.main` (Lead decisions). A bad date prints `todo: bad date <value>` and exits 1. `store.py` accepts and keeps the optional `due` field (absent or an ISO date string, per DESIGN Data).
- **Criteria:**
  - P1-3 a: `add TEXT --due YYYY-MM-DD` stores the date and `list` shows ` (due YYYY-MM-DD)`: unittest in `tests/test_cli.py` checking stdout and the stored JSON.
  - P1-3 b: `list --overdue` shows only open items due before today, today injected: unittest with a fixed `today` covering past, today, future, no-due and done items.
  - P1-3 c: a bad date prints `todo: bad date <value>` and exits 1: unittest with malformed and impossible dates (e.g. `2026-13-01`, `2026-02-30`, `tomorrow`), file unchanged.
- **Ledger items:** none target M3.
- **Spec revision:** a34dc4ab73772a41d5d39925752ec7bc54a47668, pipeline `main`.
- **Tasks:**
  - **M3-A** due dates on add and list, bad date. Files: `todo/cli.py`, `todo/store.py`, `tests/test_cli.py`, `tests/test_store.py`. Done when: P1-3 a and c tests pass with the suite.
  - **M3-B** `list --overdue` with injected today. Files: `todo/cli.py`, `tests/test_cli.py`. Done when: P1-3 b tests pass with the suite. Runs after M3-A is merged (same files).

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |

### Parked questions

- none
