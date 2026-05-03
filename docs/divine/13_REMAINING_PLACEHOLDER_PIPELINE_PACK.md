# Remaining Placeholder Pipeline Pack

Status: bulk file-based task  
Task: RM1.22-G-BULK  
Scope: assign placeholder assets and wire contracts for all remaining pending official heroes

## Purpose

This pack replaces the one-by-one rarity approach for the remaining pending official heroes.

It covers 79 heroes:

- 22 remaining native 3★ heroes
- 24 native 4★ heroes
- 20 native 5★ heroes
- 12 native 6★ launch-base heroes
- 1 extra premium Borea

It excludes:

- `greek_hoplite`
- `norse_berserker`

because they are already active custom 3★ heroes with working custom assets/contracts.

## What this task does

It can:

1. copy shared placeholder assets into canonical hero folders;
2. validate the copied assets;
3. install a generated placeholder contract module;
4. wire the new contracts into `hopliteAssets.ts`;
5. append all remaining heroes to Combat QA Lab options.

## What this task does not do

It does not:

- write DB;
- change `show_in_*`;
- set `obtainable=true`;
- activate pending heroes;
- change gacha rates;
- mark assets as final.

## Activation is separate

After this pack, all official heroes may have placeholder assets/contracts available for QA.

DB activation must remain a later explicit backup/gated apply task.
