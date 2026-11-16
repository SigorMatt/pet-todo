# Missions

```agent-room-state
lease_session: ee4486a1
lease_generation: 5
phase: 2
room: 5
mission: M4
step: build
pr: none
cursor: none
counter: 1
intent: none
waiting_for_owner: no
status: running
mission_started: 2026-11-16T08:52:44Z
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
| M4 | `mission/M4-text-and-ids` | in progress | | P2-2, P2-3 (ledger L-3, L-4, L-5, L-6) |
| M5 | `mission/M5-edit` | planned | | P2-4 |
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
- Lock path is `$TODO_FILE` + `.lock` literally (D-4 wording); the lock file stays on disk (lock file mode is lead's discretion).

## Current mission

- **Mission:** M4, `mission/M4-text-and-ids`.
- **Scope:** `add` rejects bad text per D-2 with `todo: bad text`; `done` and `remove` reject malformed IDs per D-3 with `todo: bad id <value[:20]>`; `add` past MAX_ID prints `todo: no more ids`. All three exit 1 and leave the file unchanged. The text and ID checks are shared helpers in `todo/cli.py` so M5's `edit` can reuse them.
- **Criteria:** P2-2 c1 (unittest per bad-text case, file unchanged); P2-2 c2 (unittest: `list` one line per accepted text, plus strict-UTF-8 stdout subprocess); P2-3 c1 for `done`/`remove` (unittests for `01`, `-1`, `1.0`, `abc`, 5000 digits; `edit`'s share in M5); P2-3 c2 (unittest with a prepared file at MAX_ID).
- **Ledger items:** L-3, L-4, L-5, L-6 (all targeted `phase 2 backlog`, placed here).
- **Spec revision:** d7e84b85dccdedcbe662ae5a538a211673415a77, pipeline main.
- **Tasks:**
  - T1+T2 (text, one builder): D-2 check on `add` before load (empty/whitespace, any Cc, non-UTF-8 argv i.e. surrogate escapes); tests per case incl. a subprocess with non-UTF-8 argv bytes; `list` one-line-per-item test for accepted texts and a strict-UTF-8 stdout run. Files: `todo/cli.py`, `tests/test_cli.py`. Done when: `<test>` green with those tests.
  - T3+T4 (IDs, one builder): D-3 ID check on `done`/`remove` before load; update phase 1 tests that now expect `bad id`; `add` past MAX_ID gives `todo: no more ids` (replacing the `cannot write` test), `cannot write` kept for OS errors. Files: `todo/cli.py`, `tests/test_cli.py`. Done when: `<test>` green with those tests.

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |
| M4-T1T2 (text) | builder a0ebbbde7d925bed6 | 1 | running |
| M4-T3T4 (IDs) | builder af3123fa0f0cbbee0 | 1 | merged (870fa40) |

### Parked questions

- none
