# Cold review M3 round 1
covers: 581d2d85780d7dda806fb6654e0f6fadb8004239
base: 9ffe9a100d394a5afc6fd6c82670b58925dd7ffd
spec: a34dc4ab73772a41d5d39925752ec7bc54a47668

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R1-1 | low | todo/cli.py:50 | A bad `--due` value that begins with `-` (and is not a plain negative number) is rejected by argparse as a usage error instead of the specified `todo: bad date <value>` message. | `python3 -m todo add x --due -2026-11-20` prints `todo: argument --due: expected one argument` (exit 1, file unchanged) rather than `todo: bad date -2026-11-20`; the `--due=-2026-11-20` form does print `bad date`, so the two spellings of the same bad input give different errors. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-3 a | yes | `tests/test_cli.py` `DueTest.test_add_with_due_stores_date_and_list_shows_it` checks stdout `added 1`, the stored JSON item `{"id": 1, "text": "buy milk", "done": false, "due": "2026-11-20"}` and `list` output `1 [ ] buy milk (due 2026-11-20)`; also `test_items_without_due_show_no_suffix`, `test_list_all_shows_due_on_done_items`. Store keeps `due` (`tests/test_store.py` `test_valid_due_is_loaded_and_kept_on_save`). All 81 tests pass. |
| P1-3 b | yes | `tests/test_cli.py` `OverdueTest` with `today = date(2026, 11, 15)` passed through `cli.main(..., today=...)`: past shown (`test_past_due_open_item_is_shown`), today hidden, future hidden, no-due hidden, done-past hidden, mixed case in ID order, and `test_today_is_injected` shows the parameter changes the result. |
| P1-3 c | yes | `tests/test_cli.py` `DueTest.test_bad_date_exits_1_and_leaves_file_unchanged` covers `2026-13-01`, `2026-02-30`, `tomorrow` and others, asserting `(1, "", "todo: bad date <value>\n")` and byte-identical file; `test_bad_date_on_missing_file_creates_nothing` asserts no file is created. |

## Scope

The diff touches only `todo/cli.py`, `todo/store.py`, `tests/test_cli.py` and `tests/test_store.py`, all within the mission. Beyond the literal spec, `store.load` now rejects a file whose stored `due` is not a valid YYYY-MM-DD date (reported as `todo: cannot read <path>`); this follows DESIGN Data ("`due` is absent or an ISO date string") and existing item validation, so it is consistent rather than out of scope. No existing tests were deleted or weakened (the only removed test line is `run_cli` gaining the `today=` argument). Nothing in the spec is missing from the diff.
