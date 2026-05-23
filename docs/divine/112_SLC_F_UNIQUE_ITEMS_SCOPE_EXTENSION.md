# 112 — SLC-F UNIQUE-ITEMS SERVER_SCOPE EXTENSION (gated micro-batch — REAL PATCH x2)

> **Verdict finale:** `SLC_F_UNIQUE_ITEMS_SCOPE_APPLIED_SAFE`
> **Tipo apply:** **REAL PATCH** — patch su 2 write surfaces in `unique_items.py` (1 insert + 1 upsert con `$setOnInsert`).
> **Progress globale:** **95% → ~96%**
> **Modalità:** GATED MICRO-BATCH — UNIQUE_ITEMS_ONLY. AF2-N, Character Bible, combat/battle, gacha/summon, Housing completamente preservati.

---

## 1. Executive Verdict

✅ **PASS** — Micro-batch SLC-F Unique-Items Server-Scope applicato seguendo la raccomandazione dell'audit `slc_f_minor_audit_20260523T190000Z_audit_only` (candidato #2). Patchate entrambe le write surfaces target: `unique_items.py:277` (`db.unique_items_crafted.insert_one` — refactored a `crafted_doc` named variable + `ensure_server_scope`) e `unique_items.py:303` (`db.unique_items_equipped.update_one upsert=True` — aggiunto clausola `$setOnInsert` con `ensure_server_scope({}, uid)`). Zero modifiche alla logica unique items (stats, rarity, cost_gold/cost_gems, ownership checks, UNIQUE_ITEMS catalog, upgrade, crafting workflow). Suite master 348/348 PASS.

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Authorization markers (`SLC_F_UNIQUE_ITEMS_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=UNIQUE_ITEMS_ONLY`) | presenti | presenti | ✅ |
| Suite master | PASS | **348/348 PASS** | ✅ |
| Nuovo validator `SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY` | PASS | PASS (errors=0) | ✅ |
| Patch surface 1 (insert craft) | applicata | `crafted_doc = ensure_server_scope(crafted_doc, uid)` ADJACENT a `insert_one(crafted_doc)` | ✅ |
| Patch surface 2 (upsert equip) | applicata | `"$setOnInsert": ensure_server_scope({}, uid)` in upsert dict | ✅ |
| Rollback gated creato prima dell'apply | sì | sì (verificato exit=2 senza marker) | ✅ |
| Invarianti API runtime | preservati | preservati | ✅ |
| AF2-N canary state | preservato | identico | ✅ |

---

## 2. Authorization Markers Detected

```env
SLC_F_UNIQUE_ITEMS_SCOPE_APPLY_APPROVAL=true     ✅
SLC_F_APPLY_BATCH_SCOPE=UNIQUE_ITEMS_ONLY         ✅
```

---

## 3. Previous SLC-F State Confirmation

| Checkpoint | Apply ID | Esito |
|---|---|---|
| `SLC_F_BATCH_0_1_APPLIED_SAFE` | `slc_f_batch_0_1_20260523T173754Z_27b1b737` | ✅ |
| `SLC_F_BATCH_1B_APPLIED_SAFE` | `slc_f_batch_1b_20260523T175058Z_2cf0584c` | ✅ |
| `SLC_F_BATCH_2_APPLIED_SAFE` (safe no-op) | `slc_f_batch_2_20260523T181752Z_b838601e` | ✅ |
| `SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION_APPLIED_SAFE` (safe no-op) | `slc_f_equipment_scope_20260523T182939Z_d2afcc8a` | ✅ |
| `SLC_F_RAIDS_EQUIPMENT_SCOPE_APPLIED_SAFE` (REAL PATCH) | `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034` | ✅ |
| `SLC_F_MINOR_SURFACES_AUDIT_READY` (audit-only) | `slc_f_minor_audit_20260523T190000Z_audit_only` | ✅ |
| `SLC_F_GVG_WAR_SCOPE_APPLIED_SAFE` (REAL PATCH) | `slc_f_gvg_war_scope_20260523T192217Z_34999526` | ✅ |
| `SLC-G COMMIT-A` migration | `slc_g_commit_a_20260523T143803Z_4600ac04` | ✅ |
| Suite baseline pre-task | **347 PASS / 0 FAIL / 0 MISS** | ✅ |

