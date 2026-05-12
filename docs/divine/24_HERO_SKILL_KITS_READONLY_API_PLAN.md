# RM1.26-C — Hero Skill Kit Read-Only Catalog API Plan

## Goal

Expose the inert hero skill kit catalogs created in RM1.26-A and RM1.26-B2 through backend read-only API endpoints.

This is a catalog inspection/API foundation task only. It must not connect hero skill kits to combat, battle balance, HP bar, status runtime, VFX runtime, gacha, roster activation, or any frontend combat runtime.

## Source catalogs

Use only these files:

- `/app/data/design/hero_skill_kits/hero_skill_kit_schema_v1.json`
- `/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json`
- `/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json`
- `/app/data/design/hero_skill_kits/hero_skill_kits_5star_manifest_v1.json` if needed for cross-checking only

Do not modify the source files.

## Proposed implementation

Create:

- `backend/data/hero_skill_kits_loader.py`
- `backend/routes/hero_skill_kits_catalogs.py`
- register the route module in `backend/game_systems.py`

The loader must be read-only, lazy and cache-based. It must read JSON from design files only and must not query or mutate the database.

## Endpoints

- `GET /api/hero-skill-kits/catalogs/summary`
- `GET /api/hero-skill-kits/catalogs/schema`
- `GET /api/hero-skill-kits/catalogs/5star`
- `GET /api/hero-skill-kits/catalogs/6star`
- `GET /api/hero-skill-kits/catalogs/by-hero/{hero_id}`

## Summary expectations

The summary endpoint should expose:

- `five_star_entries_count = 20`
- `six_star_launch_base_entries_count = 12`
- `six_star_extra_premium_entries_count = 1`
- `six_star_total_entries_count = 13`
- `total_catalog_entries_count = 33`
- `runtime_attached = false`
- `battle_runtime_attached = false`
- `ui_runtime_attached = false`
- `hp_bar_runtime_attached = false`
- `balance_values_finalized = false`
- `do_not_treat_as_live_kit = true`

## By-hero behavior

`GET /api/hero-skill-kits/catalogs/by-hero/{hero_id}` should search the inert 5★ and 6★ catalogs by canonical `hero_id`.

Examples expected to work:

- `greek_atalanta` → 5★ catalog entry
- `greek_athena` → 6★ catalog entry
- `greek_borea` → 6★ extra premium entry, still inert and hidden in live roster APIs

Unknown IDs should return 404 without side effects.

## Absolute safety rules

- No DB writes
- No migrations
- No `--apply`
- No `battle_engine.py` changes
- No battle balance changes
- No live skill/status/VFX/icon activation
- No HP bar changes
- No gacha changes
- No roster activation
- Do not activate Borea
- Do not modify legacy `borea`
- Do not modify Character Bible
- Do not modify source `heroes_kits_5star.json`
- Do not modify runtime kit JSON files
- Do not modify assets
- Do not import these catalogs into battle runtime
- Do not connect these catalogs to frontend combat runtime
- Do not create UI in this task
- Only GET endpoints are allowed

## Runtime smoke

Required after implementation:

- `GET /api/health` returns 200
- `GET /api/heroes` count remains 100
- Borea remains hidden/pending
- legacy `borea` remains non-official/legacy
- grep verifies no imports in `battle_engine.py` or frontend combat files

## Report required

The final report must include:

1. Files installed from ZIP
2. Files created/modified by implementation
3. Requirements validator output
4. Endpoint smoke results
5. Summary payload key counts and flags
6. By-hero smoke results
7. Runtime smoke
8. Safety checks
9. Explicit confirmation that catalogs are read-only and not connected to battle runtime or HP bar runtime
