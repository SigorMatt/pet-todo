| ID | severity | file | finding | disposition | evidence |
| --- | --- | --- | --- | --- | --- |
| R1-1 | low | todo/cli.py | A bad `--due` value beginning with `-` gave an argparse usage error instead of `todo: bad date <value>`. | fixed in 8b00a16 | `tests/test_cli.py` dash-led `--due` tests (values `-x`, `-h`, `--help`, `--`, `-1`, `--due`, -2026-11-20 style, flag spellings `--due`/`--du`/`--d`) assert exit 1, `todo: bad date <value>`, file unchanged; they failed before the fix. 84 tests pass. |
