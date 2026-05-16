# RM1.32-C2 — Numeric Trim Foundation Drafts + Baseline v5

**Task ID:** RM1.32-C2
**Status:** ✅ COMPLETE (design-data-only mutation; numeric trim on 6★ foundation_draft)
**Baseline:** `hero_skill_kit_catalog_baseline_rm132c2_v5` (now latest); v4 preserved on disk
**Runtime attached:** `false`
**DB / Gacha / Roster writes:** none
**Borea visibility:** unchanged (catalog-only, hidden)

---

## 1. Purpose

Conservative, idempotent, design-data-only numeric trim of `foundation_draft.final_numbers` values on the 6★ catalog where RM1.32-C had emitted WARNs. Strictly limited to numeric values clearly above cap; no skill identity, names, descriptions, slots, status/effect tags, hero_id, divine_weapon_id or release_group are changed. After the trim, a new anchor baseline `v5` is published.

---

## 2. Files

### Created
- `/app/backend/scripts/apply_foundation_numeric_trim_rm132c2.py` — idempotent patch script
- `/app/backend/scripts/validate_foundation_numeric_trim_rm132c2.py` — dedicated validator
- `/app/data/design/hero_skill_kits/hero_skill_kit_numeric_trim_rm132c2_result_v1.json` — machine-readable trim result
- `/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132c2_v5.json` — new baseline v5
- `/app/docs/divine/56_NUMERIC_TRIM_FOUNDATION_DRAFTS_RM132C2.md` — this checkpoint

### Modified (catalog mutation)
- `/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json`
  - 19 slots received numeric trims on `final_numbers` (26 trim records total — see §5)
  - Top-level: `numeric_trim_pass_id = "RM1.32-C2"`, `last_numeric_trim_write`, `balance_values_finalized=false`, `do_not_treat_as_live_kit=true`, `runtime_attached=false`, `battle_runtime_attached=false`
  - Per-slot: `trim_metadata.history` entries added only when a value changed

### Modified (suite runner)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — added **RM1.32-C2 as REQUIRED** (patch applied)

### Operational maintenance (not part of catalog change)
- `/usr/local/bin/start-expo.sh` recreated after recurring disappearance, now using `CI=1` per Expo CLI guidance (does not disable Metro HMR; eliminates `--non-interactive is not supported` exit cycle)

### Not modified
- 5★ catalog `hero_skill_kits_5star_full_v1.json` (no values were out-of-cap → SHA unchanged)
- Divine Weapon catalog
- Status catalog
- Boss policy tables (RM1.34, RM1.34-B, RM1.34-C)
- Baseline v4 (preserved on disk as historical anchor)
- `battle_engine.py`, `battle_core.py`, `combat.tsx`, HP bar runtime
- UI catalog screens
- DB / migrations / seed / gacha / roster
- Character Bible / assets
- All API routes / Pressables / runtime flags

---

## 3. Backup Manifest

```
/app/backups/hero_skill_kits/backup_20260516T213239Z/MANIFEST.json
```

Files captured pre-patch (sha256 prefixes):
- `hero_skill_kits_5star_full_v1.json`: `330b337e629e03ab…` (unchanged post-trim)
- `hero_skill_kits_6star_borea_v1.json`: `abf9b2a2f02b5912…` → post-trim `9cb1fc49ca19aaea…`
- `divine_weapons_catalog_v1.json`: `e3ed42f54e85bf48…` (unchanged)
- `hero_skill_kit_schema_v1.json`: `f5b30b6d6d323c50…` (unchanged)
- `hero_skill_kit_catalog_baseline_rm132pre_v1.json`: `f75d20aab42e023a…` (unchanged)

---

## 4. Trim Summary

| Metric | Value |
|---|---|
| Files scanned | 2 (5★, 6★) |
| Values scanned | 178 (100 5★ + 78 6★) |
| Slots trimmed | **19** (all on 6★) |
| Trim records | **26** |
| Files touched | 1 (`hero_skill_kits_6star_borea_v1.json`) |
| Idempotent | ✅ rerun confirmed: 0 new mutations, SHA unchanged |

**By category:**
- `status_chance_pct`: 19 records (95→85 on ultimate × 11, 90→85 on skill_2 × 6, plus 2 more on ultimate at 95→85 → all heroes with high-chance ultimate normalized)
- `damage_multiplier_pct` AoE ultimate (`tgt≥2`, `>380`): 3 records (raijin 440→380, tiamat 400→380, greek_borea 400→380)
- `damage_multiplier_pct` ST burst (`tgt=1`, `>600`): 4 records (artemis 680→600, susanoo 720→600, sekhmet 700→600, morrigan 700→600)
- `marchio_boreale_stack_values`: 0 records (already at 3/5 — boss=None, no mutation needed)

