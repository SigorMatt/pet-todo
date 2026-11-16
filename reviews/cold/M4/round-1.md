# Cold review M4 round 1
covers: fd20b596ca8ecd3e56fbc75b4073c645f53d10b1
base: 35b908d6ea6581fecaa3758707f463e35b5bd109
spec: d7e84b85dccdedcbe662ae5a538a211673415a77

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| none | | | | |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-2 c1 | yes | `BadTextTest` in tests/test_cli.py has one test each for empty, spaces only, newline, CR, tab, NUL, DEL, U+0085 and surrogate-escaped bytes. Each checks `todo: bad text`, exit 1, the file not created when missing, and the file byte-identical when present. `TextSubprocessTest.test_non_utf8_argv_is_bad_text` sends real non-UTF-8 argv bytes. Manual check: lone-surrogate bytes `\xed\xa0\x80` and NBSP-only text are also rejected. |
| P2-2 c2 | yes | `OneLinePerItemTest` (open items, and done items with a due date) checks that each accepted text, including U+2028 and U+2029, lists as exactly one `\n`-terminated line. `TextSubprocessTest.test_list_on_strict_utf8_stdout_does_not_crash` runs with `PYTHONIOENCODING=utf-8:strict` and decodes stdout strictly. |
| P2-3 c1 (done/remove) | yes | `BadIdTest` covers `01`, `-1`, `1.0`, `abc`, 5000 digits and more (`0`, empty, full-width and Arabic-Indic digits, `1\n`, `-h`, `--help`, 20 digits) for both `done` and `remove`. It checks the exact `todo: bad id <raw[:20]>` message, exit 1 and an unchanged file. `test_bad_id_checked_before_file_is_loaded` shows the check runs before load. |
| P2-3 c2 | yes | `AddTest.test_add_above_max_id_no_more_ids_and_saves_nothing` prepares a file holding an item at MAX_ID (next_id 1 and MAX_ID+1). It asserts `todo: no more ids`, exit 1 and identical bytes, and the existing MAX_ID boundary test still passes. |

## Scope

The diff touches only `todo/cli.py` and `tests/test_cli.py`. It adds the shared helpers `check_text` and `parse_id` (with `BadTextError` and `BadIdError`), plus `NoMoreIdsError`, and wires them into `add`, `done` and `remove`. That matches L-3 to L-6. Nothing in the diff falls outside the spec. Tests were deleted, but each removed case expected `todo: no item` for an ID that D-3 now classes as malformed (`0`, `-1`, `abc`, `1.5`, empty, dash-led, `-h`/`--help`, 5000 digits, non-ASCII digits). Every such case reappears in `BadIdTest` with the new message, and a well-formed unknown ID still has `no item` coverage. So no check was weakened. Nothing in the spec is missing: `edit` and its share of P2-3 c1 are left to M5, as the spec says. The D-4 lock is absent at both base and head, which is outside this mission. All 103 tests pass.
