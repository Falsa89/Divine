# RM1.26-D — Hero Skill Kit Browser UI Extension

## Objective

Create a mobile-first, internal/read-only frontend screen to browse the inert Hero Skill Kit catalogs exposed by RM1.26-C.

This task is a catalog browser only. It must not connect hero skill kit catalogs to battle runtime, HP bar runtime, status runtime, VFX runtime, gacha, roster activation, or final balance.

## Source API

Use only these read-only endpoints:

- `GET /api/hero-skill-kits/catalogs/summary`
- `GET /api/hero-skill-kits/catalogs/schema`
- `GET /api/hero-skill-kits/catalogs/5star`
- `GET /api/hero-skill-kits/catalogs/6star`
- `GET /api/hero-skill-kits/catalogs/by-hero/{hero_id}`

Do not import frontend JSON directly from `data/design`.

## Route

Create:

- `/app/frontend/app/hero-skill-kits-catalog.tsx`

Route:

- `/hero-skill-kits-catalog`

Add menu entry in:

- `/app/frontend/app/(tabs)/menu.tsx`

Suggested label:

- `📖 Kit Skill Eroi`

## Required UI Sections

### 1. Summary

Show catalog counts and flags:

- 5★ entries: 20
- 6★ launch_base: 12
- 6★ extra premium: 1
- total catalog entries: 33
- `runtime_attached=false`
- `battle_runtime_attached=false`
- `ui_runtime_attached=false`
- `hp_bar_runtime_attached=false`
- `balance_values_finalized=false`
- `do_not_treat_as_live_kit=true`

A persistent banner must say that the page is read-only and not connected to battle runtime.

### 2. 5★ Catalog

Show all 20 5★ entries.

Must show:

- hero_id
- name / display name if present
- element / faction / role if present
- slot chips: `basic`, `passive_base`, `skill_1`, `passive_advanced`, `skill_2`
- passive_advanced TODO/missing status where present
- legacy ultimate converted to `skill_2` with `is_true_ultimate=false`, where present

### 3. 6★ Catalog

Show all 13 6★ entries.

Must separate or visually label:

- 12 launch_base
- 1 launch_extra_premium: Borea

Must show:

- divine_weapon_id
- slots including ultimate
- Borea catalog-only note: roster/gacha/battle availability is not affected.

### 4. By Hero Search

Provide a lookup UI for:

- `greek_atalanta`
- `greek_athena`
- `greek_borea`
- `unknown_hero_xyz`

Unknown must show a clean 404/empty state without side effects.

### 5. Schema

Show schema / slot progression summary and reminder that final numbers are not finalized.

## Read-only Rules

- No activation buttons
- No upgrade buttons
- No edit buttons
- No write actions
- Only GET requests to the catalog endpoints
- No POST/PUT/PATCH/DELETE from this screen
- No combat runtime connection
- No HP bar runtime connection

## Absolute Safety Rules

- No DB writes
- No migrations / `--apply`
- No `battle_engine.py` changes
- No battle balance changes
- No live skill/status/VFX/icon activation
- No frontend HP bar changes
- No gacha/roster/Borea activation
- Do not modify Character Bible
- Do not modify `heroes_kits_5star.json`
- Do not modify inert hero skill kit JSON catalogs
- Do not modify runtime kit JSON files
- Do not modify asset files

## Acceptance Criteria

- Requirements validator PASS
- New screen renders on mobile without React error overlay
- Menu entry navigates correctly
- All sections/tabs accessible
- Summary shows counts and runtime flags
- 5★ section shows 20 entries
- 6★ section shows 13 entries
- By-hero lookup works for `greek_atalanta`, `greek_athena`, `greek_borea`, and `unknown_hero_xyz`
- Search/filter has no network spam
- Zero POST/PUT/PATCH/DELETE to catalog endpoints
- `/api/heroes` remains 100
- Borea remains hidden/pending
- TS: zero new errors in modified files

## Report Required

Return:

1. Files installed from ZIP
2. Files created/modified by implementation
3. Requirements validator output
4. Frontend smoke results
5. API/network smoke results
6. Runtime smoke
7. Safety checks
8. Explicit confirmation that the UI is read-only and not connected to battle/HP-bar runtime
