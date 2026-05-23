# 109 — SLC-F RAIDS EQUIPMENT SERVER_SCOPE EXTENSION (gated micro-batch — REAL PATCH APPLIED)

> **Verdict finale:** `SLC_F_RAIDS_EQUIPMENT_SCOPE_APPLIED_SAFE`
> **Tipo apply:** **REAL PATCH** (non no-op): +2 righe minimali su `raids.py` (1 import + 1 chiamata `ensure_server_scope` prima di `insert_one`).
> **Progress globale:** **93% → ~94%**
> **Modalità:** GATED MICRO-BATCH — RAIDS_EQUIPMENT_ONLY. AF2-N, Character Bible, combat/battle, gacha/summon, Housing completamente preservati.

---

## 1. Executive Verdict

✅ **PASS** — Il micro-batch SLC-F Raids Equipment Server-Scope Extension è stato applicato con successo. La surface bersaglio identificata (`craft_exclusive_item` in `raids.py`, dizionario `equip` immediatamente prima di `db.user_equipment.insert_one(equip)`) è stata patchata con `ensure_server_scope(equip, uid)` per stampare `server_id`/`account_id` con semantica set-only-if-missing sui nuovi documenti `user_equipment` esclusivi creati. Zero modifiche alla logica raid (cost, reward, drop, ranking, participation, damage, currency, ownership checks, item stats, rarity). Suite master 345/345 PASS.

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Authorization markers (`SLC_F_RAIDS_EQUIPMENT_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=RAIDS_EQUIPMENT_ONLY`) | presenti | presenti | ✅ |
| Suite master | PASS | **345/345 PASS** | ✅ |
| Nuovo validator `SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY` | PASS | PASS (errors=0) | ✅ |
| Pre-apply audit eseguito prima del code-change | sì | sì | ✅ |
| Patch minimale e contestuale (solo equip dict + insert_one) | sì | sì (+2 righe esatte) | ✅ |
| Rollback gated creato prima dell'apply | sì | sì (refuse exit=2 senza marker) | ✅ |
| Invarianti API runtime | preservati | preservati | ✅ |
| AF2-N canary state | preservato | identico (allowlist=2500, cap=50000) | ✅ |

---

## 2. Authorization Markers Detected

```env
SLC_F_RAIDS_EQUIPMENT_SCOPE_APPLY_APPROVAL=true   ✅
SLC_F_APPLY_BATCH_SCOPE=RAIDS_EQUIPMENT_ONLY       ✅
```

Forniti dall'utente nel messaggio di task.

---

## 3. Previous SLC-F State Confirmation

| Checkpoint | Apply ID | Esito |
|---|---|---|
| `SLC_F_BATCH_0_1_APPLIED_SAFE` | `slc_f_batch_0_1_20260523T173754Z_27b1b737` | ✅ marker presente |
| `SLC_F_BATCH_1B_APPLIED_SAFE` | `slc_f_batch_1b_20260523T175058Z_2cf0584c` | ✅ marker presente |
| `SLC_F_BATCH_2_APPLIED_SAFE` (safe no-op) | `slc_f_batch_2_20260523T181752Z_b838601e` | ✅ marker presente |
| `SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION_APPLIED_SAFE` (safe no-op) | `slc_f_equipment_scope_20260523T182939Z_d2afcc8a` | ✅ marker presente |
| `SLC-G COMMIT-A` migration | `slc_g_commit_a_20260523T143803Z_4600ac04` (`migration_applied=True`) | ✅ preservato |
| Helper `backend/utils/server_scope.py` | presente, exports `ensure_server_scope` + `LEGACY_DEFAULT_SERVER_ID="s1"` | ✅ |
| Suite baseline prima del task | **344 PASS / 0 FAIL / 0 MISS** | ✅ |

---

## 4. Git Status Before / After

