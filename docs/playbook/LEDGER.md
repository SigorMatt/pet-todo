# Ledger

Owned by the lead. Deferred findings, each with a target: a later mission in this phase, or the next phase's backlog, never "later". Deferring an item a second time is an owner decision. Known debt from the playbook's Phase 0 enters here as backlog items for phase 1.

| ID | Source review | Finding | Reason | Target | Status |
| --- | --- | --- | --- | --- | --- |
| L-1 | cold M1 R1-6; qodo PR #2: Concurrent adds silently lose tasks | Concurrent `todo` runs can lose an item and reuse an ID: load, change and save take no lock. | Real, but locking is outside phase 1 scope (DESIGN has no concurrency requirement) and needs a design choice of lock mechanism. | phase 2 backlog | open |
| L-2 | cold M1 R2-1; qodo PR #2: Edited lists can reuse or reverse IDs | `load` accepts a `next_id` not above every stored ID (or below 1), so a hand-edited file makes `add` reuse or hand out bad IDs. | Low, needs a corrupted file; M2 owns P1-2 "IDs are never reused" and touches ID handling. | M2 | fixed in 9ffe9a1 |
| L-3 | cold M1 R2-2; qodo PR #2: One task can make every list fail | Text with undecodable argument bytes is stored as surrogates, and a later `list` crashes with `UnicodeEncodeError` on a strict stdout. | Low edge case; how to handle non-UTF-8 input is a behaviour choice DESIGN does not settle. | phase 2 backlog | open |
| L-4 | cold M1 R2-3; qodo PR #2: Task text can impersonate list entries | `add` accepts text with newlines, so `list` prints one item over several lines. | Low; reject versus escape is a user-visible choice DESIGN does not settle. | phase 2 backlog | open |
| L-5 | cold M2 S1-1 | A zero-padded ID over 4300 characters that names a real item (`000…01`) gets `todo: no item` because `int()` refuses strings over 4300 digits. | Low and contrived; whether zero-padded IDs are valid at all is a behaviour choice DESIGN does not settle. | phase 2 backlog | open |
| L-6 | cold M2 S2-1 | When IDs are used up (top ID 2**63-1, reachable only by a hand-edited file), `add` prints `todo: cannot write <path>`, which points at permissions rather than ID exhaustion. | Low and contrived; the wording of a dedicated message is a user-visible choice DESIGN does not settle. The file is left unchanged. | phase 2 backlog | open |
