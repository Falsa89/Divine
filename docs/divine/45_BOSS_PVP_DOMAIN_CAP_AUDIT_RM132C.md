# RM1.32-C — Boss / PvP / Domain Resistance & Cap Audit + Delta Plan

**Task:** RM1.32-C
**Date (UTC):** 2026-05-15
**Mode:** Read-only audit + design-only delta plan. **NO** patch, **NO** runtime, **NO** DB, **NO** catalog edits, **NO** baseline change.

---

## 1. Audit purpose

After RM1.32-B (6★ Balance Pass Foundation, baseline v4 anchored), this task inspects the foundation_draft values in 5★ (100 slots) and 6★ (78 slots) BEFORE the Runtime Adapter Skeleton (RM1.33-A) is implemented. It identifies:

- PvP cap candidates (damage / shield / heal / status chance / control duration)
- Boss resistance requirements (hard control, DoT scaling, heal block/reduction)
- Heal / shield / revive anti-loop risks
- Marchio Boreale boundary safety (Borea-only)
- Domain / effect stacking policy (currently no domain tags present)
- Divine Weapon synergy placeholder future constraints

It produces a **design-only** delta-plan JSON to seed a hypothetical future v5 baseline IF (and only if) the user approves an optional RM1.32-C2 numeric patch later.

## 2. Files created (3)

| Path | Purpose |
|---|---|
| `/app/backend/scripts/audit_balance_foundation_boss_pvp_caps.py` | Read-only audit script |
| `/app/data/design/hero_skill_kits/hero_skill_kits_balance_cap_delta_plan_v1.json` | Design-only delta plan |
| `/app/docs/divine/45_BOSS_PVP_DOMAIN_CAP_AUDIT_RM132C.md` | This checkpoint |

## 3. Files modified

**None.** No catalogs, validators, suite, runtime, API, UI, or baselines were modified.

## 4. WARN findings by category

Total: **86** WARNs (informational, non-fatal). Audit exits PASS.

| Section | Code | Count |
|---|---|---|
| `2.burst` | `boss_mitigation_candidate` (ultimate dmg ≥ 600) | 4 |
| `2.burst` | `pvp_cap_aoe_ultimate` (AoE ult ≥ 380/target) | 5 |
| `2.burst` | `pvp_cap_single_target_burst` (ST burst ≥ 600) | 4 |
| `3.control_status` | `boss_resistance_hard_control` (hard CC present) | 10 |
| `3.control_status` | `pvp_hard_control_duration_cap` (dur ≥ 3 hard CC) | 2 |
| `3.control_status` | `pvp_status_chance_cap` (chance ≥ 90) | 19 |
| `3.control_status` | `soft_control_review` | 26 |
| `4.heal_shield_revive` | `pvp_heal_cap` (heal ≥ 480) | 2 |
| `4.heal_shield_revive` | `pvp_shield_cap` (shield ≥ 460) | 3 |
| `4.heal_shield_revive` | `revive_loop_anti` (revive/death_protection carriers) | 4 |
| `5.marchio_boreale` | `marchio_pvp_cap` (Borea 4 slots) | 4 |
| `6.domain` | `domain_stack_policy` | 2 |
| `7.dw_synergy` | `dw_future_cap` (future runtime cap reco) | 1 |

All hard invariants are preserved (no FAIL).

## 5. Delta plan summary

`plan_id = hero_skill_kits_balance_cap_delta_plan_v1`
`task_origin = RM1.32-C`, `scope = 5star_and_6star_foundation_balance`
`patch_applied = false`, `runtime_attached = false`, `balance_values_finalized = false`

Safety flags: `no_patch=true`, `no_runtime=true`, `no_db=true`, `no_borea_activation=true`, `design_only=true`.

The plan declares: PvP cap principles, boss resistance policy, domain stacking policy, Marchio Boreale boundaries, DW synergy future constraints, heal/shield/revive anti-loop rules, candidate followups (RM1.32-C2 optional, RM1.33-A prerequisites, RM1.34 boss table).

## 6. PvP cap recommendations

