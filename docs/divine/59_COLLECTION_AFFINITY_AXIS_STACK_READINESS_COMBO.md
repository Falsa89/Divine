# MEGA-COMBO — CS2-B + AF2-B + AXIS-A + UI-PREVIEW-A + STACK-A

Data: 2025-06 — Read-only, inert, design-only one-shot.

## 1. Scopo del Mega-Combo

Eseguire in un singolo passaggio cinque blocchi di preparazione totalmente inerti:

- **CS2-B**: skeleton del resolver di Collection Synergy V2 (OFF).
- **AF2-B**: bozza economy + cap policy per Affinity Phase 2.
- **AXIS-A**: audit di consistenza degli assi canonici Faction × Element.
- **UI-PREVIEW-A**: piano di readiness UI read-only per Collection/Affinity.
- **STACK-A**: audit cross-system di sicurezza dello stack progressione.

Nessuna modifica a runtime, DB, gacha, roster, catalog source, baseline, UI, battle_engine, combat.tsx, Borea.

## 2. Collection Resolver Skeleton OFF (CS2-B)

File creati:
- `/app/backend/data/collection_synergy_preview_resolver.py`
- `/app/backend/scripts/audit_collection_synergy_preview_resolver_safety.py`

Caratteristiche:
- Feature flag `COLLECTION_SYNERGY_BATTLE_ENABLED` con singolo token truthy `true_explicit_collection_runtime_on`; default OFF; tutti i token comuni (true/1/yes/on/TRUE) rifiutati.
- Funzioni puramente di lettura: `is_collection_synergy_runtime_enabled`, `load_collection_synergy_readiness`, `preview_collection_synergy_categories`, `preview_collection_milestone_policy`, `preview_collection_synergy_for_mock_roster`, `get_disabled_collection_runtime_result`.
- `ADAPTER_MANIFEST` dichiara: `writes_to_db=false`, `writes_to_catalogs=false`, `imported_by_battle_engine=false`, `imported_by_combat_tsx=false`, `applied_to_combat=false`, `no_borea_activation=true`.
- Forbidden ID `borea` / `primordial_gaia` filtrati dal mock roster.
- Audit: 50/50 check PASS.

## 3. Affinity Economy + Cap Policy Draft (AF2-B)

File creati:
- `/app/data/design/affinity/affinity_phase2_economy_cap_policy_draft_v1.json`
- `/app/backend/scripts/validate_affinity_phase2_economy_cap_policy.py`

Contenuto:
- 5 `gift_value_tiers` (universal_small, faction_favored, element_favored, faction_element_favored, event_limited_future) — punti placeholder, tutti Borea-locked, no adult naming.
- 5 `affinity_tiers` (tier_0…tier_4 con label acquaintance/trusted/bonded/devoted/oathbound_future), `stat_buff_live=false` ovunque.
- Cap policy: nessun buff combat iniziale; PvP cap `<=2` per source, `<=6` totale; no adult; no paid-only mandatory; daily/weekly cap placeholder; diminishing returns futuro.
- Prerequisiti futuri: DB schema, inventario, gift-spend endpoint auth-gated, anti-abuso, UI confirm, balance review, Borea unlock gate, rollback plan.
- Validator: 74/74 PASS.

## 4. Canonical Axis Audit (AXIS-A)

File creati:
- `/app/data/design/shared/canonical_faction_element_axis_resolution_plan_v1.json`
- `/app/backend/scripts/audit_canonical_faction_element_axes.py`

Discrepanze documentate:
- `element_dark_vs_darkness` — roster usa `dark`, RM1.34-B usa `darkness`. Soluzione: alias map `darkness→dark`, nessuna mutazione di RM1.34-B (proposto patch futuro `RM1.34-B-PATCH-A`).
- `faction_tides_in_matrix_only` — `tides` presente in RM1.34-B ma assente dal roster e dal gift draft. Soluzione: status `design_pending`, nessun mint di gift `tides_*` né collection synergy `tides`. Patch futuro `RM1.34-B-PATCH-B`.

Alias map:
- elements: `darkness→dark`, `oscurita→dark`, `shadow→dark`, `dark→dark`.
- factions: `yokai→japanese_yokai`, `creatures→creature_beast`, `beasts→creature_beast`, `celtics→celtic`.

Activation gate `faction_element_axis_activation_gate` definito; **currently_blocking_runtime_on=true**.

Live roster confermato via `/api/heroes` (count=100): 12 factions, 7 elements, nessun `tides`, element `dark`. Audit: 28/28 PASS.

