# Missions

```agent-room-state
lease_session: 9078db43
lease_generation: 7
phase: 2
room: 5
mission: M5
step: cold round 1
pr: none
cursor: 6919484038
counter: 1
intent: none
waiting_for_owner: no
status: running
mission_started: 2026-11-16T14:39:41Z
```

Owned by the lead. Only `room.py` edits the block above (`state set`, `state next`, `lease take`, `handoff`); edit the rest by hand and commit with `room.py state commit -m MSG`. `status` is running, paused, stopped or done; `mission_started` is the ISO-8601 UTC time the mission's spec was recorded.

## Phase 1

| Mission | Branch | Status | PR | Criteria |
| --- | --- | --- | --- | --- |
| M1 | `mission/M1-store-add-list` | merged | #2 (12d2b13) | P1-1 (also makes `main` green) |
| M2 | `mission/M2-done-remove` | merged | #3 (9ffe9a1) | P1-2 |
| M3 | `mission/M3-due-overdue` | merged | #4 (35b908d) | P1-3 |

## Phase 2

| Mission | Branch | Status | PR | Criteria |
| --- | --- | --- | --- | --- |
| M4 | `mission/M4-text-and-ids` | merged | #6 (afaabb6) | P2-2, P2-3 (ledger L-3, L-4, L-5, L-6) |
| M5 | `mission/M5-edit` | in progress | | P2-4 |
| M6 | `mission/M6-lock` | planned | | P2-1 (ledger L-1; c3 waits on Q-1) |

## Lead decisions

- Phase 1 plan: the template's placeholder M1 row was replaced, so missions are M1–M3 (planner's draft numbered them M2–M4).
- `list --all --overdue` behaves like `list --overdue` (DESIGN: overdue shows only open items).
- A failed save prints `todo: cannot write <path>` and exits 1 (DESIGN Interfaces: errors start `todo: `, exit 1; cold M1 R1-3).
- L-2: `load` repairs a bad `next_id` to `max(stored ids)+1` (at least 1) rather than refusing the file; this keeps DESIGN's "IDs are never reused" without a new error message. A missing or non-integer `next_id` still reads as `todo: cannot read <path>` (existing shape check kept; M2-T2 question).
- For `done` and `remove`, a single argument is always the ID, including `-h`/`--help`, which give `todo: no item <arg>`; `todo -h`, `add -h` and `list -h` still show help (cold M2 R1-2; the earlier choice to keep `done -h` as help failed audit twice).
- Stored item IDs must be 1..MAX_ID (2**63-1) and `next_id` at most MAX_ID+1, else `todo: cannot read`; an `add` past MAX_ID prints `todo: cannot write <path>` (qodo PR #3 findings on negative and large IDs).
- Today for `list --overdue` is injected through a `today` parameter of `cli.main` (playbook: lead's discretion).
- Phase 2 plan: M4 text and IDs, M5 edit, M6 lock last (its criteria name `edit`, and P2-1 c3 waits on Q-1, escalated at phase start).
- `0` and the empty string are `bad id` (D-3); a well-formed 19-digit ID above MAX_ID is `no item`.
- `done -h` / `remove --help` now give `todo: bad id -h` (D-3), superseding the phase 1 choice that they give `no item`.
- Argument checks (text, ID, date) run before the file is loaded (and before the lock in M6). For `edit` with a bad ID and bad text, `bad id` wins.
- Dash-led TEXT for `edit` behaves like `add` (usage error unless after `--`).
- D-2 is applied as written: only category Cc is rejected, so U+2028/U+2029 are accepted.
- Stored text that D-2 would reject (hand-edited files) is out of scope: P2-2 c2 covers only text `add` accepts.
- `edit` check order: bad id, bad text, then load, then no item, then item is done (D-6 check after lookup).
- Lock path is `$TODO_FILE` + `.lock` literally (D-4 wording); the lock file stays on disk (lock file mode is lead's discretion).

## Current mission

- **Mission:** M5, `mission/M5-edit`.
- **Scope:** Add `edit ID TEXT` to the CLI (DESIGN Interfaces): replace an item's text and print `edited <id>`, keeping its ID, done state and due date. A done item can't be edited (D-6). Reuse M4's text and ID checks so bad text gives `todo: bad text` and a bad ID gives `todo: bad id <value>`, both before the file is loaded; an unknown ID gives `todo: no item <id>`. No locking (M6).
- **Criteria:**
  - P2-4 c1: `edit ID TEXT` replaces the text, prints `edited <id>`, done/due/ID unchanged — unittest in `tests/test_cli.py`.
  - P2-4 c2: unknown ID → `todo: no item <id>`; bad text and bad IDs fail as P2-2/P2-3 (exit 1, file unchanged) — unittests.
  - P2-4 c3 (CHANGE-1, D-6): `edit` on a done item → `todo: item <id> is done`, exit 1, file unchanged — unittest.
- **Ledger items:** none target M5.
- **Spec revision:** b5e0959251057487342e9ade7f4ef375f32ead9f, pipeline main (CHANGE-1 applies now: D-6, P2-4 c3; was 1fadca5).
- **Tasks:**
  - T1: `edit` subcommand in `todo/cli.py` (parser, `_cmd_edit`, ID/text guards like `done`/`remove`/`add`, dash-led TEXT as for `add`) plus unittests in `tests/test_cli.py` covering both criteria. Done when: `python3 -m unittest discover -s tests -t .` passes and `python3 -m todo edit` works end to end on a temp `TODO_FILE`.
  - T2 (CHANGE-1): `edit` on a done item refuses with `todo: item <id> is done`, exit 1, file unchanged; adjust T1's tests that edited done items to edit open ones (the criterion changed, not a weakening). Done when: a unittest for c3 passes and the full suite passes.

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |
| M5-T1 | builder abe2cab05e345285b (worktree) | 1 | merged (1e62492) |
| M5-T2 | builder abe2cab05e345285b (resumed) | 1 | running |

### Parked questions

- none
