# Placeholder Assignment 1★/2★

Status: planned assignment task  
Task: RM1.22-C  
Scope: copy shared placeholder assets into canonical hero folders for official 1★/2★ heroes

## Purpose

This task assigns development placeholder assets to the 20 official low-rarity heroes:

- 8 native 1★ heroes
- 12 native 2★ heroes

The purpose is to unblock future integration and QA for starter-rarity heroes without waiting for final art.

## What this task does

It copies files from the shared placeholder library:

```text
frontend/assets/placeholders/heroes/<profile>/
```

into canonical hero folders:

```text
frontend/assets/heroes/<hero_id>/
```

using final/canonical filenames.

The copied files remain placeholder development assets and are tracked with:

```text
placeholder_status.json
```

## What this task does not do

It does not:

- write DB;
- change `show_in_*`;
- set `obtainable=true`;
- activate pending heroes;
- wire frontend runtime contracts;
- add heroes to gacha;
- mark any asset as final.

## Next required task

After this assignment, a separate contract wiring task is required:

```text
RM1.22-D — Placeholder Contract Wiring for 1★/2★ Heroes
```

Only after contract wiring and Combat QA validation should the project consider controlled activation for starter use.
