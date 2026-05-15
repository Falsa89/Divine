# RM1.34-B — Boss Family × Element/Faction Resistance Matrix (Design-Only)

**Task ID:** RM1.34-B
**Status:** ✅ COMPLETE (design-only / inert)
**Baseline anchor:** `hero_skill_kit_catalog_baseline_rm132b_v4`
**Runtime attached:** `false`
**DB / Catalog writes:** none
**Borea visibility change:** none

---

## 1. Purpose

Supplemental **design-only** matrix that defines future resistance/modifier principles for the 9 boss families along two orthogonal axes: **elements** and **faction groups**.

This matrix is a **modifier layer**, not a hard immunity table. Hard control immunities continue to live exclusively in `boss_family_resistance_table_v1.json` (RM1.34). No live formula reads this matrix.

---

## 2. Files

### Created
- `/app/data/design/boss_systems/boss_family_element_faction_matrix_v1.json` (~67 KB)
- `/app/backend/scripts/validate_boss_element_faction_matrix.py`
- `/app/docs/divine/51_BOSS_ELEMENT_FACTION_MATRIX_RM134B.md` (this file)

### Modified
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — added optional RM1.34-B entry pointing to the new validator. No required checks weakened.

### Not modified (invariant)
- `boss_family_resistance_table_v1.json`
- 5★ / 6★ / Divine Weapon / Status catalogs
- Baseline v4
- Runtime adapter (`skill_kit_runtime_adapter.py`, `skill_kit_cap_policy_adapter.py`)
- Debug endpoints
- `battle_engine.py`, `battle_core.py`, `combat.tsx`
- UI catalog screens
- DB / migrations / seed / gacha / roster
- Character Bible / assets

---

## 3. Matrix Summary

| Axis | Values |
|---|---|
| Boss families | 9 (`story_boss`, `normal_boss`, `elite_boss`, `raid_boss`, `world_boss`, `event_boss`, `guild_boss`, `training_dummy`, `pvp_dummy`) |
| Elements | 7 (`fire`, `water`, `earth`, `wind`, `lightning`, `light`, `darkness`) |
| Faction groups | 13 (`greek`, `norse`, `egyptian`, `japanese_yokai`, `celtic`, `angelic`, `demonic`, `cursed`, `creature_beast`, `primordial`, `arcane`, `tides`, `mesopotamian`) |
| Total flavor rows | 9×7 element rows + 9×13 faction rows = 63 + 117 = **180 modifier cells** |

Safe design ranges:
- `damage_taken_multiplier` ∈ [0.70, 1.30]
- `status_chance_multiplier` ∈ [0.50, 1.20]
- `dot_tick_multiplier` ∈ [0.40, 1.10]
- Combination clamp: `min ≥ 0.50`, `max ≤ 1.50`

---

## 4. Element Policy Highlights

| Family | Element flavor |
|---|---|
| `story_boss`, `normal_boss`, `event_boss` | Effectively neutral (~1.00) across elements; mild status/DoT damping. |
| `elite_boss` | Slight broad resistance (base 0.95), DoT damping moderate. |
| `raid_boss` | Broad mild resistance (base 0.90, +0.03 element band); status chance 0.90; DoT tick 0.60. |
| `guild_boss` | Similar to raid; broad resistance band 0.88–0.90. |
| `world_boss` | Tightest spread (0.85 base ±0.04), strongest status damping (0.85), DoT tick 0.55. No hard counters. |
| `training_dummy` | Neutral 1.00 across all elements (within 0.95–1.05 band). |
| `pvp_dummy` | PvP-safe neutral 1.00 across all elements. |

No element acts as a hard counter — vulnerability swings are bounded inside ±0.30 from baseline 1.0.

---

## 5. Faction Policy Highlights

| Family | Faction flavor |
|---|---|
| `story_boss`, `normal_boss` | Flat baseline (1.00); `cursed_thematic_anchor` tag on cursed faction column for thematic foreshadowing. |
| `elite_boss`, `event_boss` | -0.01 broad resistance band; `angelic_flavor_only` tag where applicable. |
| `raid_boss`, `guild_boss` | -0.02 broad band; status chance 0.90. |
| `world_boss` | -0.03 broad band; status chance 0.85; `primordial_world_boss_neutral_band` tag on primordial column. |
| `training_dummy` | Strictly neutral (1.00 dmg / 1.00 status). |
| `pvp_dummy` | Strictly PvP-safe neutral; combination policy explicitly overrides resistances. |

