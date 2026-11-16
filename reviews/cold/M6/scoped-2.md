# Cold review M6 scoped 2
covers: b0c86ae2b6d3f87c4246f4d58f3834a87a5bccc4
base: fe04c70c68e8a449752007b2754ef5768690952d
spec: b5e0959251057487342e9ade7f4ef375f32ead9f
since: 3574f314380bf10f5316b12248f43880fba1d40d

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| S2-1 | low | todo/store.py:158 | The resolve-once fix (3e0aa0f) leaves a gap. When `TODO_FILE` does not exist yet, `resolve` returns it unchanged. If a symlink then appears at that name after the lock is taken, `load` follows it and reads another file under the wrong lock. `save` then `os.replace`s over the link and turns it into a regular file. This is the same "lock key differs from file read" class that Qodo's finding names. | `TODO_FILE=d/todo.json` is missing and `d/other.json` holds item 1. Command A resolves to `d/todo.json` and takes `d/todo.json.lock`. Then `d/todo.json -> other.json` is created. A reads other.json's items without holding `other.json.lock`, so a writer B that holds that lock is not excluded. A then writes `{items 1,2}` to `d/todo.json` as a regular file, so the link is gone and B's later additions to other.json no longer show through `TODO_FILE`. Reproduced with a patched `store.lock` in /tmp/cold-M6-scoped-2/exp/race.py: `added 2`, `islink(todo.json)` is False, and other.json is unchanged. Opening `target` with `O_NOFOLLOW`, or re-resolving after the lock and refusing on a change, would close it. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-1 c1 | yes | tests/test_concurrency.py `test_two_processes_adding_50_each_leave_100_distinct_items` passes. At b0c86ae the full suite is 155 tests OK. |
| P2-1 c2 | yes | tests/test_cli.py `LockTest.test_lock_held_across_load_and_rename_and_released_after` covers add/done/remove/edit. The `test_lock_released_after_*` tests cover no item, item is done, cannot write and cannot read. All pass. The `spy` helper's `load` now takes `**kwargs` and passes them on to the real `load`. It still records `lock_is_free()` at load and at replace, and the same assertions run, so the helper is not weakened: it only lets the new `target=` keyword reach the real `load`. |
| P2-1 c3 | yes | tests/test_cli.py `test_busy_lock_gives_file_is_locked_and_leaves_file`, `test_lock_released_within_timeout_is_waited_for`, `test_lock_held_by_another_process`; tests/test_store.py `test_busy_lock_times_out_with_data_path`, `test_lock_released_within_timeout_is_waited_for`. All pass. Leaving `O_NONBLOCK` set does not change flock, which already polls with `LOCK_NB`. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| S1-1 | yes | Both lock-file opens use `O_NONBLOCK`, and a lock file that `fstat` does not report as a regular file is closed and refused with an OSError, which becomes `todo: cannot write <path>`. Real-permission check (not mocked): in a 0777 directory, root ran `mkfifo -m 644 todo.json.lock` beside a 0666 `todo.json`. As `nobody`, `add b` and `done 1` each printed `todo: cannot write <dir>/todo.json` at once and exited 1, with the file unchanged. Root, which takes the O_RDWR path on the FIFO, got the same result. A lock path symlinked to `/dev/null` is also refused, and once the lock path is removed `add` succeeds. The new tests `test_fifo_lock_file_this_user_cannot_write_gives_cannot_write_promptly` and `test_non_regular_lock_file_raises_oserror` fail on 3574f31 (the CLI test hits its "hung" timeout) and pass at b0c86ae. |
| Qodo "Retargeted links can lose additions" | yes | `_cmd_add/done/remove/edit` call `store.resolve(path)` once and pass that `target` to `lock`, `load` and `save`. Errors still name the path as given (`test_errors_name_the_link_as_given`). `test_link_retargeted_after_the_lock_still_changes_the_locked_file` fails for all four commands on 819eaab and passes at b0c86ae. A retarget between `resolve` and `lock` is harmless: the command locks, reads and writes the old target consistently. The one remaining gap is a link created at a missing path (S2-1). |

## Scope

The focus diff stays within the two fixes. `todo/store.py` adds `resolve`, a `target=` keyword on `lock`, `load` and `save`, and the non-blocking, regular-file-only `_open_lock_file`. `todo/cli.py` threads the one resolved target through the four changing commands. `list` is untouched and still takes no lock. Argument checks still run before `resolve` and the lock. The tests add one FIFO test in each of `tests/test_store.py` and `tests/test_cli.py`, and add the retarget and error-naming tests. The only change to an existing test is that `spy` forwards `**kwargs`, which does not weaken it. No test was deleted. The rest is review records (scoped-1, a DISPOSITIONS row, the Qodo archives). Nothing outside the spec was added, and no secrets appear. All 155 tests pass.