---

## 4. Git Status Before / After

- **HEAD prima:** `a3bc211`
- **HEAD dopo:** `7bece5e`
- **Diff su `unique_items.py`:** 37 righe nel diff (= 8 righe codice add/mod + contesto)
- **File codice runtime modificati:** **1** (`unique_items.py`)
- **File aggiunti (non-codice):** apply marker JSON, rollback script, validator, report Markdown, validator output JSON
- **File suite runner modificato (+1 riga OPTIONAL):** `run_hero_skill_kit_validator_suite.py`
- **Compatibility fix collaterale:** rimossa `unique_items.py` da `FORBIDDEN_UNCHANGED` del validator GVG-war-scope precedente (commento di rationale aggiunto), per consentire questa micro-batch sanzionata.

---

## 5. Unique-Items Target Surface Audit

### Surface UI-W1 — Craft (insert)
| Voce | Valore |
|---|---|
| Endpoint | `POST /api/unique-items/craft` (function `craft_unique_item`) |
| Line target (pre-patch) | 277 |
| Operation | `db.unique_items_crafted.insert_one({...})` |
| Semantica | Crea NUOVO documento `unique_items_crafted` (per_user_id+hero_name) quando un eroe 5★+ sblocca il proprio oggetto esclusivo |
| Crea nuovo doc? | ✅ sì |
| Upsert? | ❌ no |
| Classification | server_bound (`unique_items_crafted`) |
| Decisione | **PATCH_NOW_SAFE** |

