# 29 — 5★ Legacy Status Tags Normalization Result

**Task origin:** RM1.28-D  
**Status:** design-only / catalog patched / read-only fields added  
**Runtime:** NOT attached  
**Borea:** unchanged — hidden / pending / catalog-only

---

## 1. Summary

Patched `hero_skill_kits_5star_full_v1.json` to remove all 111 legacy
status_tag occurrences from `status_tags` in the non-`passive_advanced`
slots (basic / passive_base / skill_1 / skill_2). They were redistributed
across:

- `design_taxonomy_tags` (taxonomy: damage / buff / debuff / control / heal + Bucket B-review)
- `rule_tags` (Bucket C: conditional_bonus)
- `trigger_tags` (Bucket C: trigger)
- `normalization_notes` (Bucket B / D ambiguous → manual review)

`passive_advanced` was **not touched** (already clean from RM1.28-A).

## 2. Before / After

| Metric | Before | After |
|---|---:|---:|
| Total legacy tags in `status_tags` | 111 | **0** |
| Distinct legacy tags in `status_tags` | 12 | **0** |
| Slots flagged `manual_review_required` | 0 | **5** |
| `passive_advanced` approved | 20/20 | 20/20 |
| `skill_2.is_true_ultimate=false` | 20/20 | 20/20 |
| Catalog-level `runtime_attached` | false | false |
| Catalog-level `balance_values_finalized` | false | false |
| Catalog-level `do_not_treat_as_live_kit` | true | true |
| Total entries | 20 | 20 |

## 3. Bucket-by-bucket result

### Bucket A — category_tag_keep_as_design_metadata
Moved out of `status_tags` into `design_taxonomy_tags`:
- `damage` (52), `buff` (24), `debuff` (11), `control` (6), `heal` (3) → **96 moves**

### Bucket B — likely_status_mapping_needed
| hero_id | slot | legacy_tag | action |
|---|---|---|---|
| `creature_lernaean_hydra` | skill_1 | `dot` | **mapped → `poison`** |
| `cursed_pestilence_herald` | skill_1 | `dot` | **mapped → `poison`** |
| `demonic_gehenna_witch` | skill_1 | `dot` | **mapped → `burn`** |
| `yokai_oni_kunoichi` | skill_1 | `dot` | **mapped → `bleed`** |
| `egyptian_claw_of_sekhmet` | skill_1 | `dot` | **manual_review** (ambiguous burn/bleed) |
| `creature_crimson_phoenix` | passive_base | `hot` | **mapped → `regeneration`** |
| `creature_crimson_phoenix` | skill_1 | `hot` | **manual_review** (direct heal vs regen) |
| `creature_lernaean_hydra` | skill_2 | `hot` | **manual_review** (ambiguous) |
| `angelic_bastion_angel` | skill_1 | `shield` | **mapped → `physical_shield`** |
| `angelic_bastion_angel` | skill_2 | `shield` | **mapped → `physical_shield`** |

Mapped: 7 · Manual review: 3.

### Bucket C — trigger_or_rule_tag_not_status
| hero_id | slot | legacy_tag | new field |
|---|---|---|---|
| `creature_crimson_phoenix` | passive_base | `trigger` | `trigger_tags` |
| `egyptian_bastet` | skill_2 | `conditional_bonus` | `rule_tags` |
| `norse_dawn_valkyrie` | skill_1 | `conditional_bonus` | `rule_tags` |

### Bucket D — ambiguous_needs_manual_review
| hero_id | slot | legacy_tag | result |
|---|---|---|---|
| `celtic_mist_banshee` | passive_base | `aura_debuff` | **manual_review** |
| `cursed_pestilence_herald` | passive_base | `debuff_aura` | **manual_review** |

### Bucket E — forbidden_or_invalid
**Zero occurrences.** No leaks of marchio_boreale, true_ultimate, divine_weapon, greek_borea, legacy borea, domain_effect_apply.

## 4. Manual_review_required entries left (5 total)

| hero_id.slot | reason |
|---|---|
| `celtic_mist_banshee.passive_base` | `aura_debuff` — needs per-skill mapping |
| `cursed_pestilence_herald.passive_base` | `debuff_aura` — needs per-skill mapping |
| `creature_crimson_phoenix.skill_1` | `hot` — ambiguous direct-heal vs regen |
| `creature_lernaean_hydra.skill_2` | `hot` — ambiguous direct-heal vs regen |
| `egyptian_claw_of_sekhmet.skill_1` | `dot` — ambiguous burn vs bleed |

## 5. New slot-level fields added (additive, idempotent)

- `design_taxonomy_tags: list[str]`
- `rule_tags: list[str]`
- `trigger_tags: list[str]`
- `normalization_notes: list[str]`
- `manual_review_required: bool`
- `normalization_metadata: { task_origin, first_normalized_at_utc, last_normalized_at_utc }`

No existing field renamed or removed.

## 6. Safety confirmation

```json
{
  "catalog_only": true,
  "design_audit_only": false,
  "runtime_attached": false,
  "battle_runtime_attached": false,
  "db_write_allowed": false,
  "auto_fix_applied": "conservative-controlled (RM1.28-D)",
  "borea_activation_allowed": false,
  "do_not_treat_as_live_kit": true,
  "manual_review_required_slots": 5
}
```

- `battle_engine.py` / `combat.tsx` / HP bar runtime / gacha / roster / Character Bible / asset → **not touched**
- DB / migrations / seed → **0 writes**
- 6★ catalog / Divine Weapon catalog / Marchio Boreale → **not touched**
- `/api/heroes` count → **100** (unchanged)
- `greek_borea` / legacy `borea` → **not visible in `/api/heroes`**
- RM1.28-C plan file → **restored to original snapshot** (audit script no longer auto-overwrites; pass `--write-plan` to refresh manually)

## 7. Files

| Path | Type |
|---|---|
| `/app/backend/scripts/normalize_5star_legacy_status_tags.py` | new patch script |
| `/app/backend/scripts/validate_5star_legacy_status_tags_normalized.py` | new post-patch validator |
| `/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json` | **patched** |
| `/app/backend/scripts/audit_5star_legacy_status_tags.py` | small safety tweak (no auto-overwrite of plan file) |

## 8. Re-run commands

```bash
python3 /app/backend/scripts/validate_5star_passive_advanced_source.py
python3 /app/backend/scripts/audit_5star_skill_kits_crosslinks.py
python3 /app/backend/scripts/validate_5star_legacy_status_tags_normalized.py
python3 /app/backend/scripts/validate_divine_weapon_catalog.py
python3 /app/backend/scripts/audit_divine_weapon_crosslinks.py
# Read-only audit can be re-run to confirm zero legacy tags remain in status_tags
python3 /app/backend/scripts/audit_5star_legacy_status_tags.py
# (use --write-plan only if explicitly refreshing the plan)
```

## 9. Future task (only after manual review of the 5 flagged slots)

**RM1.28-E (proposed)** — apply the 5 manual_review_required mappings
based on hero/skill description analysis, with explicit per-hero design
approval.
