# Missions

```agent-room-state
lease_session: 589c8742
lease_generation: 8
phase: 2
room: 5
mission: M6
step: PR
pr: none
cursor: 6920067803
counter: 1
intent: open PR mission/M6-lock
waiting_for_owner: no
status: running
mission_started: 2026-11-16T15:02:32Z
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
| M5 | `mission/M5-edit` | merged | #7 (fe04c70) | P2-4 (with CHANGE-1, D-6) |
| M6 | `mission/M6-lock` | in progress | | P2-1 (ledger L-1; c3 settled by D-5) |

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
- Lock timeout and poll interval are injectable through `store.LOCK_TIMEOUT` / `store.LOCK_INTERVAL` (and `store.lock()` arguments), not a `cli.main` parameter (playbook: lead's discretion).
- A lock file that can't be opened (missing or read-only directory) gives `todo: cannot write <path>` for every changing command, before the item lookup; so `done 9` in a read-only directory says `cannot write`, not `no item` (the change can't be made either way).
- Lock path is the resolved data file plus `.lock` (`realpath($TODO_FILE) + ".lock"`), so every name for one data file shares one lock (cold M6 R1-1, R1-2; supersedes the earlier literal-path choice). Messages still name the path as given. The lock file stays on disk (lock file mode is lead's discretion). An existing lock file that can't be opened for writing is opened read-only, since `flock` needs no write access (cold M6 R2-1).

## Current mission

- **Mission:** M6, `mission/M6-lock`.
- **Scope:** Every command that changes the file (`add`, `done`, `remove`, `edit`) takes an exclusive `fcntl.flock` on `<file>.lock` from before loading until after the atomic rename, and releases it on every exit path (D-4). Acquisition polls `LOCK_EX | LOCK_NB` for up to 5 seconds, then prints `todo: file is locked <path>` (the data file path) and exits 1 with the file unchanged (D-5). `list` takes no lock. Argument checks still run before the lock.
- **Criteria:**
  - P2-1 c1: unittest runs two subprocesses that each `add` 50 times against one `TODO_FILE`; the file then holds 100 items with 100 distinct IDs.
  - P2-1 c2: unittests show the lock is held across load and rename for `add`, `done`, `remove`, `edit`, and released after success and after errors (no item, item is done, cannot write).
  - P2-1 c3: unittests with an injectable wait: a lock held past the timeout gives `todo: file is locked <path>`, exit 1, file unchanged; a lock released within the timeout is waited for and the command succeeds.
- **Ledger items:** L-1 (targets phase 2 backlog; this mission fixes it).
- **Spec revision:** b5e0959251057487342e9ade7f4ef375f32ead9f, pipeline main.
- **Tasks:**
  - **M6-T1: lock and wire it in.** Files: `todo/store.py`, `todo/cli.py`, `tests/test_store.py`, `tests/test_cli.py`. A lock context manager in `store.py` (timeout and poll interval injectable), used by `add`, `done`, `remove`, `edit` in `cli.py`. Done when: `python3 -m unittest discover -s tests -t .` passes, with new tests for c2 and c3.
  - **M6-T2: concurrent-run test.** Files: `tests/test_concurrency.py`. Depends on M6-T1. Done when: the c1 test (2 subprocesses × 50 adds, one `TODO_FILE`, 100 items, 100 distinct IDs) passes, and the full `<test>` passes.

### Tasks in flight

| Task | Branch | Attempt | Status |
| --- | --- | --- | --- |
| M6-T1 | builder a4fc1de31586d4703 (worktree) | 1 | merged (a3869be) |
| M6-T2 | builder ab9d0b147964089bd (worktree) | 1 | merged (1f611b2) |
| M6-F1 (cold R1-1, R1-2) | builder a88d74440d1287ae4 (worktree) | 1 | merged (65be81c) |
| M6-F2 (cold R2-1) | builder a85339448c3e42c50 (worktree) | 1 | merged (2e9f0d6) |

### Parked questions

- none
