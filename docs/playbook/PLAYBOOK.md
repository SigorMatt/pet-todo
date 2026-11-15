# Playbook

pipeline: main
repo: SigorMatt/pet-todo
room: 0
test: <command>

Owned by the architect; the lead reads it and acts on it. Every item has testable acceptance criteria that a cloud machine can check (4 CPUs, 16 GB, no GPU, internet only through the allowlist). Anything else is marked as a manual check for Matthew.

## Phases

### Phase 1: <name>

Goal: <one sentence>. Items: P1-1. Mission budget: 8 hours.

## Items with criteria

### P1-1: <title>

- [ ] <criterion, with the check that proves it>
- [ ] <criterion> (manual check for Matthew)

## Merge-hold list

A PR touching any of these areas is held for Matthew (`MERGE-HOLD-n`). Edit the patterns per project: `*` stays within one path segment, `**/` matches any number of directories, including none, and matching ignores case. Holding too much is cheaper than missing a change.

<!-- Architect: this default list is broad on purpose; trim it to the project's layout with Matthew. -->

- CI and workflow files: `.github/workflows/**`, `.github/actions/**`
- Authentication, cryptography or secrets handling: `**/*auth*`, `**/*auth*/**`, `**/*security*`,
  `**/*security*/**`, `**/*account*`, `**/*crypto*`, `**/*crypto*/**`, `**/*secret*`, `**/*secret*/**`,
  `**/*password*`, `**/*token*`, `**/*credentials*`, `**/.env*`, `**/*.key`, `**/*.pem`, `**/*.keystore`, `**/*.p12`
- New dependencies: `**/requirements*.txt`, `**/requirements/*.txt`, `**/pyproject.toml`, `**/setup.py`,
  `**/setup.cfg`, `**/Pipfile`, `**/environment.yml`, `**/package.json`, `**/package-lock.json`, `**/*.lock`,
  `**/go.mod`, `**/Cargo.toml`, `**/Gemfile*`, `**/*.gemspec`, `**/pom.xml`, `**/build.gradle*`, `**/*.csproj`
- Destructive data migrations: `**/migrations/**`, `**/migrate/**`, `**/alembic/**`
- Deleted or weakened tests: `**/tests/**`, `**/test/**`, `**/spec/**`, `**/__tests__/**`, `**/*_test.*`,
  `**/*.test.*`, `**/*_spec.*`, `**/*.spec.*`, `**/test_*`, `**/conftest.py`

## Environment needs

- Domains to allow: none
- Secrets to add: none

## Lead's discretion

- <areas the lead decides without escalating, e.g. internal naming, test layout>

## Phase 0 known debt

None. For an existing codebase: what exists, the known debt, and a green `main` as the first criterion.
