# CS2-A + AF2-A — Collection Synergies V2 Readiness & Affinity Phase 2 Gift Catalog Readiness

**Task IDs:** CS2-A, AF2-A (combo)
**Status:** ✅ COMPLETE (readiness / design-only / inert)
**Baseline anchor:** `hero_skill_kit_catalog_baseline_rm132c2_v5`
**Runtime attached:** `false`
**DB / Catalog / Gacha / Roster / Inventory writes:** none
**Source catalogs / baseline / battle_engine / combat:** unchanged

---

## 1. Purpose (Combined)

- **CS2-A** — Readiness audit and design-only documentation for the future **Collection Synergies V2** system, separated clearly from the existing **Team Synergy V2** (which remains read-only / auth-gated / no battle hook). Includes an optional schema draft for collection synergy records and the activation prerequisites required before any future buff hits combat.
- **AF2-A** — Readiness audit and design-only documentation for the future **Affinity Phase 2 / Faction × Element gift catalog**. Includes an optional 85-entry draft catalog (12 factions × 7 elements + 1 universal) with safety constraints, future feature flag dependency, and zero stat-buff/DB/inventory implementation.

---

## 2. Files

### Created
- `/app/data/design/synergies/collection_synergies_v2_readiness_plan_v1.json`
- `/app/data/design/synergies/collection_synergy_v2_schema_draft_v1.json`
- `/app/data/design/affinity/affinity_phase2_gift_catalog_readiness_plan_v1.json`
- `/app/data/design/affinity/affinity_gift_catalog_faction_element_draft_v1.json` (85 entries)
- `/app/backend/scripts/audit_collection_synergies_v2_readiness.py`
- `/app/backend/scripts/audit_affinity_phase2_gift_catalog_readiness.py`
- `/app/backend/scripts/validate_collection_affinity_readiness_combo.py`
- `/app/docs/divine/58_COLLECTION_SYNERGIES_V2_READINESS_AND_AFFINITY_PHASE2.md` (this file)

### Modified
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — added three optional entries (CS2-A, AF2-A, CS2/AF2-COMBO); no required check weakened.

### Not modified
- 5★ / 6★ / Divine Weapon / Status / Borea catalogs
- Baseline v5 (latest), baseline v4 (preserved)
- Boss policy tables (RM1.34/-B/-C) and cross-table report
- `battle_engine.py`, `battle_core.py`, `combat.tsx`, HP bar runtime
- UI screens (no new Pressables, no new POST/PUT/PATCH/DELETE)
- DB / migrations / seed / gacha / roster
- Character Bible / assets
- Borea visibility (catalog-only, hidden)
- API routes (no new endpoint)

---

## 3. Collection Synergies V2 Readiness Summary

**Plan:** `/app/data/design/synergies/collection_synergies_v2_readiness_plan_v1.json`

- **Team vs Collection distinction (canonical):**
  - *Team Synergy*: active synergy computed from the current 5-hero squad. Already lives in `team_synergies_v2_initial_10.json` (10 definitions) + `synergy_definitions_v2.py` + `synergies.py`. Routes: `/api/synergies/v2/all` (200, public), `/api/synergies/codex` & `/api/synergies/by_hero/<id>` (401, auth-gated). **No battle buff applied today.**
  - *Collection Synergy*: passive, account-wide bonus computed from owned roster milestones. **Out-of-scope today**; only readiness defined.

- **Proposed collection categories (6):** `faction_collection`, `element_collection`, `rarity_collection`, `origin_group_collection`, `mythic_set_collection`, `divine_weapon_collection_link_future`.

- **Milestone model:** `owned_count_thresholds_tiered = [3, 5, 10]`, optional `star_threshold ∈ {5, 6}`, max total bonus **15%**, max per category **5%**, stacking `additive_capped`, applies to `non_pvp_initial` (PvP opt-in only later).

- **Activation prerequisites:** READ-ONLY resolver first (RM1.33-A pattern), server-side roster validation, read-only UI preview, cap policy ratified, anti-whale caps, Borea safety gate (contributions hidden until visibility unlock), `COLLECTION_SYNERGY_BATTLE_ENABLED` feature flag default OFF, DB write only after migration plan, PvP impact frozen until separate balance review.

