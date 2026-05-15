# RM1.32-B — 6★ Balance Pass Foundation + Baseline v4

**Task:** RM1.32-B
**Date (UTC):** 2026-05-15
**Scope:** 6★ Balance Foundation (design data only) + Baseline v4 anchor
**Mode:** Inert / design-data only. NO runtime / DB / gacha / roster / Borea activation.

---

## 1. Files created (6)

| Path | Purpose |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kits_6star_balance_contract_v1.json` | 6★ balance contract (allowed fields, ranges, safety rules) |
| `/app/data/design/hero_skill_kits/hero_skill_kits_6star_balance_foundation_source_v1.json` | 6★ source numeric anchors for 13×6 slots |
| `/app/backend/scripts/rm132b_build_6star_balance_foundation.py` | One-shot builder/patcher |
| `/app/backend/scripts/validate_6star_balance_foundation.py` | New 6★ balance validator |
| `/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json` | **Baseline v4** (post-RM1.32-B) |
| `/app/docs/divine/44_6STAR_BALANCE_FOUNDATION_RM132B.md` | This checkpoint |

## 2. Files modified (6 — all narrow / authorized)

| File | Change |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json` | **Patched**: 78 slots received `final_numbers` foundation_draft; top-level `balance_pass_id=RM1.32-B`, `last_balance_foundation_write` block added. NO other fields touched. |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Added `RM1.32-B → validate_6star_balance_foundation.py` to required suite + `--allow-changed` pass-through |
| `/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py` | Diff invariants: accept 6★ `foundation_draft` (same allowance that already existed for 5★) |
| `/app/backend/scripts/validate_5star_balance_foundation.py` | 6★ cross-check accepts `foundation_draft` (was requiring null) |
| `/app/backend/scripts/validate_6star_catalog_safety_metadata.py` | 78/78 slot inertness accepts `foundation_draft`/`runtime_ready=false` |
| `/app/backend/scripts/audit_6star_skill_kits_crosslinks.py` | Acceptance #15 accepts `foundation_draft` |
| `/app/backend/scripts/audit_hero_skill_kit_catalog_consolidation.py` | 6★ block accepts `foundation_draft` |
| `/app/backend/scripts/audit_6star_balance_readiness.py` | Forward-compatible: accepts both pre- and post-RM1.32-B states |

No catalog data (other than `final_numbers` blocks + safe top-level balance metadata) was modified. NO change to: hero_id, skill_id, slot names, skill names/effects/descriptions, status tags, core_status_ids, core_effect_tags, divine_weapon_id, release_group, or any 5★ / Divine Weapon / status catalog data.

## 3. Backup manifest

**Pre-patch backup:** `/app/backups/hero_skill_kits/backup_20260515T205957Z/MANIFEST.json`

Contents (5 files):
- `hero_skill_kits_5star_full_v1.json` (sha `330b337e…`, 273,597 B)
- `hero_skill_kits_6star_borea_v1.json` (sha `4172da0d…`, 60,143 B) ← rollback target
- `divine_weapons_catalog_v1.json` (sha `e3ed42f5…`, 159,805 B)
- `hero_skill_kit_schema_v1.json` (sha `f5b30b6d…`, 2,755 B)
- `hero_skill_kit_catalog_baseline_rm132pre_v1.json` (sha `f75d20aa…`, 3,382 B)

Reason: `pre-RM1.32-B 6star balance foundation patch`.

## 4. 6★ balance contract / source summary

### Contract
- `contract_id = hero_skill_kits_6star_balance_contract_v1`
- `task_origin = RM1.32-B`
- 13 entries × 6 slots = 78 expected slots
- Allowed fields per slot defined per-slot-kind (basic / passive_base / skill_1 / passive_advanced / skill_2 / ultimate)
- Ultimate alone allows `is_true_ultimate=true`
- Borea-only additional fields: `marchio_boreale_stack_values`, `unique_mechanic_placeholder`
- Numeric ranges:
  - basic damage 85–130, status_chance 0–50, cd=0
  - skill_1 damage 140–340 (per target), cd=3
  - skill_2 damage 220–520, cd 4–5
  - ultimate damage 260–720, cd 6–7, status_chance 85–100
  - passive `stat_modifier_pct` 12–28
  - Marchio: stacks 1–3 (PvP) / 1–5 (PvE), dmg/stack 3–10, freeze/stack 2–6
