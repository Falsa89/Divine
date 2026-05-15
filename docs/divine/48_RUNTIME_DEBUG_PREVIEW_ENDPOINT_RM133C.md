# RM1.33-C — Debug-only Read-Through Endpoint + Runtime Adapter Preview (OFF)

**Task:** RM1.33-C
**Date (UTC):** 2026-05-15
**Mode:** GET-only debug/read-through. Feature flag `SKILL_KIT_RUNTIME_ENABLED` **OFF**. **NO** mutation, **NO** runtime hookup, **NO** baseline change, **NO** UI change.

---

## 1. File creati (3)

| Path | Scopo |
|---|---|
| `/app/backend/routes/skill_kit_runtime_debug.py` | Route GET-only `/api/hero-skill-kits/runtime/debug/preview` (1 endpoint) |
| `/app/backend/scripts/audit_skill_kit_runtime_debug_endpoint_safety.py` | Safety audit endpoint RM1.33-C (10 sezioni) |
| `/app/docs/divine/48_RUNTIME_DEBUG_PREVIEW_ENDPOINT_RM133C.md` | Questo checkpoint |

## 2. File modificati (2, narrow)

| Path | Cambio |
|---|---|
| `/app/backend/game_systems.py` | Registrazione `register_skill_kit_runtime_debug_routes(router)` sotto `/api`. Solo 2 righe aggiunte (import + chiamata). |
| `/app/backend/data/skill_kit_cap_policy_adapter.py` | **Fix dual-import**: l'import di `is_skill_kit_runtime_enabled` ora supporta sia il path `from backend.data...` (script audit da `/app`) sia `from data...` (FastAPI da `/app/backend`). Nessun cambio di logica/safety. |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Aggiunta entry OPTIONAL `RM1.33-C → audit_skill_kit_runtime_debug_endpoint_safety.py`. |

Nessun catalogo / runtime / battle_engine / combat / battle_core / HP-bar / VFX / status / DW runtime / API esistenti / UI / .env / baseline modificato.

## 3. Endpoint summary

