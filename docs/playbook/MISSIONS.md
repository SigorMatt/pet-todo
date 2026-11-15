# Missions

```agent-room-state
lease_session: 635a4978
lease_generation: 1
phase: 1
room: 1
mission: M1
step: PR
pr: none
cursor: none
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
| M1 | `mission/M1-store-add-list` | in progress | | P1-1 (also makes `main` green) |
| M2 | `mission/M2-done-remove` | planned | | P1-2 |
| M3 | `mission/M3-due-overdue` | planned | | P1-3 |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- A failed save prints `todo: cannot write <path>` and exits 1 (DESIGN Interfaces: errors start `todo: `, exit 1; cold M1 R1-3).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).

## Current mission

- **Mission:** M1, `mission/M1-store-add-list`.
- **Scope:** Create the `todo` package (run as `python3 -m todo`) and the `tests` package, which makes the test command pass on `main`. `todo/store.py` loads and atomically saves the JSON list at `$TODO_FILE` (else `./todo.json`); `todo/cli.py` implements `add TEXT` and `list`. Nothing of P1-2 or P1-3.
- **Criteria:**
  - P1-1 add: unittest that `add "buy milk"` prints `added 1` and creates `$TODO_FILE`, and a second add prints `added 2`.
  - P1-1 list: unittest that `list` prints `1 [ ] buy milk`, `2 [ ] …` in ID order, and nothing for an empty list.
  - P1-1 read errors: unittest that a missing file reads as empty, and a non-JSON file prints `todo: cannot read <path>` on stderr and exits 1.
  - P1-1 atomic save: unittest that a failing write leaves the original file intact and no temporary file behind.
- **Ledger items:** none.
- **Spec revision:** 45f27de060f74f758513aea77cd1487419202b10, pipeline main.
- **Tasks:**
  - M1-A store: `todo/__init__.py`, `todo/store.py`, `tests/__init__.py`, `tests/test_store.py`. API: `default_path()`, `load(path) -> dict` (missing file gives `{"next_id": 1, "items": []}`), `save(path, data)` (temp file in the same directory, then `os.replace`), `StoreError` carrying the path. Done when: store tests cover missing, non-JSON and failed-write cases, and the test command passes.
  - M1-B CLI add and list: `todo/__main__.py`, `todo/cli.py` (`main(argv=None) -> int`), `tests/test_cli.py`. Done when: the add, list and cannot-read criteria above pass as unittests with a per-test temporary `TODO_FILE`, and the test command passes. Depends on M1-A.

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |
| M1-A | worktree-agent-a8a69e04a7a6ab938 | 1 | merged 4b3489d |
| M1-B | worktree-agent-a4776bb98a0ea3690 | 1 | merged 9c4fe8a |
| M1-F1 (fix R1-1..R1-5) | worktree-agent-a7e28fbc235b08920 | 1 | merged dc80748 |

### Parked questions

- none