- **HEAD prima del task:** `b8f1715`
- **HEAD dopo il task:** `1c991ec` (auto-commit per patch + marker + script + report + suite runner edit)
- **Diff su `backend/routes/raids.py` vs HEAD pre-task:** **2 righe aggiunte** (1 import + 1 call)
- **File codice runtime modificati:** **1** (`backend/routes/raids.py`)
- **File aggiunti (non-codice runtime):**
  - `data/design/system_safety/slc_f_raids_equipment_scope_apply_marker_v1.json`
  - `backend/scripts/rollback_slc_f_raids_equipment_scope.py`
  - `backend/scripts/validate_slc_f_raids_equipment_scope_post_apply_v1.py`
  - `docs/divine/109_SLC_F_RAIDS_EQUIPMENT_SCOPE_EXTENSION.md`
  - `data/design/server_lifecycle/_slc_f_raids_equipment_scope_post_apply_v1_result.json`
- **File suite runner modificato (+1 riga `OPTIONAL`):** `backend/scripts/run_hero_skill_kit_validator_suite.py`
- **Equipment-scope validator aggiornato (–1 voce in `FORBIDDEN_UNCHANGED`):** rimosso `backend/routes/raids.py` da `FORBIDDEN_UNCHANGED` del validator precedente con commento di rationale (raids.py ora sanzionato da successivo micro-batch gated).

---

## 5. Raids Target Surface Audit

| Voce | Valore |
|---|---|
| **File** | `/app/backend/routes/raids.py` |
| **Endpoint** | `POST /api/exclusive-items/craft` |
| **Function** | `craft_exclusive_item` |
| **Target dict (pre-patch)** | righe 142–149 (`equip = {...}`) |
| **Target insert (pre-patch)** | riga 150: `await db.user_equipment.insert_one(equip)` |
| **Operation** | `db.user_equipment.insert_one(equip)` |
| **Semantica** | Crea un NUOVO documento `user_equipment` per un Character-Exclusive Item appena craftato dall'utente. |
| **Crea nuovo doc?** | ✅ sì |
| **Upsert?** | ❌ no |
| **Classification** | server_bound (`user_equipment`) |
| **Decisione** | **PATCH_NOW_SAFE** |

**Confronto con Batch-1B `forge.py`:** identico pattern di applicazione (`ensure_server_scope(rune, uid)` immediatamente prima di `insert_one` su una collection server_bound `user_runes`). Stessa semantica `set-only-if-missing` via `$setOnInsert`-equivalente nel dict.

---

## 6. Files Changed

### File di codice runtime patchato
1. `backend/routes/raids.py` (+2 righe; 0 righe rimosse)

### File di sicurezza/marker/script generati
- `data/design/system_safety/slc_f_raids_equipment_scope_apply_marker_v1.json` (apply marker con `route_patch_applied=true`, `route_patch_applied_partial=true`, `route_patch_applied_full=false`)
- `backend/scripts/rollback_slc_f_raids_equipment_scope.py` (rollback gated, rimuove le 2 righe esatte)
- `backend/scripts/validate_slc_f_raids_equipment_scope_post_apply_v1.py` (post-apply validator)
- `data/design/server_lifecycle/_slc_f_raids_equipment_scope_post_apply_v1_result.json` (output validator, verdict `PASS`)
- `docs/divine/109_SLC_F_RAIDS_EQUIPMENT_SCOPE_EXTENSION.md` (questo report)
- `/tmp/slc_f_raids_suite.json` (suite master JSON report)

### Validator esistente aggiornato (compatibility fix)
- `backend/scripts/validate_slc_f_equipment_scope_post_apply_v1.py` — rimossa `backend/routes/raids.py` da `FORBIDDEN_UNCHANGED` (era ridondante e impediva la successiva micro-batch sanzionata; commento esplicativo aggiunto).

### Suite runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 riga `OPTIONAL` per `SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY`).

---

## 7. Exact raids.py Patch Summary

**Diff completo (`git diff` pre-task → post-task):**