All `special_rule_tags` arrays are present (possibly empty) per acceptance contract.

---

## 6. Combination Policy

For every family:
- `element_and_faction_stack_mode`: `multiplicative`
- `min_total_damage_taken_multiplier`: `0.55` (≥ 0.50 floor required)
- `max_total_damage_taken_multiplier`: `1.45` (≤ 1.50 ceiling required)
- `boss_family_priority`: `family_base → element_modifier → faction_modifier`
  - The family base policy from `boss_family_resistance_table_v1` is evaluated **first**; element and faction modifiers compose multiplicatively under the min/max clamp.
- `pvp_dummy_override`: `true` only for `pvp_dummy`, `false` elsewhere.
- `training_dummy_neutral`: `true` only for `training_dummy`, `false` elsewhere.

Note: hard immunities (e.g. `taunt_immunity`, `freeze_resist`) are NOT in this matrix; they remain in RM1.34.

---

## 7. Marchio Boreale Policy

Per every family `special_cases.marchio_boreale`:
- `design_only = true`, `runtime_ready = false`
- `owner_hero_id = "greek_borea"` (sole owner)
- `team_wide_amp_allowed = false`
- `applies_only_to_owner_target = true`
- `max_effective_stacks_in_this_family`: 4 (3 only on `pvp_dummy` for PvP safety)
- `freeze_bonus_multiplier_on_boss = 0.50` (descriptive only)
- `damage_bonus_multiplier_on_boss = 0.75` (descriptive only)

Borea remains hidden/pending — no visibility flag, no `/api/heroes` exposure, no Marchio leak into other heroes (validated by `validate_status_resolver_contract.py` → `marchio_boreale total (Borea only): 6`).

---

## 8. Divine Weapon & Domain Policy

`divine_weapon_synergy` (per family):
- `design_only = true`, `runtime_ready = false`
- `live_numeric_modifier_applied = false`
- `per_owner_only = true`, `no_teamwide_global_amp = true`
- Future caps reserved: `numeric_modifier_cap_future_pct = 10`, `pvp_modifier_cap_future_pct = 5`

`domain_effect` (per family):
- `design_only = true`, `runtime_ready = false`
- `one_domain_active_per_side = true`
- `override_policy = "strongest_wins"`
- `max_duration_turns = 3`, `refresh_same_turn_allowed = false`, `cleansable = true`

`primordial_or_world_boss_exception` (only on `world_boss`):
- Broad resistance band, no extreme counter multiplier, floor `0.70`.

---

## 9. Validator Results

`python3 /app/backend/scripts/validate_boss_element_faction_matrix.py` → **PASS**
- 9/9 boss families verified
- 7/7 elements present per family
- 13/13 factions present per family
- All multipliers within safe ranges
- Training/PvP dummies confirmed neutral (0.95–1.05)
- Marchio owner = `greek_borea`, `team_wide_amp_allowed = false` everywhere
- DW synergy + Domain special cases design-only across all families
- No `runtime_attached / battle_runtime_attached / used_by_battle_engine / db_write / patch_applied_to_catalogs = true` anywhere
- Baseline v4 anchor still present and unmodified
- `boss_family_resistance_table_v1` still present, `design_only=true`, `task_origin=RM1.34`

---

## 10. Suite / Baseline Results

`run_hero_skill_kit_validator_suite.py` → **PASS** (22/22, 0 fail, 0 miss)
- 13 required + 9 optional checks all green
- RM1.34-B entry added as optional

