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

An unknown ID prints `todo: no item <id>` and exits 1. A bad date prints `todo: bad date <value>` and exits 1.

## Data

A JSON file at `$TODO_FILE`, else `./todo.json`, created on the first write:

```json
{"next_id": 3, "items": [{"id": 1, "text": "buy milk", "done": false, "due": "2026-11-20"}]}
```

`due` is absent or an ISO date string. Writes replace the file atomically: write a temporary file in the same directory, then rename it. A missing file reads as an empty list. A file that isn't valid JSON prints `todo: cannot read <path>` and exits 1.

## Decision log

### D-1: Standard library only

- **Date:** 2026-11-15
- **Decision:** `todo` uses only the Python standard library, and `unittest` for tests.
- **Rationale:** keeps the rehearsal free of dependency holds and environment needs.
- **Rejected alternatives:** `click` and `pytest`: nicer, but each is a new dependency the merge gate would hold.
