# MEGA-COMBO — CS2-D + AF2-D + AF2-E + STACK-C + AXIS-C

Data: 2025-06 — Read-only, inert, design-only one-shot.
Baseline anchor: `hero_skill_kit_catalog_baseline_rm132c2_v5`.

## 1. Scopo del Mega-Combo

Quinto combo accelerato che porta il sistema dal piano puro (CS2-A..C, AF2-A..C, STACK-A..B, AXIS-A..B) alla **prima superficie utente + endpoint pubblico read-only** del progetto Affinity/Collection, mantenendo zero attivazione runtime:

- **CS2-D** — UI stub strictly read-only `/app/frontend/app/collection-synergies-preview.tsx`.
- **AF2-D** — migration plan draft inerte per le 3 future collezioni.
- **AF2-E** — endpoint GET-only `/api/affinity/gifts` (+ `/summary`, `/by-faction/{id}`).
- **STACK-C** — 12 edge case fixtures + validator per `preview_combined_cap`.
- **AXIS-C** — dynamic axis preview helper inerte.

Nessuna mutazione a runtime, DB, gacha, roster, catalog source, baseline, `battle_engine.py`, `battle_core.py`, `combat.tsx`, Borea.

## 2. Collection Preview UI Stub (CS2-D)

File creati:
- `/app/frontend/app/collection-synergies-preview.tsx` (strictly read-only)
- `/app/backend/scripts/audit_collection_synergy_preview_ui_stub.py`

Caratteristiche stub:
- Banner top "**Preview / Design-only / Non attivo**" sempre visibile.
- Cap policy panel: max totale 15%, max per categoria 5%, soglie owned 3/5/10, stacking `additive_capped`, applies_to non_pvp_initial / opt_in_pvp_future_only.
- 6 categorie statiche (`STATIC_DESIGN_CATEGORIES`) derivate da CS2-A readiness plan; ognuna con badge "Locked / Future" e `future_runtime_feature_flag` echeggiato.
- `Pressable` solo per: (a) back navigation, (b) expand/collapse delle card (toggle locale `useState`, nessuna fetch). Touch target ≥44 dp.
- `apiCall('/api/synergies/v2/all')` opzionale solo come heartbeat di reachability; il payload non viene usato per popolare la UI.
- Zero `POST/PUT/PATCH/DELETE`. Zero `axios.create`. Zero `AsyncStorage.setItem`. Zero feature flag toggle. Zero reference a `battle_engine`/`combat`.
- Borea: nessun riferimento a obtainable/playable; le categorie non includono entry per hero specifici.
- Footer mostra sorgente (`live design` o `static fallback`) + nota "Borea hidden / Legacy aliases excluded".

Audit context-aware (esclude negazioni `not equip`/`no equip`): **12/12 PASS**.

## 3. Affinity Migration Plan (AF2-D)

File creati:
- `/app/data/design/affinity/affinity_phase2_migration_plan_draft_v1.json`
- `/app/backend/scripts/validate_affinity_phase2_migration_plan_draft.py`

Plan:
- 3 future collections con campi + 5 indexes proposti totali (uniq + sparse + composite). Tutte `create_in_migration=false`, `is_design_only_today=true`.
- Rollback plan documentato (drop_new_collections_only, 7-day audit window, no cross-collection cascade).
- Backfill plan: `no_backfill_initial` (subsystem nuovo, collezioni partono vuote, document creation lazy).
- Privacy / right-to-erasure documentati (cascade via user_id index).
- 7 migration_gates enumerati (`auth_model_approved`, `endpoint_design_approved`, `rollback_tested`, `rate_limits_configured`, `borea_visibility_gate_tested`, `economy_finalized`, `stack_b_global_cap_resolver_audited`) — **tutti `currently_satisfied=false`**.
- Eredita 8 vettori di abuso da AF2-C anti-exploit policy.

Validator 51/51 PASS (con esclusione context-aware del pre-esistente `sanctuary.py` POST `/sanctuary/affinity/gain`, sistema indipendente da Phase 2).

## 4. Affinity Gifts Read-Only Endpoint (AF2-E)

File creati:
- `/app/backend/routes/affinity_gifts.py` (GET-only)
- `/app/backend/scripts/audit_affinity_gifts_readonly_endpoint_safety.py`

File modificati:
- `/app/backend/game_systems.py` — import + registrazione `register_affinity_gifts_readonly_routes(router)` sotto il prefisso `/api`.