`run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS** (23/23)
- Baseline diff under `hero_skill_kit_catalog_baseline_rm132b_v4` clean **without** `--allow-changed`
- Invariants confirmed: 5★=20, 6★=13, DW=13, Marchio leak in non-Borea = 0, forbidden hero IDs = 0

---

## 11. API Smoke

| Endpoint | Result |
|---|---|
| `GET /api/health` | 200 |
| `GET /api/heroes` | 200 — **count = 100** |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_athena` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 (catalog-only) |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | **404** ✓ |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` | 200 |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 (catalog-only) |
| `GET /api/hero-skill-kits/runtime/debug/coverage` | 200 (`runtime_enabled=false`) |
| `GET /api/hero-skill-kits/runtime/debug/preview?hero_id=greek_borea&slot=ultimate&context=boss` | 200, `safety_envelope.runtime_enabled=false`, `applied_to_combat=false`, `db_write=false`, `runtime_attached=false`, `battle_runtime_attached=false` |

No new API route was created. No matrix endpoint exposed.

---

## 12. UI Safety

- `hero-skill-kits-catalog.tsx` and `divine-weapons-catalog.tsx` audited: **no** POST/PUT/PATCH/DELETE, no runtime/matrix action buttons, no `SKILL_KIT_RUNTIME_ENABLED` flag toggle.
- Frontend audit: zero references to `boss_family_element_faction_matrix`, runtime debug endpoints, or adapter tokens.
- No new UI screens / Pressables created.
- Expo dev server: RUNNING; localhost:3000 → 200.

---

## 13. /api/heroes Safety

- `count = 100` (invariant respected).
- `borea` → hidden ✓
- `greek_borea` → hidden ✓
- `primordial_gaia` → hidden ✓

---

## 14. Runtime / DB / Gacha / Roster / Catalog Safety

| Surface | Status |
|---|---|
| `SKILL_KIT_RUNTIME_ENABLED` | remains `false` |
| Runtime adapter | OFF / inert (`audit_skill_kit_runtime_adapter_wiretest.py` → adapter imported by runtime = `False`) |
| Battle runtime / `battle_engine.py` | unmodified |
| Combat UI / `combat.tsx` | unmodified |
| Debug endpoints | unchanged, still inert (`runtime_enabled=false`) |
| DB writes | none |
| Catalog files (5★/6★/DW/Status) | unmodified |
| Baseline v4 | unmodified (diff PASS clean) |
| Boss family resistance table v1 | unmodified |
| Gacha / Roster | unmodified |
| Borea visibility | unchanged (catalog-only, hidden from `/api/heroes`) |
| New API routes / UI buttons | none |

---

## 15. Warnings / Discrepancies

- `audit_balance_foundation_boss_pvp_caps.py` continues to report **2 domain_stack_policy** + **1 dw_future_cap** WARNs (informational, no FAIL). These match the RM1.32-C delta plan — no escalation introduced by RM1.34-B.
- No other warnings.

---

## 16. Final Recommendation

✅ **RM1.34-B is accepted.** All acceptance criteria are met:

1. Matrix JSON created.
2. Validator created (`/app/backend/scripts/validate_boss_element_faction_matrix.py`).
3. Checkpoint doc created.
4. No catalog data modified.
5. No baseline modified (diff PASS, no `--allow-changed` needed).
6. `boss_family_resistance_table_v1` untouched.
7. No runtime/DB/gacha/roster changes.
8. 9 boss families × 7 elements × 13 factions present.
9. Multipliers in safe range.
10. Training & PvP dummies neutral.
11. Combination policy present per family.
12. Marchio owner = Borea only, no team-wide amp.
13. DW & Domain special cases design-only.
14. Validator + Suite + Baseline diff PASS.
15. API smoke PASS.
16. UI safety PASS.
17. `/api/heroes` = 100, Borea hidden.
18. Runtime adapter remains OFF / inert.

The matrix is now available as a **future reference layer** for the boss balancing milestone but exerts zero effect on any live system.

---

## 17. Suggested Next Tasks

- **P2 — RM1.34-C (opt)**: Boss enrage / phase transition policy table (design-only), referencing the boss family table + this matrix as compositional inputs.
- **P3 — RM1.32-C2 (opt)**: Trim numeric foundation drafts ahead of baseline v5.
- **P3 — RM1.33-F (opt)**: Second snapshot fixture set v2 covering all 13 6★ ultimates.
- **P2 (future)**: Collection Synergies V2 Activation.
- **P2 (future)**: Affinity System Phase 2 — Gift catalog driven by Faction × Element matrix (will read this matrix in design-only mode first).