---

## 5. Values Trimmed Table

| # | Catalog | Hero | Slot | Field | Before | After | Reason |
|---|---|---|---|---|---|---|---|
| 1 | 6★ | greek_athena | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 2 | 6★ | greek_artemis | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 3 | 6★ | greek_artemis | ultimate | damage_multiplier_pct | 680 | **600** | pvp_cap_single_target_burst |
| 4 | 6★ | greek_gaia | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 5 | 6★ | primordial_nyx | skill_2 | status_chance_pct | 90 | **85** | pvp_status_chance_cap |
| 6 | 6★ | primordial_nyx | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 7 | 6★ | japanese_raijin | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 8 | 6★ | japanese_raijin | ultimate | damage_multiplier_pct | 440 | **380** | pvp_cap_aoe_ultimate |
| 9 | 6★ | japanese_susanoo | skill_2 | status_chance_pct | 90 | **85** | pvp_status_chance_cap |
| 10 | 6★ | japanese_susanoo | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 11 | 6★ | japanese_susanoo | ultimate | damage_multiplier_pct | 720 | **600** | pvp_cap_single_target_burst |
| 12 | 6★ | japanese_amaterasu | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 13 | 6★ | egyptian_sekhmet | skill_2 | status_chance_pct | 90 | **85** | pvp_status_chance_cap |
| 14 | 6★ | egyptian_sekhmet | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 15 | 6★ | egyptian_sekhmet | ultimate | damage_multiplier_pct | 700 | **600** | pvp_cap_single_target_burst |
| 16 | 6★ | mesopotamian_tiamat | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 17 | 6★ | mesopotamian_tiamat | ultimate | damage_multiplier_pct | 400 | **380** | pvp_cap_aoe_ultimate |
| 18 | 6★ | egyptian_isis | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 19 | 6★ | celtic_morrigan | skill_2 | status_chance_pct | 90 | **85** | pvp_status_chance_cap |
| 20 | 6★ | celtic_morrigan | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 21 | 6★ | celtic_morrigan | ultimate | damage_multiplier_pct | 700 | **600** | pvp_cap_single_target_burst |
| 22 | 6★ | cursed_pestilence_horseman | skill_2 | status_chance_pct | 90 | **85** | pvp_status_chance_cap |
| 23 | 6★ | cursed_pestilence_horseman | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 24 | 6★ | greek_borea | skill_2 | status_chance_pct | 90 | **85** | pvp_status_chance_cap |
| 25 | 6★ | greek_borea | ultimate | status_chance_pct | 95 | **85** | pvp_status_chance_cap |
| 26 | 6★ | greek_borea | ultimate | damage_multiplier_pct | 400 | **380** | pvp_cap_aoe_ultimate |

5★ catalog: **0 trims** (no values were out-of-cap). 5★ SHA `330b337e629e03ab…` unchanged.

---

## 6. Remaining WARNs / Cap Audit Delta

`audit_balance_foundation_boss_pvp_caps.py` WARN total: **86 → 67 (−19)**.

| WARN category | Before | After | Delta |
|---|---|---|---|
| `pvp_status_chance_cap` | 19 | **0** | **−19** ✅ |
| `pvp_cap_aoe_ultimate` | 5 | 5 | 0 (informational; audit threshold `>= 380` still triggers at-cap values 380) |
| `pvp_cap_single_target_burst` | 4 | 4 | 0 (informational; threshold `>= 600` triggers at-cap values 600) |
| `boss_mitigation_candidate` | 4 | 4 | 0 (PvE-side, intentionally not trimmed) |
| `boss_resistance_hard_control` | 10 | 10 | 0 (design tag review, not a numeric trim target) |
| `pvp_hard_control_duration_cap` | 2 | 2 | 0 (no explicit PvP flag on the field; conservative skip) |
| `soft_control_review` | 26 | 26 | 0 (design review tag) |
| `pvp_heal_cap` | 2 | 2 | 0 (heal trim explicitly skipped per prompt rule) |
| `pvp_shield_cap` | 3 | 3 | 0 (shield trim only on explicit PvP fields per prompt) |
| `revive_loop_anti` | 4 | 4 | 0 (anti-loop policy is RM1.34-C design, not numeric here) |
| `marchio_pvp_cap` | 4 | 4 | 0 (already aligned to 3/5; informational reminder) |
| `domain_stack_policy` | 2 | 2 | 0 (RM1.32-C delta plan, pre-existing) |
| `dw_future_cap` | 1 | 1 | 0 (RM1.32-C delta plan, pre-existing) |