- **Path**: `GET /api/hero-skill-kits/runtime/debug/preview`
- **Metodo**: solo GET (verificato dall'audit: 0 occorrenze di POST/PUT/PATCH/DELETE nel file route)
- **Query params**:
  - `hero_id` (required)
  - `slot` (required)
  - `context` (optional, default `pve`; valori ammessi `pvp` | `boss` | `pve`)
- **Comportamento**:
  - 200 → ritorna `normalized_skill_slot` + `cap_policy_preview` + `runtime_candidate` + `safety_envelope` (+ `borea_preview` se hero_id == `greek_borea`)
  - 400 → `hero_id` o `slot` mancante / `context` invalido
  - 404 → `forbidden_legacy_hero_id` (aliases) | `hero_not_in_catalog` | `invalid_slot` (es. 5★ ultimate)
- **Safety envelope** in ogni risposta:
  ```
  debug_only=true, read_only=true, method=GET,
  runtime_enabled=false, applied_to_combat=false,
  runtime_attached=false, battle_runtime_attached=false,
  db_write=false, catalog_write=false, roster_write=false,
  gacha_write=false, ui_runtime_control=false,
  feature_flag_name=SKILL_KIT_RUNTIME_ENABLED,
  warning="Preview only. Not used by battle runtime."
  ```

## 4. Feature flag / runtime disabled summary

- `SKILL_KIT_RUNTIME_ENABLED` **OFF** in tutti i test (env assente). Token allowlist strict `"true_explicit_runtime_on"` mai impostato.
- Ogni risposta valida → `runtime_candidate.enabled=false`, `runtime_candidate.reason="feature_flag_off"`, `runtime_candidate.payload=null`, `runtime_attached=false`, `battle_runtime_attached=false`.
- Cap policy preview pvp/boss/pve → `enabled=false`, `applied_to_combat=false`, `runtime_attached=false`.
- Nessun esempio ha mai prodotto un payload runtime live.

## 5. Sample debug responses summary

| Query | HTTP | Note |
|---|---|---|
| `hero_id=greek_atalanta&slot=skill_2&context=pvp` | **200** | 5★ slot, runtime_candidate disabled, pvp cap policy inert |
| `hero_id=greek_athena&slot=ultimate&context=boss` | **200** | 6★ ultimate, `is_true_ultimate=true` preservato come preview meta, boss cap policy inert |
| `hero_id=greek_borea&slot=ultimate&context=pvp` | **200** | Borea **catalog-only** preview con `no_activation=true`, `release_group=launch_extra_premium`, `not_visible_in_heroes=true` |
| `hero_id=norse_eir&slot=skill_2&context=pve` | **200** | 5★ healer slot, pve cap policy inert |

Sample debug GETs (4/4): 200 + `runtime_candidate` disabled + `cap_policy_preview` inert.

## 6. Forbidden alias / invalid param results

| Scenario | HTTP | Detail.error |
|---|---|---|
| `hero_id=borea&slot=ultimate&context=pvp` | **404** | `forbidden_legacy_hero_id`, `fallback_disabled=true` |
| `hero_id=primordial_gaia&slot=skill_1&context=pvp` | **404** | `forbidden_legacy_hero_id`, `fallback_disabled=true` |
| `hero_id=greek_boreas&slot=skill_1&context=pvp` | **404** | `forbidden_legacy_hero_id`, `fallback_disabled=true` |
| `hero_id=olympian_borea&slot=skill_1&context=pvp` | **404** | `forbidden_legacy_hero_id`, `fallback_disabled=true` |
| `hero_id=greek_atalanta&slot=ultimate&context=pvp` | **404** | `invalid_slot`, `reason=invalid_slot_for_5star`, `fallback_disabled=true` |
| `slot=skill_1&context=pvp` (no hero_id) | **400** | `missing_param`, `param=hero_id` |
| `hero_id=greek_atalanta&context=pvp` (no slot) | **400** | `missing_param`, `param=slot` |
| `hero_id=greek_atalanta&slot=skill_1&context=garbage` | **400** | `invalid_context`, `allowed_contexts=[pvp,boss,pve]` |

**Nessun fallback automatico a `greek_borea`.** Nessun crash.

## 7. Endpoint safety audit

`audit_skill_kit_runtime_debug_endpoint_safety.py`: **PASS** (10/10 check OK):

1. ✓ Route file: GET-only (0 occorrenze POST/PUT/PATCH/DELETE)
2. ✓ Route file: 0 DB write patterns (`db.`, `insert_one`, `update_one`, `delete_one`, ecc.)
3. ✓ Route file: 0 catalog write patterns (`.write_text`, `json.dump`, ecc.)
4. ✓ Adapter/route isolation: `battle_engine.py`, `combat.tsx`, `battle_core.py` contengono 0 riferimenti
5. ✓ 4 sample debug GET → 200 + `runtime_candidate` disabled + cap policy inert
6. ✓ 4 forbidden aliases → 404 `forbidden_legacy_hero_id` + `fallback_disabled=true`
7. ✓ 5★ ultimate → 404 `invalid_slot_for_5star`
8. ✓ Missing hero_id / missing slot / invalid context → 400
9. ✓ `/api/heroes` count=100; borea/greek_borea/primordial_gaia hidden
10. ✓ Baseline v4 presente e identificabile
11. ✓ UI files: nessun riferimento al debug endpoint / adapter tokens

## 8. Validator / suite / baseline results

| Run | Esito |
|---|---|
| `audit_skill_kit_runtime_debug_endpoint_safety.py` (NEW) | **PASS** |
| `audit_skill_kit_runtime_adapter_wiretest.py` | **PASS** (178/178) |
| `audit_skill_kit_runtime_adapter_safety.py` | **PASS** |
| `validate_5star_balance_foundation.py` | **PASS** |
| `validate_6star_balance_foundation.py` | **PASS** |
| `audit_balance_foundation_boss_pvp_caps.py` | **PASS** (86 WARN, 0 FAIL) |
| `validate_hero_skill_kit_catalog_baseline_diff.py` (auto → v4) | **PASS** |
| `validate_status_resolver_contract.py` | **PASS** |
| `validate_divine_weapon_catalog.py` | **PASS** |
| `audit_divine_weapon_crosslinks.py` | **PASS** |
| Suite default | **PASS 18/18** |
| Suite `--include-baseline-diff` | **PASS 19/19 senza `--allow-changed` sotto v4** ✅ |

**Baseline v4 invariata.**

## 9. API smoke

| Endpoint | Atteso | Effettivo |
|---|---|---|
| `GET /api/health` | 200 | **200** |
| `GET /api/heroes` count | 100 | **100** ✓ |
| Borea / legacy borea / primordial_gaia hidden in `/api/heroes` | hidden | **hidden** ✓ |
| `GET /api/hero-skill-kits/catalogs/summary` | 200 | **200** |
| `GET …/5star` | 200 | **200** |
| `GET …/6star` | 200 | **200** |
| `GET …/by-hero/greek_atalanta` | 200 | **200** |
| `GET …/by-hero/greek_athena` | 200 | **200** |
| `GET …/by-hero/greek_borea` (catalog-only) | 200 | **200** |
| `GET …/by-hero/borea` | 404 | **404** ✓ |
| `GET …/by-hero/primordial_gaia` | 404 | **404** ✓ |
| `GET /api/divine-weapons/catalogs/summary` | 200 | **200** |
| `GET /api/divine-weapons/catalogs/by-hero/greek_borea` | 200 | **200** |
| **Debug** `/runtime/debug/preview?hero_id=greek_atalanta&slot=skill_2&context=pvp` | 200 | **200** |
| **Debug** `…?hero_id=greek_athena&slot=ultimate&context=boss` | 200 | **200** |
| **Debug** `…?hero_id=greek_borea&slot=ultimate&context=pvp` | 200 | **200** (catalog-only Borea preview) |
| **Debug** `…?hero_id=borea&slot=ultimate&context=pvp` | 404 | **404** ✓ |
| **Debug** `…?hero_id=greek_atalanta&slot=ultimate&context=pvp` | 404 | **404** ✓ |
| **Debug** missing hero_id | 400 | **400** ✓ |
| **Debug** invalid context | 400 | **400** ✓ |

## 10. UI safety

| File | mutation | runtime button | adapter/debug ref |
|---|---|---|---|
| `/app/frontend/app/hero-skill-kits-catalog.tsx` | 0 | 0 | 0 |
| `/app/frontend/app/divine-weapons-catalog.tsx` | 0 | 0 | 0 |

UI non modificata.

## 11. `/api/heroes` safety

Count = **100** ✓. `greek_borea`, legacy `borea`, `primordial_gaia` tutti **hidden**.

## 12. Borea / Marchio safety

- `greek_borea` resta `catalog_only`, `release_group=launch_extra_premium`, `runtime_attached=false`.
- Endpoint debug per `greek_borea` ritorna `borea_preview = { catalog_only: true, no_activation: true, borea_activation_allowed: false, not_visible_in_heroes: true, marchio_boreale_owner_only: true, release_group: "launch_extra_premium" }`.
- Marchio Boreale: 0 leak (verificato da audit precedenti); il preview cap policy dichiara `marchio_owner_hero_id=greek_borea`, `team_wide_amp_allowed=false`.

## 13. Runtime / DB / gacha / roster / catalog safety

- ❌ Nessuna modifica a `battle_engine.py`, `combat.tsx`, `battle_core.py`, HP bar / status / VFX / DW runtime, API esistenti, UI, DB, gacha, roster, Character Bible, assets, `final_numbers`, runtime flags, `divine_weapon_id`, `release_group`, hero_id, skill_id, nomi, descrizioni, status_ids, effect_tags, baseline files.
- ✅ Solo aggiunti: 1 route GET-only + 1 audit script + 1 doc + 2 entry orchestrali (game_systems include + suite optional) + 1 fix dual-import nell'adapter cap policy (preserva piena safety).
- ✅ Audit verifica esplicitamente che il file route NON contiene pattern di mutazione DB (`db.`, `insert_one`, `update_one`, `delete_one`, ecc.) né di scrittura file (`.write_text`, `json.dump`, ecc.).

## 14. Warning / discrepanze

- Fix dual-import in `skill_kit_cap_policy_adapter.py`: l'import precedente (`from backend.data...`) funzionava solo dagli script lanciati da `/app`, ma non quando FastAPI carica il modulo da `/app/backend`. Risolto con un blocco `try/except ImportError` che prova prima `backend.data.*`, poi `data.*`. Nessun cambio di logica/safety. Il wire-test e l'audit safety RM1.33-A continuano a passare invariati.

## 15. Final recommendation

**ACCEPTED.** Tutti i 23 criteri di accettazione di RM1.33-C soddisfatti:

1–3 Endpoint GET-only creato; 0 mutation methods ✅
4–6 Feature flag OFF; runtime candidate disabled in tutti i sample; cap policy inert ✅
7–8 Borea catalog-only/no activation; 4/4 forbidden aliases rejected ✅
9–10 5★ ultimate safely rejected; missing/invalid params → 400 ✅
11–12 Endpoint safety audit PASS; adapter wire-test ancora PASS ✅
13–14 Baseline diff PASS sotto v4; Suite PASS 19/19 ✅
15–16 API smoke PASS; UI safety PASS ✅
17–18 `/api/heroes`=100; Borea hidden ✅
19–22 Zero DB / catalog / battle_engine import / gacha-roster-Bible-assets ✅
23 Docs/checkpoint creato ✅

## 16. Suggested next tasks

1. 🟡 **P2 RM1.33-D — Test snapshot baseline** (raccomandato). Salvare in `/app/data/design/hero_skill_kits/runtime_adapter_disabled_payload_snapshot_v1.json` un fixture canonico del payload `runtime_candidate` disabled + di un `cap_policy_preview` per i 3 context, ancorato in CI: ogni futura PR che muta l'adapter dovrebbe regenerare e validare lo snapshot. Garantisce stabilità contrattuale dell'endpoint debug.
2. 🟢 **P3 RM1.32-C2 (opt)** — Trim numerici minimi foundation_draft per generare baseline v5 (rimasto in coda).
3. 🟢 **P3 RM1.34** — Boss family resistance/immunity table referenziando il delta plan RM1.32-C.
4. 🟢 **P3 RM1.33-E (opt)** — Debug-only endpoint per dump aggregate read-only (es. `/api/hero-skill-kits/runtime/debug/coverage`) che riporta lo stato del wire-test 178/178 come oggetto JSON consultabile via QA. Gated dal feature flag.

---

### Appendix — baseline chain (invariata)

```
v1 → v2 → v3 → v4 (CURRENT, intatta in RM1.33-C)
```

### Appendix — endpoint façade

```
              GET /api/hero-skill-kits/runtime/debug/preview
                            │
        ┌─────────────── validazione param (400) ───────────────┐
        │                                                        │
   forbidden alias (404)                              context invalido (400)
        │                                                        │
        └───────────── normalize_skill_slot ─────────────────────┘
                            │
        ┌───────── invalid_slot (404, no fallback) ──────────────┐
        │                                                        │
        └──── preview_cap_policy_for_skill (inert) ──────────────┘
                            │
        └──── get_skill_runtime_candidate → disabled (flag OFF) ─┘
                            │
              ┌─── safety_envelope (debug_only, read_only) ──────┐
              │                                                  │
              │   debug_only=true, read_only=true, GET,          │
              │   runtime_enabled=false,                         │
              │   applied_to_combat=false,                       │
              │   runtime_attached=false,                        │
              │   battle_runtime_attached=false,                 │
              │   db_write=false, catalog_write=false,           │
              │   roster_write=false, gacha_write=false,         │
              │   ui_runtime_control=false                       │
              │                                                  │
              └──────────────────────────────────────────────────┘
                            │
                            ▼
                       JSON 200 response
```
