# MEGA-COMBO — CS2-C + AF2-C + STACK-B + AXIS-B

Data: 2025-06 — Read-only, inert, design-only one-shot.

## 1. Scopo del Mega-Combo

Quattro blocchi di foundation totalmente inerti, costruiti sopra il precedente combo (CS2-B/AF2-B/AXIS-A/UI-PREVIEW-A/STACK-A):

- **CS2-C** — contratto UI preview Collection Synergy (plan-only, nessuno stub creato).
- **AF2-C** — schema gift inventory + anti-exploit policy.
- **STACK-B** — Global Modifier Cap Resolver skeleton OFF.
- **AXIS-B** — Canonical Axis Alias Helper inert (read-through).

Nessuna mutazione a runtime, DB, gacha, roster, catalog source, baseline, UI, `battle_engine.py`, `combat.tsx`, Borea.

## 2. Collection UI Preview Readiness (CS2-C)

File creati:
- `/app/data/design/ui/collection_synergy_preview_screen_contract_v1.json`
- `/app/backend/scripts/audit_collection_synergy_ui_preview_contract.py`

Strategia adottata: **plan-only**. Nessuno stub UI creato (`ui_files_created=[]`, `ui_files_modified=[]`). Motivazione: lo stub richiederebbe oggi (a) un fetch player-data che non esiste, (b) duplicazione di primitive da `synergy-codex.tsx`; entrambi aumentano rischio rispetto a valore.

Il contratto enumera:
- 3 data source (CS2-A readiness, CS2-A schema draft, CS2-B resolver preview).
- 6 screen goals (categorie, milestone, cap policy, badge locked/future, Borea hidden, disclaimer read-only).
- 12 forbidden actions (claim/activate/spend/equip/enable_runtime/apply_buff/POST/PUT/PATCH/DELETE/purchase/give/summon/break_seal/battle_test).
- Mobile constraints (touch ≥44/48 dp, WCAG AA, safe area, dark mode, FlashList, breakpoint iPhone 12/13/14 + Galaxy S21).
- Borea hidden handling: silent hide per `greek_borea`, `borea`/`primordial_gaia` permanentemente esclusi.
- Future implementation path candidato: `/app/frontend/app/collection-synergies-preview.tsx` (solo dopo CS2-D).

Audit 34/34 PASS.

## 3. Affinity Gift Inventory Schema + Anti-Exploit (AF2-C)

File creati:
- `/app/data/design/affinity/affinity_gift_inventory_schema_draft_v1.json`
- `/app/data/design/affinity/affinity_gift_anti_exploit_policy_v1.json`
- `/app/backend/scripts/validate_affinity_gift_inventory_schema.py`

**Schema** documenta 3 collezioni future (tutte `is_design_only=true`, `is_migration_created=false`, `is_indexed_in_runtime=false`):
- `user_gift_inventory_future` (user/gift/source_bucket stack)
- `gift_transaction_ledger_future` (append-only, idempotency_key unique-indexed)
- `hero_affinity_state_future` (snapshot derivabile da ledger)

Integrity constraints: no negative quantity, ledger required for spend, idempotency key required, server authoritative, no client-trusted grant, Borea locked, gift_id must exist in catalog, tides gift ids forbidden, `stat_buff_live=false`.

**Anti-exploit policy** copre 8 vettori di abuso documentati: `double_spend_replay`, `double_grant_via_event_rerun`, `client_trusted_grant`, `borea_leak`, `stat_buff_runaway`, `negative_quantity_underflow`, `rate_limit_circumvention_via_multi_account`, `tides_orphan_gift`. Mitigations enumerate: idempotency keys 24h, replay protection con HTTP 409 + same payload, rate limit (30/min user, 240/h, 60/min IP, burst 6/10s), Mongo multi-doc transaction, premium currency separation, no paid-only mandatory progression, PvP caps ereditati da AF2-B (≤2 source, ≤6 total).

Validator 83/83 PASS. Nessuna migration creata, nessun endpoint, nessun pulsante UI.

## 4. Global Modifier Cap Resolver (STACK-B)

File creati:
- `/app/backend/data/global_modifier_cap_resolver.py`
- `/app/backend/scripts/audit_global_modifier_cap_resolver_safety.py`

