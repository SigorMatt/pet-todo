# Cold review M6 round 1
covers: 1f611b2131873496faf8dbf6dbd4fd88b3c37640
base: fe04c70c68e8a449752007b2754ef5768690952d
spec: b5e0959251057487342e9ade7f4ef375f32ead9f

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R1-1 | medium | todo/store.py:43 | The lock is keyed on the unresolved `TODO_FILE` path, but `store.save` resolves symlinks (`os.path.realpath`) and replaces the target, so two runs that reach the same data file by different names (a symlink and its target, or two symlinks) take different lock files and still race, so L-1 is not fixed for them. | `ln -s real.json link.json`; run 30 `add`s with `TODO_FILE=$D/real.json` and at the same time 30 `add`s with `TODO_FILE=$D/link.json`: every run exits 0, but `real.json` ends with 58 items, not 60 (reproduced under /tmp/cold-M6-round-1/exp2; `link.json.lock` and `real.json.lock` both exist). Fix: lock `os.path.realpath(path) + ".lock"`, or resolve once and use that path for lock, load and save. |
| R1-2 | low | todo/store.py:81 | The lock file is created next to the symlink, not next to the file that is actually written, so a symlinked data file whose link lives in a directory the user cannot write now fails every change, where before this diff it saved. | `TODO_FILE=/ro/todo.json` is a symlink in a read-only directory `/ro`, pointing to `/home/u/todo.json`; before this diff `add x` replaced the target. Now `os.open("/ro/todo.json.lock", O_CREAT)` fails with EACCES, so `add`, `done`, `remove` and `edit` all print `todo: cannot write /ro/todo.json` and exit 1. The same realpath fix resolves it. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-1 c1 | yes | tests/test_concurrency.py `test_two_processes_adding_50_each_leave_100_distinct_items`: two worker processes each run `python3 -m todo add` 50 times against one `TODO_FILE`, with a shared start file; it asserts every run exits 0, the returned IDs are 1..100, and the file holds 100 items with 100 distinct IDs. It passes. It does not cover two different paths to the same file (R1-1). |
| P2-1 c2 | yes | tests/test_cli.py `LockTest`: `test_lock_held_across_load_and_rename_and_released_after` (spies on `store.load` and `os.replace` for add/done/remove/edit), `test_lock_released_after_no_item`, `test_lock_released_after_item_is_done`, `test_lock_released_after_cannot_write`, `test_lock_released_after_cannot_read`; tests/test_store.py `test_lock_is_released_when_body_raises`. All pass. |
| P2-1 c3 | yes | Wait injectable via `store.LOCK_TIMEOUT` and `LOCK_INTERVAL`, and via the `timeout` and `interval` arguments of `store.lock`. tests/test_cli.py `test_busy_lock_gives_file_is_locked_and_leaves_file` (all four commands: message names the data path, exit 1, file unchanged), `test_lock_released_within_timeout_is_waited_for`, `test_lock_held_by_another_process`; tests/test_store.py `test_busy_lock_times_out_with_data_path`, `test_lock_released_within_timeout_is_waited_for`. All pass. |

## Scope

The diff stays inside the spec. It touches only `todo/store.py` (a `LockedError`, `lock_path`, `FileLock`, and `lock` with a 5 s timeout and 0.05 s poll), `todo/cli.py` (wraps load, change and save in `add`, `done`, `remove` and `edit` with the lock; maps an unopenable lock file to `cannot write`; maps `LockedError` to `todo: file is locked <path>`), and new tests. `list` takes no lock (`test_list_takes_no_lock`). Argument checks run before the lock (`test_argument_checks_run_before_the_lock`). No existing tests were deleted or weakened, and the full suite passes (144 tests). Two things are beyond the spec's literal text. Neither is harmful. The lock file is left on disk. A lock file that cannot be opened is reported as `todo: cannot write <path>`, which the spec does not define. Nothing in the spec is missing from the diff, but the "concurrent runs never lose an item" guarantee (D-4, L-1) does not hold when the data file is reached through a symlink (R1-1).