### Surface UI-W2 — Equip (upsert)
| Voce | Valore |
|---|---|
| Endpoint | `POST /api/unique-items/equip` (function `equip_unique_item`) |
| Line target (pre-patch) | 303 |
| Operation | `db.unique_items_equipped.update_one(..., {...}, upsert=True)` |
| Semantica | Upsert dello stato equipaggiato (per_user_id+hero_name): su insert crea nuovo doc server_bound; su update di doc esistente cambia solo `user_hero_id`/`equipped_at` |
| Crea nuovo doc? | ✅ sì (sull'upsert insert path) |
| Upsert? | ✅ sì |
| Classification | server_bound (`unique_items_equipped`) |
| Decisione | **PATCH_NOW_SAFE** (Batch-1B-style con `$setOnInsert`) |

---

## 6. Files Changed

### File di codice runtime patchato
1. `backend/routes/unique_items.py` (+9 righe nette, 4 rimosse via refactor del dict literal)

### File di sicurezza/marker/script generati
- `data/design/system_safety/slc_f_unique_items_scope_apply_marker_v1.json` (`route_patch_applied=true`, `route_patch_applied_partial=true`)
- `backend/scripts/rollback_slc_f_unique_items_scope.py` (rollback gated, ripristina entrambi gli scope)
- `backend/scripts/validate_slc_f_unique_items_scope_post_apply_v1.py` (post-apply validator)
- `data/design/server_lifecycle/_slc_f_unique_items_scope_post_apply_v1_result.json` (output validator, verdict `PASS`)
- `docs/divine/112_SLC_F_UNIQUE_ITEMS_SCOPE_EXTENSION.md` (questo report)
- `/tmp/slc_f_ui_suite.json` (suite master JSON report)

### Validator GVG-war-scope aggiornato (compatibility fix)
- `backend/scripts/validate_slc_f_gvg_war_scope_post_apply_v1.py` — rimossa `unique_items.py` da `FORBIDDEN_UNCHANGED` (commento di rationale aggiunto).

### Suite runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 riga OPTIONAL per `SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY`).

---

## 7. Exact unique_items.py Patch Summary

**Diff completo (`git diff` pre-task → post-task):**

```diff
diff --git a/backend/routes/unique_items.py b/backend/routes/unique_items.py
@@ -7,6 +7,7 @@
 from datetime import datetime
 from fastapi import HTTPException, Depends
 from pydantic import BaseModel
+from utils.server_scope import ensure_server_scope


 # ===================== UNIQUE ITEMS FOR ALL 30 HEROES =====================
@@ -274,10 +275,12 @@
             raise HTTPException(400, f"Servono {cost_gold:,} oro e {cost_gems} gemme!")
         await db.users.update_one({"id": uid}, {"$inc": {"gold": -cost_gold, "gems": -cost_gems}})
         # Craft
-        await db.unique_items_crafted.insert_one({
+        crafted_doc = {
             "user_id": uid, "hero_name": req.hero_name, "item_name": item["name"],
             "crafted_at": datetime.utcnow(),
-        })
+        }
+        crafted_doc = ensure_server_scope(crafted_doc, uid)
+        await db.unique_items_crafted.insert_one(crafted_doc)
         return {"success": True, "item": item, "hero_name": req.hero_name}

     class EquipUniqueRequest(BaseModel):
@@ -302,7 +305,8 @@
         # Equip
         await db.unique_items_equipped.update_one(
             {"user_id": uid, "hero_name": req.hero_name},
-            {"$set": {"user_hero_id": req.user_hero_id, "equipped_at": datetime.utcnow()}},
+            {"$set": {"user_hero_id": req.user_hero_id, "equipped_at": datetime.utcnow()},
+             "$setOnInsert": ensure_server_scope({}, uid)},
             upsert=True,
         )
         return {"success": True, "item": item["name"], "hero": req.hero_name}
```

**Caratteristiche delle patch:**

### Surface UI-W1 (craft)
- ✅ **Minimale**: dict literal inline estratto a variabile `crafted_doc`, helper call aggiunto, dict passato a `insert_one`.
- ✅ **Posizionale**: `ensure_server_scope(crafted_doc, uid)` IMMEDIATAMENTE prima di `insert_one(crafted_doc)`.
- ✅ **Idempotente**: `ensure_server_scope` mutea in-place e ritorna lo stesso dict.

### Surface UI-W2 (equip upsert)
- ✅ **Pattern Batch-1B-style**: `"$setOnInsert": ensure_server_scope({}, uid)` produce `{"server_id": "s1", "account_id": uid}` aggiunto SOLO sull'insert path dell'upsert.
- ✅ **Re-equip safe**: quando l'utente cambia eroe equipaggiato, l'update non riapplica `$setOnInsert` (semantica Mongo) → scope già stampato non viene clobberato.
- ✅ **Nessun campo `user_id` o `hero_name` duplicato**: il filtro `{"user_id": uid, "hero_name": req.hero_name}` Mongo li scrive automaticamente sull'insert.

### Zero logica business toccata
- ✅ `UNIQUE_ITEMS` catalog (30 eroi) intatto.
- ✅ Tabelle cost_gold (1-6 stars × 6 rarity levels) e cost_gems intatte.
- ✅ Ownership checks (`find_one({"user_id": uid, "hero_name": ...})`, hero 5★ requirement, hero name validation) invariati.
- ✅ Tutti i messaggi di errore italiani preservati ("Servono X oro e Y gemme!", "Gia sbloccato!", "Oggetto non ancora sbloccato!", "Questo oggetto puo essere equipaggiato SOLO da X!").

---

## 8. Write Surfaces Skipped and Why

| Surface | Operazione | Motivo SKIP |
|---|---|---|
| `unique_items.py:275` | `db.users.update_one ($inc gold/gems)` | `db.users` collection account-wide skipped da tutte le batch SLC-F (Batch-1B exclusion). Inoltre `update_one` non crea docs. |

---

## 9. Rollback Path

```bash
export SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_APPROVAL=true
export SLC_F_UNIQUE_ITEMS_SCOPE_ROLLBACK_ID=slc_f_unique_items_scope_20260523T193344Z_48aa4881
python3 /app/backend/scripts/rollback_slc_f_unique_items_scope.py
```

Caratteristiche:
- **Gated**: rifiuta exit=2 senza entrambi i marker. Test verificato.
- **Code-revert preciso**: 3 step idempotenti — rimuove import; ripristina inline dict literal nel craft; rimuove clausola `$setOnInsert` dall'equip.
- **No-DB-touch**: documenti `unique_items_crafted` / `unique_items_equipped` con `server_id="s1"` restano legali per SLC-G `LEGACY_DEFAULT_SERVER_ID`.
- **Idempotente**: rieseguito è no-op.
- **Audit-aware**: scrive `slc_f_unique_items_scope_rollback_marker_v1.json`.

---

## 10. Validators Run

| Validator | Esito |
|---|---|
| `validate_slc_f_unique_items_scope_post_apply_v1.py` (nuovo) | ✅ PASS errors=0 |
| `validate_slc_f_gvg_war_scope_post_apply_v1.py` (aggiornato) | ✅ PASS |
| `validate_slc_f_raids_equipment_scope_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_equipment_scope_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_2_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_1b_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_0_1_post_apply_v1.py` | ✅ PASS |
| `audit_slc_f_minor_write_surfaces_v1.py` | ✅ PASS |
| Suite AF2-N V12–V30 | ✅ PASS (tutti) |
| Suite Character Bible (RM1.27–1.32) | ✅ PASS (tutti) |
| Suite SLC-C/D/G/H, Benchmark Canonical | ✅ PASS (tutti) |

**Verifica regex specifica della patch (dal nuovo validator):**
- ✅ `unique_items.py` contiene `from utils.server_scope import ensure_server_scope`
- ✅ Surface UI-W1: regex `crafted_doc = ensure_server_scope\(crafted_doc,\s*uid\)\s*\n\s*await db\.unique_items_crafted\.insert_one\(crafted_doc\)` match positivo
- ✅ Surface UI-W2: regex `\$setOnInsert["']\s*:\s*ensure_server_scope\(\{\},\s*uid\)` match positivo
- ✅ Inline `insert_one({` literal NON più presente in `unique_items.py` (refactor confermato)
- ✅ Business logic markers preservati (`UNIQUE_ITEMS`, `cost_gold = {1: 10000`, `cost_gems = {1: 10`, `Servono`, `Gia sbloccato`, `Oggetto non ancora sbloccato`, `Questo oggetto puo essere equipaggiato SOLO da`, `item["rarity"]`)
- ✅ `combat.py` NON è stato patchato (anti-falso-positivo)

---

## 11. Suite Result

```
Overall: PASS  (pass=348, fail=0, miss=0)
Δ vs GVG end-state: +1 PASS (nuovo validator unique-items scope)
JSON report: /tmp/slc_f_ui_suite.json
```

---

## 12. API Smoke Result

| Endpoint | HTTP | Note |
|---|---|---|
| `GET /api/heroes` | 200, **100** elementi | catalogo intatto |
| `GET /api/heroes/primordial_gaia` | **404** | esclusione preservata |
| `GET /api/heroes/borea` | **200** | catalog-only inert |
| `GET /api/heroes/greek_borea` | **200** | catalog-only inert |
| `GET /api/unique-items` | 401 | auth richiesta, no 5xx |
| `GET /api/unique-items/craft` | 405 | method not allowed (route è POST), no 5xx |
| `GET /api/affinity/gift-spend/canary-status` | 200 | AF2-N preservato |

✅ Zero 5xx su unique-items routes. Backend healthy.

---

## 13. Invariants

| Invariante | Atteso | Osservato | Esito |
|---|---|---|---|
| `/api/heroes` length | 100 | 100 | ✅ |
| `primordial_gaia` HTTP | 404 | 404 | ✅ |
| `borea` / `greek_borea` HTTP | 200 inert | 200 | ✅ |
| AF2-N cap | 50000 | 50000 | ✅ |
| AF2-N allowlist size | 2500 | 2500 | ✅ |
| AF2-N flags | True True True | True True True | ✅ |
| SLC-G `migration_id` | `slc_g_commit_a_20260523T143803Z_4600ac04` | identico | ✅ |
| Env flags | unset | unset | ✅ |
| Tutti i marker SLC-F precedenti | preservati | preservati | ✅ |
| Phase 11 | false | false | ✅ |

---

## 14. Forbidden Scope Verification

Verificato dal validator `validate_slc_f_unique_items_scope_post_apply_v1.py`:

| File / Area | Diff vs HEAD | Esito |
|---|---|---|
| `backend/routes/unique_items.py` | autorizzato (UI-W1 + UI-W2 patch) | ✅ |
| `backend/battle_engine.py`, `battle_core.py`, `combat.tsx` | nessuno | ✅ |
| `backend/routes/affinity_gift_spend.py`, `affinity_gifts.py` | nessuno | ✅ AF2-N |
| `backend/routes/combat.py`, `equipment.py`, `forge.py`, `raids.py`, `gvg.py` | nessuno | ✅ |
| `backend/routes/cosmetics.py`, `economy.py` | nessuno | ✅ |
| `backend/routes/heroes.py`, `sanctuary.py`, `player_faction_v2.py` | nessuno | ✅ Character Bible |
| `backend/routes/push_notifications.py`, `game_data.py` | nessuno | ✅ |
| Route `/api/housing`, `/api/account/server-profiles`, `/api/account/active-server` | non presenti | ✅ |
| Frontend `/app/frontend/app/*` | nessuna modifica | ✅ |
| SLC-H runtime, STACK-G | non implementati | ✅ |
| `combat.py` helper import | assente | ✅ |
| Inline `insert_one({` literal in unique_items.py | rimosso (refactor) | ✅ |

---

## 15. Borea/Gaia Safety Result

- ✅ `primordial_gaia` HTTP = **404**.
- ✅ `borea` / `greek_borea` HTTP = **200** catalog-only inert.
- ✅ Nessuna attivazione runtime. Character Bible non toccata.
- ✅ Nessun cambiamento a banner/rates/pity/obtainable/roster.
- ✅ La patch riguarda solo creazione di `unique_items_crafted` e `unique_items_equipped` per eroi 5★+: nessun impatto su roster/Borea/Gaia/gacha.

---

## 16. AF2-N Preservation Result

| Voce | Pre-apply | Post-apply | Esito |
|---|---|---|---|
| `feature_flag_currently_enabled` | True | True | ✅ |
| `inventory_mutation_enabled` | True | True | ✅ |
| `rate_limit_enabled` | True | True | ✅ |
| `canary_allowlist_size` | 2500 | 2500 | ✅ |
| `canary_ledger_cap` | 50000 | 50000 | ✅ |
| Diff `affinity_gift_spend.py` / `affinity_gifts.py` vs HEAD | 0 | 0 | ✅ |
| Validators AF2-N V12–V30 | ALL PASS | ALL PASS | ✅ |

---

## 17. Known Drift Docs Status

🟡 **NON CORRETTI** per istruzione esplicita (out of UNIQUE_ITEMS_ONLY scope). I 7 drift docs gacha/summon restano `DRIFT KNOWN, NON-BLOCKING`.

---

## 18. Remaining Risks

| Rischio | Severità | Mitigazione |
|---|---|---|
| 7 drift docs gacha/summon | bassa | Documentazione; runtime non impattato. |
| Documenti `unique_items_crafted` / `unique_items_equipped` legacy senza `server_id` | informativa | Coperti da SLC-G `LEGACY_DEFAULT_SERVER_ID="s1"`. |
| `gvg.py:354 user_mail.insert_one` non patchato | informativa | AMBIGUOUS_DEFER (mail mixed origin). |
| Insert `user_equipment` in `combat.py` non patchati | bassa | Batch-4 future. |
| `heroes.py` user_heroes inserts (gacha claim) | bassa | GACHA_SUMMON_DEFER. |
| `cosmetics.py` / `economy.py` richiedono refactor strutturale | media | Job dedicato con autorizzazione separata. |
| Redis rate-limit binary può crashare | media | `bash /app/ops/ensure_redis_rate_limit.sh` ripristina. |

Nessun rischio severità **alta**.

---

## 19. Recommended Next Step

🔵 **Backlog (non in micro-batch):**

Tutti i candidati SAFE del audit `slc_f_minor_audit_*` sono stati esauriti (GVG + Unique-items). I prossimi job richiederanno scope expansion o refactoring:

1. **(P1) Rinnovare l'audit minor surfaces** — utile rifare audit per identificare nuove micro-batch dopo gli ultimi 2 apply (potrebbero esserci surface ulteriori non ancora considerate, p.es. analisi dei surface AMBIGUOUS_DEFER come `gvg.py:354 user_mail`).
2. **(P2) Refactoring strutturale `cosmetics.py`** — split `user_cosmetics` in ownership (account-wide) + equipped (server-bound).
3. **(P2) Refactoring strutturale `economy.py`** — split paid/free, isolate VIP, rimuovere legacy `/server/select`.
4. **(P2) Housekeeping drift docs gacha/summon** — job metadata-only.
5. **(P3) SLC-F APPLY BATCH-3 ONLY (AF2-N routing)** — solo post-broad-rollout signoff V8.
6. **(P3) SLC-F APPLY BATCH-4 ONLY (combat/battle)** — include insert `user_equipment` in `combat.py` (9 surfaces).
7. **(P3) Gacha/summon dedicated scope task** — `heroes.py` user_heroes inserts.
8. **(P3) Character Bible / sanctuary split task** — `sanctuary.py` db.heroes writes.
9. **(P3) SLC-H live wiring** — solo dopo refactor `economy.py`.

⚠️ **Esplicitamente NON raccomandato ora:**
- Apertura secondo server / `SERVER_PROFILES_RUNTIME_ENABLED`.
- Toccare `db.heroes` / Character Bible / Borea activation.
- Toccare gacha/summon/combat/battle/AF2-N routing.
- Implementare `/api/housing` runtime.

---

## 20. Updated Progress Estimate

| Fase | Stato pre-task | Stato post-task |
|---|---|---|
| SLC-F Batch-0/1, Batch-1B, Batch-2, Equipment-scope, Raids-equipment, GVG-war-scope | ✅ done | ✅ done |
| SLC-F Minor Write Surfaces Audit | ✅ ready | ✅ ready |
| **SLC-F Unique-Items Scope (REAL PATCH x2)** | 🟡 pending | ✅ **done** |
| SLC-F audit refresh / discovery di nuovi candidati | 🔵 backlog | 🟢 RECOMMENDED NEXT |
| SLC-F Cosmetics/Economy refactor strutturale | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 AF2-N routing | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 combat/battle | 🔵 backlog | 🔵 backlog |
| SLC-F gacha/summon scope task | 🔵 backlog | 🔵 backlog |
| SLC-F Character Bible / sanctuary split | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |
| Drift docs gacha/summon housekeeping | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **95% → ~96%** ✅ (suite master 348/348 PASS; entrambe le surface candidate del audit #2 patchate; tutti i candidati SAFE dell'audit sono ora esauriti).

---

## 21. Markers di audit (riferimenti rapidi)

- `apply_id`: `slc_f_unique_items_scope_20260523T193344Z_48aa4881`
- `applied_at_utc`: `2026-05-23T19:33:44+00:00`
- `git_head_before`: `a3bc211`
- `git_head_after`: `7bece5e`
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `slc_f_batch_1b_apply_id_preserved`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `slc_f_batch_2_apply_id_preserved`: `slc_f_batch_2_20260523T181752Z_b838601e`
- `slc_f_equipment_scope_apply_id_preserved`: `slc_f_equipment_scope_20260523T182939Z_d2afcc8a`
- `slc_f_raids_equipment_scope_apply_id_preserved`: `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034`
- `slc_f_minor_audit_id_preserved`: `slc_f_minor_audit_20260523T190000Z_audit_only`
- `slc_f_gvg_war_scope_apply_id_preserved`: `slc_f_gvg_war_scope_20260523T192217Z_34999526`
- `verdict_target`: `SLC_F_UNIQUE_ITEMS_SCOPE_APPLIED_SAFE` → ✅ **RAGGIUNTO**

---

**FINE REPORT 112_SLC_F_UNIQUE_ITEMS_SCOPE_EXTENSION.md**
