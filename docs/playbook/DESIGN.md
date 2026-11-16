# Design

Owned by the architect. Records what is being built and why; the playbook says in what order.

## Goals

- A small command-line to-do list, `todo`, that keeps items in a local JSON file.
- A rehearsal target for the agent-room pipeline: several small missions, each leaving `main` working.

## Non-goals

- No server, sync, accounts, colours or interactive UI.
- No dependencies outside the Python standard library.

## Architecture

One Python package, `todo/`, run as `python3 -m todo`. Modules:

- `todo/store.py`: loads and saves the list (the only module that touches the file).
- `todo/cli.py`: parses arguments and prints results; `todo/__main__.py` calls `cli.main()`.

Tests live in `tests/` and use `unittest`, each test with its own temporary `TODO_FILE`.

## Interfaces

`python3 -m todo <command> …` exits 0 on success, and 1 on a usage or lookup error, with a message on stderr starting `todo: `.

| Command | Behaviour | Output (stdout) |
| --- | --- | --- |
| `add TEXT [--due YYYY-MM-DD]` | Adds an open item; IDs count up from 1 and are never reused | `added <id>` |
| `list [--all] [--overdue]` | Open items by ID; `--all` includes done ones; `--overdue` shows only open items whose due date is before today | one line per item: `<id> [ ] <text>` or `<id> [x] <text>`, plus ` (due YYYY-MM-DD)` when set; nothing for an empty list |
| `done ID` | Marks the item done; doing it twice is not an error | `done <id>` |
| `remove ID` | Deletes the item | `removed <id>` |
| `edit ID TEXT` | Replaces an open item's text (phase 2); a done item can't be edited (D-6) | `edited <id>` |

An unknown ID prints `todo: no item <id>` and exits 1. A bad date prints `todo: bad date <value>` and exits 1.

Phase 2 adds these errors, each exiting 1 and leaving the file unchanged:

- `todo: bad text`: the text is empty or only whitespace, contains a control character (Unicode category Cc, which includes newline, carriage return and tab), or isn't valid UTF-8 (D-2).
- `todo: bad id <value>`: an ID argument that isn't 1 to 19 decimal digits without a leading zero (D-3). `<value>` is cut to its first 20 characters.
- `todo: no more ids`: `add` when the next ID would pass 9223372036854775807 (D-3).

## Data

A JSON file at `$TODO_FILE`, else `./todo.json`, created on the first write:

```json
{"next_id": 3, "items": [{"id": 1, "text": "buy milk", "done": false, "due": "2026-11-20"}]}
```

`due` is absent or an ISO date string. Writes replace the file atomically: write a temporary file in the same directory, then rename it. Every command that changes the file holds an exclusive lock on `<file>.lock` (`fcntl.flock`) from before it loads the file until after the rename (D-4). A missing file reads as an empty list. A file that isn't valid JSON prints `todo: cannot read <path>` and exits 1.

## Decision log

### D-1: Standard library only

- **Date:** 2026-11-15
- **Decision:** `todo` uses only the Python standard library, and `unittest` for tests.
- **Rationale:** keeps the rehearsal free of dependency holds and environment needs.
- **Rejected alternatives:** `click` and `pytest`: nicer, but each is a new dependency the merge gate would hold.

### D-2: Clean task text

- **Date:** 2026-11-16
- **Decision:** `add` and `edit` reject text that is empty or only whitespace, contains any control character (Unicode category Cc), or isn't valid UTF-8, with `todo: bad text`. Text is stored as given otherwise.
- **Rationale:** one line per item in `list` (ledger L-4), and no crash on undecodable input (L-3).
- **Rejected alternatives:** escaping control characters (changes what the user typed); replacing bad bytes (silently alters the text).

### D-3: Strict IDs

- **Date:** 2026-11-16
- **Decision:** an ID argument is 1 to 19 decimal digits with no leading zero, else `todo: bad id <value>`. `add` refuses with `todo: no more ids` when the next ID would pass 9223372036854775807.
- **Rationale:** settles zero-padded and huge IDs (L-5) and gives ID exhaustion its own message (L-6).
- **Rejected alternatives:** accepting zero-padded IDs (two spellings of one ID).

### D-4: Lock around every change

- **Date:** 2026-11-16
- **Decision:** commands that change the file take an exclusive `fcntl.flock` on `<file>.lock` around load, change and save, so concurrent runs never lose an item or reuse an ID (L-1). POSIX only, like the rest of the rehearsal. `list` takes no lock.
- **Rationale:** the simplest correct fix with the standard library.
- **Rejected alternatives:** retry on a version number (more code, same guarantee).
- **Q-1:** settled by D-5.

### D-5: Waiting for a busy lock (answers Q-1)

- **Date:** 2026-11-16
- **Decision:** a command that changes the file polls `fcntl.flock(LOCK_EX | LOCK_NB)` for up to 5 seconds. If the lock is still held, it prints `todo: file is locked <path>`, exits 1 and leaves the file unchanged. `<path>` is the data file, not the lock file.
- **Rationale:** never hangs on a stuck run, and 5 seconds covers ordinary contention such as P2-1's 2 × 50 concurrent adds (ESCALATION-1, option 2, the lead's recommendation).
- **Rejected alternatives:** waiting without limit (a stuck run blocks every change silently); failing at once (concurrent adds would often fail).

### D-6: Done items can't be edited

- **Date:** 2026-11-16
- **Decision:** `edit` on a done item prints `todo: item <id> is done`, exits 1 and leaves the file unchanged.
- **Rationale:** a done item is a record of what was done; changing its text silently rewrites history.
- **Rejected alternatives:** allowing it (simpler, but loses the record); reopening the item on edit (surprising).
