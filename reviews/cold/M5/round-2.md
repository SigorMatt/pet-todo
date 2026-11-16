# Cold review M5 round 2
covers: 697cfd617573458a4b7423b330d2c7273d59ce24
base: afaabb6a2b452a255db3d15132d3f46e87982cfc
spec: b5e0959251057487342e9ade7f4ef375f32ead9f

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| none | | | | |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-4 c1 | yes | `EditTest.test_edit_replaces_text_and_keeps_id_done_and_due` (open item with due: text replaced, `edited 1`, id/due/done=false and `next_id` unchanged, the done item 3 untouched), `test_edit_open_item_without_due`, `test_edit_accepted_texts`, `EditSubprocessTest.test_edit_end_to_end`. `_cmd_edit` (todo/cli.py:203-213) assigns only `item["text"]`. Full suite: 122 tests OK. Manual run: `edit 1 -5` on an item with due keeps `due` and `done: false`. |
| P2-4 c2 | yes | `test_unknown_id_is_no_item` (`4`, 19 nines, MAX_ID), `test_removed_id_is_no_item`, `test_unknown_id_on_missing_file` (file not created); `test_bad_text` and `EditSubprocessTest.test_non_utf8_argv_is_bad_text` (empty, whitespace, LF, CR, tab, NUL, DEL, NEL, non-UTF-8 argv); `test_bad_ids` (`01`, `-1`, `1.0`, `abc`, 5000 digits cut to 20, plus `-x`, `-h`, `--help`, Arabic-Indic digit); `test_checks_run_before_file_is_loaded` (corrupt and missing file); each asserts exit 1 and a byte-identical file. `parse_id` and `check_text` are M4's, called before `store.load`. |
| P2-4 c3 | yes | `EditTest.test_done_item_is_refused` (`edit 3 ...` on a done item → `todo: item 3 is done`, exit 1, file byte-identical) and `test_done_check_comes_after_id_and_text_checks`. `DoneItemError` is raised before the text is assigned and before `_save`, and is caught in `main` (todo/cli.py:305). Manual run: `edit 2 x` on a done item → `todo: item 2 is done`, rc=1, file unchanged. |

## Earlier fixes

| ID | holds | evidence |
| --- | --- | --- |
| none | | Round 1 (`reviews/cold/M5/round-1.md`) reported no findings and `DISPOSITIONS.md` lists none. The only change since round 1 (697cfd6) implements CHANGE-1/D-6; it changed `EditTest.setUp` so c1's test now edits an open item (the old test asserted editing a done item, which D-6 forbids) and adds a separate done item; no assertion was dropped or weakened otherwise. |

## Scope

The diff touches `todo/cli.py` (the `edit` subparser, `_cmd_edit`, `DoneItemError` and its `main` handler, the `_COMMANDS` entry, and `_protect_edit_id` so a dash-led ID such as `edit -x TEXT` reports `bad id -x`), `tests/test_cli.py` (new `EditTest` and `EditSubprocessTest`; existing tests untouched), and the round-1 review files under `reviews/cold/M5/`. `_protect_edit_id` serves the spec's bad-ID requirement and mirrors `_protect_id` for done/remove; probes (`edit -1 -2` → `bad id -1`, `edit -- -1 x` → `bad id -1`, `edit -x -y` and `edit -x --` → usage error, exit 1, file unchanged) do not contradict the spec. No locking was added, as the spec defers it to M6. The `# Drill (M6 rehearsal)` comment at todo/cli.py:2 is in the base, not this diff. Nothing in the spec is missing from the diff.
