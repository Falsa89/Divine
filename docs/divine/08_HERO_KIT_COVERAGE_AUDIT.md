# Hero Kit Coverage Audit

Status: approved utility doc  
Task: RM1.21-G  
Scope: design-data validation only

## Purpose

The Hero Kit Coverage Audit validates that every official hero in the Character Bible has exactly one kit entry across the design-data kit files.

It validates the following files:

- `data/design/heroes_kits_1star_2star.json`
- `data/design/heroes_kits_3star.json`
- `data/design/heroes_kits_4star.json`
- `data/design/heroes_kits_5star.json`
- `data/design/heroes_kits_6star_extra.json`

Against:

- `backend/data/character_bible.py`

Expected total coverage:

- 100 `launch_base` heroes
- 1 `launch_extra_premium` hero: `greek_borea`
- 101 official heroes total

## Command

```bash
python backend/scripts/validate_hero_kits_coverage.py
```

The script writes a JSON report to:

```text
backend/reports/hero_kits_coverage_audit_<timestamp>.json
```

`backend/reports/` must remain gitignored.

## Required pass conditions

- All kit JSON files parse correctly.
- Every official Character Bible hero has exactly one kit.
- No kit uses an unknown `hero_id`.
- No duplicate `hero_id` exists across kit files.
- `native_rarity`, `max_stars`, `element`, `role`, `faction`, and `release_group` match the Character Bible.
- `greek_borea` exists exactly once and is marked `launch_extra_premium`.
- Slot rules are respected by rarity.
- Low-rarity kits do not use forbidden advanced effects.
- 6★ kits include an iconic mechanic marker.

## Runtime safety

This audit is read-only.

It must not:

- write to DB;
- run migrations;
- run `--apply` scripts;
- change backend runtime;
- change frontend runtime;
- change battle engine;
- change gacha;
- modify Character Bible;
- modify kit JSON contents.
