# Ledger

Owned by the lead. Deferred findings, each with a target: a later mission in this phase, or the next phase's backlog, never "later". Deferring an item a second time is an owner decision. Known debt from the playbook's Phase 0 enters here as backlog items for phase 1.

| ID | Source review | Finding | Reason | Target | Status |
| --- | --- | --- | --- | --- | --- |
| L-1 | cold M1 R1-6 | Concurrent `todo` runs can lose an item and reuse an ID: load, change and save take no lock. | Real, but locking is outside phase 1 scope (DESIGN has no concurrency requirement) and needs a design choice of lock mechanism. | phase 2 backlog | open |