- **Damage cap**: PvP ST ultimate/skill_2 ≤ 600; PvP AoE ultimate ≤ 380/target; one-shot prevention (≥10% max_hp survives any single non-true-damage hit).
- **Shield cap**: max 2 concurrent shields/ally; effective `shield_multiplier_pct` ≤ 460 in PvP; oldest decays first.
- **Heal cap**: PvP heal effectiveness ≈ 75% of PvE (−25%); raid bosses heal effectiveness ≈ 50%; `healing_block` reduces heal to 0 while active.
- **Hard control duration cap**: freeze/stun/silence ≤ 2 turns in PvP (3 in PvE); taunt ≤ 2 in PvP.
- **Status chance cap**: PvP cap at 85% for freeze/stun/silence/taunt/burn/poison/frostbite/shock/curse, even if foundation says ≥90%.

**Enforcement layer**: PvP caps are runtime adapter responsibility (RM1.33-A); they must NEVER mutate foundation_draft numbers.

## 7. Boss resistance recommendations

- **Hard control resistance**: diminishing returns — 1st app full duration, 2nd within N turns 50% duration, 3rd immune (immunity window 2 turns).
- **Mark / Marchio**: stack cap 5 PvE / 3 PvP for `mark`; bosses cap effective Marchio Boreale stacks at `max_stacks_pve − 1 = 4`.
- **DoT scaling**: boss DoT multiplier capped at 0.5× of standard tick; no crit on DoT vs bosses; max 3 distinct DoTs per boss target (PvE) / 2 (PvP).
- **Healing reduction/block**: `healing_block` max duration 2 turns; `healing_reduction` cap at −60%/stack, never below 20% baseline.

## 8. Marchio Boreale recommendations

- **Owner**: `greek_borea` only (audit confirmed 4 Borea slots carry stack values, 0 leak on the other 12 entries).
- **Stacks**: PvP=3, PvE=5; bosses effective cap = `max_stacks_pve − 1` = 4.
- **Team-wide amp**: **forbidden** — per-target personal status; no transfer to other heroes.
- **Cleanse**: standard cleanse removes all stacks at once; no partial cleanse.
- **Immunity**: prevents new stacks; existing stacks decay normally.
- **Decay**: 1 stack decays at end of marked unit turn unless re-applied; resets on cleanse.
- **Activation**: `borea_activation=false`; `runtime_ready=false` (design-only).

## 9. Domain / DW recommendations

### Domain
- Audit confirms **0 domain-like tags or status IDs** present in 5★/6★ (foundation pass intentionally domain-free).
- Reserved policy for future domain-introducing tasks:
  - Stacking: `one_domain_active_per_battle_side` (max 1 ally + 1 enemy).
  - Override: strongest_wins; ties → FIFO; cleansable.
  - Duration: max 3 turns; no refresh in same turn.

### Divine Weapon synergy
- Current state: **78/78** placeholders `design_only=true`, `runtime_ready=false`, `numeric_modifier_pct=null` ✓
- Future runtime caps:
  - max numeric modifier ≤ **+10%** global
  - additive only at first runtime pass (no multiplicative with other buffs)
  - per-owner-hero only (no team-wide amp)
  - PvP yields ≤ **+5%**
- No live hooks until RM1.33-A feature flag `SKILL_KIT_RUNTIME_ENABLED=false` is explicitly flipped.

## 10. Validator / suite / baseline results

| Validator | Result |
|---|---|
| `audit_balance_foundation_boss_pvp_caps.py` (NEW) | **PASS** (86 WARN, 0 FAIL) |
| `validate_5star_balance_foundation.py` | **PASS** |
| `validate_6star_balance_foundation.py` | **PASS** |
| `validate_hero_skill_kit_catalog_baseline_diff.py` (auto → v4) | **PASS** |
| `validate_status_resolver_contract.py` | **PASS** |
| `audit_hero_skill_kit_catalog_consolidation.py` | **PASS** |
| `validate_divine_weapon_catalog.py` | **PASS** |
| `audit_divine_weapon_crosslinks.py` | **PASS** |
| `run_hero_skill_kit_validator_suite.py` (default) | **PASS 14/14** |
| `run_hero_skill_kit_validator_suite.py --include-baseline-diff` | **PASS 15/15** (no `--allow-changed`, anchored on v4) |