Endpoint:
- `GET /api/affinity/gifts` → 200, 85 entries totali, `safety_envelope` con 11 flag run/db/inventory/gift_spend/stat_buff/borea = `false`.
- `GET /api/affinity/gifts/summary` → 200, no entries, include economy_pvp_cap_per_source_pct=2, economy_pvp_cap_total_pct=6.
- `GET /api/affinity/gifts/by-faction/{faction_id}` → 200 per faction live; 404 per `borea`/`primordial_gaia`/`tides` o sconosciuti.
- **Tutti i metodi mutazione (POST/PUT/PATCH/DELETE) restituiscono 405** (Method Not Allowed) verificato live.
- Public (no auth) perché non espone user state.
- Zero DB write tokens (`insert_one`/`update_*`/`delete_*`/`bulk_write`/`replace_one`) nel route file.

Audit 48/48 PASS (include API smoke live).

## 5. Global Cap Edge Tests (STACK-C)

File creati:
- `/app/data/design/system_safety/global_modifier_cap_resolver_edge_case_fixtures_v1.json`
- `/app/backend/scripts/validate_global_modifier_cap_resolver_edge_cases.py`

12 casi documentati:
1. empty_sources → sum=0
2. collection_only_under_cap (4%) → clamp=4
3. collection_over_15 (18%) → clamp=12 (combined PvP cap)
4. affinity_over_6_pvp (9%) → clamp=9
5. dw_over_5_pvp (8%) → clamp=8
6. combined_over_12_pvp (5+6+5=16) → clamp=12
7. pve_permissive → target_cap=null, sum echo=16
8. negative_modifier (-3%) → echo=-3 (per preview; future validation)
9. unknown_source_safe (dict senza `pct`, stringa non-dict) → silently dropped, no exception
10. borea_locked_source → echo OK + nota future runtime filter required
11. multiplicative_source → echo OK + nota future reject required
12. huge_value_clamp (9999%) → clamp=12

Validator esegue tutti i 12 casi, asserisce `is_disabled_global_cap_result=true`, runtime/db/applied_to_combat=false, no exception, clamp ≤ target. **102/102 PASS.**

## 6. Dynamic Axis Preview Helper (AXIS-C)

