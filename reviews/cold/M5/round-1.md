# Cold review M5 round 1
covers: 1e62492f9bbbb63dd3ad99eb3b32be9793ad3aa1
base: afaabb6a2b452a255db3d15132d3f46e87982cfc
spec: 1fadca536b8bc64f89d8d43646f333386c94aa1d

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| none | | | | |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P2-4 c1 | yes | `EditTest.test_edit_replaces_text_and_keeps_id_done_and_due` (done item with due: text replaced, id/done/due/next_id unchanged, `edited 1`), `test_edit_open_item_without_due`, `test_edit_accepted_texts`, `EditSubprocessTest.test_edit_end_to_end`; `_cmd_edit` (todo/cli.py:195-202) only assigns `item["text"]`. Full suite: 120 tests OK. |
| P2-4 c2 | yes | `EditTest.test_unknown_id_is_no_item`, `test_removed_id_is_no_item`, `test_unknown_id_on_missing_file` (`todo: no item <id>`, exit 1, file unchanged/not created); `test_bad_text` and `EditSubprocessTest.test_non_utf8_argv_is_bad_text` (P2-2 cases incl. non-UTF-8 argv); `test_bad_ids` (`01`, `-1`, `1.0`, `abc`, 5000 digits, value cut to 20); `test_checks_run_before_file_is_loaded` (bad id/text reported against a corrupt and a missing file). `_cmd_edit` reuses M4's `parse_id` and `check_text` before `store.load`. |

## Scope

The diff touches only `todo/cli.py` (the `edit` subparser, `_cmd_edit`, its `_COMMANDS` entry, and `_protect_edit_id` so that a dash-led ID such as `edit -x TEXT` reaches the ID check as `bad id -x` rather than a usage error) and `tests/test_cli.py` (new `EditTest` and `EditSubprocessTest` classes; no existing tests removed or weakened). `_protect_edit_id` is a small parsing addition that serves the spec's "bad ID gives `todo: bad id <value>`" requirement, consistent with the existing `_protect_id` for done/remove. No locking was added, as the spec defers that to M6. Probed edge cases (`edit 1 -h` prints help and exits 0 without editing, `edit 1 -5` stores text `-5`, `edit -- 1 -h` stores text `-h`) match how `add` already treats the same arguments and do not contradict the spec. Nothing in the spec is missing from the diff.
