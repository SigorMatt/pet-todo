# Cold review M2 round 1
covers: 3759fc6275bd7a8ee3d0d2ebe562a655288da9a6
base: 12d2b1334fdf19792a58b40104ad547741e8bdf3
spec: 45f27de060f74f758513aea77cd1487419202b10

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R1-1 | low | todo/cli.py:63 | `_find` parses the ID with plain `int(raw)`, which accepts surrounding whitespace, a leading `+` and non-ASCII digits, so some IDs that are not plain integers act on an item when they should give `todo: no item <id>`. | With items 1-3: `done " 1"` prints `done 1`, `done +2` prints `done 2`, `done ٣` (Arabic-Indic three) prints `done 3`, all exit 0 and mark items done. The spec says a non-integer ID prints `todo: no item <id>` and exits 1. |
| R1-2 | low | todo/cli.py:46 | An ID that starts with `-` and is not a number is parsed as an option, so it gives an argparse usage error (or help text with exit 0) instead of `todo: no item <id>`. | `done -x` prints `todo: the following arguments are required: id` (exit 1, wrong message); `done -h` prints usage and exits 0. Expected `todo: no item -x` and exit 1. |
| R1-3 | low | todo/cli.py:66 | `_find` stops at the first match and `load` does not reject duplicate IDs, so `remove` reports success while an item with that ID is still stored. | File `{"next_id":1,"items":[{"id":1,"text":"a","done":false},{"id":1,"text":"b","done":false}]}` (hand-edited, the same kind of file L-2 covers): `remove 1` prints `removed 1` and exits 0, then `list --all` still shows `1 [ ] b`. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-2 a | yes | `tests/test_cli.py` DoneTest: `test_done_prints_id_and_saves`, `test_list_hides_done_and_all_shows_x` and `test_done_twice_is_not_an_error`, plus SubprocessTest `test_done_remove_and_unknown_id`. All pass (45 tests OK). |
| P1-2 b | yes | `tests/test_cli.py` RemoveTest: `test_remove_prints_id_and_deletes` and `test_ids_not_reused_after_removing_highest` (remove 2 then add gives 3; remove 3 and 1 then add gives 4). Passes. |
| P1-2 c | yes, with gaps | `tests/test_cli.py` NoItemTest `test_unknown_or_non_integer_id` covers `2`, `0`, `-1`, `abc`, `1.5` and the empty string for both commands, and checks the file is unchanged. Inputs like ` 1`, `+2` and `-x` are not covered and behave differently (R1-1, R1-2). |
| L-2 | yes | `todo/store.py:33` raises `next_id` to at least one above the highest stored ID, and to at least 1. Covered by `tests/test_store.py` `test_low_next_id_is_repaired_above_stored_ids`, `test_next_id_below_one_is_repaired_with_no_items`, `test_higher_next_id_is_kept` and `test_add_after_hand_edited_next_id_gets_fresh_id`. A non-integer `next_id` still gives `cannot read`, the same as before this change. |

## Scope

The diff stays within the spec. It adds `done`, `remove` and `list --all` to `todo/cli.py`, the L-2 `next_id` repair in `todo/store.py`, and tests that only add to `tests/test_cli.py` and `tests/test_store.py`; the usage-error test gains argv cases and loses none. No test was deleted or weakened, and the diff adds no dependency or CI file. Moving the save into a `_save` helper and changing `item.get("done")` to `item["done"]` (safe, because `load` checks that `done` is a bool) are refactors that come with the feature. Nothing the spec asks for is missing. `--overdue` and `--due` are absent, which is correct: they belong to P1-3.