```diff
diff --git a/backend/routes/raids.py b/backend/routes/raids.py
@@ -7,6 +7,7 @@
 from datetime import datetime
 from fastapi import HTTPException, Depends
 from pydantic import BaseModel
 from .game_data import RAID_BOSSES, EXCLUSIVE_ITEMS
+from utils.server_scope import ensure_server_scope


 def register_raids_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):
@@ -147,5 +148,6 @@
             "description": ei["item"].get("description", ""),
             "obtained_at": datetime.utcnow(),
         }
+        equip = ensure_server_scope(equip, uid)
         await db.user_equipment.insert_one(equip)
         return {"success": True, "item": equip}
```

**Caratteristiche della patch:**
- ✅ **Minimale**: solo 2 righe aggiunte; 0 righe rimosse; 0 righe modificate.
- ✅ **Posizionale**: la chiamata `ensure_server_scope(equip, uid)` è IMMEDIATAMENTE prima di `insert_one(equip)` (verificato dal regex del validator: `equip = ensure_server_scope\(equip,\s*uid\)\s*\n\s*await db\.user_equipment\.insert_one\(equip\)`).
- ✅ **Idempotente**: `ensure_server_scope` usa semantica set-only-if-missing, quindi se invocata su un dict che già ha `server_id`/`account_id` (non è il caso qui) sarebbe no-op.
- ✅ **Backward-compatible**: `LEGACY_DEFAULT_SERVER_ID="s1"` quindi tutti i documenti pre-esistenti restano leggibili.
- ✅ **Nessuna logica business toccata**: cost (gold/gems), rarity, slot, stats, ownership checks, EXCLUSIVE_ITEMS lookup, is_exclusive flag, exclusive_hero binding — tutto invariato.

---

## 8. Write Surfaces Skipped and Why

Il file `raids.py` contiene anche altre operazioni che sono state **deliberatamente lasciate intatte**:

| Area | Operazione | Motivo SKIP |
|---|---|---|
| `db.active_raids.find({})` | read-only list | Non scrive; nessun bisogno di scope. |
| `db.user_heroes.find(...)` | read-only check ownership | Non scrive. |
| `db.heroes.find(...)` | read-only catalog | Character Bible read; vietato toccare. |
| `db.users.find_one(...)` | read-only currency check | Non scrive. |
| `db.user_equipment.find_one(...)` | read-only existence check (line 133) | Non scrive. |
| `db.users.update_one({"id": uid}, {"$inc": ...})` (line 141) | `$inc` su currency su doc utente esistente | `db.users` è collection esplicitamente skipped in tutte le batch SLC-F precedenti (account-wide identity). Inoltre `update_one` non crea documenti, non serve scope helper. |

---

## 9. Rollback Path

```bash
export SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL=true
export SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_ID=slc_f_raids_equipment_scope_20260523T184512Z_a46a6034
python3 /app/backend/scripts/rollback_slc_f_raids_equipment_scope.py
```