The remaining WARNs are **all informational and pre-existing** (audit thresholds are `>=`, so at-cap values still surface). They are aligned with the RM1.32-C delta plan and contain no FAIL.

---

## 7. Baseline v5 Summary

`/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132c2_v5.json`
- `baseline_id = "hero_skill_kit_catalog_baseline_rm132c2_v5"`
- `task_origin = "RM1.32-C2"`
- `supersedes = "hero_skill_kit_catalog_baseline_rm132b_v4"`
- `tracked_files` (5 entries, full path keys with `{sha256, size_bytes, label}`):
  - 5★ catalog: `330b337e629e03ab…` (unchanged)
  - 6★ catalog: `9cb1fc49ca19aaea…` (post-trim)
  - Divine Weapon catalog: `e3ed42f54e85bf48…` (unchanged)
  - Schema: `f5b30b6d6d323c50…` (unchanged)
  - Baseline v1 anchor: `f75d20aab42e023a…` (unchanged)
- Invariants block: `/api/heroes=100`, Borea hidden, all runtime flags false, 5★ 100/100, 6★ 78/78, Marchio Borea-only, 6★ ultimate=13, forbidden hero ids visible=0, boss policy tables unchanged, baseline v4 preserved
- `generated_at_utc` strictly later than v4 → auto-detector picks v5 (confirmed by `validate_hero_skill_kit_catalog_baseline_diff.py`)

v4 file remains on disk as historical anchor; the baseline-diff validator now auto-targets v5.

---

## 8. Validator Results

- `validate_foundation_numeric_trim_rm132c2.py` → **PASS** (counts, caps, marchio, dw_synergy inert, result JSON, baseline v5, baseline v4 preserved)
- `validate_5star_balance_foundation.py` → PASS
- `validate_6star_balance_foundation.py` → PASS (post-trim values within cap)
- `audit_balance_foundation_boss_pvp_caps.py` → PASS (67 informational WARNs, down from 86)
- `validate_runtime_debug_5star_snapshot_rejections.py` → PASS (100 valid + 20 invalid)
- `validate_runtime_debug_6star_ultimate_snapshots.py` → PASS (13/13)
- `audit_boss_policy_cross_table_consistency.py` → PASS (20/20)
- `validate_boss_enrage_phase_policy_table.py` / `validate_boss_element_faction_matrix.py` / `validate_boss_family_resistance_table.py` → PASS
- `validate_status_resolver_contract.py` → PASS (`marchio_boreale total Borea-only: 6`)
- `validate_divine_weapon_catalog.py` / `audit_divine_weapon_crosslinks.py` → PASS
- `validate_hero_skill_kit_catalog_baseline_diff.py` → PASS (auto-detects v5, all 5 tracked files unchanged vs v5)

Idempotency rerun of `apply_foundation_numeric_trim_rm132c2.py` → `NO_PATCH_NEEDED`, 6★ SHA unchanged.

---

## 9. Suite / Baseline Results

