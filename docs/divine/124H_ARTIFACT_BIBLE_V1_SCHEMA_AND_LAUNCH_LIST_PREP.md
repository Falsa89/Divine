# 124H — PROJECT_B Track H — ARTIFACT_BIBLE_V1_SCHEMA_AND_LAUNCH_LIST_PREP

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_B`  
**Track**: H  
**Mode**: `design_schema_import_plan_only`  
**Verdict**: 🟢 `TRACK_H_ARTIFACT_BIBLE_V1_SCHEMA_READY`  
**Lifecycle status**: `design_only`

---

## 1. Scopo

Introdurre il **primo canonical schema dell'Artifact System**, allineato alla direzione user-approved: gli artefatti **NON sono equipaggiamenti**, **NON sono Divine Weapons**, **NON occupano gear slot**. Sono **oggetti da collezione roster-wide**, evocabili/potenziabili, con bonus globali roster/account a cap severi.

## 2. Hard rules canonical (9)

1. Artifacts are **NOT** equipment.
2. Artifacts are **NOT** equipped on heroes.
3. Artifacts do **NOT** occupy hero gear slots.
4. Artifacts are **NOT** Divine Weapons.
5. Artifacts are **NOT** unique 6⋆ weapons.
6. Artifacts do **NOT** replace standard equipment/gear.
7. Artifacts are **summonable/upgradeable roster-wide** collection objects.
8. Artifact bonuses are **global roster/account bonuses with strict caps**.
9. Artifact **live bonuses remain OFF** until Artifact Bible v1 e' approvata.

## 3. Distinct from

- divine_weapons (unique 6⋆ weapons)
- equipment / gear
- housing (passive room bonuses)
- skins / sprites (cosmetics)
- hero skill kits (innate kit)

## 4. Obtainment

**Allowed**: artifact_summon_banner (separato dal gacha eroi), event_reward, login_milestone, achievement_unlock, shop_limited_offer, crafting_from_fragments.  
**Forbidden v1**: hero_summon_banner, random_battle_drop.

## 5. Upgrade methods

**Allowed**: shard_consumption, dust_consumption_from_dupes, event_currency.  
**Forbidden v1**: hero_xp_consumption, gear_enhancement_stones.

## 6. Anti-power-creep caps (canonical)

| Cap | Valore |
|---|---|
| Per-artifact max bonus % | **5.0** |
| Per-category max stacked bonus % | 10.0 |
| Global master cap (account total %) | **25.0** |
| Max active artifacts at once | 12 |
| Per-rarity active cap | 1⋆=99, 2⋆=99, 3⋆=30, 4⋆=12, 5⋆=6, 6⋆=3 |

## 7. Schema v1 (Artifact Bible)

**Path**: `/app/data/design/artifacts/artifact_bible_schema_v1.json`

Campi canonical: `artifact_id` (pattern `^art_[a-z0-9_]+$`), `name`, `rarity` (1–6), `linked_hero_or_theme`, `linked_faction`, `linked_pantheon`, `linked_myth`, `collection_category` (6 categorie `_relic`), `obtainment_source`, `upgrade_method`, `global_roster_account_bonus` (scope + stat + value_pct ≤5.0), `anti_power_creep_caps_applied`, `launch_patch`, `status`, **hard invariants** `is_equipment=false`, `occupies_gear_slot=false`, `is_divine_weapon=false`.

## 8. Launch candidates v1 (5 draft)

**Path**: `/app/data/design/artifacts/artifact_bible_launch_candidates_v1.json`

Copertura: 5/5 fazioni (greek, norse, egyptian, japanese, celtic). 5/6 categorie (banner_relic deferred a v2).

| ID | Faction | Rarity | Scope | Stat | % |
|---|---|---|---|---|---|
| `art_aegis_of_olympus` | greek | 5⋆ | faction_wide | def | 3.0 |
| `art_yggdrasil_seed` | norse | 4⋆ | roster_wide | healing | 2.0 |
| `art_ankh_of_ra` | egyptian | 5⋆ | element_wide | atk | 3.5 |
| `art_kusanagi_fragment` | japanese | 4⋆ | role_wide | crit_damage | 2.5 |
| `art_cauldron_of_dagda` | celtic | 3⋆ | global_account | hp | 1.5 |

Tutti `status=design_only`, `is_equipment=false`, `is_divine_weapon=false`, `occupies_gear_slot=false`, `anti_power_creep_caps_applied=true`. Nessun `obtainment_source=hero_summon_banner`. Tutti rispettano `value_pct ≤ 5.0`.

## 9. Validator

- **Path**: `/app/backend/scripts/validate_project_b_artifact_bible_schema_v1.py`
- **Suite task_id**: `PROJECT-B-TRACK-H-ARTIFACT-BIBLE-SCHEMA` (OPTIONAL)
- **Type**: read-only schema + hard invariants enforcement (per ogni candidate)

## 10. Runtime activation gate

Lo `ARTIFACT_RUNTIME_ENABLED` feature flag puo' essere attivato solo dopo:
1. Artifact Bible v1 approved by user
2. Artifact Bonus Resolver pure stub created and inert
3. Anti-power-creep cap enforcement validator live
4. Explicit enable in dedicated pack

## 11. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Artifact runtime activation | ❌ No |
| Artifact live bonus application | ❌ No |
| Summon/gacha behavior change | ❌ No |
| Pricing/currency changes | ❌ No |
| Frontend/UI | ❌ No |
