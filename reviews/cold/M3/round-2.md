# Cold review M3 round 2
covers: 9913e8fe0335911aecd85d4f093c22a8a205c926
base: 9ffe9a100d394a5afc6fd6c82670b58925dd7ffd
spec: a34dc4ab73772a41d5d39925752ec7bc54a47668

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| none | | | | |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-3 a | yes | `tests/test_cli.py` `DueTest.test_add_with_due_stores_date_and_list_shows_it` asserts stdout `added 1`, stored JSON `{"id": 1, "text": "buy milk", "done": false, "due": "2026-11-20"}` and `list` output `1 [ ] buy milk (due 2026-11-20)`; `test_items_without_due_show_no_suffix`, `test_due_survives_done_and_remove_saves` and `tests/test_store.py` `test_valid_due_is_loaded_and_kept_on_save` cover the store keeping `due`. Manual run with `TODO_FILE` under /tmp confirmed `--due X`, `--due=X`, `--du X` all store and list correctly. Full suite: 84 tests OK. |
| P1-3 b | yes | `tests/test_cli.py` `OverdueTest` (`today = date(2026, 11, 15)` passed via `cli.main(argv, today=...)`) covers past shown, today hidden, future hidden, no-due hidden, done-past hidden, mixed set in ID order, `--all --overdue`, and `test_today_is_injected` / `test_today_defaults_to_date_today` show the parameter drives the result. |
| P1-3 c | yes | `DueTest.test_bad_date_exits_1_and_leaves_file_unchanged` covers `2026-13-01`, `2026-02-30`, `tomorrow`, `2025-02-29`, full-width digits and others, asserting `(1, "", "todo: bad date <value>\n")` and a byte-identical file; `test_bad_date_on_missing_file_creates_nothing` asserts no file is created. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| R1-1 | yes | `DueTest.test_dash_due_value_is_a_bad_date_not_a_usage_error` and `test_dash_text_and_due_after_double_dash_still_work` pass at 9913e8f; with `todo/cli.py` from 581d2d8 swapped in (in a /tmp copy) `DueTest` fails 36 subtests, so the test guards the fix. Attempts to break `_protect_due`: `--due` after `--` stays text, trailing `--due` stays a usage error without touching the file, `--due --due`/`--d -h`/`--du --help` give `bad date`, `done`/`remove`/`list` argv untouched (only `argv[0] == "add"` is rewritten), and `_protect_id` runs first on a disjoint set of commands. No regression found. |

## Scope

The diff touches only `todo/cli.py`, `todo/store.py`, `tests/test_cli.py`, `tests/test_store.py` and the review records under `reviews/cold/M3/`. Beyond the literal spec, `store.load` rejects a stored `due` that is not a real YYYY-MM-DD date (reported as `todo: cannot read <path>`), which follows DESIGN Data ("`due` is absent or an ISO date string") and the existing item validation; and `_protect_due` rewrites dash-led `--due` values so they reach the date check, which is the R1-1 fix and serves the spec's bad-date message. No existing tests were deleted or weakened (the only changed line is `run_cli` passing `today=`). Nothing in the spec is missing from the diff.