- **Safety flags:** `runtime_attached=false`, `battle_runtime_attached=false`, `used_by_battle_engine=false`, `db_write=false`, `applied_to_combat=false`, `borea_activation_allowed=false`, `feature_flag_currently_enabled=false`, `hidden_aliases_blocked=["borea","primordial_gaia"]`.

**Optional schema draft:** `collection_synergy_v2_schema_draft_v1.json` defines per-record shape (id/category/axis_value/thresholds/bonus/stacking_rule/applies_to/borea_safety/runtime) with `loaded_by_runtime=false` and `validation_invariants` (`max_total_bonus_pct=15`, `max_per_category_bonus_pct=5`, `allowed_categories_count=6`).

---

## 4. Affinity Phase 2 Readiness Summary

**Plan:** `/app/data/design/affinity/affinity_phase2_gift_catalog_readiness_plan_v1.json`

- **Current affinity state:** no live affinity stat buffs, no spend endpoint, no DB write, no Pressable (verified by grep across `/app/backend/routes/*.py` and `/app/frontend/app/*.tsx`).

- **Proposed scope:** Faction × Element axes. Live roster canonical sources:
  - **12 factions** (greek, norse, egyptian, japanese_yokai, celtic, angelic, demonic, cursed, creature_beast, primordial, arcane, mesopotamian).
  - **7 elements** (water, fire, earth, wind, lightning, light, dark).
  - Documented spelling drift: roster uses `dark`, RM1.34-B used `darkness` — draft adopts roster spelling.
  - Documented missing faction: `tides` exists in RM1.34-B but **NOT** in the live roster — not minted in the gift draft; flagged `needs_roster_source_confirmation` for future.

- **Gift categories (4):** `faction_favored_gift` (12), `element_favored_gift` (7), `universal_small_gift`, `event_limited_future` (reserved).

- **Activation prerequisites:** approved affinity economy, non-destructive DB schema, server-side inventory with anti-dup/anti-exploit, gift_claim/spend gated behind `AFFINITY_GIFT_RUNTIME_ENABLED` (default OFF), PvP cap (≤2% per gift, ≤6% total), Borea gift records locked until Borea visibility unlocks, legacy `borea` / `primordial_gaia` excluded permanently, adult/explicit naming forbidden, cross-system audit with Collection Synergy V2.

- **Safety flags:** `runtime_attached=false`, `applied_to_combat=false`, `db_write=false`, `inventory_mutation=false`, `borea_activation_allowed=false`, `adult_explicit_naming=false`, `feature_flag_currently_enabled=false`, `hidden_aliases_blocked=["borea","primordial_gaia"]`.

---

## 5. Gift Catalog Draft Summary

**Draft:** `/app/data/design/affinity/affinity_gift_catalog_faction_element_draft_v1.json`

- `catalog_id = affinity_gift_catalog_faction_element_draft_v1`, `task_origin = AF2-A`, anchor `baseline_v5`
- **Total entries: 85** (`factions_count × elements_count = 12 × 7 = 84` faction_element_favored_gift + 1 universal)
- Per entry: `gift_id` (e.g. `greek_fire_token`), `faction_token`, `element_token`, placeholder `affinity_value_tier`, localized name key placeholder, all `design_only=true`, `runtime_attached=false`, `db_write=false`, `applied_to_combat=false`, `no_stat_buff_until_future_approved_task=true`, `borea_gift_locked_until_visibility_unlock=true`, `no_competitive_pvp_advantage_initial=true`, `naming_safe_for_rating=true`
- Constraints: `no_stat_buffs_from_gifts_until_future_task=true`, `pvp_cap_future_pct=2`, `pvp_total_cap_future_pct=6`, `borea_gifts_locked_until_visibility_unlock=true`, `adult_explicit_naming_forbidden=true`, `no_inventory_implementation_in_this_task=true`, `no_runtime_resolver_in_this_task=true`
- No adult/explicit substring (`xxx`, `nsfw`, `lewd`) found in any `gift_id` or `display_name_localized_key_placeholder`.

---

## 6. Borea Safety