- Forbidden fields: `final_runtime_attached`, `battle_runtime_id`, `live_hooks`, `db_resolver`, `runtime_target`, `vfx_runtime`
- Safety rules: `runtime_ready=false`, `balance_values_finalized=false`, `runtime_attached=false`, `battle_runtime_attached=false`, `do_not_treat_as_live_kit=true`, ultimate `is_true_ultimate=true` on all 13, non-ultimate cannot be true ultimate, Marchio only on greek_borea, Borea hidden in `/api/heroes`, `borea_activation_allowed=false`, no legacy `borea`/`primordial_gaia`.

### Source
- `source_id = hero_skill_kits_6star_balance_foundation_source_v1`
- 13 entries → 6 slots each → 78 final_numbers anchors
- Role-aware archetype mapping:

| Hero | Archetype |
|---|---|
| greek_athena | tank_support |
| greek_artemis | ranged_dps |
| greek_gaia | tank_revive |
| primordial_nyx | aoe_control_mage |
| japanese_raijin | aoe_dps_mage |
| japanese_susanoo | assassin_burst |
| japanese_amaterasu | healer_buffer |
| egyptian_sekhmet | melee_dps |
| mesopotamian_tiamat | tank_aoe |
| egyptian_isis | healer_revive |
| celtic_morrigan | assassin_control |
| cursed_pestilence_horseman | control_dot |
| greek_borea | control_mage_freeze (+ Marchio) |

## 5. Patch summary

- 78/78 slots → `final_numbers` foundation_draft objects ✅
- 13/13 ultimate slots → `is_true_ultimate=true` ✅
- 0/65 non-ultimate slots → `is_true_ultimate` set ✅
- Marchio Boreale draft values: 4 slots on `greek_borea` only (`basic`, `skill_1`, `skill_2`, `ultimate`) ✅
- Divine Weapon synergy placeholders: 78/78 slots — all `design_only=true`, `runtime_ready=false`, `numeric_modifier_pct=null` ✅
- Top-level `balance_pass_id = RM1.32-B`, `last_balance_foundation_write` block present, `runtime_attached=false`, `battle_runtime_attached=false`, `balance_values_finalized=false`, `do_not_treat_as_live_kit=true` ✅
- NO change to: hero_id, skill_id, slot names, skill names, effects, descriptions, status tags, core_status_ids, core_effect_tags, divine_weapon_id, release_group, any 5★ data, any DW data, any status catalog data.

## 6. Representative 6★ values (sample)

### greek_athena (tank_support, light, faction=greek)
| slot | dmg% | shield% | status% | cd | tgt | notes |
|---|---|---|---|---|---|---|
| basic | 100 | — | 30 | 0 | 1 | — |
| skill_1 | 170 | 200 | 70 | 3 | 3 | — |
| skill_2 | 240 | 300 | 85 | 5 | 5 | — |
| ultimate | 360 | 460 | 95 | 7 | 5 | `is_true_ultimate=true` |

### greek_artemis (ranged_dps, wind)
| slot | dmg% | status% | cd | tgt | notes |
|---|---|---|---|---|---|
| basic | 120 | 30 | 0 | 1 | — |
| skill_1 | 260 | 75 | 3 | 1 | — |
| skill_2 | 420 | 85 | 5 | 1 | — |
| ultimate | 680 | 95 | 7 | 1 | `is_true_ultimate=true` |

### greek_borea (control_mage_freeze, wind, Marchio Boreale)
| slot | dmg% | status% | cd | tgt | Marchio draft |
|---|---|---|---|---|---|
| basic | 110 | 35 | 0 | 1 | yes (design-only) |
| skill_1 | 180 | 80 | 3 | 3 | yes |
| skill_2 | 280 | 90 | 5 | 5 | yes |
| ultimate | 400 | 95 | 7 | 5 | yes; `is_true_ultimate=true` |

## 7. Borea / Marchio handling

- `greek_borea` included as **catalog-only design data**: kept `release_group=launch_extra_premium`, `runtime_attached=false`, `battle_runtime_attached=false`.
- Borea **NOT visible** in `/api/heroes` (confirmed: count=100, `greek_borea`/`borea`/`primordial_gaia` all absent).
- Marchio Boreale draft values present **ONLY** on the 4 non-passive Borea slots:
  - `personal_status_id=marchio_boreale`, `owner_hero_id=greek_borea`
  - `max_stacks_pvp=3`, `max_stacks_pve=5`
  - `damage_bonus_per_stack_pct=7`, `freeze_chance_bonus_per_stack_pct=4`
  - `decay_rule`, `cleanse_rule`, `boss_resistance_notes`, `pvp_caution_notes` — all `design_only`
  - `runtime_ready=false`
