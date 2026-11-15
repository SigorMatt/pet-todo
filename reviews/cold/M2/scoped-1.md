# Cold review M2 scoped 1
covers: 3c55c4a787e5184ebeace9547d11e6e04ff73582
base: 12d2b1334fdf19792a58b40104ad547741e8bdf3
spec: 45f27de060f74f758513aea77cd1487419202b10
since: 62f6a92c949250cce8cfaa999a7ab46fcfbf173b

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| S1-1 | low | todo/cli.py:66 | The new `except ValueError` assumes "no stored ID is that long", but Python's 4300-digit limit counts leading zeros. `_find` accepts leading zeros elsewhere (`01` means ID 1), so a zero-padded ID that names an existing item is reported as unknown once the string passes 4300 characters. | With item 1 stored, `done 0001` prints `done 1`, and `done` with 4299 zeros then `2` prints `done 2`. But `done` with 4300 zeros then `1` (4301 characters) prints `todo: no item 000…01` and exits 1, though item 1 exists. Checked on Python 3.13.18. This is unlikely in real use. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-2 a | yes | `tests/test_cli.py` DoneTest (`test_done_prints_id_and_saves`, `test_list_hides_done_and_all_shows_x`, `test_done_twice_is_not_an_error`) and SubprocessTest `test_done_remove_and_unknown_id` pass. The full suite passes at 3c55c4a (52 tests OK). |
| P1-2 b | yes | `tests/test_cli.py` RemoveTest `test_remove_prints_id_and_deletes` and `test_ids_not_reused_after_removing_highest` pass. |
| P1-2 c | yes | `tests/test_cli.py` NoItemTest passes. It now includes `test_overlong_digit_id_is_no_item` (5000 digits, both commands → `todo: no item <id>`, exit 1), which closes the R2-1 gap. Manual checks via `cli.main` with 4300, 4301 and 1,000,000 digits all give `no item` and exit 1 in under 10 ms. With `PYTHONINTMAXSTR=0`, 5000 digits also gives `no item`. |
| L-2 | yes | `todo/store.py:33` raises `next_id` to at least `max(id)+1` and at least 1. `tests/test_store.py` `test_low_next_id_is_repaired_above_stored_ids`, `test_next_id_below_one_is_repaired_with_no_items`, `test_higher_next_id_is_kept` and `test_add_after_hand_edited_next_id_gets_fresh_id` pass. The focus diff does not touch this. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| R2-1 | yes | d5ee97d wraps `int(raw)` in `try/except ValueError` → `NoItemError`. `test_overlong_digit_id_is_no_item` passes at 3c55c4a. With the 62f6a92 `todo/cli.py` dropped into a /tmp copy of the tree, it fails (errors=2). The only `ValueError` `int()` can raise after the ASCII-digit guard is the digit limit, so nothing else is swallowed. Stored IDs cannot exceed the limit either, because `json.load` rejects them as a `ValueError` → `cannot read`. The one gap is the leading-zero case (S1-1). |

## Scope

The focus diff (62f6a92..3c55c4a) contains four changes: the four-line `try/except` in `todo/cli.py` `_find`, one new test in `tests/test_cli.py`, the round-2 review file and an R2-1 row in `DISPOSITIONS.md`. All of them serve criterion P1-2 c (an unknown ID prints `todo: no item <id>`). Nothing falls outside the spec. No test is removed or weakened, and no dependency or CI file changes. Nothing the spec asks for is missing from it.
