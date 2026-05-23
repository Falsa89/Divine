# 105 · SLC-F APPLY BATCH-0/1 ONLY — GATED ROUTE PATCH APPLY

## 1. Executive Verdict

> ## ✅ `SLC_F_BATCH_0_1_APPLIED_SAFE`

Primo apply gated controllato del route patch SLC-F, limitato esclusivamente
a **BATCH-0** (helper/resolver condivisi) e **BATCH-1** (route server-bound
low-risk, focalizzato su `hero_progression.py`).

**Progress**: 85% → **88%** ✅

---

## 2. Authorization markers detected

| Marker | Atteso | Rilevato |
|---|---|---|
| `SLC_F_ROUTE_PATCH_APPLY_APPROVAL` | `true` | ✅ presente nel prompt |
| `SLC_F_APPLY_BATCH_SCOPE` | `BATCH_0_1_ONLY` | ✅ presente nel prompt |

`SLC_F_WRITE_GATE_EXPLICIT_APPROVAL` non confuso con marker SLC-G migration
commit (separato e già acquisito in task precedente).

---

## 3. Git status before / after

| | Value |
|---|---|
| HEAD before | `c382e25` |
| Files in scope toccati | 2 (helper nuovo + 1 route patched) |
| Forbidden files diff lines | **0** (battle_engine, battle_core, combat.tsx, affinity_gift_spend, heroes, combat) |

---

## 4. Files changed

| File | Tipo | LOC delta |
|---|---|---|
| `backend/utils/server_scope.py` | **NEW** (Batch-0 helper) | +105 |
| `backend/routes/hero_progression.py` | **MODIFIED** (Batch-1) | 4 helper-call insertions + 2 `$setOnInsert` |

Tutte le modifiche sono **purely additive** (set-only-if-missing). Nessun
campo esistente sovrascritto. Nessuna funzione esistente rimossa o rinominata.

---

## 5. Routes patched

Solo la route family **`hero_progression`** (file `backend/routes/hero_progression.py`).

| Endpoint patchato | Tipo write | Collection target | Patch semantics |
|---|---|---|---|
| `GET /api/hero-progression/fragments` (initial insert) | `insert_one` | `user_fragments` | `ensure_server_scope(doc, uid)` |
| `POST /api/hero-progression/fragments/combine` | `insert_one` | `user_heroes` | `ensure_server_scope(doc, uid)` |
| `POST /api/hero-progression/fragments/add` | `update_one` (upsert) | `user_fragments` | `$setOnInsert: server_id=s1, account_id=uid` |
| `GET /api/hero-progression/materials` (initial insert) | `insert_one` | `user_materials` | `ensure_server_scope(doc, uid)` |
| `POST /api/hero-progression/materials/buy` | `update_one` (upsert) | `user_materials` | `$setOnInsert: server_id=s1, account_id=uid` |

Tutte le 5 modifiche sono **set-only-if-missing** e **idempotenti**.

---

## 6. Batch classification proof

| Verifica | Risultato |
|---|---|
| `hero_progression.py` classified `server_bound` in `slc_f_route_scope_inventory_v1.json` | ✅ (`scope=server_bound`, `server_id_required_future=true`) |
| `hero_progression.py` NOT in `protected_route_files_no_diff_required` | ✅ |
| Nessuna modifica a file in `protected_route_files_no_diff_required` | ✅ (5/5 forbidden files: 0 diff lines) |
| Nessuna route Batch-2 (mixed/account-wide) toccata | ✅ (users, cosmetics, economy intatti) |
| Nessuna route Batch-3 (AF2-N) toccata | ✅ (`affinity_gift_spend.py`, `affinity_gifts.py` intatti) |
| Nessuna route Batch-4 (combat/battle) toccata | ✅ (`combat.py`, `battle_engine.py`, `battle_core.py`, `combat.tsx` intatti) |

---

## 7. Rollback path

**Script**: `/app/backend/scripts/rollback_slc_f_batch_0_1.py`

**Apply ID**: `slc_f_batch_0_1_20260523T173754Z_27b1b737`

**Gating env vars** (entrambi obbligatori):
```bash
SLC_F_BATCH_0_1_ROLLBACK_APPROVAL=true
SLC_F_BATCH_0_1_ROLLBACK_ID=slc_f_batch_0_1_20260523T173754Z_27b1b737
```

**Strategia rollback**:
1. `git checkout c382e25 -- backend/routes/hero_progression.py` (revert al pre-apply HEAD)
2. `unlink backend/utils/server_scope.py` (file non esisteva pre-apply)
3. `unlink slc_f_batch_0_1_apply_marker_v1.json`
4. `sudo supervisorctl restart backend`
5. Verifica smoke API

Lo script NON gira automaticamente: refuse-by-default in assenza di env vars.

---

## 8. Validators run

