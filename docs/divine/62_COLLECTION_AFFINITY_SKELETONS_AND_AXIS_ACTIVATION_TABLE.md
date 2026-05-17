# MEGA-COMBO — CS2-E + AF2-F + AF2-G + STACK-D + AXIS-D

Data: 2025-06 — Read-only, inert, design-only one-shot.
Baseline anchor: `hero_skill_kit_catalog_baseline_rm132c2_v5`.

## 1. Scopo

Sesto combo accelerato che porta a:
- **CS2-E** — deep-link/menu entry per la preview Collection Synergy.
- **AF2-F** — rollback rehearsal dry-run del migration plan AF2-D.
- **AF2-G** — POST `/api/affinity/gift-spend` skeleton DISABILITATO (HTTP 423).
- **STACK-D** — rejection delle fonti multiplicative in `preview_combined_cap`.
- **AXIS-D** — activation validation table con `activation_ready=false`.

Nessuna mutazione di runtime, DB, gacha, roster, catalog source, baseline, `battle_engine.py`, `battle_core.py`, `combat.tsx`, Borea.

## 2. CS2-E Navigation Entry

Voce di menu "Sinergie Collezione" nella sezione "Altro" di `(tabs)/menu.tsx`, route `/collection-synergies-preview`. Schermata registrata in `_layout.tsx`. Nessun pulsante mutativo sulla stessa riga del menu, nessun Borea reveal. Audit context-aware: **12/12 PASS**.

## 3. AF2-F Rollback Rehearsal Dry-Run

Script `affinity_phase2_migration_rollback_rehearsal.py`:
- Default dry-run, `--commit` rifiutato con exit-code 2.
- Zero `motor` / `pymongo` import nel codice.
- Simula in-memory i 4 step documentati dal plan AF2-D.
- Output JSON `affinity_phase2_rollback_rehearsal_result_v1.json` con `dry_run=true`, `db_write=false`, `migration_applied=false`, `rollback_executed=false`, `collections_touched=[]`, `idempotent_rerun=true`, `borea_rollback_safe=true`.
- Validator esegue dry-run + tentativo `--commit` (rifiutato): **31/31 PASS**.

## 4. AF2-G Gift-Spend POST Skeleton (DISABLED)

