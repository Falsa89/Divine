# RM1.34-C — Boss Enrage / Phase Transition Policy Table (Design-Only)

**Task ID:** RM1.34-C
**Status:** ✅ COMPLETE (design-only / inert)
**Baseline anchor:** `hero_skill_kit_catalog_baseline_rm132b_v4`
**Runtime attached:** `false`
**DB / Catalog writes:** none
**Borea visibility change:** none

---

## 1. Purpose

Supplemental **design-only** policy table that defines:

- HP-threshold phase transitions per boss family
- Turn/time-based enrage triggers and caps
- Anti-loop protections (revive/heal/shield/control/DoT)
- Marchio Boreale behavior across phases (owner-only, never team-wide)
- Domain behavior across phase transitions
- Divine Weapon synergy constraints during enrage (descriptive only)
- VFX presentation notes (no runtime)

It complements RM1.34 (hard immunities) and RM1.34-B (element/faction modifier layer). No live formula reads this table; battle runtime is untouched.

---

## 2. Files

### Created
- `/app/data/design/boss_systems/boss_enrage_phase_policy_table_v1.json` (~38 KB)
- `/app/backend/scripts/validate_boss_enrage_phase_policy_table.py`
- `/app/docs/divine/52_BOSS_ENRAGE_PHASE_POLICY_RM134C.md` (this file)

### Modified
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — added optional RM1.34-C entry (no required checks weakened)

### Not modified (invariant)
- `boss_family_resistance_table_v1.json` (RM1.34)
- `boss_family_element_faction_matrix_v1.json` (RM1.34-B)
- 5★ / 6★ / Divine Weapon / Status catalogs
- Baseline v4
- Runtime adapter + debug endpoints (still OFF/inert)
- `battle_engine.py`, `battle_core.py`, `combat.tsx`, HP bar runtime
- UI catalog screens
- DB / migrations / seed / gacha / roster
- Character Bible / assets

---

## 3. Phase / Enrage Table Summary

| Family | Phases | HP Thresholds | Enrage | Dmg Cap | Spd Cap | Status Cap |
|---|---|---|---|---|---|---|
| `story_boss` | 2 | [60] | mild @HP20 | 1.15 | 1.10 | 1.05 |
| `normal_boss` | 2 | [60] | @HP30 / turn 8 | 1.18 | 1.15 | 1.05 |
| `elite_boss` | 3 | [70, 35] | @HP35 / turn 8 | 1.25 | 1.20 | 1.10 |
| `event_boss` | 3 | [65, 30] | @HP30 / turn 10 | 1.25 | 1.15 | 1.10 |
| `raid_boss` | 3 | [66, 33] | @HP25 / 12-turn soft | 1.35 | 1.20 | 1.10 |
| `guild_boss` | 3 | [70, 40] | @HP20 / 14-turn soft | 1.35 | 1.20 | 1.10 |
| `world_boss` | 4 | [80, 50, 20] | @HP20 / 15-turn soft | 1.45 | 1.25 | 1.15 |
| `training_dummy` | 1 | – | disabled | 1.00 | 1.00 | 1.00 |
| `pvp_dummy` | 1 | – | disabled | 1.00 | 1.00 | 1.00 |

All caps respect prompt ceilings (story/normal ≤ 1.20, elite/event ≤ 1.30, raid/guild ≤ 1.40, world ≤ 1.50, dummies ≤ 1.05/1.00).

---

## 4. Family Policy Highlights

- **`story_boss`** — 2 phases, single HP-only mild enrage. Anti-loop generous (3 control chain, 5 DoT stacks). Marchio stacks [3, 4].
- **`normal_boss`** — 2 phases, hp_threshold + turn_count enrage triggers, no stacking enrage.
- **`elite_boss`** — 3 phases, capped moderate enrage at HP35, healing cap tightened to 0.95.
- **`event_boss`** — 3 phases, configurable event profile, design-only enrage.
- **`raid_boss`** — 3 phases [66, 33], stackable enrage max 2 stacks, healing cap 0.90, hard_control_chain ≤ 2.
- **`guild_boss`** — raid-like 3 phases [70, 40], soft 14-turn timer, identical anti-loop tightness as raid.
- **`world_boss`** — 4 phases [80, 50, 20], escalating enrage stackable up to 3 (capped < 1.50), strictest healing cap (0.85), hard_control_chain ≤ 2.
- **`training_dummy`** — 1 phase, **enrage disabled**, all multipliers strictly 1.00, anti-loop neutral (effectively unrestricted).
- **`pvp_dummy`** — 1 phase, **enrage disabled** (no boss enrage in PvP), `hard_control_chain_limit = 2`, status cap = 1.00.

