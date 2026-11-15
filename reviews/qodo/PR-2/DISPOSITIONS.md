qodo: on
fetches: 1
reviewed: 05110a1f291bccb1e349968a5108546b9e1f4b2f

| # | severity | finding | tags | file | disposition | Qodo now | cold caught |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Remediation recommended | Concurrent adds silently lose tasks | 🐞 Bug, ≡ Correctness | todo/cli.py | deferred: L-1 to phase 2 backlog | open | yes (R1-6) |
| 2 | Remediation recommended | Edited lists can reuse or reverse IDs | 🐞 Bug, ≡ Correctness | todo/store.py | deferred: L-2 to M2 | open | yes (R2-1) |
| 3 | Remediation recommended | One task can make every list fail | 🐞 Bug, ☼ Reliability | todo/cli.py | deferred: L-3 to phase 2 backlog | open | yes (R2-2) |
| 4 | Remediation recommended | Task text can impersonate list entries | 🐞 Bug, ≡ Correctness | todo/cli.py | deferred: L-4 to phase 2 backlog | open | yes (R2-3) |
| 5 | Remediation recommended | Concurrent saves can weaken file modes | 🐞 Bug, ⛨ Security | todo/store.py | dismissed: the umask read in `_file_mode` (todo/store.py:64-65) races only with another thread in the same process; nothing under todo/ starts a thread or imports threading, and `store.save` has one caller (todo/cli.py `_cmd_add`), run once per `python3 -m todo` process | open | no |
