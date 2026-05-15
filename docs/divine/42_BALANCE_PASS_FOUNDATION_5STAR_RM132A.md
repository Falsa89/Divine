# RM1.32-A — 5★ Balance Pass Foundation

**Status:** ✅ **PASS** — Conservative foundation balance numbers applied to all 20 × 5 = 100 5★ slots. ZERO runtime/DB/gacha/roster changes. 6★/DW catalogs untouched. Borea remains hidden. Baseline NOT regenerated (deferred to follow-up).

---

## 1. Files Created

| Path | Role |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kits_5star_balance_contract_v1.json` | Allowed fields per slot, numeric ranges, forbidden fields, safety rules |
| `/app/data/design/hero_skill_kits/hero_skill_kits_5star_balance_foundation_source_v1.json` | Per-hero per-slot conservative `final_numbers` (foundation_draft) |
| `/app/backend/scripts/validate_5star_balance_foundation.py` | Dedicated validator (top-level + 100/100 final_numbers + ranges + status resolver) |
| `/app/docs/divine/42_BALANCE_PASS_FOUNDATION_5STAR_RM132A.md` | This checkpoint |
| `/app/backups/hero_skill_kits/backup_20260515T203...Z/` | Pre-patch backup (5 files + MANIFEST.json, reason `RM1.32-A_pre_balance_foundation`) |

## 2. Files Modified

| Path | Change |
|---|---|
| `/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json` | All 100 5★ slots received a `final_numbers` `foundation_draft` object; added top-level `balance_pass_id="RM1.32-A"` + `last_balance_foundation_write` metadata block. NO skill content / status / effect tag / divine_weapon_id / release_group change. |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Added `('RM1.32-A', 'validate_5star_balance_foundation.py')` to REQUIRED list. |
| `/app/backend/scripts/validate_5star_passive_advanced_source.py` | Allow `foundation_draft` `final_numbers` (5★) instead of failing on non-null. |
| `/app/backend/scripts/audit_5star_skill_kits_crosslinks.py` | Same allowance. |
| `/app/backend/scripts/validate_5star_legacy_status_tags_normalized.py` | Same allowance (2 sites). |
| `/app/backend/scripts/validate_5star_manual_review_residuals_resolved.py` | Same allowance (2 sites). |
| `/app/backend/scripts/audit_hero_skill_kit_catalog_consolidation.py` | Same allowance, **scoped to label `5★` only**. 6★ continues to require strict null. |
| `/app/backend/scripts/validate_hero_skill_kit_catalog_baseline_diff.py` | Same allowance, scoped to label `5★` only. 6★ stays strict. |

No catalog data outside the 5★ catalog was modified. No DB / runtime / API route / loader / UI / asset / Character Bible change.

## 3. Backup Manifest Path

```
/app/backups/hero_skill_kits/backup_20260515T2032??Z/MANIFEST.json
reason: RM1.32-A_pre_balance_foundation
files : 5 (5★ pre-patch, 6★, DW, schema, baseline)
```

Pre-patch 5★ SHA256 prefix: `fc87088e…` (recorded in manifest).
Post-patch 5★ SHA256 prefix: **`330b337e…`**.

## 4. Balance Contract / Source Summary

**Contract** (`hero_skill_kits_5star_balance_contract_v1.json`)
- `task_origin = RM1.32-A`
- `is_foundation_pass = true`
- Per-slot allowed fields:
  - basic / skill_1 / skill_2: `status, runtime_ready, damage_multiplier_pct, healing_multiplier_pct, shield_multiplier_pct, status_chance_pct, status_duration_turns, cooldown_turns, target_count, scaling_stat, effect_strength_tier, draft_balance_notes, review_required, notes` (+ `is_true_ultimate` for skill_2)
  - passive_*: `status, runtime_ready, trigger, stat_modifier_pct, status_chance_pct, status_duration_turns, internal_cooldown_turns, scaling_stat, effect_strength_tier, draft_balance_notes, review_required, notes`
- Numeric ranges (examples):
  - `basic.damage_multiplier_pct ∈ [70,130]`
  - `skill_1.damage_multiplier_pct ∈ [80,260]` / `skill_2 ∈ [120,400]`
  - `skill_1.cooldown_turns ∈ [2,3]` / `skill_2 ∈ [4,5]`
  - `skill_*.status_chance_pct` ∈ [30,90]/[40,95]
  - `passive.stat_modifier_pct ∈ [5,25]` / `internal_cooldown_turns ∈ [0,6]`
- Forbidden fields: `final_runtime_attached, battle_runtime_id, live_hooks, db_resolver, runtime_target, vfx_runtime`
- Safety rules: `runtime_ready_must_be_false`, `balance_values_finalized_must_stay_false`, `runtime_attached_must_stay_false`, `battle_runtime_attached_must_stay_false`, `do_not_treat_as_live_kit_must_stay_true`, `skill_2_is_true_ultimate_must_be_false_for_all_20`, `no_ultimate_slot_in_5star`, `no_divine_weapon_in_5star`, `no_domain_in_5star`, `no_marchio_boreale_in_5star`, `no_legacy_borea_hero_id`.

**Source** (`hero_skill_kits_5star_balance_foundation_source_v1.json`)
- 20 entries, role-aware conservative defaults per slot (`role` field per hero, see §5).

## 5. Patch Summary

- **Slots patched:** 100/100 (20 heroes × 5 slots each).
- **Top-level fields added/refreshed on 5★ catalog:** `balance_pass_id="RM1.32-A"`, `balance_values_finalized=false`, `runtime_attached=false`, `battle_runtime_attached=false`, `do_not_treat_as_live_kit=true`, `last_balance_foundation_write{...}`.
- **Per-slot field added:** `final_numbers` (foundation_draft).
- **Unchanged per slot:** `slot`, `skill_id`, `display_name`, `design_summary`, `skill_type`, `element`, `status_tags`, `status_interactions`, `core_effect_tags`, `core_status_ids`, `effect_tags`, `design_status`, `is_true_ultimate` (preserved as false), names, descriptions.

The `skill_2.is_true_ultimate=false` is duplicated into `final_numbers.is_true_ultimate=false` for traceability; the original slot-level field remains false on 20/20.

## 6. Representative Balance Values (foundation_draft, NOT runtime)

| Hero | Role | basic.dmg% / sc% | skill_1.dmg%/tc/cd | skill_2.dmg%/tc/cd | passive_base/advanced modifier% |
|---|---|---|---|---|---|
| `greek_atalanta` | assassin | 110 / 30 | 230 / 1 / 3 | 340 / 1 / 5 | 10 / 15 |
| `norse_eir` | healer | 80 / 25 | heal 130 / 3 / 3 | heal 200 + shield 150 / 3 / 5 | 10 / 15 |
| `angelic_bastion_angel` | tank | 90 / 25 | 110 + shield 160 / 1 / 3 | 170 + shield 200 / 5 / 5 | 10 / 15 |
| `greek_nike` | support_buff | 80 / 25 | heal 110 + shield 140 / 3 / 3 | heal 170 + shield 180 / 5 / 5 | 10 / 15 |
| `japanese_miko_of_raijin` | aoe_dps_shock | 95 / 25 | 110 / 3 / 3 | 170 / 5 / 5 | 10 / 15 |
| `greek_medusa` | control_petrify | 85 / 30 | 130 / 1 / 3 | 180 / 3 / 5 | 10 / 15 |
| `yokai_oni_kunoichi` | assassin | 110 / 30 | 230 / 1 / 3 | 340 / 1 / 5 | 10 / 15 |
| `creature_lernaean_hydra` | aoe_dot_regen | 95 / 25 | 110 / 3 / 3 | 170 / 5 / 5 | 10 / 15 |

All values are well inside the contract ranges. `runtime_ready=false`, `status="foundation_draft"`, `notes="foundation draft; not runtime"` on every object.

## 7. Validator Changes

To accommodate the foundation pass without breaking the regression suite, six existing validators were extended to accept a **5★ `foundation_draft` `final_numbers` dict with `runtime_ready=false`** in place of `null`. The strict-`null` rule is preserved for 6★ everywhere it matters (consolidation, baseline diff). A dedicated new validator `validate_5star_balance_foundation.py` then enforces the actual 5★ foundation constraints (status, ranges, forbidden fields, status resolver, etc.).

## 8. Validator / Suite / Baseline Results

| Run | Result |
|---|---|
| **Suite default** | ✅ **PASS 13/13** (12 standard + RM1.32-A balance foundation; optional RM1.31-C also green) |
| **Suite `--include-baseline-diff`** (against v2) | **FAIL on baseline diff** (5★ SHA changed) — **expected** without `--allow-changed` |
| Baseline diff `--allow-changed <5★>` | ✅ PASS (4 unchanged + 1 allow-changed, invariants clean) |
| `validate_5star_balance_foundation.py` standalone | ✅ PASS (20/20 entries, 100/100 final_numbers foundation_draft, all ranges OK, status references resolve) |

## 9. API Smoke Results — 11/11

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | 200 ✅ |
| `GET /api/heroes` | 200 (count=100) | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 (now exposes `final_numbers`) | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 | 200 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | 404 | 404 ✅ |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | 404 ✅ |
| `GET /api/divine-weapons/catalogs/summary` | 200 | 200 ✅ |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | 200 ✅ |

`by-hero/greek_atalanta` body confirms the new `final_numbers` is visible at every slot. The `by-hero/greek_athena` (6★) confirms `final_numbers` is **still null** for every slot.

## 10. UI Safety Audit

| File | non-GET fetch | runtime-verb Pressables |
|---|---|---|
| `frontend/app/hero-skill-kits-catalog.tsx` | NONE ✅ | NONE ✅ |
| `frontend/app/divine-weapons-catalog.tsx` | NONE ✅ | NONE ✅ |

## 11. `/api/heroes` Safety

| Check | Result |
|---|---|
| Total heroes count | **100** ✅ (unchanged) |
| `greek_borea` visible | ❌ NOT VISIBLE ✅ |
| Legacy `borea` visible | ❌ NOT VISIBLE ✅ |
| `primordial_gaia` visible | ❌ NOT VISIBLE ✅ |

## 12. Borea Safety

- `greek_borea` stays catalog-only / launch_extra_premium / `divine_weapon_id=borea_wings_of_the_north_wind`.
- Legacy `borea` forbidden in CLI (exit 3) and absent from API.
- `marchio_boreale` Borea-only (6 occurrences, 0 leak) — **unchanged**.
- This task did NOT touch the 6★ catalog. Borea remains pending/catalog-only.

## 13. Runtime / DB / Gacha / Roster / Catalog Safety

ZERO modifications to:
- 6★ catalog (`hero_skill_kits_6star_borea_v1.json` SHA256 `4172da0d…`)
- Divine Weapon catalog (`divine_weapons_catalog_v1.json` SHA256 `e3ed42f5…`)
- Status catalog
- `battle_engine.py`, `combat.tsx`, HP bar / status / VFX / Divine Weapon runtime
- gacha / summon / roster / visibility logic
- MongoDB / migrations / seed
- Character Bible / assets
- API routes / loaders / UI files
- `divine_weapon_id`, `release_group`, `hero_id`, `skill_id`, `slot`, skill names / effects / descriptions
- top-level `runtime_attached`, `battle_runtime_attached`, `balance_values_finalized`, `do_not_treat_as_live_kit` (all kept at the safe values)

## 14. Changed File SHA (Before / After)

| File | SHA256 prefix BEFORE | SHA256 prefix AFTER |
|---|---|---|
| `hero_skill_kits_5star_full_v1.json` | `fc87088e…` (post-RM1.31-F) | **`330b337e…`** (post-RM1.32-A) |
| `hero_skill_kits_6star_borea_v1.json` | `4172da0d…` | `4172da0d…` (unchanged) |
| `divine_weapons_catalog_v1.json` | `e3ed42f5…` | `e3ed42f5…` (unchanged) |
| `hero_skill_kit_catalog_baseline_rm132preb2_v2.json` | (baseline v2 anchor) | unchanged — **NOT regenerated** as instructed |

## 15. Warnings / Discrepancies

**None blocking.**

Informational:
1. The 5★ SHA256 legitimately changed. The suite `--include-baseline-diff` correctly reports the mismatch unless `--allow-changed <5★>` is passed. This is the intended behavior until baseline v3 is approved (follow-up).
2. The CLI `summary` 5★ section now shows `runtime_attached=False`, `battle_runtime_attached=False`. The CLI authoring `--commit` path STILL rejects `final_numbers` (FROZEN, exit 7). Future authoring updates to balance numbers must go through a separate, scoped task.
3. The balance values are deliberately conservative and uniform per role. Hero-specific tuning is out of scope and should be done in a dedicated future pass (RM1.32-B or similar).

## 16. Recommendation — Final Status

✅ **ACCEPT — RM1.32-A PASS.**

- All ~40 acceptance criteria of the prompt are met.
- 5★ foundation balance numbers in place across 100/100 slots, conservatively bounded.
- Runtime stays disabled in every safety dimension.
- 6★/Divine Weapon catalogs untouched (SHA256 verified).
- `/api/heroes` count remains 100, Borea hidden.
- Regression suite green (13/13 default).

## 17. Suggested Next Tasks (prioritized)

| Priority | ID | Task | Safety |
|---|---|---|---|
| 🟢 P0 | **RM1.32-A-POST (opt)** | Regenerate baseline **v3** anchored on post-RM1.32-A state with `approved_changes_since_v2` documenting the foundation balance pass. | HIGHEST |
| 🟢 P0 | **RM1.32-A-REVIEW (opt)** | Design review of the conservative numbers (per-hero tuning) before unlocking `runtime_ready`. | HIGHEST |
| 🟢 P0 | **RM1.31-F-B (opt)** | Negative-rollback drill: force a validator-failing edit on a `/tmp` catalog clone to exercise STEP 4/4 auto-rollback end-to-end. | HIGHEST |
| 🟡 P1 | **RM1.32-B** | 6★ Balance Pass Foundation (same shape, 6 slots × 13 heroes = 78 final_numbers, still `foundation_draft`, still no runtime). | MEDIUM |
| 🟠 P2 | **RM1.33-A** | Runtime Adapter Skeleton — `SKILL_KIT_RUNTIME_ENABLED=false`, battle_engine read-only adapter scaffold. Full QA gate. Borea activation MUST remain isolated. | LOW |

Borea activation remains an isolated, separate task. NOT to be bundled with any balance pass.