## 5. UI Preview Readiness (UI-PREVIEW-A)

File creati:
- `/app/data/design/ui/collection_affinity_preview_ui_readiness_plan_v1.json`
- `/app/backend/scripts/audit_collection_affinity_ui_preview_safety.py`

Piano:
- **Nessuna implementazione UI in questo task** (`ui_files_modified=[]`, `ui_files_created=[]`).
- 3 candidati futuri read-only: `collection_synergy_milestone_preview_future`, `affinity_gift_catalog_preview_future`, `hero_detail_readonly_affinity_tab_future`.
- Strict no-buttons policy globale: claim/spend/activate/equip/enable_runtime/purchase/give = `false`.
- Sorgenti dati future: design JSON statico → API read-only auth-gated → player data solo dopo DB/migration.
- Vincoli a11y/mobile: touch target ≥44 dp (≥48 Android), WCAG AA, safe area insets, keyboard avoiding, FlashList, breakpoint iPhone 12/13/14 + Galaxy S21.
- Borea hidden handling: rendering silenzioso (no «locked»), legacy alias `borea`/`primordial_gaia` 404.

Audit grep su `synergy-codex.tsx`, `hero-detail.tsx`, `hero-skill-kits-catalog.tsx`, `divine-weapons-catalog.tsx`: 24/24 PASS, 0 warning. Pre-esistenti pattern non correlati (rune/equipment/forge/inventory) classificati non-bloccanti via context-aware regex.

## 6. Cross-System Stack Safety (STACK-A)

File creati:
- `/app/data/design/system_safety/cross_system_progression_stack_safety_report_v1.json`
- `/app/backend/scripts/audit_cross_system_progression_stack_safety.py`

Stato corrente: tutti i sistemi inerti (Collection / Affinity / Divine Weapons / Skill Kit / Boss Policies). Battle engine e combat.tsx non importano alcun resolver.

Cap raccomandati (futuri):
- Collection total ≤15%, per category ≤5%.
- Affinity PvP per source ≤2%, totale ≤6%.
- Divine Weapons global ≤10%, PvP ≤5%.
- **Combined future PvP total ≤12%**, enforced da un futuro `global_modifier_cap_resolver` (oggi non implementato).

Rischi documentati: `additive_summed_buffs`, `multiplicative_stacking` (critico — vietato inizialmente), `axis_mismatch_runtime_drift` (blocking — vedi AXIS-A gate), `double_counting_cross_system`, `borea_hidden_leak` (critico).

Audit: 51/51 PASS.

## 7. Borea Safety

- `greek_borea`: catalog-only / hidden in `/api/heroes` (0 occorrenze), 200 su `/api/hero-skill-kits/catalogs/by-hero/greek_borea` (lookup-only).
- `borea` legacy: 404 su catalogs/by-hero.
- `primordial_gaia` legacy: 404 su catalogs/by-hero.
- Nessun artifact MEGA-COMBO referenzia Borea per attivazione; tutti i gift/collection records `borea_locked=true`.

## 8. Risultati Validator (MEGA-COMBO)

| Validator | Check | Risultato |
|---|---|---|
| CS2-B audit | 50 | PASS |
| AF2-B validator | 74 | PASS |
| AXIS-A audit | 28 | PASS |
| UI-PREVIEW-A audit | 24 | PASS |
| STACK-A audit | 51 | PASS |
| MEGA-COMBO combo validator | 39 | PASS |

## 9. Risultati Suite + Baseline

`python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff`:

- Required: 14/14 PASS (5★/6★ legacy + crosslinks + foundation + Divine Weapons + baseline trim).
- Optional: 24/24 PASS (status resolver, balance caps, runtime adapter OFF, debug snapshots 5★/6★, boss family/B/C/D/E, DW preview fixture, CS2-A, AF2-A, CS2/AF2 combo, **CS2-B, AF2-B, AXIS-A, UI-PREVIEW-A, STACK-A, MEGA-COMBO**).
- Baseline diff RM1.32-PRE (v5): PASS.
- **Totale: 39 PASS, 0 FAIL, 0 MISS.**

## 10. API Smoke