- `unique_mechanic_placeholder` also Borea-only (4 slots), design-only.
- 0 Marchio leak on the other 12 entries (verified by `validate_status_resolver_contract` and `audit_6star_skill_kits_crosslinks`).

## 8. Divine Weapon synergy placeholders

- Present on **78/78** slots inside `final_numbers.divine_weapon_synergy_placeholder`.
- Every placeholder: `design_only=true`, `runtime_ready=false`, `linked_weapon_id_from_entry=true`, `numeric_modifier_pct=null`.
- No numeric runtime modifier applied at this foundation pass. Strictly taxonomy/descriptive.
- No `divine_weapon_id` reassignment (preserved unchanged for all 13).

## 9. Validator / suite / baseline results

| Run | Result |
|---|---|
| `validate_5star_balance_foundation.py` | **PASS** (100/100 5★ foundation_draft preserved) |
| `validate_6star_balance_foundation.py` (NEW) | **PASS** (78/78 6★ foundation_draft, 13/13 ultimate true) |
| `run_hero_skill_kit_validator_suite.py` (default) | **PASS 14/14** |
| `… --include-baseline-diff --allow-changed 6★` (pre-v4) | **PASS 15/15** |
| `… --include-baseline-diff` (post-v4, **no allow-changed**) | **PASS 15/15** ✅ |
| `validate_hero_skill_kit_catalog_baseline_diff.py` (default → auto v4) | **PASS** |
| `validate_status_resolver_contract.py` | **PASS** (197 6★ refs resolve, 0 Marchio leak in non-Borea) |
| `audit_hero_skill_kit_catalog_consolidation.py` | **PASS** |
| `audit_6star_skill_kits_crosslinks.py` | **PASS** (13/13 DW cross-link) |
| `validate_6star_catalog_safety_metadata.py` | **PASS** (78/78 slots inert) |
| `audit_6star_effect_tags_taxonomy.py` | **PASS** (taxonomy unchanged) |
| `validate_divine_weapon_catalog.py` | **PASS** |
| `audit_divine_weapon_crosslinks.py` | **PASS** |
| `audit_6star_balance_readiness.py` (forward-compat) | **PASS** (now reflects post-RM1.32-B state) |

## 10. Baseline v4 summary

- `baseline_id = hero_skill_kit_catalog_baseline_rm132b_v4`
- `based_on = 6star_balance_foundation_approved`
- `previous_baseline = hero_skill_kit_catalog_baseline_rm132apost_v3`
- `generated_at_utc = 2026-05-15T21:03:24.663650Z`
- v1/v2/v3 **preserved** (chain documented).
- Tracked SHAs updated for 6★ catalog only (others unchanged):

| File | sha256 |
|---|---|
| 5★ catalog | `330b337e…` (unchanged from v3) |
| **6★ catalog** | **`abf9b2a2…` (NEW, post-RM1.32-B)** |
| Divine Weapon catalog | `e3ed42f5…` (unchanged) |
| Schema | `f5b30b6d…` (unchanged) |
| Status catalog | `16441076…` (unchanged) |

Counts: `5★=20 (100 fn)`, `6★=13 (78 fn)`, `DW=13`.

Critical invariants encoded:
- `api_heroes_expected_count = 100`
- `greek_borea_visible_in_api_heroes = false`
- `legacy_borea_visible_in_api_heroes = false`
- `primordial_gaia_visible_anywhere = false`
- `5star_final_numbers_state = foundation_draft`, runtime_ready=false
- `6star_final_numbers_state = foundation_draft`, runtime_ready=false
- `6star_ultimate_is_true_ultimate_count = 13`
- runtime/battle_runtime attached = false everywhere
- `marchio_boreale_borea_only = true`
- `divine_weapon_synergy_placeholders_design_only = true`

## 11. API smoke

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | **200** |
| `GET /api/heroes` count | 100 | **100** ✓ |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | **200** (20 entries, 100/100 foundation_draft) |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | **200** (13 entries, **78/78 foundation_draft**, 13/13 `is_true_ultimate=true`) |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_athena` | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/by-hero/japanese_raijin` | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` (catalog-only) | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | 404 | **404** ✓ |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` | 200 | **200** |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | **200** |

## 12. UI safety audit

