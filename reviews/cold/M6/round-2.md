# Cold review M6 round 2
covers: 04c738d63ebc85a2c94518574c5c3576c3b4ca18
base: fe04c70c68e8a449752007b2754ef5768690952d
spec: b5e0959251057487342e9ade7f4ef375f32ead9f

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R2-1 | low | todo/store.py:85 | `lock` opens the lock file with `O_RDWR`, though `flock` works on a read-only descriptor, so a user who can write the data file and its directory, but not a lock file another user created, now fails every change where before this diff it saved. | In a shared 0777 (non-sticky) directory, root (umask 022) runs `add a`, which leaves `todo.json.lock` at 0644; `todo.json` is then made 0666. User `nobody` runs `add b`: at fe04c70 it prints `added 2` and exits 0. At 04c738d it prints `todo: cannot write <dir>/todo.json` and exits 1 (reproduced under /tmp/cold-M6-round-2/exp3). Opening with `O_RDONLY` (or falling back to it on EACCES) avoids this. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-1 c1 | yes | tests/test_concurrency.py `test_two_processes_adding_50_each_leave_100_distinct_items` passes. An extra run of 3 × 30 concurrent adds through `real.json`, `link.json` and `link2.json` (a two-step symlink chain) left 90 items with 90 distinct IDs and one lock file, `real.json.lock` (/tmp/cold-M6-round-2/exp1b). |
| P2-1 c2 | yes | tests/test_cli.py `LockTest`: `test_lock_held_across_load_and_rename_and_released_after` (add/done/remove/edit), `test_lock_released_after_no_item`, `test_lock_released_after_item_is_done`, `test_lock_released_after_cannot_write`, `test_lock_released_after_cannot_read`; tests/test_store.py `test_lock_is_released_when_body_raises`. All pass. |
| P2-1 c3 | yes | Wait injectable via `store.LOCK_TIMEOUT`/`LOCK_INTERVAL` and the `timeout`/`interval` arguments of `store.lock`; tests/test_cli.py `test_busy_lock_gives_file_is_locked_and_leaves_file`, `test_lock_released_within_timeout_is_waited_for`, `test_lock_held_by_another_process`; tests/test_store.py `test_busy_lock_times_out_with_data_path`, `test_lock_released_within_timeout_is_waited_for`. All pass. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| R1-1 | yes | `lock_path` returns `os.path.realpath(path) + ".lock"`, the same resolution `save` uses. Regression tests `test_lock_path_resolves_symlinks` and `test_symlink_and_target_take_the_same_lock` (test_store and test_cli) pass. 90 concurrent adds through a target, a symlink and a symlink to the symlink lost nothing and created only `real.json.lock` (exp1b). |
| R1-2 | yes | The lock file now sits beside the resolved target; `tests/test_cli.py` `test_symlink_saves_when_no_lock_file_can_sit_beside_it` passes. |

## Scope

The diff stays within the spec: `todo/store.py` adds `LockedError`, `lock_path`, `FileLock` and a polling `lock` (5 s timeout, 0.05 s interval); `todo/cli.py` wraps load, change and save in `add`, `done`, `remove` and `edit` with the lock, and maps `LockedError` to `todo: file is locked <path>`; the rest is new tests and review records. `list` takes no lock, and argument checks run before the lock (`test_list_takes_no_lock`, `test_argument_checks_run_before_the_lock`). No tests were deleted or weakened; all 148 tests pass. The diff goes beyond the spec's literal text in three ways: the lock file for a symlinked `TODO_FILE` is `<resolved target>.lock`, not `<file>.lock`, which the R1-1 fix needed and which matches D-4's intent; a lock file that cannot be opened is reported as `todo: cannot write <path>`; and the lock file is left on disk. Nothing in the spec is missing from the diff.