| Validator | Verdict |
|---|---|
| `SLC-F-BATCH-0-1-POST-APPLY` | ✅ PASS (registered as OPTIONAL in suite) |
| `SLC-F-APPLY-PREP-STAGED-PLAN` | ✅ PASS |
| `SLC-F-APPLY-READINESS-GATES` | ✅ PASS |
| `SLC-F-APPLY-PREP-HOUSING-ADDENDUM-COMBO` | ✅ PASS |
| `HOUSING-DIMORA-DIVINA-V2` | ✅ PASS |
| `DIMORA-DIVINA-RUNTIME-SAFETY-AUDIT` | ✅ PASS |
| `SLC-G-COMMIT-A-POST-APPLY` | ✅ PASS (migration_applied invariato) |
| `SLC-H-COMBO` | ✅ PASS (NO runtime route SLC-H registrata) |
| Hero skill kit catalog baseline diff RM1.32-PRE | ✅ PASS |

---

## 9. Suite result

```
RM1.31-B — Hero Skill Kit Validator Suite Runner
Overall: PASS  (pass=341, fail=0, miss=0)
JSON report: /app/backend/reports/slc_f_batch_0_1_suite_run.json
```

Delta vs pre-task: **340 → 341** (+1 OPTIONAL `SLC-F-BATCH-0-1-POST-APPLY`).

---

