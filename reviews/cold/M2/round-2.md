# Cold review M2 round 2
covers: 62f6a92c949250cce8cfaa999a7ab46fcfbf173b
base: 12d2b1334fdf19792a58b40104ad547741e8bdf3
spec: 45f27de060f74f758513aea77cd1487419202b10

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R2-1 | low | todo/cli.py:64 | The R1-1 fix (7ee3406) replaced `try: int(raw) except ValueError` with an `isascii() and isdigit()` guard followed by a bare `int(raw)`. The `ValueError` that Python raises for strings over 4300 digits now escapes `main` uncaught. This is a regression the fix introduced: the pre-fix `_find` turned it into `NoItemError`. | `python3 -m todo done $(python3 -c 'print("9"*5000)')` (and the same with `remove`) prints a Python traceback ending in `ValueError: Exceeds the limit (4300 digits) for integer string conversion` and exits 1. It should print `todo: no item <id>` on stderr, which the spec requires for an unknown ID. Checked on Python 3.13.18. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-2 a | yes | `tests/test_cli.py` DoneTest: `test_done_prints_id_and_saves`, `test_list_hides_done_and_all_shows_x` and `test_done_twice_is_not_an_error`, plus SubprocessTest `test_done_remove_and_unknown_id`. The full suite passes (51 tests OK). |
| P1-2 b | yes | `tests/test_cli.py` RemoveTest `test_ids_not_reused_after_removing_highest`: remove 2 then add gives 3; remove 3 and 1 then add gives 4. `test_remove_prints_id_and_deletes` checks the `removed <id>` output. Both pass. |
| P1-2 c | yes, with one gap | `tests/test_cli.py` NoItemTest covers `2`, `0`, `-1`, `abc`, `1.5`, the empty string, whitespace, `+2`, non-ASCII digits, dash-led IDs, `-h`/`--help`, a missing file and a removed ID, for both commands. All pass. An integer string over 4300 digits gives a traceback instead (R2-1). |
| L-2 | yes | `todo/store.py:33` raises `next_id` to `max(stored IDs)+1`, and to at least 1. The tests are `tests/test_store.py` `test_low_next_id_is_repaired_above_stored_ids` (next_id 1, 3, 0, -5 all become 4), `test_next_id_below_one_is_repaired_with_no_items`, `test_higher_next_id_is_kept` and `test_add_after_hand_edited_next_id_gets_fresh_id`. All pass. A non-integer `next_id` still gives `todo: cannot read <path>`, so no ID is reused. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| R1-1 | yes, but it introduced R2-1 | `test_id_must_be_plain_ascii_digits` passes at 62f6a92. With the pre-fix `todo/cli.py` (3759fc6) dropped into a /tmp copy, it fails 9 subtests. ` 1`, `+2`, `٣`, `１` and `1_0` now give `todo: no item`. Removing the `ValueError` catch is what lets huge digit strings crash (R2-1). |
| R1-2 | yes | `test_dash_id_is_no_item_not_an_option` and `test_help_flag_after_done_or_remove_is_an_id` pass. Both fail with the pre-fix cli.py. Manual checks: `done -- -h` gives `no item -h`, exit 1; `remove -1 x` gives a usage error, exit 1. `-h`/`--help` on `add`, `list` and at the top level still show help (`test_help_still_shows_help`). |
| R1-3 | yes | `test_duplicate_ids_raise_store_error` and `test_remove_with_duplicate_ids_reports_cannot_read` pass. Both fail with the pre-fix store.py. A file with duplicate IDs gives `todo: cannot read <path>`, exit 1, and the file is left unchanged. |

## Scope

The diff stays within the spec. It adds `done`, `remove` and `list --all` to `todo/cli.py`, the L-2 `next_id` repair and a duplicate-ID check in `todo/store.py` (the R1-3 fix), new tests, and the round-1 review files under `reviews/cold/M2/`. Only two test lines are removed, and both are rewritten: the module docstring, and the usage-error argv list, which only gains cases. No test is weakened, and no dependency or CI file is touched. The `_protect_id` argv rewrite and the ASCII-digit guard go slightly beyond the spec's literal wording, but they serve criterion P1-2 c. Rejecting duplicate IDs in `load` is a new read-time rule. It is defensible, since it prevents `remove` from reporting success while the item stays stored. Nothing the spec asks for is missing. `--due` and `--overdue` are correctly left to P1-3.
