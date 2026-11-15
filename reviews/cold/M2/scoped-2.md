# Cold review M2 scoped 2
covers: 41f5b7585b711869fa6e44c3ee4dde8e219e1122
base: 12d2b1334fdf19792a58b40104ad547741e8bdf3
spec: 45f27de060f74f758513aea77cd1487419202b10
since: 3c55c4a787e5184ebeace9547d11e6e04ff73582

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| S2-1 | low | todo/cli.py:77 | When IDs are used up, `add` reports `todo: cannot write <path>`, the message for a failed write, though nothing tried to write and the file is writable. | File `{"next_id": 1, "items": [{"id": 9223372036854775807, ...}]}` in a writable directory → `add b` prints `todo: cannot write t.json` and exits 1 (reproduced). The user goes looking at permissions or disk space, but the real cause is that no new ID is left. The file is not damaged (it stays unchanged), and the same happens after `remove 9223372036854775807` (stored `next_id` 9223372036854775808). |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-2 a | yes | `tests/test_cli.py` `DoneTest.test_done_prints_id_and_saves`, `test_list_hides_done_and_all_shows_x`, `test_done_twice_is_not_an_error`; all 60 tests pass at 41f5b75 |
| P1-2 b | yes | `tests/test_cli.py` `RemoveTest.test_remove_prints_id_and_deletes`, `test_ids_not_reused_after_removing_highest`; L-2: `tests/test_store.py` covers a low or invalid `next_id` (it is repaired, never lowered), and the focus adds `test_item_ids_below_one_raise_store_error` and `test_item_id_one_is_allowed`. Checked by hand: `{"next_id": -5, "items": []}` → `added 1`, and a `next_id` of -(4299 nines) with item 3 → `added 4` |
| P1-2 c | yes | `tests/test_cli.py` `NoItemTest.test_unknown_or_non_integer_id` (both commands), plus `test_unknown_id_on_missing_file`, `test_removed_id_is_unknown` and `SubprocessTest.test_done_remove_and_unknown_id` |

## Earlier fixes

| finding | fixed | evidence |
| --- | --- | --- |
| Qodo PR-3/1 "New items can receive unusable negative IDs" | yes | 42144c5 makes `load` reject item IDs below 1 (`_is_item_id`). 532b2d3 floors `_fresh_id` at 1. `next_id` becomes `max(next_id, fresh)` ≥ 1, so `add` can no longer hand out an ID of 0 or below. `test_item_ids_below_one_raise_store_error` (12 subtests) fails on the 3c55c4a code and passes now. Hand checks: a negative `next_id` with an empty list gives `added 1`. |
| Qodo PR-3/1 "Large stored IDs make edits crash" | yes | 5208016 makes `load` reject item IDs above MAX_ID (2^63-1) and a `next_id` above MAX_ID+1 as `cannot read`. 41f5b75 makes `add` refuse to go past MAX_ID, so every ID that gets saved stays far below json's 4300-digit limit. A next_id over 4300 digits is rejected by json.load (ValueError → StoreError). Tests `test_ids_above_max_raise_store_error`, `test_add_and_done_with_huge_stored_id_report_cannot_read`, `test_add_up_to_max_id_saves_a_loadable_file` and `test_add_above_max_id_cannot_write_and_saves_nothing` all fail or error on the 3c55c4a code and pass now. Hand check: `done`/`remove` at ID MAX_ID work, then `add` refuses and the file is unchanged. I found no remaining path where a save crashes. |

## Scope

The focus diff stays inside L-2 and the two Qodo findings. In code it adds `MAX_ID`, the ID range check in `load`, the floor on `_fresh_id` and the exhaustion guard in `add`. The rest is new tests plus the review and Qodo archive files. No test was deleted or weakened: the test diffs only add tests and change one import. Rejecting a hand-edited file whose IDs fall outside 1..MAX_ID, which used to load, is a behaviour change, but it is what the Qodo fixes need, and the data on disk is left untouched. Nothing in the spec is missing from the diff.