| Endpoint | HTTP | Stato atteso |
|---|---|---|
| `/api/health` | 200 | OK |
| `/api/heroes` | 200 (count=100) | OK ✓ invariant 100 |
| `/api/synergies/v2/all` | 200 | OK public read-only |
| `/api/synergies/codex` | 401 | OK auth-gated (atteso) |
| `/api/synergies/by_hero/greek_athena` | 401 | OK auth-gated |
| `/api/synergies/by_hero/greek_borea` | 401 | OK auth-gated (Borea catalog-only) |
| `/api/hero-skill-kits/catalogs/summary` | 200 | OK |
| `/api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 | OK (catalog-only path) |
| `/api/hero-skill-kits/catalogs/by-hero/borea` | 404 | OK forbidden alias |
| `/api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | OK forbidden alias |
| `/api/divine-weapons/catalogs/summary` | 200 | OK |
| `/api/hero-skill-kits/runtime/debug/coverage` | 200 | OK inert |
| `/api/affinity/gifts` | 404 | OK (endpoint non creato — atteso) |

`/api/heroes` ID check: `borea`, `primordial_gaia`, `greek_borea` assenti.

## 11. UI Safety

Nessun file UI modificato/creato. Audit grep context-aware su `synergy-codex.tsx`, `hero-detail.tsx`, `hero-skill-kits-catalog.tsx`, `divine-weapons-catalog.tsx`: 0 button bottoni di runtime CS/AF, 0 attivazioni di feature flag, 0 warning.

## 12. /api/heroes Safety

count=100, Borea/primordial_gaia hidden, sequenza fixata.

## 13. Runtime / DB / Gacha / Roster / Catalog Safety

- Nessuna scrittura DB.
- Nessuna mutazione gacha/summon/roster.
- Nessuna mutazione di `hero_skill_kits_5star_full_v1.json`, `hero_skill_kits_6star_borea_v1.json`, `divine_weapons` catalog, status catalog, boss policy source tables, baseline v5.
- Nessun import nuovo in `battle_engine.py`, `battle_core.py`, `combat.tsx`.
- Runtime adapter `SKILL_KIT_RUNTIME_ENABLED` default OFF (invariante).
- Tutti i nuovi resolver/skeleton dichiarano `runtime_attached=false`, `applied_to_combat=false`, `db_write=false`.

## 14. Warning / Discrepanze

- **AXIS-A**: Documentate due discrepanze non risolvibili in questo task (richiedono future controlled patch RM1.34-B-PATCH-A/B): `darkness` vs `dark`, `tides` orphan. Risolte oggi via alias map design-only + activation gate bloccante.
- **AF2-B**: Falso positivo iniziale sul token `adult` (presente nei nomi di campo che lo *vietano*) — risolto rendendo la regex context-aware (esclude `no_adult_*` e `adult_explicit_naming_forbidden`).
- **AF2-A → AF2-B**: gift draft non minta `tides_*`, allineato col plan AXIS-A.

## 15. Recommendation Finale

Tutti i blocchi del MEGA-COMBO sono PASS. Lo stato corrente rispetta invariants di sicurezza assoluti (Borea hidden, `/api/heroes=100`, baseline v5 clean, runtime adapter OFF). Le future attivazioni runtime di Collection / Affinity / DW / Skill Kit devono attendere:

1. `global_modifier_cap_resolver_future` implementato e auditato.
2. AXIS-A activation gate soddisfatto (controlled patch RM1.34-B + alias coverage).
3. Cap policy combinata PvP ratificata (≤12% totale).
4. DB schema + migration approvati.
5. Unit test Borea-hidden invariant a livello runtime.
6. Rollback plan per ogni feature flag.

## 16. Suggested Next Tasks

- **P2 — CS2-C**: implementare schermo UI read-only preview Collection Synergy (no buttons), seguendo `collection_affinity_preview_ui_readiness_plan_v1`.
- **P2 — AF2-C**: bozza schema inventario gift + anti-exploit invariants.
- **P2 — STACK-B**: skeleton inerte `global_modifier_cap_resolver_future` con unit test cap clamping.
- **P2 — AXIS-B**: helper inerte read-through per alias_map (consumato solo da resolver inerti).
- **P3 — RM1.34-B-PATCH-A**: migrazione controllata `darkness→dark` con rebaseline (richiede balance review).
- **P3 — RM1.34-B-PATCH-B**: decisione live roster `tides` (mint hero ufficiale oppure rimozione dalla matrix).
- **P3 — Hero detail deep-link infinite-loading**: bug fix pre-esistente non bloccante.
- **P3 — `hero-encyclopedia` 404 senza `?hero_id=`**: bug fix pre-esistente non bloccante.
- **P3 — EXP curves mockate in `buildPostBattleSummary.ts`**: refactor pre-esistente.