## 10. API smoke result

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` | 200, count=100 | **200, 100** ✅ |
| `GET /api/heroes/primordial_gaia` | 404 | **404** ✅ |
| `GET /api/heroes/borea` | 200 catalog-only inert | **200** ✅ |
| `GET /api/heroes/greek_borea` | 200 catalog-only inert | **200** ✅ |

Nessun 5xx. Nessuna auth regression. Backend ha hot-reloaded correttamente
con il nuovo import + helper module.

---

## 11. Invariants

| Invariant | Valore |
|---|---|
| `/api/heroes` count | **100** ✅ |
| `primordial_gaia` HTTP | **404** ✅ |
| `borea` HTTP | **200** ✅ |
| `greek_borea` HTTP | **200** ✅ |
| AF2-N cap | **50000** ✅ |
| AF2-N allowlist | **2500** ✅ |
| AF2-N `user_gift_inventory` rows | **2500** ✅ (preserved) |
| AF2-N `gift_transaction_ledger` rows | **502** ✅ (preserved) |
| AF2-N `user_affinity_state` rows | **1914** ✅ (preserved) |
| SLC-G `migration_applied` | **true** (immutato) ✅ |
| SLC-G `migration_id` | `slc_g_commit_a_20260523T143803Z_4600ac04` (immutato) ✅ |
| `route_patch_applied` (full) | **false** ✅ |
| `route_patch_applied_partial` | **true** (Batch-0/1 solo) |
| `second_server_opening_allowed` | **false** ✅ |
| `phase_11_executed` | **false** ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | **unset** ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | **unset** ✅ |
| Housing `runtime_implemented` | **false** ✅ |
| Housing `ui_implemented` | **false** ✅ |
| `active_bonus_resolver_implemented` | **false** ✅ |
| Baseline diff RM1.32-PRE | **PASS** ✅ |

---

## 12. Forbidden scope verification

| Forbidden | Verifica | Risultato |
|---|---|---|
| BATCH-2 mixed/account-wide | `users`/`economy`/`cosmetics` files diff | **0 diff lines** ✅ |
| BATCH-3 AF2-N | `affinity_gift_spend.py`/`affinity_gifts.py` diff | **0 diff lines** ✅ |
| BATCH-4 combat/battle | `combat.py`/`battle_engine.py`/`battle_core.py`/`combat.tsx` diff | **0 diff lines** ✅ |
| SLC-H live wiring | grep `/api/servers`/`/api/account/server-profiles`/`/api/account/active-server` in routes | **0 match** ✅ |
| Second server opening | `SECOND_SERVER_OPENING_ENABLED` env | **unset** ✅ |
| Feature flag enable | `SERVER_PROFILES_RUNTIME_ENABLED` env | **unset** ✅ |
| Phase 11 | n/a (non eseguito) | ✅ |
| Fallback removal | `LEGACY_DEFAULT_SERVER_ID` ancora `s1` | ✅ |
| UI | nessun file in `frontend/app/` modificato | ✅ |
| Housing runtime | `audit_dimora_divina_runtime_safety_v1.py` | **PASS** ✅ |
| `/api/housing` route | grep su routes | **0 match** ✅ |
| HousingBonusResolver | grep su routes + server.py | **0 match** ✅ |
| Broad rollout | n/a (apply scope = singolo file) | ✅ |
| Public spend UI | n/a (no UI change) | ✅ |
| STACK-G | n/a (non toccato) | ✅ |
| Combat routing | `combat.py` diff | **0 diff lines** ✅ |
| Battle routing | `battle_engine.py`/`battle_core.py` diff | **0 diff lines** ✅ |
| Gacha/summon routing | n/a (non in scope Batch-1) | ✅ |
| Affinity gift spend changes | `affinity_gift_spend.py` diff | **0 diff lines** ✅ |
| Borea activation | catalog/visibility flag invariati | ✅ (verified via baseline diff + smoke) |

---

## 13. Borea / Gaia safety result

| Check | Risultato |
|---|---|
| `primordial_gaia` HTTP | **404** ✅ (nascosto come da invariante storica) |
| `borea` HTTP | **200** (catalog-only inert) ✅ |
| `greek_borea` HTTP | **200** (catalog-only inert) ✅ |
| Borea ancora `is_official=false`, `is_legacy_placeholder=true`, `obtainable=false`, `show_in_catalog=false`, `show_in_summon=false`, `show_in_battle_picker="owned_only"` | ✅ (verified via response body) |
| `greek_borea` ancora `is_official=true` ma `obtainable=false`, `show_in_catalog=false`, `show_in_summon=false`, `show_in_battle_picker=false`, `do_not_expose_until_assets_ready=true` | ✅ |
| Character Bible non toccato | ✅ (`backend/routes/heroes.py` 0 diff lines) |

---

## 14. AF2-N preservation result

| Metrica | Pre-apply | Post-apply |
|---|---|---|
| `user_gift_inventory` rows | 2500 | **2500** ✅ |
| `gift_transaction_ledger` rows | 502 | **502** ✅ |
| `user_affinity_state` rows | 1914 | **1914** ✅ |
| `affinity_gift_spend.py` diff lines | 0 | **0** ✅ |
| `affinity_gifts.py` diff lines | 0 | **0** ✅ |
| AF2-N cap | 50000 | **50000** ✅ |
| AF2-N allowlist | 2500 | **2500** ✅ |

---

## 15. Remaining risks

1. **Post-commit drift in altre route**: 7 docs in `user_heroes` creati DOPO il commit-A da route ancora non patchate (gacha/summon non in scope Batch-1). Saranno coperti quando un Batch-1B futuro estenderà il pattern a quelle route (con autorizzazione separata).
2. **Helper module è additivo ma usato in 1 solo file**: il pattern `ensure_server_scope` è disponibile globalmente ma per ora chiamato solo da `hero_progression.py`. Ogni nuova route patched in Batch-1B importerà lo stesso helper, mantenendo coerenza.
3. **Idempotenza apply script**: rerun del comando apply non è stato testato (deliberatamente — questa è la prima e unica applicazione di Batch-0/1). Se richiesto si può creare un test specifico in task futuro.
4. **Drift docs storici**: i 7 docs senza `_slc_g_commit_marker` non vengono toccati da questo patch (è write-time, non backfill). Per pulirli serve un ulteriore mini-cleanup come SLC-G-GUILDS-UNSAFE-CLEANUP-B ma per `user_heroes`. Non bloccante.

---

## 16. Recommended next step

**Batch-1B**: estendere il pattern `ensure_server_scope` ad altre route server-bound low-risk:
- `items.py` (inventory)
- `forge.py`
- `achievements.py`
- `level_sharing.py`
- `social.py`
- `player_faction_v2.py`
- `soul_forge.py`
- `artifacts.py`
- `sanctuary.py` (con Borea guard verification)
- `guild.py`

Stessa autorizzazione, scope esteso. Marker richiesti:
- `SLC_F_ROUTE_PATCH_APPLY_APPROVAL=true`
- `SLC_F_APPLY_BATCH_SCOPE=BATCH_1_EXTENSION_ONLY` (o equivalente)

In alternativa: cleanup mini-target per i 7 drift docs user_heroes prima di estendere il pattern.

---

## 17. Updated progress estimate

| Phase | Status | Progress |
|---|---|---|
| Pre-task baseline | Completata | 85% |
| **SLC-F BATCH-0 + Batch-1 (hero_progression.py)** | ✅ **APPLIED_SAFE** | **88%** |
| Restante: Batch-1B extension, Batch-2, Batch-3 plan-only, Batch-4 plan-only, SLC-H live, Housing runtime, Phase 11 | NOT_APPLIED (gated) | 12% |

**Current progress estimate: 88%** ✅ (in linea con spec)

---

## Riepilogo guardrail rispettati

- ✅ Solo 2 file in scope autorizzato modificati
- ✅ Forbidden files: 0 diff lines su tutti i 5+ file protetti
- ✅ Nessuna route forbidden (`/api/housing`, `/api/servers`, ...) registrata
- ✅ Feature flags ancora unset
- ✅ AF2-N invariants preservate al byte
- ✅ Borea/Gaia safety preservato
- ✅ Character Bible non toccato
- ✅ Battle/combat/gacha/summon non toccati
- ✅ Housing runtime/UI/resolver non implementati
- ✅ Rollback creato e gated PRIMA dell'apply
- ✅ Suite globale PASS senza regressioni
- ✅ Migration_id SLC-G preservato verbatim

**Verdict finale: `SLC_F_BATCH_0_1_APPLIED_SAFE`** ✅
