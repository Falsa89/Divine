# RM1.26-B — Convert Approved 5★ Skill Design Source into Inert Hero Skill Kit Catalog

## Purpose

This task converts the already-approved consolidated 5★ Skill Design source into a machine-readable inert/read-only catalog.

This is **not** a creative authoring task. The 5★ kits were already discussed and approved earlier. Do not re-open, rewrite, rebalance, or reconstruct them.

## Critical correction

A previously rewritten 5★ Tank block in chat is non-canonical. Ignore it if it conflicts with the approved consolidated 5★ source.

## Required behavior

1. Install this requirements pack.
2. Search the repo for the consolidated approved 5★ Skill Design source.
3. If the source is found and clearly canonical, convert it into:

```text
/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json
```

4. If the source is missing, stop and report `source_missing`.
5. If multiple conflicting sources are found, stop and report `source_conflict`.

## Valid source locations

Search these first:

```text
/app/docs/divine/
/app/data/design/
/app/data/design/hero_skill_kits/
```

Also consider any explicit user-provided file imported for this task.

## Output catalog constraints

The full catalog, if created, must be inert/read-only:

```json
{
  "runtime_attached": false,
  "balance_values_finalized": false,
  "do_not_treat_as_live_kit": true
}
```

Every 5★ hero entry must contain exactly these expected slots:

```text
basic
passive_base
skill_1
passive_advanced
skill_2
```

Forbidden for native 5★ entries:

```text
ultimate
native 6★ divine_weapon_hooks
true 6★ domain_hooks
final balance numbers
```

All balance values must remain null or marked as not finalized.

## Required 5★ hero IDs

The output must cover exactly these 20 native 5★ launch_base heroes:

```text
greek_nemean_lioness
norse_frost_jotunn
angelic_bastion_angel
norse_dawn_valkyrie
egyptian_claw_of_sekhmet
greek_atalanta
greek_circe
japanese_raijin_miko
infernal_gehenna_witch
egyptian_bastet
japanese_oni_kunoichi
greek_nike
norse_fate_volva
norse_eir
greek_medusa
celtic_mist_banshee
japanese_yuki_onna
crimson_phoenix
greek_lernaean_hydra
cursed_pestilence_herald
```

## Absolute safety rules

- No DB writes
- No migrations
- No `--apply`
- No battle engine changes
- No live skill/status/VFX activation
- No HP bar changes
- No gacha changes
- No roster activation
- Do not activate Borea
- Do not modify legacy `borea`
- Do not modify Character Bible
- Do not modify runtime kit JSON
- Do not modify assets
- Do not import this catalog into combat runtime
- Do not add endpoints
- Do not create UI

## Validation

Run:

```bash
python /app/backend/scripts/validate_hero_skill_kits_5star_conversion.py
```

The validator validates the requirements and, if the full catalog exists, validates its structure.

If the full catalog is not created because the source is missing, the validator should still pass the requirements file but the report must state `source_missing`.

## Final report required

Respond with:

1. Files installed
2. Approved source search result
3. If source found: source path(s) used
4. If source missing/conflict: exact stop reason
5. Files created/modified beyond ZIP
6. Validator output
7. Runtime smoke
8. Safety checks
9. Explicit confirmation that the catalog is inert/read-only and not connected to battle runtime
