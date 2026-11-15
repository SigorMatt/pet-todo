# Cold review M1 round 1
covers: 9c4fe8aed57ab32b5d2f1c509741209869f3460d
base: fe0b8a9303e5241ee55ced57e98f76889a3c66ad
spec: 45f27de060f74f758513aea77cd1487419202b10

## Findings

| ID | severity | file:line | finding | failure scenario |
| --- | --- | --- | --- | --- |
| R1-1 | medium | todo/store.py:43 | `os.replace(tmp, path)` replaces a symlinked `$TODO_FILE` with a regular file, so the file the link points at is never updated again. | `ln -s real.json link.json; TODO_FILE=link.json python3 -m todo add x` prints `added 1`, but afterwards `link.json` is a regular file holding the item and `real.json` is unchanged. A list kept in a synced or dotfiles folder and linked into place silently stops receiving changes. |
| R1-2 | low | todo/store.py:38 | `mkstemp` creates the temporary file with mode 0600 and the rename keeps that mode, so every save resets the list file's permissions. | `chmod 644 todo.json; python3 -m todo add x; stat -c %a todo.json` gives `600`, so other users or group members who could read the list can no longer read it. |
| R1-3 | low | todo/cli.py:59 | Only `StoreError` is caught, so a failed save (an `OSError` from `mkstemp`, the write or `os.replace`) ends in a Python traceback rather than a `todo: ` message on stderr. | `TODO_FILE=/no/such/dir/t.json python3 -m todo add x` exits 1 with a `FileNotFoundError` traceback. The same happens with a read-only directory or a full disk. |
| R1-4 | low | todo/store.py:30 | `load` checks only that the JSON is a dict, so valid JSON in the wrong shape crashes with a traceback rather than printing `todo: cannot read <path>`. | A file containing `{}` makes `add` fail with `KeyError: 'next_id'` and `list` fail with `KeyError: 'items'`, with a traceback each time. `{"next_id":"3","items":[]}` gives a `TypeError` on `add`. |
| R1-5 | low | todo/store.py:40 | `save` writes and renames without `os.fsync` on the temporary file, so a crash or power loss just after the rename can leave an empty or truncated `todo.json` in place of the old one. | Power is lost right after `todo add`: on file systems that delay allocation, the renamed file can come back zero-length, the next run prints `todo: cannot read todo.json`, and the whole list is gone. |
| R1-6 | low | todo/cli.py:31 | Load, change and save happen with no lock, so two `add` runs at the same time lose one item and both get the same ID. | Two `todo add` runs start together: both load `next_id: 1`, both print `added 1`, and the second rename overwrites the first, so one item is lost without any error. |

## Criteria

| criterion | met | evidence |
| --- | --- | --- |
| P1-1 add | yes | `AddTest.test_first_add_prints_id_1_and_creates_file` and `test_second_add_prints_id_2` in tests/test_cli.py check `added 1`, file creation and `added 2`; `SubprocessTest.test_add_then_list` checks the same through `python3 -m todo` with `$TODO_FILE`. All 19 tests pass with `python3 -m unittest discover -s tests -t .`. |
| P1-1 list | yes | `ListTest.test_lists_items_in_id_order`, `test_sorts_by_id_whatever_the_file_order`, `test_empty_list_prints_nothing` and `test_missing_file_prints_nothing` in tests/test_cli.py. |
| P1-1 read errors | yes | `test_missing_file_loads_empty` in tests/test_store.py and `ListTest.test_missing_file_prints_nothing` check that a missing file reads as empty. `ErrorTest.test_list_on_non_json_file`, `test_add_on_non_json_file_leaves_it_alone` and `SubprocessTest.test_cannot_read` check the exact stderr `todo: cannot read <path>` and exit 1. |
| P1-1 atomic save | yes | `test_failed_dump_leaves_original_and_no_temp` and `test_failed_replace_leaves_original_and_no_temp` in tests/test_store.py check that the original bytes are unchanged and the directory holds only `todo.json` after the write fails. |

## Scope

The diff adds only `todo/__init__.py`, `todo/__main__.py`, `todo/cli.py`, `todo/store.py`, `tests/__init__.py`, `tests/test_cli.py` and `tests/test_store.py`, which matches the M1 scope. It has nothing of P1-2 (no `done`, `remove` or `--all`) and nothing of P1-3 (no `--due` or `--overdue`). `list` skips items with `done` set, which is harmless forward-compatibility rather than P1-2 behaviour. No existing tests are deleted or weakened (the base has only README.md and .gitignore), and no dependencies or workflow files are touched. Nothing the spec asks for is missing.
