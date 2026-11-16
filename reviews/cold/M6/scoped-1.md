# Cold review M6 scoped 1
covers: 3574f314380bf10f5316b12248f43880fba1d40d
base: fe04c70c68e8a449752007b2754ef5768690952d
spec: b5e0959251057487342e9ade7f4ef375f32ead9f
since: 04c738d63ebc85a2c94518574c5c3576c3b4ca18

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| S1-1 | low | todo/store.py:84 | The new read-only fallback opens the lock path with `O_RDONLY` and no `O_NONBLOCK` and does not check that it is a regular file, so a FIFO at the lock path that this user cannot write makes the open block forever, before the 5-second polling loop starts. This breaks D-5's bounded wait. | In a shared 0777 directory, another user (here root) runs `mkfifo -m 644 todo.json.lock` beside a 0666 `todo.json`. User `nobody` runs `todo add b`: at 3574f31 it hangs with no output until killed (`timeout 15` gave exit 124). At 04c738d the same run prints `todo: cannot write <dir>/todo.json` and exits 1. A regular lock file that is held only gives the 5 s `file is locked` error. Reproduced under /tmp/cold-M6-scoped-1/exp/d2. Adding `O_NONBLOCK` to the fallback open, or an `fstat` check for a regular file, would bound it. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-1 c1 | yes | tests/test_concurrency.py `test_two_processes_adding_50_each_leave_100_distinct_items` passes (151 tests OK at 3574f31). |
| P2-1 c2 | yes | tests/test_cli.py `LockTest`: `test_lock_held_across_load_and_rename_and_released_after` (add/done/remove/edit), `test_lock_released_after_no_item`, `test_lock_released_after_item_is_done`, `test_lock_released_after_cannot_write`, `test_lock_released_after_cannot_read`. The new `test_lock_file_another_user_owns_still_saves` also checks that the lock is free after a save with a read-only lock fd. All pass. |
| P2-1 c3 | yes | tests/test_cli.py `test_busy_lock_gives_file_is_locked_and_leaves_file`, `test_lock_released_within_timeout_is_waited_for`, `test_lock_held_by_another_process`; tests/test_store.py `test_busy_lock_times_out_with_data_path`, `test_lock_released_within_timeout_is_waited_for`. All pass. Extra check: while root held flock on a 0644 root-owned lock file, `nobody`'s `add` (through the read-only fallback) printed `todo: file is locked <path>`, exited 1 after 5.0 s and left the file unchanged (exp/d1). |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| R2-1 | yes | `_open_lock_file` falls back to `O_RDONLY` on `PermissionError` and re-raises the original error if that open also fails. Real-permission test (not mocked): root ran `add a`, which left `todo.json.lock` at 0644 root:root, and `todo.json` was then set to 0666. `nobody` then ran `add b`, which printed `added 2`, exited 0 and saved both items (exp/d1). The read-only descriptor still excludes others: with root holding the lock, `nobody` timed out with `file is locked` (see c3). A missing lock file in a directory where it cannot be created still raises the original `PermissionError` and creates no file (`test_missing_lock_file_that_cannot_be_created_raises_permission_error`). The fallback does open a FIFO without a bound (S1-1). |

## Scope

The focus diff stays within the R2-1 fix. `todo/store.py` adds `_open_lock_file`, which keeps the `O_RDWR | O_CREAT` open and falls back to a read-only open on `PermissionError`, and updates the `lock` docstring. Two tests in `tests/test_store.py` and one in `tests/test_cli.py` patch `os.open` to refuse write modes on the lock file. The rest is review records (`round-2.md` and a `DISPOSITIONS.md` row). No test was deleted or weakened, and the PR diff removes no test lines. All 151 tests pass. Nothing outside the spec was added. The fallback's one gap is that it opens a non-regular file without a bound (S1-1).