---

## 5. Anti-Loop Policy Highlights

Across families, anti-loop caps tighten with boss difficulty:

| Cap | story/normal | elite/event | raid/guild | world | training | pvp |
|---|---|---|---|---|---|---|
| revive per unit | 1 | 1 | 1 | 1 | 99 | 1 |
| revive per team | 2 | 2 | 1 | 1 | 99 | 1 |
| shield refresh | 3 | 3 | 2 | 2 | 99 | 2 |
| heal cap | 1.00 | 0.95 | 0.90 | 0.85 | 1.00 | 1.00 |
| heal floor | 0.50 | 0.45 | 0.40 | 0.40 | 1.00 | 0.50 |
| hard control chain | 3 | 3 | 2 | 2 | 99 | 2 |
| DoT stack | 5 | 5 | 4 | 4 | 99 | 4 |

These caps are **descriptive only**: they describe future runtime intent without altering the live engine.

---

## 6. Marchio Boreale Phase Policy

Per family (uniform):
- `owner_hero_id = "greek_borea"` — sole owner across all 9 families
- `team_wide_amp_allowed = false`
- `no_activation = true`, `design_only = true`, `runtime_attached = false`, `runtime_ready = false`
- `phase_transition_behavior = "preserve"` (stacks persist across phase boundary)
- `boss_enrage_interaction = "capped_no_amp"` — boss enrage cannot amplify Marchio team-wide
- `max_stacks_by_phase` array length always equals `phase_count`, with each entry ∈ [0, 4]
  - story / normal: [3, 4]
  - elite / event / guild / raid: [3, 3, 4]
  - world: [3, 3, 4, 4]
  - training: [4]; pvp: [3]

Borea remains hidden/catalog-only — no `/api/heroes` exposure, no Marchio leak to other heroes (cross-checked by `validate_status_resolver_contract.py` → `marchio_boreale total (Borea only): 6`).

---

## 7. Domain & Divine Weapon Phase Policy

`domain_phase_policy`:
- `one_domain_active_per_side = true`
- `strongest_wins = true`
- `no_same_turn_refresh = true`
- `max_duration_turns = 3`
- `phase_transition_domain_behavior = "persist_with_clamp"`
- `design_only = true`, `runtime_attached = false`, `runtime_ready = false`

`divine_weapon_phase_policy`:
- `design_only = true`, `runtime_attached = false`, `runtime_ready = false`
- `live_numeric_modifier_applied = false`
- `per_owner_only = true`, `no_teamwide_global_amp = true`
- Future caps reserved: `enrage_modifier_cap_future_pct = 5`, `pvp_modifier_cap_future_pct = 3`

---

## 8. Validator Results

`python3 /app/backend/scripts/validate_boss_enrage_phase_policy_table.py` → **PASS**
- 9/9 families verified
- Phase counts ∈ [1, 4], thresholds strictly descending, threshold count = `phase_count - 1` everywhere
- Trigger types subset of `{hp_threshold, turn_count, soft_timer, failed_mechanic, none}`
- Damage / speed / status caps within family-specific safe ceilings
- Training & PvP dummies confirmed neutral (enrage disabled, caps = 1.00)
- Anti-loop fields all present and within safe bounds
- `pvp_dummy.hard_control_chain_limit = 2` (≤ 2 enforced)
- Marchio owner = `greek_borea`, `team_wide_amp_allowed = false`, `no_activation = true` everywhere
- Marchio `max_stacks_by_phase` length = `phase_count` per family, entries ∈ [0, 4]
- Domain `one_domain_active_per_side`, `strongest_wins`, `no_same_turn_refresh` all `true`, `max_duration_turns` ∈ [1, 5]
- DW phase policy `design_only = true`, `live_numeric_modifier_applied = false`, `per_owner_only = true`
- No `runtime_attached / battle_runtime_attached / used_by_battle_engine / db_write / patch_applied_to_catalogs = true` anywhere
- Source tables (RM1.34, RM1.34-B) and baseline v4 still present, `design_only = true`

---

## 9. Suite / Baseline Results

