# Playbook

pipeline: main
repo: SigorMatt/pet-todo
room: 5
watchdog: trig_01GqT8CNMzZjLFuGEWeSaoTU
lead-task: trig_01NmgWKaWHkvvJatfDvxVdoZ
test: python3 -m unittest discover -s tests -t .

Owned by the architect; the lead reads it and acts on it. Every item has testable acceptance criteria that a cloud machine can check (4 CPUs, 16 GB, no GPU, internet only through the allowlist). Anything else is marked as a manual check for Matthew.

## Phases

### Phase 1: Core to-do CLI

Goal: a working `python3 -m todo` with add, list, done, remove and due dates, as in DESIGN.md. Items: P1-1, P1-2, P1-3. Mission budget: 3 hours.

### Phase 2: Hardening and edit

Goal: settle phase 1's deferred edge cases and add `edit`, as in DESIGN.md (D-2 to D-4). Items: P2-1, P2-2, P2-3, P2-4. Mission budget: 2 hours.

## Items with criteria

### P1-1: Store, add and list

- [ ] `python3 -m todo add "buy milk"` prints `added 1` and creates the file at `$TODO_FILE`; a second add prints `added 2` (unittest in `tests/`)
- [ ] `python3 -m todo list` prints `1 [ ] buy milk` and `2 [ ] …` in ID order, and nothing for an empty list (unittest)
- [ ] A missing file reads as empty; a file that isn't JSON prints `todo: cannot read <path>` and exits 1 (unittest)
- [ ] Saving is atomic: the store writes a temporary file and renames it (unittest that checks no partial file is left when the write fails)

### P1-2: Done and remove

- [ ] `done ID` marks the item done (`done <id>`); `list` hides it and `list --all` shows `[x]` (unittest)
- [ ] `remove ID` deletes it (`removed <id>`); IDs are never reused after a removal (unittest)
- [ ] An unknown ID prints `todo: no item <id>` and exits 1, for both commands (unittest)

### P1-3: Due dates and overdue

- [ ] `add TEXT --due YYYY-MM-DD` stores the date, and `list` shows ` (due YYYY-MM-DD)` (unittest)
- [ ] `list --overdue` shows only open items due before today, with today injectable for the test (unittest)
- [ ] A bad date prints `todo: bad date <value>` and exits 1 (unittest)

### P2-1: Safe concurrent runs (D-4)

- [ ] Two processes that each run `add` 50 times at the same time leave 100 items with 100 distinct IDs (unittest with subprocesses and one `TODO_FILE`)
- [ ] `add`, `done`, `remove` and `edit` hold an exclusive lock on `<file>.lock` from before loading until after the rename, and release it on every exit path, errors included (unittest)
- [ ] While another run holds the lock for more than 5 seconds, a changing command prints `todo: file is locked <path>`, exits 1 and leaves the file unchanged; a lock released within 5 seconds is waited for (D-5; unittest with the wait injectable)

### P2-2: Clean task text (D-2)

- [ ] `add` with text that is empty or whitespace, contains a newline, carriage return, tab or another control character, or isn't valid UTF-8 prints `todo: bad text`, exits 1 and leaves the file unchanged (unittest for each case)
- [ ] `list` prints exactly one line per item for every text `add` accepts (unittest)

### P2-3: Strict IDs (D-3)

- [ ] `done`, `remove` and `edit` with an ID like `01`, `-1`, `1.0`, `abc` or 5000 digits print `todo: bad id <value>` (value cut to 20 characters), exit 1 and leave the file unchanged (unittest)
- [ ] When the next ID would pass 9223372036854775807, `add` prints `todo: no more ids`, exits 1 and leaves the file unchanged (unittest with a prepared file)

### P2-4: Edit

- [ ] `edit ID TEXT` replaces the text and prints `edited <id>`; done state, due date and ID stay (unittest)
- [ ] `edit` with an unknown ID prints `todo: no item <id>`; bad text and bad IDs fail as in P2-2 and P2-3 (unittest)

## Merge-hold list

A PR touching any of these areas is held for Matthew (`MERGE-HOLD-n`). Edit the patterns per project: `*` stays within one path segment, `**/` matches any number of directories, including none, and matching ignores case. Holding too much is cheaper than missing a change.

<!-- Trimmed for pet-todo: a standard-library Python CLI with no auth, no secrets and no migrations. -->

- CI and workflow files: `.github/workflows/**`, `.github/actions/**`
- Secrets handling: `**/*secret*`, `**/*token*`, `**/*credentials*`, `**/.env*`, `**/*.key`, `**/*.pem`
- New dependencies: `**/requirements*.txt`, `**/pyproject.toml`, `**/setup.py`, `**/setup.cfg`, `**/Pipfile`
- Deleted or weakened tests: `**/tests/**`, `**/test_*`

## Environment needs

- Domains to allow: none
- Secrets to add: none

## Lead's discretion

- Internal naming, module layout inside `todo/`, test layout and helper functions.
- How "today" is injected into `list --overdue` for tests (an environment variable or a parameter).
- The lock file's open mode, the polling interval, and the test harness for concurrent runs.

## Phase 0 known debt

None.