Caratteristiche:
- Flag `GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED` default OFF, unico token truthy `true_explicit_global_cap_runtime_on`; token comuni (true/1/yes/on/TRUE) rifiutati.
- Funzioni inerti: `is_global_modifier_cap_resolver_enabled`, `preview_stack_policy`, `preview_cap_sources`, `preview_combined_cap`, `get_disabled_global_cap_result`.
- `CAP_PRINCIPLES` allineati con STACK-A report: Collection ≤15 total / ≤5 category, Affinity PvP ≤2 source / ≤6 total, DW global ≤10 / PvP ≤5, **combined PvP target cap = 12%**, no multiplicative stacking initial.
- `preview_combined_cap(mock_sources, context)` esegue un clamping in-memoria *solo documentazionale* (`clamped_pct_preview`), mai applicato a combat.
- ADAPTER_MANIFEST conferma: `writes_to_db=false`, `imported_by_battle_engine=false`, `imported_by_battle_core=false`, `imported_by_combat_tsx=false`, `applied_to_combat=false`, `no_borea_activation=true`.

Audit 59/59 PASS (include verifica che i CAP_PRINCIPLES matchino con `cross_system_progression_stack_safety_report_v1.json`).

## 5. Canonical Axis Alias Helper (AXIS-B)

File creati:
- `/app/backend/data/canonical_axis_alias_helper.py`
- `/app/backend/scripts/audit_canonical_axis_alias_helper_safety.py`

Funzioni inerti: `get_axis_alias_map`, `normalize_element_axis`, `normalize_faction_axis`, `validate_axis_value`, `preview_axis_alignment`.

Mappings verificati:
- Elements: `darkness→dark` (aliased_to_live), `dark→dark` (live), `Oscurita→dark`, `shadow→dark`, `water→water`, `fire→fire`. Token sconosciuti → `status='unknown'`, no raise.
- Factions: `tides → status='design_pending'` (canonical=None, in_roster=False); `greek/japanese_yokai/celtic/…→live`; `yokai→japanese_yokai`, `beasts→creature_beast`, `celtics→celtic` (aliased_to_live).
- `validate_axis_value('darkness','element').valid=True`, `validate_axis_value('tides','faction').valid=False`.

Manifest conferma: `mutates_source_tables=false`, `patches_rm134b=false`, `patches_af2a=false`, helper non importato da `battle_engine.py`/`battle_core.py`/`combat.tsx`.

Source tables intatte: RM1.34-B contiene ancora `darkness` + `tides`; AF2-A gift draft usa ancora `dark` e non minta `tides_*`.

Audit 70/70 PASS.

## 6. Borea Safety

- `greek_borea`: catalog-only / hidden in `/api/heroes` (0 occorrenze), 200 su `/api/hero-skill-kits/catalogs/by-hero/greek_borea`.
- `borea` legacy: 404.
- `primordial_gaia` legacy: 404.
- Nessun artifact MEGA-COMBO-2 referenzia Borea per attivazione; tutti i record Borea-locked (`borea_locked=true` o equivalente).

## 7. Risultati Validator (questo task)

| Validator | Check | Risultato |
|---|---|---|
| CS2-C audit | 34 | PASS |
| AF2-C validator | 83 | PASS |
| STACK-B audit | 59 | PASS |
| AXIS-B audit | 70 | PASS |
| MEGA-COMBO-2 combo | 67 | PASS |

## 8. Risultati Suite + Baseline v5

`python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff`:

- Required: 14/14 PASS.
- Optional: 29/29 PASS (inclusi CS2-C, AF2-C, STACK-B, AXIS-B, MEGA-COMBO-2 appena registrati).
- Baseline diff RM1.32-PRE (v5): PASS.
- **Totale: 44 PASS / 0 FAIL / 0 MISS.**

## 9. API Smoke

| Endpoint | HTTP | Atteso |
|---|---|---|
| `/api/health` | 200 | OK |
| `/api/heroes` | 200 count=100 | OK ✓ invariant |
| `/api/synergies/v2/all` | 200 | OK public read-only |
| `/api/synergies/codex` | 401 | OK auth-gated |
| `/api/synergies/by_hero/greek_athena` | 401 | OK auth-gated |
| `/api/hero-skill-kits/catalogs/by-hero/greek_borea` | 200 | OK catalog-only |
| `/api/hero-skill-kits/catalogs/by-hero/borea` | 404 | OK forbidden alias |
| `/api/hero-skill-kits/catalogs/by-hero/primordial_gaia` | 404 | OK forbidden alias |
| `/api/divine-weapons/catalogs/summary` | 200 | OK |
| `/api/hero-skill-kits/runtime/debug/coverage` | 200 | OK inert |
| `/api/affinity/gifts` | 404 | OK (endpoint non creato — atteso) |