**Baseline v4 remains the current default anchor** — no new baseline created by this task.

## 11. API smoke

| Endpoint | Expected | Actual |
|---|---|---|
| `GET /api/health` | 200 | **200** |
| `GET /api/heroes` count | 100 | **100** ✓ |
| Borea / legacy `borea` / `primordial_gaia` in `/api/heroes` | hidden | **hidden** ✓ |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/5star` | 200 | **200** |
| `GET /api/hero-skill-kits/catalogs/6star` | 200 | **200** |
| `GET …/by-hero/greek_atalanta` | 200 | **200** |
| `GET …/by-hero/greek_athena` | 200 | **200** |
| `GET …/by-hero/greek_borea` (catalog-only) | 200 | **200** |
| `GET …/by-hero/borea` | 404 | **404** ✓ |
| `GET …/by-hero/primordial_gaia` | 404 | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` | 200 | **200** |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | **200** |

## 12. UI safety audit

| File | axios/fetch mutations | `method:POST/PUT/PATCH/DELETE` | Pressable+runtime kw |
|---|---|---|---|
| `/app/frontend/app/hero-skill-kits-catalog.tsx` | 0 | 0 | 0 |
| `/app/frontend/app/divine-weapons-catalog.tsx` | 0 | 0 | 0 |

UI files **not modified**. SAFE.

## 13. `/api/heroes` safety

Count = **100** ✓. Borea, legacy `borea`, `primordial_gaia` all hidden ✓.

## 14. Runtime / DB / gacha / roster / catalog safety

- ❌ No `battle_engine.py`, `combat.tsx`, HP bar runtime, API routes/loaders, UI files modified.
- ❌ No DB / migration / seed writes.
- ❌ No gacha / roster / Character Bible / asset changes.
- ❌ No status runtime / VFX runtime / Divine Weapon runtime touched.
- ❌ No catalog data (5★, 6★, DW, status, baselines) modified.
- ❌ No `final_numbers` / runtime flags / `divine_weapon_id` / `release_group` / hero_id / skill_id / slot / names / descriptions / tags / status_ids changed.
- ❌ Borea visibility unchanged (catalog-only, hidden).

## 15. Recommendation — final status

**ACCEPTED.** All 20 acceptance criteria of RM1.32-C satisfied:

1–3 Audit script, delta plan JSON, checkpoint docs created ✅
4–5 No catalog/runtime/DB/gacha/roster change ✅
6 Audit PASS with WARNs allowed ✅
7–10 5★ / 6★ / suite / baseline diff under v4 all PASS ✅
11–12 API smoke + UI safety PASS ✅
13–16 `/api/heroes=100`, Borea/legacy/Gaia hidden ✅
17–18 Marchio Borea-only, DW placeholders design-only ✅
19 No baseline change ✅
20 RM1.33-A runtime adapter prerequisites enumerated in plan ✅

## 16. Suggested next task — prioritized

1. 🟡 **P2 RM1.33-A — Runtime Adapter Skeleton** (recommended). Implements feature flag `SKILL_KIT_RUNTIME_ENABLED=false`, reads foundation_draft values, applies PvP/Boss caps from this plan at runtime layer, never mutates catalogs. Highest forward value.
2. 🟢 **P3 RM1.32-C2 (optional, only if user requests)** — Apply the lowest-risk numeric tweaks to foundation_draft (e.g. trim `status_chance_pct` ≥ 90 down to 85 inside the foundation_draft) → would produce baseline v5. Low risk, fully reversible.
3. 🟢 **P3 RM1.34 boss table design** — Author boss family resistance/immunity table referencing this delta plan as design contract. Pure design task.

---

### Appendix — current baseline chain (unchanged)

```
v1: hero_skill_kit_catalog_baseline_rm132pre_v1
v2: hero_skill_kit_catalog_baseline_rm132preb2_v2
v3: hero_skill_kit_catalog_baseline_rm132apost_v3
v4: hero_skill_kit_catalog_baseline_rm132b_v4   ← CURRENT (untouched by RM1.32-C)
```