Caratteristiche:
- **Gated**: rifiuta exit=2 senza entrambi i marker. Test verificato: senza marker risponde `REFUSED: SLC_F_RAIDS_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL must be set to "true"`.
- **Code-revert preciso**: rimuove esattamente le 2 righe aggiunte (l'import e la call) tramite `text.replace(..., '', 1)` sui pattern esatti.
- **No-DB-touch**: nessuna scrittura su MongoDB. I documenti `user_equipment` già creati con `server_id="s1"` resteranno legali per SLC-G `LEGACY_DEFAULT_SERVER_ID` policy.
- **Idempotente**: rieseguito è no-op.
- **Audit-aware**: scrive `slc_f_raids_equipment_scope_rollback_marker_v1.json` con timestamp e dettagli rimozione.

---

## 10. Validators Run

| Validator | Esito |
|---|---|
| `validate_slc_f_raids_equipment_scope_post_apply_v1.py` (nuovo) | ✅ PASS errors=0 |
| `validate_slc_f_equipment_scope_post_apply_v1.py` (aggiornato) | ✅ PASS |
| `validate_slc_f_batch_2_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_1b_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_0_1_post_apply_v1.py` | ✅ PASS |
| Suite AF2-N V12–V30 | ✅ PASS (tutti) |
| Suite Character Bible (RM1.27–1.32) | ✅ PASS (tutti) |
| Suite SLC-C/D/G/H | ✅ PASS (tutti) |
| Suite Benchmark Canonical | ✅ PASS (tutti) |

**Verifica regex specifica della patch (dal nuovo validator):**
- ✅ `raids.py` contiene `from utils.server_scope import ensure_server_scope`
- ✅ `raids.py` contiene `equip = ensure_server_scope(equip, uid)`
- ✅ La call è ADIACENTE all'`insert_one` (pattern regex `equip = ensure_server_scope\(equip,\s*uid\)\s*\n\s*await db\.user_equipment\.insert_one\(equip\)` match positivo)
- ✅ Markers di business logic preservati (`EXCLUSIVE_ITEMS`, `cost_gold = 20000`, `cost_gems = 50`, `is_exclusive`, `exclusive_hero`)
- ✅ `combat.py` NON è stato patchato (assenza di helper import)

---

## 11. Suite Result

```
Overall: PASS  (pass=345, fail=0, miss=0)
Δ vs Equipment-scope end-state: +1 PASS (nuovo validator raids equipment scope aggiunto)
JSON report: /tmp/slc_f_raids_suite.json
```

- Nessun FAIL.
- Nessun MISS.
- Nessun validator SUPERSEDED inatteso.

---

## 12. API Smoke Result

| Endpoint | HTTP | Note |
|---|---|---|
| `GET /api/heroes` | 200, **100** elementi | catalogo intatto |
| `GET /api/heroes/primordial_gaia` | **404** | esclusione preservata |
| `GET /api/heroes/borea` | **200** | catalog-only inert baseline |
| `GET /api/heroes/greek_borea` | **200** | catalog-only inert baseline |
| `GET /api/raids` | 401 | auth richiesta (read-only), no 5xx |
| `GET /api/affinity/gift-spend/canary-status` | 200 | AF2-N preservato (allowlist=2500, cap=50000) |

✅ Zero 5xx su raids routes. Zero regressioni di auth. Zero mutazioni DB esterne ai metadata scope sui nuovi insert.

---

## 13. Invariants

| Invariante | Atteso | Osservato | Esito |
|---|---|---|---|
| `/api/heroes` length | 100 | 100 | ✅ |
| `primordial_gaia` HTTP | 404 | 404 | ✅ |
| `borea` HTTP | 200 catalog-only inert | 200 | ✅ |
| `greek_borea` HTTP | 200 catalog-only inert | 200 | ✅ |
| AF2-N cap | 50000 | 50000 | ✅ |
| AF2-N allowlist size | 2500 | 2500 | ✅ |
| AF2-N feature_flag_currently_enabled | True | True | ✅ |
| AF2-N inventory_mutation_enabled | True | True | ✅ |
| AF2-N rate_limit_enabled | True | True | ✅ |
| SLC-G `migration_id` | `slc_g_commit_a_20260523T143803Z_4600ac04` | identico | ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset | unset | ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | unset | ✅ |
| Markers Batch-0/1, Batch-1B, Batch-2, Equipment-scope | preservati | preservati | ✅ |
| Phase 11 executed | false | false | ✅ |

---

## 14. Forbidden Scope Verification

Verificato dal validator `validate_slc_f_raids_equipment_scope_post_apply_v1.py`:

| File / Area | Diff vs HEAD | Esito |
|---|---|---|
| `backend/routes/raids.py` | 2 righe aggiunte (autorizzate) | ✅ apply controllato |
| `backend/battle_engine.py` | nessuno | ✅ |
| `backend/battle_core.py` | nessuno | ✅ |
| `frontend/app/combat.tsx` | nessuno | ✅ |
| `backend/routes/affinity_gift_spend.py` | nessuno | ✅ |
| `backend/routes/affinity_gifts.py` | nessuno | ✅ |
| `backend/routes/combat.py` | nessuno | ✅ (Batch-4 future) |
| `backend/routes/equipment.py` | nessuno | ✅ |
| `backend/routes/forge.py` | nessuno | ✅ (Batch-1B preservato) |
| `backend/routes/cosmetics.py` | nessuno | ✅ |
| `backend/routes/economy.py` | nessuno | ✅ |
| `backend/routes/push_notifications.py` | nessuno | ✅ |
| `backend/routes/game_data.py` | nessuno | ✅ |
| `backend/routes/heroes.py` | nessuno | ✅ |
| `backend/routes/sanctuary.py` | nessuno | ✅ (Character Bible) |
| `backend/routes/player_faction_v2.py` | nessuno | ✅ |
| Route `/api/housing` | non presente | ✅ |
| Route `/api/account/server-profiles` | non presente | ✅ |
| Route `/api/account/active-server` | non presente | ✅ |
| Frontend `/app/frontend/app/*` | nessuna modifica | ✅ |
| SLC-H runtime endpoints | non implementati | ✅ |
| STACK-G | non toccato | ✅ |

**Verifica anti-falso-positivo:** il validator controlla che `combat.py` NON contenga `from utils.server_scope import ensure_server_scope` ⇒ check passa ⇒ patch confinata a `raids.py`.

---

## 15. Borea/Gaia Safety Result

- ✅ `primordial_gaia` HTTP = **404** (esclusione storica preservata).
- ✅ `borea` HTTP = **200**, `greek_borea` HTTP = **200**, entrambi catalog-only inert.
- ✅ Nessuna attivazione runtime; nessun cambiamento a banner/rates/pity/obtainable/fragments/roster visibility.
- ✅ Character Bible (`sanctuary.py`, `db.heroes`) NON toccata.
- ✅ La patch su `raids.py` riguarda esclusivamente la creazione di documenti `user_equipment` (oggetti esclusivi craftati): nessun impatto su roster/Borea/Gaia.

---

## 16. AF2-N Preservation Result

| Voce | Pre-apply | Post-apply | Esito |
|---|---|---|---|
| `feature_flag_currently_enabled` | True | True | ✅ |
| `inventory_mutation_enabled` | True | True | ✅ |
| `rate_limit_enabled` | True | True | ✅ |
| `canary_allowlist_size` | 2500 | 2500 | ✅ |
| `canary_ledger_cap` | 50000 | 50000 | ✅ |
| Diff `affinity_gift_spend.py` vs HEAD | 0 | 0 | ✅ |
| Diff `affinity_gifts.py` vs HEAD | 0 | 0 | ✅ |
| Validators AF2-N V12–V30 | ALL PASS | ALL PASS | ✅ |

**Conclusione:** AF2-N **identico** allo stato pre-apply. Nessuna interferenza laterale.

---

## 17. Known Drift Docs Status

I 7 documenti di drift `user_heroes` da gacha/summon restano in stato **DRIFT KNOWN, NON-BLOCKING, NON CORRETTI** per istruzione esplicita del guardrail del pack.

- Non in scope `RAIDS_EQUIPMENT_ONLY`.
- Deferiti a job housekeeping documentale dedicato.

---

## 18. Remaining Risks

| Rischio | Severità | Mitigazione |
|---|---|---|
| 7 drift docs gacha/summon non corretti | bassa | Documentazione; runtime non impattato. |
| Documenti `user_equipment` legacy (creati prima della patch) senza `server_id` esplicito | informativa | Coperti da SLC-G `LEGACY_DEFAULT_SERVER_ID="s1"` fallback. Nessuna regressione runtime. |
| Insert `user_equipment` in `combat.py` (linee 87/140/232) non patchati | bassa | Batch-4 future (combat/battle). |
| Operazione `db.users.update_one` su currency in `craft_exclusive_item` (line 141) non patchata | informativa | `db.users` è collection account-wide esplicitamente skipped in tutte le batch SLC-F precedenti; corretto non toccarla. |
| Redis rate-limit binary può crashare nel container | media | `bash /app/ops/ensure_redis_rate_limit.sh` ripristina. |

Nessun rischio severità **alta** identificato.

---

## 19. Recommended Next Step

🔵 **Prossimi job possibili (NON in questo apply):**

1. **(P2) Cleanup pattern Batch-1B/raids consolidation** — audit di tutti gli `insert_one`/upsert su collection server-bound che NON contengono ancora `ensure_server_scope` (potrebbero esserci surface minori non ancora coperte).
2. **(P2) Refactoring strutturale `cosmetics.py`** — split ownership/equipped.
3. **(P2) Refactoring strutturale `economy.py`** — split paid/free currency, isolate VIP, rimuovere legacy `/server/select`.
4. **(P2) Housekeeping drift docs gacha/summon** — job metadata-only.
5. **(P3) SLC-F APPLY BATCH-3 ONLY (AF2-N routing)** — solo post-broad-rollout signoff V8.
6. **(P3) SLC-F APPLY BATCH-4 ONLY (combat/battle)** — include insert `user_equipment` in `combat.py`.
7. **(P3) SLC-H live wiring** — solo dopo refactoring `economy.py`.

⚠️ **Esplicitamente NON raccomandato ora:**
- Apertura secondo server / attivazione runtime `SERVER_PROFILES_RUNTIME_ENABLED`.
- Toccare `db.heroes` / Character Bible / Borea activation.
- Toccare gacha/summon/combat/battle/AF2-N routing.
- Implementare `/api/housing` runtime.

---

## 20. Updated Progress Estimate

| Fase | Stato pre-task | Stato post-task |
|---|---|---|
| SLC-F Design / Dry-run / Combo | ✅ done | ✅ done |
| SLC-F Apply Prep + Housing Addendum | ✅ done | ✅ done |
| SLC-F Batch-0/1 | ✅ done | ✅ done |
| SLC-F Batch-1B (7 route server_bound) | ✅ done | ✅ done |
| SLC-F Batch-2 (mixed/account-wide; safe no-op) | ✅ done | ✅ done |
| SLC-F Equipment-scope (safe no-op) | ✅ done | ✅ done |
| **SLC-F Raids-equipment-scope (REAL PATCH)** | 🟡 pending | ✅ **done** |
| SLC-F Cosmetics/Economy refactor strutturale | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 (AF2-N routing) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 (combat/battle, include insert user_equipment) | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |
| Drift docs gacha/summon housekeeping | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **93% → ~94%** ✅ (suite master 345/345 PASS; patch reale minima applicata; nessuna espansione di scope).

---

## 21. Markers di audit (riferimenti rapidi)

- `apply_id`: `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034`
- `applied_at_utc`: `2026-05-23T18:45:12+00:00`
- `git_head_before`: `b8f1715`
- `git_head_after`: `1c991ec`
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `slc_f_batch_1b_apply_id_preserved`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `slc_f_batch_2_apply_id_preserved`: `slc_f_batch_2_20260523T181752Z_b838601e`
- `slc_f_equipment_scope_apply_id_preserved`: `slc_f_equipment_scope_20260523T182939Z_d2afcc8a`
- `verdict_target`: `SLC_F_RAIDS_EQUIPMENT_SCOPE_APPLIED_SAFE` → ✅ **RAGGIUNTO**

---

**FINE REPORT 109_SLC_F_RAIDS_EQUIPMENT_SCOPE_EXTENSION.md**