- Borea ALWAYS hidden in `/api/heroes` (validator confirms `count=100`, `borea`/`greek_borea`/`primordial_gaia` absent).
- Collection plan: Borea contributions to collection synergies locked until visibility unlock; aliases `borea`/`primordial_gaia` permanently blocked.
- Affinity plan: Borea gift records explicitly locked (`borea_gift_locked_until_visibility_unlock=true`); legacy aliases blocked permanently.
- DW Borea record left intact (catalog-only, owner=`greek_borea`, `borea_activation_allowed=false` at DW catalog level).
- Cross-verified by `validate_status_resolver_contract.py`: `marchio_boreale total (Borea only): 6`.

---

## 7. Validator Results

All three dedicated scripts PASS:
- `audit_collection_synergies_v2_readiness.py` → **PASS** (0 warn, 0 fail). Cross-checked: plan flags, 6 category set, milestone caps ≤15/5%, optional schema draft, team_synergies_v2_initial_10 = 10, synergies.py no POST/PUT/PATCH/DELETE, battle_engine.py no collection hook, UI codex + hero-detail no Pressable in synergy/collection/affinity context (chirurgico per evitare false positives sul sistema rune pre-esistente), API smoke clean.
- `audit_affinity_phase2_gift_catalog_readiness.py` → **PASS** (0 warn, 0 fail). Cross-checked: plan flags, draft 85 entries (12×7 + 1), per-entry safety, no adult naming, no battle_engine hook, no routes spend/claim, no UI gift_claim/spend, `/api/affinity/gifts` → 404 (as expected).
- `validate_collection_affinity_readiness_combo.py` → **PASS** (0 fail). Cross-checked: both plans + both drafts design-only, no runtime tokens in battle_engine/combat.tsx, `/api/heroes`=100 + Borea hidden, baseline v5 present, no forbidden endpoint tokens in routes.

---

## 8. Suite / Baseline Results

`run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS 33/33** (16 required + 16 optional + 1 baseline diff). 0 fail, 0 miss. Baseline diff under **v5** clean, no `--allow-changed`.

---

## 9. API Smoke

| Endpoint | Result |
|---|---|
| `GET /api/health` | 200 |
| `GET /api/heroes` | 200 — **count = 100** |
| `GET /api/synergies/v2/all` | 200 (public read-only) |
| `GET /api/synergies/codex` | 401 (auth-gated; expected) |
| `GET /api/synergies/by_hero/greek_athena` | 401 (auth-gated; expected) |
| `GET /api/synergies/by_hero/greek_borea` | 401 (auth-gated / hidden; expected) |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 |
| `GET /api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 (catalog-only) |
| `GET /api/hero-skill-kits/catalogs/by-hero/borea` | **404** ✓ |
| `GET /api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` | 200 |
| `GET /api/hero-skill-kits/runtime/debug/coverage` | 200 (`runtime_enabled=false`) |
| `GET /api/affinity/gifts` | 404 (not exposed; expected) |

No new endpoint created by this task.

---

## 10. UI Safety

- No new Pressable, no new POST/PUT/PATCH/DELETE in any frontend file.
- `synergy-codex.tsx` and `hero-detail.tsx` checked CHIRURGICALLY — forbidden Pressable tokens (Activate/Claim/Spend/Equip/Battle Test/Enable Runtime, onPress activate/claim/spend, HTTP mutations) are flagged **only when they appear on a line that also mentions `synerg`/`collection`/`affinity`/`gift`**. This protects against false positives from the pre-existing **runes equipment** system in `hero-detail.tsx` (which legitimately uses `Equip` / `method: 'POST'` for runes — a separate, pre-existing feature that this readiness task does not touch).
- Frontend grep: zero references to `collection_synergy_resolve`, `apply_collection_synergy_buff`, `apply_affinity_buff`, `gift_claim`, `gift_spend`, `GiveGift`, `ClaimGift`, `SpendGift`.
- Expo dev server RUNNING; localhost:3000 → 200.

---

## 11. `/api/heroes` Safety

`count = 100`. `borea` / `greek_borea` / `primordial_gaia` all hidden ✓.

---

## 12. Runtime / DB / Gacha / Roster / Catalog Safety