`run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS 24/24** (0 fail, 0 miss)
- 13 required + 10 optional + 1 baseline diff = 24 checks, all green
- Baseline diff clean under `hero_skill_kit_catalog_baseline_rm132b_v4` **without** `--allow-changed`
- Invariants confirmed: 5★=20, 6★=13, DW=13, Marchio leak in non-Borea = 0, forbidden hero IDs = 0

---

## 10. API Smoke

| Endpoint | Result |
|---|---|
| `GET /api/health` | 200 |
| `GET /api/heroes` | 200 — **count = 100** |
| `GET /api/hero-skill-kits/catalogs/summary` / `5star` / `6star` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_atalanta` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_athena` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 (catalog-only) |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | **404** ✓ |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` / `by-hero/greek_borea` | 200 |
| `GET /api/hero-skill-kits/runtime/debug/coverage` | 200 (`runtime_enabled=false`) |
| `GET /api/hero-skill-kits/runtime/debug/preview?hero_id=greek_borea&slot=ultimate&context=boss` | 200, `safety_envelope`: `runtime_enabled=false`, `applied_to_combat=false`, `db_write=false`, `runtime_attached=false` |

No new API route was created.

---

## 11. UI Safety

- `hero-skill-kits-catalog.tsx`, `divine-weapons-catalog.tsx`: no POST/PUT/PATCH/DELETE; no runtime/phase action buttons; no `SKILL_KIT_RUNTIME_ENABLED` toggle.
- Frontend audit: zero references to `boss_enrage_phase_policy`, `boss_family_element_faction_matrix`, runtime debug endpoints, or adapter tokens.
- No new UI screens / Pressables.
- Expo dev server RUNNING; localhost:3000 → 200.

---

## 12. `/api/heroes` Safety

`count = 100` (invariant respected). `borea` / `greek_borea` / `primordial_gaia` all hidden.

---

## 13. Runtime / DB / Gacha / Roster / Catalog Safety

| Surface | Status |
|---|---|
| `SKILL_KIT_RUNTIME_ENABLED` | remains `false` |
| Runtime adapter | OFF / inert (wiretest: adapter imported by runtime = `False`) |
| Battle runtime / `battle_engine.py` / `battle_core.py` | unmodified |
| Combat UI / `combat.tsx` | unmodified |
| Debug endpoints | unchanged, still inert |
| DB writes | none |
| Catalogs (5★/6★/DW/Status) | unmodified |
| Baseline v4 | unmodified (diff PASS clean) |
| RM1.34 table / RM1.34-B matrix | unmodified |
| Gacha / Roster | unmodified |
| Borea visibility | unchanged (catalog-only, hidden from `/api/heroes`) |
| New API routes / UI buttons | none |

---

## 14. Warnings / Discrepancies

- `audit_balance_foundation_boss_pvp_caps.py` continues to report the pre-existing **2 domain_stack_policy** + **1 dw_future_cap** WARNs (informational, aligned with RM1.32-C delta plan). **No new warnings** introduced by RM1.34-C.
- No other warnings.

---

## 15. Final Recommendation

✅ **RM1.34-C is accepted.** All 25 acceptance criteria from the prompt are met:

1. Table JSON created.
2. Validator created.
3. Checkpoint doc created.
4. No catalog data modified.
5. No baseline modified (diff PASS, no `--allow-changed`).
6. RM1.34 + RM1.34-B tables untouched.
7. No runtime/DB/gacha/roster changes.
8. 9 required boss families present.
9. Phase model present for each family.
10. Enrage policy present for each family.
11. Anti-loop policy present for each family.
12. Marchio owner = Borea only.
13. `team_wide_amp_allowed = false`.
14. Domain policy design-only.
15. DW phase policy design-only.
16. Training/PvP dummy safe (enrage disabled, neutral multipliers).
17. Validator PASS.
18. Suite PASS.
19. Baseline diff PASS under v4.
20. API smoke PASS.
21. UI safety PASS.
22. `/api/heroes` remains 100.
23. Borea hidden.
24. Runtime adapter remains OFF/inert.
25. Docs report final status.

The table is now available as a **future reference layer** for boss phase/enrage runtime design but exerts zero effect on any live system.

---

## 16. Suggested Next Tasks

- **P3 — RM1.32-C2 (opt)**: Trim numeric foundation drafts ahead of baseline v5.
- **P3 — RM1.33-F (opt)**: Second snapshot fixture set v2 covering all 13 6★ ultimates.
- **P2 — RM1.34-D (future, hypothetical)**: Cross-table consistency audit RM1.34 × RM1.34-B × RM1.34-C, design-only, ensuring stack/cap coherence across all three layers.
- **P2 (future)**: Collection Synergies V2 Activation.
- **P2 (future)**: Affinity System Phase 2 — Gift catalog driven by Faction × Element matrix (design-only first).
