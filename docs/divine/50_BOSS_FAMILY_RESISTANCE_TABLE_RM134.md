# RM1.34 — Boss Family Resistance / Immunity Table Foundation

**Task:** RM1.34
**Date (UTC):** 2026-05-15
**Mode:** Design-data only / read-only. **NO** runtime, **NO** endpoint, **NO** DB, **NO** catalog patch, **NO** baseline change.

---

## 1. File creati (3)

| Path | Scopo |
|---|---|
| `/app/data/design/boss_systems/boss_family_resistance_table_v1.json` | Tabella design-only per 9 boss family |
| `/app/backend/scripts/validate_boss_family_resistance_table.py` | Validator dedicato (read-only) |
| `/app/docs/divine/50_BOSS_FAMILY_RESISTANCE_TABLE_RM134.md` | Questo checkpoint |

## 2. File modificati (1, narrow)

| Path | Cambio |
|---|---|
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Entry OPTIONAL `RM1.34 → validate_boss_family_resistance_table.py`. Nessuna safety rule indebolita. |

Nessun catalogo / runtime / battle_engine / combat / battle_core / HP-bar / VFX / status / DW runtime / UI / .env / baseline / API runtime modificato. Nuova directory `boss_systems/` creata sotto `/app/data/design/`.

## 3. Boss family table summary

- `table_id = boss_family_resistance_table_v1`
- `task_origin = RM1.34`
- `source_design_contract` → RM1.32-C delta plan
- `metadata`: `design_only=true`, `runtime_attached=false`, `battle_runtime_attached=false`, `used_by_battle_engine=false`, `db_write=false`, `balance_values_finalized=false`, `patch_applied_to_catalogs=false`, `applied_to_combat=false`, `feature_flag_dependency=SKILL_KIT_RUNTIME_ENABLED` (currently false), `no_borea_activation=true`, `no_borea_visibility_change=true`.
- `global_policies`: marchio (owner `greek_borea`, team-wide=false, boss default cap=4, pvp default cap=3, freeze boss factor 0.5, damage boss factor 0.85), domain (one-per-side, strongest-wins, FIFO, max 3 turni, no same-turn refresh), DW synergy (design_only=true, ≤+10% global / ≤+5% PvP, additive only).
- `baseline_anchor_at_creation = hero_skill_kit_catalog_baseline_rm132b_v4`.

**Famiglie definite (9/9)**: `story_boss`, `normal_boss`, `elite_boss`, `raid_boss`, `world_boss`, `event_boss`, `guild_boss`, `training_dummy`, `pvp_dummy`.

## 4. Policy highlights by family

| Family | Hard CC dur cap (freeze) | DR threshold | DoT tick cap | Heal effectiveness vs hero | Shield eff cap | Notes |
|---|---|---|---|---|---|---|
| story_boss | 2 | 3 | 0.75 | 100% | 460 | profilo permissivo, story-mode |
| normal_boss | 2 | 3 | 0.6 | 90% | 460 | mid-tier daily dungeon |
| elite_boss | 2 (silence/taunt 1) | 2 | 0.5 | 80% | 460 | hard mode |
| **raid_boss** | **1** | 2 | 0.5 | **50%** | 420 | raid multi-team, healing dimezzato |
| **world_boss** | **1** (no full freeze lock) | 2 | **0.4** | 50% | 400 | massima resistenza |
| event_boss | 2 (silence/taunt 1) | 2 | 0.5 | 75% | 460 | elite/raid mix configurabile |
| guild_boss | 1 | 2 | 0.5 | 60% | 420 | raid-like guild coop |
| training_dummy | 3 (no DR) | 99 | 1.0 | 100% | 999 | QA, no DR; **boss DoT crit comunque disabilitato** |
| pvp_dummy | 2 | 3 | 1.0 | 75% | 460 | mirror PvP cap, status_chance cap 85% |

Tutte le 9 famiglie:
- `runtime_attached=false`, `design_only=true`
- `hard_control_policy` ha `freeze/stun/silence/taunt` con `duration_turns_cap` + `chance_multiplier` + `diminishing_returns_threshold` + `immune_after_applications`
- `dot_policy` copre `burn/poison/bleed/frostbite/shock/curse` con `can_crit=false` (vincolo universale)
- `anti_heal_policy`: `healing_block_max_duration_turns`, `healing_reduction_cap_pct`, `minimum_healing_floor_pct`
- `shield_heal_revive_policy`: `player_heal_effectiveness_pct`, `shield_concurrent_cap_per_ally`, `shield_effective_cap_pct`, `revive_per_ally_per_battle_max=1`, `death_protection_max_window_turns=1`