| Surface | Status |
|---|---|
| `SKILL_KIT_RUNTIME_ENABLED` | remains `false` |
| `COLLECTION_SYNERGY_BATTLE_ENABLED` (future) | declared OFF in plan |
| `AFFINITY_GIFT_RUNTIME_ENABLED` (future) | declared OFF in plan |
| Runtime adapter | OFF / inert |
| `battle_engine.py` (mtime May 3) | unmodified |
| `battle_core.py`, `combat.tsx` | unmodified |
| Debug endpoints | unchanged |
| DB writes | none |
| Inventory subsystem | none introduced |
| Affection points logic | none introduced |
| Hero stat affinity buffs | none active / none introduced |
| Catalogs (5★/6★/DW/Status) | mtimes unchanged |
| Baseline v5 (mtime May 16 21:35) / v4 preserved | unchanged |
| Boss policy tables / cross-table report | unchanged |
| Gacha / Roster | unmodified |
| Borea visibility | unchanged (catalog-only, hidden) |
| New API routes / UI Pressables | none |

---

## 13. Warnings / Discrepancies

- Initial CS2-A audit pass flagged `Equip` and `method: 'POST'` in `hero-detail.tsx`. Investigation showed these are part of the pre-existing **runes equipment** feature (totally independent of Collection Synergy / Affinity). The audit was refined to operate on a **contextual line match** (forbidden token co-occurring with `synerg`/`collection`/`affinity`/`gift` on the same line), explicitly documented inside the audit script and here. No false positives remain; no legitimate concern remained.
- Documented spelling drift: roster uses `dark` while RM1.34-B used `darkness`. The gift draft adopts the live roster canonical spelling and notes the drift in the plan.
- Documented missing faction: `tides` is in the boss matrix (RM1.34-B) but absent from the live roster. The gift draft does NOT mint `tides_*` entries; this is flagged for future roster-source confirmation.
- Pre-existing 67 informational WARNs in `audit_balance_foundation_boss_pvp_caps.py` persist as before. No new WARNs introduced by CS2-A or AF2-A.

---

## 14. Final Recommendation

✅ **CS2-A + AF2-A (combo) accepted.** All 22 acceptance criteria are met:

1. CS2-A readiness plan created. 2. CS2-A optional schema draft created. 3. CS2-A audit script created. 4. AF2-A readiness plan created. 5. AF2-A draft Faction×Element gift catalog created (85 entries). 6. AF2-A audit script created. 7. Combo validator created. 8. Checkpoint doc created. 9. No runtime/DB/gacha/roster changes. 10. No `battle_engine`/`combat` changes. 11. No source catalog or baseline mutation. 12. No Borea activation. 13. `/api/heroes=100`. 14. Runtime adapter OFF/inert. 15. UI safety PASS (chirurgico contextual check). 16. Suite PASS (33/33). 17. Baseline diff PASS under v5. 18. CS2-A audit PASS. 19. AF2-A audit PASS. 20. Combo validator PASS. 21. No new endpoint created. 22. Final report complete.

Both readiness systems are now documented, drafted, and audited under a single suite run. They are ready to be promoted to next-tier implementation tasks (resolver, schema validation, UI preview, cross-stack audit) when the user approves.

---

## 15. Suggested Next Tasks

- 🟡 **P2 — CS2-B (hypothetical)**: Collection synergy READ-ONLY resolver skeleton (inert; mirrors the RM1.33-A `skill_kit_runtime_adapter` pattern).
- 🟡 **P2 — CS2-C (hypothetical)**: UI read-only preview screen for collection synergy milestones, reusing `synergy-codex.tsx` primitives (no Pressable, no POST).
- 🟡 **P2 — AF2-B (hypothetical)**: Affinity economy + cap policy draft (gift→affection_points→tier breakpoints) with anti-exploit invariants.
- 🟡 **P2 — AF2-C (hypothetical)**: Cross-system stack audit (Collection Synergy V2 × Affinity Phase 2) to prevent double-stack abuse.
- 🟢 **P3 — Optional**: Resolve `tides` faction status (roster lacks it, RM1.34-B has it) before any gift catalog activation.
- 🟢 **P1 (operational)**: Long-term fix for `start-expo.sh` disappearance (currently re-created with `CI=1`; recurring issue across container restarts).