`/api/heroes` ID check: `borea`, `primordial_gaia`, `greek_borea` assenti.

## 10. UI Safety

Nessun file UI modificato o creato. CS2-C ha esplicitamente scelto strategia plan-only. Audit grep context-aware su `synergy-codex.tsx`, `hero-detail.tsx`, `hero-skill-kits-catalog.tsx`, `divine-weapons-catalog.tsx`: 0 mutazioni Collection/Affinity/Gift/Cap.

## 11. /api/heroes Safety

count=100, Borea variants hidden, baseline invariante.

## 12. Runtime / DB / Gacha / Roster / Catalog Safety

- Zero scritture DB.
- Zero mutazioni gacha/summon/roster.
- Zero mutazioni a `hero_skill_kits_5star_full_v1.json`, `hero_skill_kits_6star_borea_v1.json`, `boss_family_element_faction_matrix_v1.json` (`darkness`/`tides` ancora presenti, non patchati), `affinity_gift_catalog_faction_element_draft_v1.json` (usa `dark`, no `tides_*`), Divine Weapons catalog, status catalog, baseline v5.
- Zero nuovi import in `battle_engine.py`, `battle_core.py`, `combat.tsx`.
- Tutti i feature flag default OFF:
  - `SKILL_KIT_RUNTIME_ENABLED` ✓
  - `COLLECTION_SYNERGY_BATTLE_ENABLED` ✓
  - `AFFINITY_GIFT_RUNTIME_ENABLED` ✓
  - `GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED` ✓ (nuovo, default OFF)

## 13. Warning / Discrepanze

- **AXIS-B**: il helper rispetta la decisione AXIS-A: `darkness` viene aliased a `dark` solo via helper inerte (read-through), mentre la matrice sorgente RM1.34-B conserva `darkness` e `tides` fino a una controlled patch RM1.34-B-PATCH-A/B.
- **AF2-C**: nuovo vettore `tides_orphan_gift` aggiunto ai vettori di abuso documentati, mitigato dal vincolo schema `gift_id must exist in catalog AND faction != tides`.
- Nessun warning bloccante. Nessun falso positivo (regex adult context-aware riutilizzata da AF2-B).

## 14. Final Recommendation

Tutti gli acceptance criteria (1–20) soddisfatti. Lo stato rispetta gli invariants di sicurezza assoluti. Prima di qualsiasi attivazione runtime futura serve completare:

1. Inert helper STACK-B integrato dal futuro skeleton di battle integration (NOT in this task).
2. AXIS-B esposto a CS2-B / AF2 future resolver come read-through (NOT in this task).
3. AF2-C schema e anti-exploit ratificati prima della migration plan AF2-D.
4. CS2-C contratto ratificato prima dell'implementazione CS2-D (stub UI read-only).
5. Patches RM1.34-B-PATCH-A/B (controlled, futuri).
6. Unit test Borea-hidden invariant a livello runtime.
7. Rollback plan per ogni feature flag.

## 15. Suggested Next Tasks

- 🟡 **P2 — CS2-D**: implementare `/app/frontend/app/collection-synergies-preview.tsx` strictly read-only (no buttons), seguendo `collection_synergy_preview_screen_contract_v1.json`.
- 🟡 **P2 — AF2-D**: migration plan draft (ancora inerte) per le 3 collezioni AF2-C.
- 🟡 **P2 — AF2-E**: endpoint inerte read-only `/api/affinity/gifts` gated by `AFFINITY_PREVIEW_ENABLED` (default OFF).
- 🟡 **P2 — STACK-C**: unit test `preview_combined_cap` con scenari edge (sum > target, sum < target, empty sources, sources con pct negativo respinti).
- 🟡 **P2 — AXIS-C**: helper avanzato che aggrega caratteri da `/api/heroes` per popolare dinamicamente `_LIVE_ROSTER_*` invece dei set hardcoded.
- 🔵 **P3 — RM1.34-B-PATCH-A**: migrazione controllata `darkness→dark` + rebaseline.
- 🔵 **P3 — RM1.34-B-PATCH-B**: decisione `tides` (mint hero ufficiale o rimozione).
- 🔵 **P3 — Bug pre-esistenti**: hero-detail deep-link infinite-loading, hero-encyclopedia 404 senza `?hero_id=`, EXP curves mockate in `buildPostBattleSummary.ts`.
