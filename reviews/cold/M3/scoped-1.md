# Cold review M3 scoped 1
covers: ad67877ae2b61bd9f7b154e14189c03e5c4144f2
base: 9ffe9a100d394a5afc6fd6c82670b58925dd7ffd
spec: a34dc4ab73772a41d5d39925752ec7bc54a47668
since: 9913e8fe0335911aecd85d4f093c22a8a205c926

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| none | | | | |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-3 a | yes | `tests/test_cli.py` `test_add_with_due_stores_date_and_list_shows_it` (plus `test_due_before_text_also_works`, `test_items_without_due_show_no_suffix`, `test_list_all_shows_due_on_done_items`, `test_due_survives_done_and_remove_saves`) check stdout and stored JSON; `todo/cli.py` `_cmd_add` stores `due`, `_cmd_list` appends ` (due YYYY-MM-DD)`. 84 tests pass at ad67877. |
| P1-3 b | yes | `tests/test_cli.py` overdue tests with a fixed `today` passed to `cli.main(..., today=...)`: `test_past_due_open_item_is_shown`, `test_due_today_is_hidden`, `test_future_due_is_hidden`, `test_no_due_is_hidden`, `test_done_past_due_is_hidden`, `test_today_is_injected`, `test_today_defaults_to_date_today`. |
| P1-3 c | yes | `tests/test_cli.py` `test_bad_date_exits_1_and_leaves_file_unchanged` covers `2026-13-01`, `2026-02-30`, `tomorrow` and more, asserting exit 1, `todo: bad date <value>` and file unchanged; `test_bad_date_on_missing_file_creates_nothing` and dash-led value tests also pass. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |

## Scope

The focus diff (9913e8f..ad67877) changes no behaviour: in code it adds a single comment line to `todo/cli.py` (line 2, "Drill (M6 rehearsal): an owner change pushed after the review..."), and the rest is review records under `reviews/` (cold round-2, qodo PR #4 fetch and dispositions). The comment sits after the module docstring, so `__doc__` is unchanged, and it has no runtime effect. No tests were deleted or weakened in the focus, and the full suite (84 tests) passes at ad67877. The comment is outside the M3 spec, but it is harmless and is described as a deliberate pipeline drill, so I report no finding for it. Reading the change against the whole PR shows no interaction with the earlier due-date, overdue or bad-date code.