## 5. Marchio Boreale / Borea policy

- **Owner**: `greek_borea` su TUTTE le 9 famiglie (verificato dal validator).
- **`team_wide_amp_allowed=false`** su tutte le 9 famiglie.
- **`personal_status_only=true`**, transfer ad altri eroi vietato.
- **Boss families** (`story_boss`/`normal_boss`/`elite_boss`/`raid_boss`/`world_boss`/`event_boss`/`guild_boss`/`training_dummy`): `max_effective_stacks=4` (≤4 garantito).
- **`pvp_dummy`**: `max_effective_stacks=3` (≤3, mirror PvP cap del delta plan).
- **Freeze bonus su boss** ridotto a 0.5× (eccetto training_dummy/pvp_dummy che sono in PvE/QA-test contesto specifico).
- **Damage bonus su boss** ridotto in base alla famiglia (0.85 → 0.65 per world boss, ecc.).
- **`borea_activation=false`** (in tutta la table; nessun toggle live).
- Borea resta `catalog-only` / `hidden` in `/api/heroes` (verificato dall'API smoke).

## 6. Domain / Divine Weapon policy

**Domain (in tutte le famiglie + globale)**:
- `one_domain_active_per_side=true`
- `strongest_wins=true`, tie-break FIFO
- `max_duration_turns=3`
- `refresh_same_turn_allowed=false`
- cleansable

**Divine Weapon synergy (in tutte le famiglie + globale)**:
- `design_only=true`
- `live_numeric_modifier_applied=false`
- `numeric_modifier_cap_future_pct=10` (≤+10% globale; ≤+5% PvP)
- `per_owner_only=true`, `no_teamwide_global_amp=true`
- `additive_only_at_first_runtime_pass=true`

## 7. Validator results

`validate_boss_family_resistance_table.py` → **PASS**:

- 9/9 famiglie presenti ✓
- Tutte le 8 policy sections obbligatorie presenti su ogni famiglia ✓
- Hard CC: freeze/stun/silence/taunt con tutti i sub-fields obbligatori ✓
- DoT: burn/poison/bleed/frostbite/shock/curse + `can_crit=false` enforced ovunque ✓
- `max_distinct_dots` in range [1,5] ovunque ✓
- `tick_multiplier_cap` in range (0, 1] ovunque ✓
- Marchio: owner=`greek_borea` ovunque ✓, `team_wide_amp_allowed=false` ovunque ✓, raid/world/guild cap≤4 ✓, pvp_dummy cap≤3 ✓
- Domain: `one_domain_active_per_side=true`, `strongest_wins=true`, `max_duration≤3`, `refresh_same_turn=false` ovunque ✓
- DW synergy: `design_only=true`, `live_numeric_modifier_applied=false`, `no_teamwide_global_amp=true` ovunque ✓
- Runtime flags forbidden true: tutti `false` ✓
- RM1.32-C delta plan presente ✓
- Baseline v4 identity intact ✓

## 8. Suite / baseline results

| Run | Esito |
|---|---|
| `validate_boss_family_resistance_table.py` (NEW) | **PASS** |
| `validate_runtime_debug_snapshot_contract.py` | **PASS** (7/7) |
| `audit_skill_kit_runtime_debug_coverage_safety.py` | **PASS** |
| `audit_skill_kit_runtime_debug_endpoint_safety.py` | **PASS** |
| `audit_skill_kit_runtime_adapter_wiretest.py` | **PASS** (178/178) |
| `audit_skill_kit_runtime_adapter_safety.py` | **PASS** |
| `validate_5star_balance_foundation.py` | **PASS** |
| `validate_6star_balance_foundation.py` | **PASS** |
| `audit_balance_foundation_boss_pvp_caps.py` | **PASS** (86 WARN, 0 FAIL) |
| `validate_hero_skill_kit_catalog_baseline_diff.py` (auto → v4) | **PASS** |
| `validate_status_resolver_contract.py` | **PASS** |
| `validate_divine_weapon_catalog.py` | **PASS** |
| `audit_divine_weapon_crosslinks.py` | **PASS** |
| **Suite** `--include-baseline-diff` | **PASS 22/22 senza `--allow-changed` sotto v4** ✅ |

**Baseline v4 invariata.**

## 9. API smoke

Tutti gli endpoint canonici + debug 200/404 come atteso:

- `/api/health` 200, `/api/heroes` 200 con count=**100**
- Catalogs summary/5star/6star → 200; by-hero atalanta/athena/greek_borea → 200; alias legacy borea/primordial_gaia → 404
- DW summary + by-hero greek_borea → 200
- **Debug coverage** → 200 (178/178)
- **Debug preview** `greek_borea&ultimate&boss` → 200 (catalog-only Borea preview)

## 10. UI safety

| File | mutation | boss-table o adapter ref |
|---|---|---|
| `/app/frontend/app/hero-skill-kits-catalog.tsx` | 0 | 0 |
| `/app/frontend/app/divine-weapons-catalog.tsx` | 0 | 0 |

UI non modificata.

## 11. `/api/heroes` safety

Count = **100** ✓. `borea`, `greek_borea`, `primordial_gaia` tutti **hidden**.

## 12. Runtime / DB / gacha / roster / catalog safety

- ❌ Nessuna modifica a `battle_engine.py`, `combat.tsx`, `battle_core.py`, HP bar / status / VFX / DW runtime, API routes runtime, UI, DB, gacha, roster, Character Bible, assets, `final_numbers`, runtime flags, `divine_weapon_id`, `release_group`, hero_id, skill_id, nomi, descrizioni, status_ids, effect_tags, baseline files, debug endpoints.
- ✅ Solo aggiunti: 1 JSON design-data + 1 validator + 1 doc + 1 entry suite OPTIONAL. Nessun endpoint creato.
- ✅ Runtime adapter resta OFF/inert. Coverage endpoint dichiara ancora `runtime_enabled=false`, `applied_to_combat=false`, `adapter_imported_by_battle_runtime=false`.

## 13. Warning / discrepanze

Nessuna. La tabella è completamente isolata dal runtime; il validator dedicato controlla 22 invarianti per famiglia (vincoli runtime, marchio caps, DoT can_crit=false, domain policy, DW design-only). Tutti i sample API e debug continuano inert.

## 14. Final recommendation

**ACCEPTED.** Tutti i 25 criteri di accettazione di RM1.34 soddisfatti:

1–3 Tabella + validator + checkpoint creati ✅
4–6 Zero modifiche a catalog/baseline/runtime/DB/gacha/roster ✅
7–8 9 boss family richieste presenti, tutte le 8 policy sections obbligatorie ✅
9 Marchio owner = `greek_borea` ovunque ✅
10 `team_wide_amp_allowed=false` ovunque ✅
11 Raid/world/guild Marchio cap ≤4 ✅
12 PvP dummy Marchio cap ≤3 ✅
13 Hard CC policies (freeze/stun/silence/taunt) presenti ovunque ✅
14 DoT policies (burn/poison/bleed/frostbite/shock/curse) + `can_crit=false` enforced ✅
15 Domain policy presente ovunque (`one_domain_active_per_side=true`) ✅
16 DW synergy design-only ovunque (no live numeric modifier) ✅
17 Validator PASS ✅
18 Suite PASS 22/22 ✅
19 Baseline diff PASS sotto v4 ✅
20 API smoke PASS ✅
21 UI safety PASS ✅
22 `/api/heroes`=100 ✅
23 Borea hidden ✅
24 Runtime adapter OFF/inert ✅
25 Docs report final status ✅

## 15. Suggested next tasks

1. 🟡 **P2 RM1.34-B — Boss family × element/faction resistance matrix** (raccomandato): authoring read-only di una matrice supplementare che mappa ciascuna famiglia a fattori di resistenza per elemento (fire/water/wind/light/shadow/thunder) e faction (greek/norse/japanese/egyptian/celtic/yokai/creature/cursed/angelic/demonic/primordial/mesopotamian). Riferimento di design contract per future formula damage. Nessun runtime hookup.
2. 🟢 **P3 RM1.32-C2 (opt)** — Trim numerici minimi foundation_draft per generare baseline v5 (rimasto in coda).
3. 🟢 **P3 RM1.34-C (opt)** — Boss enrage/phase transition policy table (design-only, separate JSON) referenziando le famiglie definite qui.

---

### Appendix — baseline chain (invariata)

```
v1 → v2 → v3 → v4 (CURRENT, intatta in RM1.34)
```

### Appendix — design contract chain

```
RM1.32-C delta plan  →  RM1.34 boss family resistance table  →  (future) RM1.33-* runtime resolver (gated da SKILL_KIT_RUNTIME_ENABLED)
```