`run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS 28/28** (14 required + 13 optional + 1 baseline diff). 0 fail, 0 miss. Baseline diff under **v5** clean, no `--allow-changed` used.

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
| `GET /api/hero-skill-kits/runtime/debug/coverage` | 200 (runtime_enabled=false) |
| `GET /api/hero-skill-kits/runtime/debug/preview?hero_id=greek_borea&slot=ultimate&context=boss` | 200 |
| `GET /api/hero-skill-kits/runtime/debug/preview?hero_id=greek_atalanta&slot=skill_2&context=pvp` | 200 |
| `GET /api/hero-skill-kits/runtime/debug/preview?hero_id=greek_atalanta&slot=ultimate&context=pvp` | **404** ✓ |

---

## 11. UI Safety

- `hero-skill-kits-catalog.tsx`, `divine-weapons-catalog.tsx`: no POST/PUT/PATCH/DELETE; no runtime action buttons; no `SKILL_KIT_RUNTIME_ENABLED` toggle.
- Frontend grep: zero references to `rm132c2`, `numeric_trim`, `RM1.32-C2`, or to the field tokens `status_chance_pct`/`damage_multiplier_pct`.
- No new UI screens / Pressables.
- Expo dev server RUNNING under recreated `start-expo.sh` wrapper (`CI=1`); localhost:3000 → 200.

---

## 12. `/api/heroes` Safety

`count = 100`. `borea`, `greek_borea`, `primordial_gaia` all hidden ✓.

---

## 13. Runtime / DB / Gacha / Roster / Catalog Safety

| Surface | Status |
|---|---|
| `SKILL_KIT_RUNTIME_ENABLED` | remains `false` |
| Runtime adapter | OFF / inert |
| Battle runtime / `battle_engine.py` / `battle_core.py` | unmodified |
| Combat UI / `combat.tsx` | unmodified |
| Debug endpoints | unchanged, still inert |
| DB writes | none |
| Divine Weapon / Status catalogs | unmodified |
| 5★ catalog | unmodified (SHA unchanged) |
| 6★ catalog | numeric `final_numbers` + trim metadata only; structural fields & identity preserved |
| Boss policy tables (RM1.34 / -B / -C) | unmodified |
| Baseline v4 | preserved on disk |
| Gacha / Roster | unmodified |
| Borea visibility | unchanged (catalog-only, hidden) |
| New API routes / UI buttons | none |

---

## 14. Warnings / Discrepancies

- Cap audit retains **67 informational WARNs** (down from 86). All are pre-existing categories aligned with the RM1.32-C delta plan, none introduced by RM1.32-C2.
- Audit threshold uses `>=` while trim policy uses `>`, so at-cap values (380, 600, 85) still surface in the audit as informational. This is intentional: it preserves audit visibility on values living exactly at cap.
- Hard control duration WARNs were NOT trimmed: the field is not explicitly PvP-tagged in the catalog; conservative prompt rule says skip.
- Heal/shield WARNs were NOT trimmed: the prompt explicitly forbids blind heal trim; PvP-specific shield trim would require an explicit PvP flag, which is not present in the foundation_draft schema.
- Marchio caps already aligned (pvp=3, pve=5, boss=None); no Marchio trim needed.
- `start-expo.sh` wrapper had vanished again (known P1 recurring issue); recreated with `CI=1` to satisfy Expo CLI non-interactive requirement.

---

## 15. Final Recommendation

✅ **RM1.32-C2 is accepted.** All 27 acceptance criteria are met:

1. Backup created. 2. Patch script created. 3. Result JSON created. 4. Validator created. 5. Checkpoint doc created. 6. Catalog changes limited to `final_numbers` numeric + metadata. 7. No skill identity/status/effect/description/slot changes. 8. No boss policy tables modified. 9. No DW/status catalog modified. 10. No runtime/DB/gacha/roster changes. 11. Runtime flags remain false. 12. Borea hidden/catalog-only. 13. Marchio Borea-only. 14. 5★ 100/100 foundation_draft preserved. 15. 6★ 78/78 foundation_draft preserved. 16. 5★ skill_2 not true ultimate. 17. 6★ ultimate true preserved (13/13). 18. Numeric trim validator PASS. 19. Existing 5★/6★ balance validators PASS. 20. Runtime debug snapshot validators PASS. 21. Boss policy audits PASS. 22. Suite PASS (28/28). 23. Baseline diff PASS under v5. 24. API smoke PASS. 25. UI safety PASS. 26. `/api/heroes` remains 100. 27. Docs report final status.

Idempotency confirmed via rerun (no further mutations). Baseline v5 is now the active anchor; the baseline-diff validator auto-targets it.

---

## 16. Suggested Next Tasks

- 🟢 **P3 — RM1.32-C3 (opt, hypothetical)**: Boss-side numeric design notes (no catalog mutation) for the remaining 4 `boss_mitigation_candidate` WARNs — emit a design-only note table referencing RM1.34/RM1.34-C anti-loop policy.
- 🟡 **P2 — RM1.33-H (future, hypothetical)**: Divine Weapon preview rejection / catalog-only safety fixture (mirror RM1.33-G pattern on the DW side).
- 🟡 **P2 — RM1.34-E (future, hypothetical)**: Boss-side test fixture seed with 1–2 example bosses per family exercising the 3 boss policy tables.
- 🟡 **P2 (future)**: Collection Synergies V2 Activation.
- 🟡 **P2 (future)**: Affinity System Phase 2 — Gift catalog driven by Faction × Element matrix.
