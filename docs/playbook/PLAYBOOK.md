# Playbook

pipeline: main
repo: SigorMatt/pet-todo
room: 0
watchdog: none
test: python3 -m unittest discover -s tests -t .

Owned by the architect; the lead reads it and acts on it. Every item has testable acceptance criteria that a cloud machine can check (4 CPUs, 16 GB, no GPU, internet only through the allowlist). Anything else is marked as a manual check for Matthew.

## Phases

### Phase 1: Core to-do CLI

Goal: a working `python3 -m todo` with add, list, done, remove and due dates, as in DESIGN.md. Items: P1-1, P1-2, P1-3. Mission budget: 3 hours.

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

## Phase 0 known debt

None.