| File | axios/fetch mutations | `method:POST/PUT/PATCH/DELETE` literal | Pressable+runtime kw |
|---|---|---|---|
| `/app/frontend/app/hero-skill-kits-catalog.tsx` | 0 | 0 | 0 |
| `/app/frontend/app/divine-weapons-catalog.tsx` | 0 | 0 | 0 |

UI files NOT modified by this task. No runtime action buttons. SAFE.

## 13. `/api/heroes` safety

- Count = **100** ✓
- `greek_borea` hidden ✓
- legacy `borea` hidden ✓
- `primordial_gaia` hidden ✓

## 14. Runtime / DB / gacha / roster / catalog safety

- ❌ No `battle_engine.py`, `combat.tsx`, HP bar runtime, API routes/loaders, UI files modified.
- ❌ No DB writes / migrations / seed.
- ❌ No gacha / roster / Character Bible / assets / status runtime / VFX runtime / Divine Weapon runtime touched.
- ❌ No Borea activation / visibility change.
- ❌ No hero_id / skill_id / slot / display_name / description / effect / status tag / core_status_id / core_effect_tag / divine_weapon_id / release_group changed.
- ✅ Only `final_numbers` (78 slots, previously null) + top-level balance metadata on 6★ catalog mutated.
- ✅ `runtime_attached / battle_runtime_attached / balance_values_finalized` all remain `false`.

## 15. Changed file SHA — before / after

| File | SHA before (v3) | SHA after (v4) |
|---|---|---|
| `hero_skill_kits_6star_borea_v1.json` | `4172da0d4a5d00e76f5240aaf768eb23ff8a211c7516b990df8fde1e07b72cc2` | `abf9b2a2f02b59127984a9eeb32993e4fb9c86aeeb89b1074d3ec81312a2d68b` |

All other tracked files: **SHA unchanged**.

## 16. Warnings / discrepancies

None. v3 baseline diff under `--allow-changed 6★` correctly transitioned to v4 default-pass without `--allow-changed`. Validators that previously expected 6★ `final_numbers null` were updated narrowly to accept the post-RM1.32-B `foundation_draft` state — they continue to enforce the strict runtime-false invariants.

## 17. Recommendation — final status

**ACCEPTED.** All 32 acceptance criteria of RM1.32-B satisfied:

1–3 Contract + Source + Backup created ✅
4–9 Catalog patched only in `final_numbers`/metadata; 13 entries × 78 fn objects; 5★/DW/names/descs/tags/IDs unchanged ✅
10–15 Safety flags, ultimate semantics, Borea catalog-only, Marchio only on Borea, DW IDs preserved ✅
16–22 5★ + 6★ validators + suite green ✅
23–25 Baseline diff allow-changed pre-v4 PASS; baseline v4 created; suite baseline diff no-allow-changed POST-v4 PASS ✅
26–28 API smoke / UI safety / `/api/heroes=100` ✅
29–32 No DB / no runtime files / no gacha-roster-Bible-assets / docs/checkpoint created ✅

## 18. Suggested next task — prioritized

1. 🟡 **P2 RM1.33-A** — Runtime Adapter Skeleton with feature flag `SKILL_KIT_RUNTIME_ENABLED=false`. Scaffolds the read path from catalog to battle engine while keeping runtime OFF. Foundation work for eventual final balance pass. *Highest forward value, safe under the feature flag.*
2. 🟡 **P2 RM1.32-C** (optional balance refinement) — Boss/Domain Resistance & PvP Cap Audit on the 6★ foundation values; produces a delta plan (still design-only) for a future v5 baseline. *Low risk, design-time value.*
3. 🟢 **P3 RM1.31-F-B (opt)** — Negative-rollback drill on `/tmp` clone for STEP 4/4 auto-rollback of the authoring CLI. *Safety drill only.*

---

### Appendix — baseline chain

```
v1: hero_skill_kit_catalog_baseline_rm132pre_v1     (RM1.32-PRE,    initial anchor)
v2: hero_skill_kit_catalog_baseline_rm132preb2_v2   (RM1.32-PRE-B2, post-RM1.31-F safe write)
v3: hero_skill_kit_catalog_baseline_rm132apost_v3   (RM1.32-A-POST, post-RM1.32-A 5★ foundation_draft)
v4: hero_skill_kit_catalog_baseline_rm132b_v4       (RM1.32-B,      post-RM1.32-B 6★ foundation_draft)  ← CURRENT
```