File creati:
- `/app/backend/data/canonical_axis_dynamic_preview.py`
- `/app/backend/scripts/audit_canonical_axis_dynamic_preview.py`
- `/app/data/design/shared/canonical_axis_dynamic_preview_result_v1.json` (output dell'audit)

Funzioni inerti:
- `preview_live_axis_sets()` — fetch `/api/heroes` con fallback statico a `heroes_master.json`; filtra alias forbidden Borea; ritorna `live_factions_sorted`, `live_elements_sorted`, `source` (api/static/unavailable).
- `preview_axis_drift_report()` — confronta live vs RM1.34-B matrix vs AF2-A gift draft vs AXIS-A plan; calcola `drift.factions_in_matrix_not_in_live` (contiene `tides`), `drift.elements_in_matrix_not_in_live` (contiene `darkness`), `tides_status='design_pending'`, `darkness_to_dark_alias_present=true`.
- `validate_alias_coverage()` — conferma `fully_covered=true`, `design_pending_factions=['tides']`, `uncovered_elements=[]`, `uncovered_factions=[]`.

Manifest: `mutates_source_tables=false`, `patches_rm134b=false`, `patches_af2a=false`, zero import in battle_engine/battle_core/combat. **Audit 38/38 PASS.**

## 7. Borea Safety

- `greek_borea`: catalog-only / hidden in `/api/heroes` (0 occorrenze), 200 su `/api/hero-skill-kits/catalogs/by-hero/greek_borea`.
- `borea`/`primordial_gaia` legacy: 404 ovunque (anche su `/api/affinity/gifts/by-faction/borea`).
- AXIS-C helper filtra esplicitamente alias forbidden quando legge `/api/heroes`.
- CS2-D UI mostra solo categorie design statiche, nessun reveal Borea.

## 8. Validator Results (questo task)
| Validator | Check | Stato |
|---|---|---|
| CS2-D audit | 12 | PASS |
| AF2-D validator | 51 | PASS |
| AF2-E audit | 48 | PASS |
| STACK-C validator | 102 | PASS |
| AXIS-C audit | 38 | PASS |
| MEGA-COMBO-3 combo | 62 | PASS |

## 9. Suite + Baseline v5

`run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **50 PASS / 0 FAIL / 0 MISS**, baseline diff RM1.32-PRE su v5 PASS.

## 10. API Smoke
| Endpoint | HTTP |
|---|---|
| `/api/health` | 200 |
| `/api/heroes` | 200, count=100 |
| `/api/affinity/gifts` | **200 (nuovo, GET-only)** |
| `/api/affinity/gifts/summary` | 200 |
| `/api/affinity/gifts/by-faction/greek` | 200 |
| `/api/affinity/gifts/by-faction/borea` | 404 (legacy alias) |
| `/api/affinity/gifts/by-faction/tides` | 404 (faction design_pending) |
| `/api/synergies/v2/all` | 200 |
| `/api/synergies/codex` | 401 (auth-gated atteso) |
| `/api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 (catalog-only) |
| `/api/hero-skill-kits/catalogs/by-hero/borea` | 404 |
| `/api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 |
| `/api/divine-weapons/catalogs/summary` | 200 |
| `/api/hero-skill-kits/runtime/debug/coverage` | 200 |
| POST/PUT/PATCH/DELETE `/api/affinity/gifts` | **405 Method Not Allowed** ✓ |

## 11. UI Safety
- CS2-D stub: zero mutation HTTP, zero forbidden action buttons in CS context (audit context-aware con esclusione `not equip` documentazione), zero DB/inventory strings, zero battle/combat refs, zero runtime flag toggles, 0 `axios.create`.
- Pressable count: 1 back + 6 toggle-expand per card ≤ 7 totali, all'interno del bound (1..6 per `min(categories.length, 6)` = OK).
- Synergy-codex, hero-detail, hero-skill-kits-catalog, divine-weapons-catalog: zero refs ai nuovi resolver / endpoint.

## 12. /api/heroes Safety
count=100, Borea/primordial_gaia/greek_borea assenti, sequenza fixata.

## 13. Runtime / DB / Gacha / Roster / Catalog Safety
- Zero scritture DB.
- Zero mutazioni gacha/summon/roster.
- Zero mutazioni a `hero_skill_kits_5star_full_v1.json`, `hero_skill_kits_6star_borea_v1.json`, `boss_family_element_faction_matrix_v1.json` (`darkness`+`tides` ancora presenti), `affinity_gift_catalog_faction_element_draft_v1.json` (usa `dark`, no `tides_*`), DW catalog, status catalog, baseline v5.
- Zero nuovi import in `battle_engine.py`, `battle_core.py`, `combat.tsx` per i 5 nuovi artifact.
- Tutti i 4 feature flag default OFF:
  - `SKILL_KIT_RUNTIME_ENABLED` ✓
  - `COLLECTION_SYNERGY_BATTLE_ENABLED` ✓
  - `AFFINITY_GIFT_RUNTIME_ENABLED` ✓
  - `GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED` ✓

## 14. Warning / Discrepanze
- **AF2-D falso positivo iniziale**: il pattern grep su `/affinity/` matchava il pre-esistente POST `/sanctuary/affinity/gain` (sistema Sanctuary indipendente). Risolto con esclusione context-aware di `sanctuary.py` + restrizione del regex ai path `affinity/(gift|inventory|spend|ledger|grant)`.
- **CS2-D falso positivo iniziale**: la parola `equip` in `description: "...catalog count, not equip..."`. Risolto con negation prefix detection (`not `, `no `, `never `, `non `).
- Nessun warning bloccante. Source RM1.34-B e AF2-A intatti (verificato).

## 15. Final Recommendation
Tutti i 21 acceptance criteria soddisfatti. Lo stato corrente espone per la prima volta una **superficie utente + endpoint pubblico** per la preview Collection/Affinity, ma in modalità totalmente inerte. Pre-requisiti per qualsiasi attivazione runtime:

1. Implementazione dell'endpoint POST auth-gated `/api/affinity/gift-spend` dietro `AFFINITY_GIFT_RUNTIME_ENABLED`.
2. Ratifica AF2-D migration plan + rollback rehearsal.
3. Ratifica STACK-B + integrazione con STACK-C edge cases nel test runtime futuro.
4. Controlled patches RM1.34-B-A/B (darkness→dark, decisione tides).
5. Unit test Borea-hidden invariant + a11y pass su CS2-D stub.
6. Bot abuse / multi-account caps in produzione.

## 16. Suggested Next Tasks
- 🟡 **P2 — CS2-E**: collegare il CS2-D stub a una route deep-link nel _layout, oppure mantenerlo accessibile solo via QA tools.
- 🟡 **P2 — AF2-F**: rollback rehearsal script inerte (dry-run) per `user_gift_inventory` / `gift_transaction_ledger` / `hero_affinity_state`.
- 🟡 **P2 — AF2-G**: inert auth-gated POST endpoint skeleton `/api/affinity/gift-spend` con feature flag OFF, idempotency stub + replay guard mock.
- 🟡 **P2 — STACK-D**: formalizzare in `preview_combined_cap` la rejection di multiplicative sources (oggi solo documentazione).
- 🟡 **P2 — AXIS-D**: helper avanzato che incorpora dynamic preview + alias map e produce una validation table per attivazione runtime (oggi gate solo documentato).
- 🔵 **P3 — RM1.34-B-PATCH-A**: migrazione controllata `darkness→dark` + rebaseline.
- 🔵 **P3 — RM1.34-B-PATCH-B**: decisione `tides` (mint hero ufficiale o rimozione).
- 🔵 **P3 — Bug pre-esistenti**: hero-detail deep-link infinite-loading, hero-encyclopedia 404 senza `?hero_id=`, EXP curves mockate in `buildPostBattleSummary.ts`.