`POST /api/affinity/gift-spend`:
- Feature flag `AFFINITY_GIFT_RUNTIME_ENABLED`, unico truthy `true_explicit_affinity_gift_runtime_on` (NON impostato).
- Default 423 (Locked) con `safety_envelope` completo: `enabled=false`, `db_write=false`, `inventory_write=false`, `affinity_points_write=false`, `gift_spend_executed=false`, `idempotency_required=true`, `no_borea_activation=true`.
- Borea alias check PRIMA del flag: `hero_id` ∈ {`borea`, `primordial_gaia`, `greek_borea`} → 404 immediato.
- Validazione shape Pydantic (gift_id/hero_id/quantity/idempotency_key) ma NESSUN write.
- Zero import `motor`/`pymongo`/`from server import db`/`from database import`.
- Zero write tokens (`insert_/update_/delete_/bulk_/replace_`).
- Auth NON aggiunto oggi (rationale: no-write endpoint per design; future task aggiungerà `Depends(get_current_user)` + rate-limit middleware PRIMA dell'attivazione del flag).
- Verificato live: `empty: 423, valid: 423, borea: 404, greek_borea: 404`. GET/PUT/PATCH/DELETE → 405.

Audit: **37/37 PASS.**

## 5. STACK-D Multiplicative Rejection

Modifica chirurgica a `preview_combined_cap`:
- Sources con `stacking_mode='multiplicative'` (case-insensitive) o `stacking='multiplicative'` ESCLUSE dalla `additive_sum`.
- Riportate in `mock_sources_rejected_multiplicative` con `reason='multiplicative_rejected_preview_only'`, `forbidden_in_initial_runtime=true`.
- Resolver resta OFF/inert: `runtime_attached=false`, `applied_to_combat=false`, `db_write=false`, `is_disabled_global_cap_result=true`.
- `multiplicative_policy='rejected_preview_only'`, `multiplicative_forbidden_in_initial_runtime=true` esposti nel payload.

Fixture file con 10 casi: collection mult, affinity mult, DW mult, mixed additive+multiplicative, huge mult, Borea mult, unknown stacking treated as additive, case-insensitive detection, PvE multiplicative, no stacking field default additive.

Aggiornato STACK-C case 11 per riflettere il nuovo comportamento (additive_sum=0 per source multiplicative, era 5). STACK-C continua a passare con **103/103**.

Validator STACK-D: **118/118 PASS.**

## 6. AXIS-D Activation Validation Table

Tabella `canonical_axis_activation_validation_table_v1.json`:
- `activation_ready=false`, `design_preview_ready=true`, `currently_blocking_any_axis_runtime_on=true`.
- 6 validation_rows: 2 fail (darkness vs dark unpatched, tides orphan unresolved), 4 pass (gift draft elements aligned, gift draft factions aligned, borea hidden, alias coverage).
- 2 blockers `severity=blocking_runtime_on`:
  - `darkness_vs_dark_unpatched` → resolution_task `RM1.34-B-PATCH-A`.
  - `tides_orphan_unresolved` → resolution_task `RM1.34-B-PATCH-B`.
- 7 `required_before_activation` gates: alias_coverage_pass, roster_source_confirmed, gift_axis_equals_roster, **boss_matrix_axis_equals_roster (currently_satisfied=false)**, **tides_decision_made (false)**, borea_hidden_check_pass, **rebaseline_after_patch (false)**.
- `recommended_patch_order` enumera 5 step (RM1.34-B-PATCH-A → -PATCH-B → re-audit AXIS → rebaseline v6 → considerare runtime ON).
- `do_not_patch_in_this_task` esplicitamente `{rm134b_matrix:true, af2a_gift_draft:true, axis_a_plan:true, baseline_v5:true}`.

Validator confronta tabella con files reali (RM1.34-B contiene ancora `darkness`+`tides`, AF2-A contiene ancora `dark` senza `tides_*`). **48/48 PASS.**

## 7. Borea Safety

- `greek_borea` catalog-only / hidden in `/api/heroes` (count check live).
- `borea` / `primordial_gaia` 404 ovunque, incluso il nuovo `/api/affinity/gift-spend` (rigetto PRIMA del flag check, esposto come `forbidden hero alias` con codice 404 neutro).
- AXIS-D table assigna `borea_visibility` come PASS row.

## 8. Validator Results
| Validator | Check | Stato |
|---|---|---|
| CS2-E audit | 12 | PASS |
| AF2-F validator | 31 | PASS |
| AF2-G audit | 37 | PASS |
| STACK-D validator | 118 | PASS |
| AXIS-D validator | 48 | PASS |
| MEGA-COMBO-4 combo | 56 | PASS |

## 9. Suite + Baseline v5

`run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **56 PASS / 0 FAIL / 0 MISS**, baseline diff RM1.32-PRE su v5 PASS.

Adjustments necessari (in-task, non-breaking): 3 validator pre-esistenti (AF2-B, AF2-C, AF2-D) facevano grep generico su `/api/affinity/gift-spend` come sentinella di "nessun endpoint creato". Esplicitamente esclusi `affinity_gift_spend.py` da quei grep, dato che AF2-G è autorizzato nel current scope, sempre 423, mai write. Nessuna logica indebolita.

## 10. API Smoke
| Endpoint | Metodo | Codice | Note |
|---|---|---|---|
| `/api/health` | GET | 200 | OK |
| `/api/heroes` | GET | 200 (count=100) | OK ✓ invariant |
| `/api/affinity/gifts` | GET | 200 | OK (AF2-E preview) |
| `/api/affinity/gifts/summary` | GET | 200 | OK |
| `/api/affinity/gifts/by-faction/greek` | GET | 200 | OK |
| `/api/affinity/gifts/by-faction/borea` | GET | 404 | OK alias rejected |
| `/api/affinity/gift-spend` empty body | POST | **423** | OK disabled |
| `/api/affinity/gift-spend` valid payload | POST | **423** | OK disabled |
| `/api/affinity/gift-spend` hero_id=borea | POST | **404** | OK alias rejected |
| `/api/affinity/gift-spend` hero_id=greek_borea | POST | **404** | OK alias rejected |
| `/api/affinity/gift-spend` | GET/PUT/PATCH/DELETE | 405 | OK only POST |
| `/api/synergies/v2/all` | GET | 200 | OK |
| `/api/hero-skill-kits/catalogs/by-hero/greek_borea` | GET | 200 | OK catalog-only |
| `/api/hero-skill-kits/catalogs/by-hero/borea` | GET | 404 | OK |
| `/api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | GET | 404 | OK |
| `/api/hero-skill-kits/runtime/debug/coverage` | GET | 200 | OK inert |

## 11. UI Safety
- CS2-E nav entry aggiunta in `(tabs)/menu.tsx` ed in `_layout.tsx`. Nessun mutating token sulla riga del menu. Nessun Borea reveal.
- CS2-D screen invariata (re-verificata strict read-only).
- Audit context-aware su screen di destinazione: zero mutation HTTP, zero DB strings, zero battle refs.
- Nessun pulsante gift-spend nelle frontend tsx (grep ricorrente).

## 12. /api/heroes Safety
count=100, Borea/primordial_gaia/greek_borea hidden, sequenza fixata.

## 13. Runtime / DB / Gacha / Roster / Catalog Safety
- Zero scritture DB.
- Zero mutazioni gacha/summon/roster.
- Zero mutazioni a `hero_skill_kits_5star_full_v1.json`, `hero_skill_kits_6star_borea_v1.json`, `boss_family_element_faction_matrix_v1.json` (`darkness`+`tides` ancora presenti), `affinity_gift_catalog_faction_element_draft_v1.json` (usa `dark`, no `tides_*`), DW catalog, status catalog, baseline v5.
- Zero nuovi import in `battle_engine.py`, `battle_core.py`, `combat.tsx`.
- 4 feature flag default OFF: `SKILL_KIT_RUNTIME_ENABLED`, `COLLECTION_SYNERGY_BATTLE_ENABLED`, `AFFINITY_GIFT_RUNTIME_ENABLED`, `GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED`.
- Resolver modificato (`global_modifier_cap_resolver.py`) ma manifest invariato: `writes_to_db=false`, `imported_by_battle_engine=false`, `applied_to_combat=false`. Nessun nuovo file di runtime importato live.

## 14. Warning / Discrepanze
- **Issue ricorrente risolta**: `start-expo.sh` era scomparso dopo restart. Wrapper ricreato in `/usr/local/bin/start-expo.sh` con cleanup `fuser -k 3000/tcp` + `pkill expo/metro` PRE-start e `exec npx expo start --port 3000`. Expo RUNNING confermato.
- 3 validator pre-esistenti (AF2-B/C/D) adattati per escludere `affinity_gift_spend.py` dal grep generico (AF2-G è autorizzato dal task corrente, sempre 423/no-write). Nessuna logica indebolita.
- STACK-C case 11 aggiornato per matchare il nuovo comportamento STACK-D (additive_sum=0 per source multiplicative). STACK-C continua a passare con 103/103.
- AF2-G non aggiunge `Depends(get_current_user)` oggi (no-write endpoint by design). Future task `AF2-H` lo aggiungerà PRIMA dell'attivazione del feature flag.

## 15. Final Recommendation

Tutti i 21 acceptance criteria soddisfatti. Status:
- Endpoint utente: `/api/affinity/gifts` (GET 200) + `/api/affinity/gift-spend` (POST 423 disabled).
- UI utente: stub Collection Synergy raggiungibile via menu → "Altro" → "Sinergie Collezione".
- Strumenti audit: dry-run rollback, multiplicative rejection, activation table.
- Activation gates: `activation_ready=false`, bloccato da darkness+tides. Necessari RM1.34-B-PATCH-A/B prima di qualsiasi flip.

## 16. Suggested Next Tasks
- 🟡 **P2 — AF2-H**: aggiunta `Depends(get_current_user)` + rate-limit middleware al POST skeleton, ancora con flag OFF.
- 🟡 **P2 — STACK-E**: formalizzare Borea-locked filtering nel preview layer (oggi solo annotation).
- 🟡 **P2 — STACK-F**: ratificare semantica debuff (oggi `pct<0` echeggiato senza clamp).
- 🟡 **P2 — AXIS-E**: implementazione inerte dell'helper "alias read-through" consumato da CS2-B / AF2-A future resolver.
- 🔵 **P3 — RM1.34-B-PATCH-A/B**: migrazione controllata `darkness→dark` + decisione `tides`, rebaseline v6.
- 🔵 **P3 — Bug pre-esistenti**: hero-detail deep-link spinner, hero-encyclopedia 404 senza `?hero_id=`, EXP curves mockate in `buildPostBattleSummary.ts`.
