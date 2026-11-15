# Cold review M1 round 2
covers: b8b2728de83605c810f73648bbc1d0dcafc7151e
base: fe0b8a9303e5241ee55ced57e98f76889a3c66ad
spec: 45f27de060f74f758513aea77cd1487419202b10

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R2-1 | low | todo/store.py:53 | The shape check added for R1-4 accepts a `next_id` that is not above every stored ID (including 0 or negative), so `add` hands out duplicate or negative IDs, breaking DESIGN's "IDs count up from 1 and are never reused". | A file holding `{"next_id":1,"items":[{"id":1,"text":"a","done":false}]}` (hand edit, or a merge of two synced copies): `todo add b` prints `added 1` and `list` prints `1 [ ] a` and `1 [ ] b`; with `{"next_id":-3,"items":[]}`, `add c` prints `added -3`. Once P1-2 lands, `done 1`/`remove 1` become ambiguous. |
| R2-2 | low | todo/cli.py:55 | `list` prints item text as stored, with no check on what `add` accepted, so text that stdout cannot encode crashes every later `list` with a traceback. | `todo add $'caf\xe9'` (a Latin-1 byte in the argument) prints `added 1` and stores `"caf\udce9"`. With a strict stdout (e.g. `PYTHONIOENCODING=utf-8`, the usual case under a non-C UTF-8 locale) every `todo list` then dies with `UnicodeEncodeError: ... surrogates not allowed` and exit 1, not a `todo: ` message, until someone edits the file by hand. |
| R2-3 | low | todo/cli.py:41 | `add` stores text that contains newlines, so `list` no longer prints one line per item, and its output can fake extra items. | `todo add $'buy milk\n2 [ ] fake'` then `todo add real`: `list` prints `1 [ ] buy milk`, `2 [ ] fake`, `2 [ ] real`, which shows an item 2 that does not exist and two lines with ID 2. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-1 add | yes | `AddTest.test_first_add_prints_id_1_and_creates_file` and `test_second_add_prints_id_2` (tests/test_cli.py) check `added 1`, that the file at `$TODO_FILE` is created, and `added 2`; `SubprocessTest.test_add_then_list` checks the same through `python3 -m todo`. All 31 tests pass with `python3 -m unittest discover -s tests -t .` at b8b2728. |
| P1-1 list | yes | `ListTest.test_lists_items_in_id_order`, `test_sorts_by_id_whatever_the_file_order`, `test_empty_list_prints_nothing`, `test_missing_file_prints_nothing`. |
| P1-1 read errors | yes | `test_missing_file_loads_empty` (test_store.py) and `ListTest.test_missing_file_prints_nothing` cover the missing file. `ErrorTest.test_list_on_non_json_file`, `test_add_on_non_json_file_leaves_it_alone` and `SubprocessTest.test_cannot_read` check the exact stderr `todo: cannot read <path>` and exit 1. |
| P1-1 atomic save | yes | `test_failed_dump_leaves_original_and_no_temp` and `test_failed_replace_leaves_original_and_no_temp` (test_store.py) check that the original bytes are unchanged and that only `todo.json` is left in the directory. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| R1-1 | yes | `save` writes to `os.path.realpath(path)`. `test_save_through_symlink_updates_target` and `test_save_through_dangling_symlink_creates_target` pass and fail on the pre-fix code (18bbe11 code with the head tests: 22 failures and 6 errors in all). By hand: a two-link chain across directories (`l2 -> s/a/l1 -> ../b/real.json`) kept both links and updated `real.json`. A symlink loop gives `todo: cannot read`, not a traceback. |
| R1-2 | yes | `test_save_keeps_existing_permissions` and `test_new_file_gets_default_mode_from_umask` pass and fail before the fix. By hand: a 0640 target reached through symlinks stayed 0640 after `add`. |
| R1-3 | yes | `test_add_into_missing_directory_cannot_write`, `test_any_oserror_on_save_cannot_write` and `SubprocessTest.test_cannot_write` pass and fail before the fix. Every `OSError` from `save` (stat, mkstemp, chmod, write, fsync, replace) is turned into `WriteError`, and directory-fsync errors after the rename are swallowed, so a save that worked is never reported as failed. Not covered: a crash at print time in `list` (R2-2), which is outside the save path. |
| R1-4 | yes, partly | `test_wrong_shape_raises_store_error` and `test_wrong_shape_file` pass and fail before the fix, and every shape from R1-1's scenario now gives `todo: cannot read <path>`. The check does not compare `next_id` with the stored IDs, so a file that is well-formed but inconsistent still gives wrong results (R2-1). |
| R1-5 | yes | The temp file is flushed and fsynced before `os.replace`, and the directory is fsynced after it (best effort). `test_save_fsyncs_temp_file_before_rename` passes and fails before the fix. It requires an fsync of the fully written size before the first replace, so taking the fsync out or moving it would fail the test. |
| R1-6 | n/a (deferred) | Deferred as L-1 to the phase 2 backlog. Still present, as expected: there is no lock around load, change and save. The DESIGN states no concurrency requirement. |

## Scope

The code diff adds only `todo/__init__.py`, `todo/__main__.py`, `todo/cli.py`, `todo/store.py`, `tests/__init__.py`, `tests/test_cli.py` and `tests/test_store.py`, which matches M1. It has nothing of P1-2 (no `done`, `remove` or `--all`) and nothing of P1-3 (no `--due` or `--overdue`). `list` skips items whose `done` is true and the loader accepts extra keys such as `due`, which is harmless forward compatibility. Outside the spec: the R1-3 fix adds a new user-visible message, `todo: cannot write <path>`, that DESIGN.md does not define. It fits the `todo: ` prefix rule, and DISPOSITIONS says it is a lead decision recorded in MISSIONS.md, which is not in this diff. The diff also commits the review records `reviews/cold/M1/round-1.md` and `DISPOSITIONS.md`, which are pipeline records, not product code. No tests are deleted or weakened (the base has only README.md and .gitignore), and no dependencies or workflow files are touched. Nothing the spec asks for is missing.
