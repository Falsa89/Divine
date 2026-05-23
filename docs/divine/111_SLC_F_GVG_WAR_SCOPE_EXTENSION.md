# 111 — SLC-F GVG WAR INSERT SERVER_SCOPE EXTENSION (gated micro-batch — REAL PATCH)

> **Verdict finale:** `SLC_F_GVG_WAR_SCOPE_APPLIED_SAFE`
> **Tipo apply:** **REAL PATCH** (non no-op): +2 righe minimali su `gvg.py` (1 import + 1 chiamata `ensure_server_scope` prima di `insert_one`).
> **Progress globale:** **94% → ~95%**
> **Modalità:** GATED MICRO-BATCH — GVG_WAR_ONLY. AF2-N, Character Bible, combat/battle, gacha/summon, Housing completamente preservati.

---

## 1. Executive Verdict

✅ **PASS** — Micro-batch GVG War Insert Server-Scope applicato con successo seguendo la raccomandazione dell'audit `slc_f_minor_audit_20260523T190000Z_audit_only` (candidato #1 highest priority). La surface bersaglio (`gvg_matchmake` in `gvg.py`, dizionario `war` immediatamente prima di `db.gvg_wars.insert_one(war)`) è stata patchata con `ensure_server_scope(war, current_user["id"])` per stampare `server_id`/`account_id` set-only-if-missing sui nuovi documenti `gvg_wars` creati. Zero modifiche alla logica GvG (matching, ranking, scoring, rewards, participants, defenders, attackers, bot guild simulation). Suite master 347/347 PASS.

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Authorization markers (`SLC_F_GVG_WAR_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=GVG_WAR_ONLY`) | presenti | presenti | ✅ |
| Suite master | PASS | **347/347 PASS** | ✅ |
| Nuovo validator `SLC-F-GVG-WAR-SCOPE-POST-APPLY` | PASS | PASS (errors=0) | ✅ |
| Pre-apply audit eseguito prima del code-change | sì | sì | ✅ |
| Patch minimale contestuale (solo `war` dict + `insert_one`) | sì | sì (+2 righe esatte) | ✅ |
| Rollback gated creato prima dell'apply | sì | sì (verificato exit=2 senza marker) | ✅ |
| Invarianti API runtime | preservati | preservati | ✅ |
| AF2-N canary state | preservato | identico (allowlist=2500, cap=50000) | ✅ |
| `user_mail.insert_one` (gvg.py:354) NON toccato | sì | sì (count=1 invariato, no helper adjacent) | ✅ |

---

## 2. Authorization Markers Detected

```env
SLC_F_GVG_WAR_SCOPE_APPLY_APPROVAL=true     ✅
SLC_F_APPLY_BATCH_SCOPE=GVG_WAR_ONLY         ✅
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
| `SLC-G COMMIT-A` migration | `slc_g_commit_a_20260523T143803Z_4600ac04` | ✅ |
| Suite baseline pre-task | **346 PASS / 0 FAIL / 0 MISS** | ✅ |

---

## 4. Git Status Before / After

- **HEAD prima:** `1c991ec`
- **HEAD dopo:** `a3bc211` (auto-commit per patch + marker + script + report + suite runner edit)
- **Diff su `backend/routes/gvg.py`:** **2 righe aggiunte** (1 import + 1 call); 0 rimosse; 0 modificate
- **File codice runtime modificati:** **1** (`backend/routes/gvg.py`)
- **File aggiunti (non-codice):**
  - `data/design/system_safety/slc_f_gvg_war_scope_apply_marker_v1.json`
  - `backend/scripts/rollback_slc_f_gvg_war_scope.py`
  - `backend/scripts/validate_slc_f_gvg_war_scope_post_apply_v1.py`
  - `docs/divine/111_SLC_F_GVG_WAR_SCOPE_EXTENSION.md`
  - `data/design/server_lifecycle/_slc_f_gvg_war_scope_post_apply_v1_result.json`
- **File suite runner modificato (+1 riga OPTIONAL):** `backend/scripts/run_hero_skill_kit_validator_suite.py`

---

## 5. GVG Target Surface Audit

| Voce | Valore |
|---|---|
| **File** | `/app/backend/routes/gvg.py` |
| **Endpoint** | `POST /api/gvg/matchmake` |
| **Function** | `gvg_matchmake` |
| **Target dict (pre-patch)** | righe 176–189 (`war = {...}`) |
| **Target insert (pre-patch)** | riga 190: `await db.gvg_wars.insert_one(war)` |
| **Operation** | `db.gvg_wars.insert_one(war)` |
| **Semantica** | Crea NUOVO documento `gvg_wars` (match GvG tra due gilde — ID, guild_a/b, scores, attacks, status, winner) |
| **Crea nuovo doc?** | ✅ sì |
| **Upsert?** | ❌ no |
| **Classification** | server_bound (`gvg_wars`) — match scoped al server context |
| **Decisione** | **PATCH_NOW_SAFE** |

Pattern **identico** al precedente `slc_f_raids_equipment_scope_*` micro-batch.

---

## 6. Files Changed

### File di codice runtime patchato
1. `backend/routes/gvg.py` (+2 righe; 0 rimosse)

### File di sicurezza/marker/script generati
- `data/design/system_safety/slc_f_gvg_war_scope_apply_marker_v1.json` (`route_patch_applied=true`, `route_patch_applied_partial=true`, `route_patch_applied_full=false`)
- `backend/scripts/rollback_slc_f_gvg_war_scope.py` (rollback gated)
- `backend/scripts/validate_slc_f_gvg_war_scope_post_apply_v1.py` (post-apply validator)
- `data/design/server_lifecycle/_slc_f_gvg_war_scope_post_apply_v1_result.json` (output validator, verdict `PASS`)
- `docs/divine/111_SLC_F_GVG_WAR_SCOPE_EXTENSION.md` (questo report)
- `/tmp/slc_f_gvg_suite.json` (suite master JSON report)

### Suite runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 riga OPTIONAL per `SLC-F-GVG-WAR-SCOPE-POST-APPLY`).

---

## 7. Exact gvg.py Patch Summary

**Diff completo (`git diff` pre-task → post-task):**

```diff
diff --git a/backend/routes/gvg.py b/backend/routes/gvg.py
@@ -6,6 +6,7 @@
 from datetime import datetime, timedelta
 from fastapi import HTTPException, Depends
 from pydantic import BaseModel
+from utils.server_scope import ensure_server_scope


 def register_gvg_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):
@@ -187,6 +188,7 @@
             "created_at": datetime.utcnow(),
             "winner_guild_id": None,
         }
+        war = ensure_server_scope(war, current_user["id"])
         await db.gvg_wars.insert_one(war)

         # If opponent is a real guild, simulate some initial attacks from bot members
```

**Caratteristiche della patch:**
- ✅ **Minimale**: solo 2 righe aggiunte; 0 righe rimosse; 0 righe modificate.
- ✅ **Posizionale**: la chiamata `ensure_server_scope(war, current_user["id"])` è IMMEDIATAMENTE prima di `insert_one(war)` (verificato dal regex del validator).
- ✅ **Inline user-id**: usato `current_user["id"]` direttamente perché in `gvg_matchmake` non era definito `uid` (a differenza di `raids.py` dove era già presente). Nessuna variabile aggiuntiva introdotta.
- ✅ **Idempotente**: `ensure_server_scope` usa semantica set-only-if-missing.
- ✅ **Backward-compatible**: SLC-G `LEGACY_DEFAULT_SERVER_ID="s1"` mantiene i documenti pre-esistenti leggibili.
- ✅ **Nessuna logica business toccata**: tutti i campi del war doc (`guild_a_id`, `guild_b_id`, `guild_a_score`, `guild_b_score`, `guild_a_attacks`, `guild_b_attacks`, `winner_guild_id`, `is_bot_guild`, status, created_at) sono invariati. Matching algorithm intatto. Bot guild simulation intatta.

---

## 8. Write Surfaces Skipped and Why

Il file `gvg.py` contiene altre operazioni di scrittura che sono state **deliberatamente lasciate intatte**:

| Surface | Operazione | Motivo SKIP |
|---|---|---|
| `gvg.py:201` | `db.gvg_wars.update_one` (bot initial attacks) | `update_one` su doc appena creato; no new doc; no metadata da iniettare. |
| `gvg.py:280+` | `db.gvg_wars.update_one` (attack scoring durante la guerra) | `update_one` su doc esistente. |
| `gvg.py:340+` | `db.gvg_wars.update_one` (war end, winner determination) | `update_one` su doc esistente. |
| `gvg.py:354` | `db.user_mail.insert_one` (mail to opponent at war end) | **AMBIGUOUS_DEFER** per audit v1 (user_mail mixed account/server origin). Esplicitamente forbidden in `GVG_WAR_ONLY` scope. |

---

## 9. Rollback Path

```bash
export SLC_F_GVG_WAR_SCOPE_ROLLBACK_APPROVAL=true
export SLC_F_GVG_WAR_SCOPE_ROLLBACK_ID=slc_f_gvg_war_scope_20260523T192217Z_34999526
python3 /app/backend/scripts/rollback_slc_f_gvg_war_scope.py
```

Caratteristiche:
- **Gated**: rifiuta exit=2 senza entrambi i marker. Test verificato.
- **Code-revert preciso**: rimuove esattamente le 2 righe (import + call) via `text.replace(..., '', 1)` su pattern esatti.
- **No-DB-touch**: i documenti `gvg_wars` creati con `server_id="s1"` resteranno legali per SLC-G `LEGACY_DEFAULT_SERVER_ID`.
- **Idempotente**: rieseguito è no-op.
- **Audit-aware**: scrive `slc_f_gvg_war_scope_rollback_marker_v1.json`.

---

## 10. Validators Run

| Validator | Esito |
|---|---|
| `validate_slc_f_gvg_war_scope_post_apply_v1.py` (nuovo) | ✅ PASS errors=0 |
| `validate_slc_f_raids_equipment_scope_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_equipment_scope_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_2_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_1b_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_0_1_post_apply_v1.py` | ✅ PASS |
| `audit_slc_f_minor_write_surfaces_v1.py` | ✅ PASS (rescan 196 surfaces) |
| Suite AF2-N V12–V30 | ✅ PASS (tutti) |
| Suite Character Bible (RM1.27–1.32) | ✅ PASS (tutti) |
| Suite SLC-C/D/G/H | ✅ PASS (tutti) |
| Suite Benchmark Canonical | ✅ PASS (tutti) |

**Verifica regex specifica della patch (dal nuovo validator):**
- ✅ `gvg.py` contiene `from utils.server_scope import ensure_server_scope`
- ✅ `gvg.py` contiene `war = ensure_server_scope(war, current_user["id"])`
- ✅ La call è ADIACENTE all'`insert_one` (regex `war = ensure_server_scope\(war,\s*current_user\["id"\]\)\s*\n\s*await db\.gvg_wars\.insert_one\(war\)`)
- ✅ Markers di business logic preservati (`guild_a_id`, `guild_b_id`, `guild_a_score`, `guild_b_score`, `guild_a_attacks`, `guild_b_attacks`, `winner_guild_id`, `is_bot_guild`)
- ✅ `user_mail.insert_one` count = 1 (invariato; non duplicato né modificato)
- ✅ Nessun `ensure_server_scope` adiacente a `user_mail.insert_one` (check anti-falso-positivo PASS)

---

## 11. Suite Result

```
Overall: PASS  (pass=347, fail=0, miss=0)
Δ vs Audit-V1 end-state: +1 PASS (nuovo validator GVG war scope)
JSON report: /tmp/slc_f_gvg_suite.json
```

---

## 12. API Smoke Result

| Endpoint | HTTP | Note |
|---|---|---|
| `GET /api/heroes` | 200, **100** elementi | catalogo intatto |
| `GET /api/heroes/primordial_gaia` | **404** | esclusione preservata |
| `GET /api/heroes/borea` | **200** | catalog-only inert |
| `GET /api/heroes/greek_borea` | **200** | catalog-only inert |
| `GET /api/gvg/wars` | 401 | auth richiesta, no 5xx |
| `GET /api/affinity/gift-spend/canary-status` | 200 | AF2-N preservato |

✅ Zero 5xx su GvG routes. Backend healthy.

---

## 13. Invariants

| Invariante | Atteso | Osservato | Esito |
|---|---|---|---|
| `/api/heroes` length | 100 | 100 | ✅ |
| `primordial_gaia` HTTP | 404 | 404 | ✅ |
| `borea` HTTP | 200 inert | 200 | ✅ |
| `greek_borea` HTTP | 200 inert | 200 | ✅ |
| AF2-N cap | 50000 | 50000 | ✅ |
| AF2-N allowlist size | 2500 | 2500 | ✅ |
| AF2-N flags (canary/inv/rate-limit) | True | True | ✅ |
| SLC-G `migration_id` | `slc_g_commit_a_20260523T143803Z_4600ac04` | identico | ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset | unset | ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | unset | ✅ |
| Markers Batch-0/1, Batch-1B, Batch-2, Equipment-scope, Raids-equipment | preservati | preservati | ✅ |
| Phase 11 | false | false | ✅ |

---

## 14. Forbidden Scope Verification

Verificato dal validator `validate_slc_f_gvg_war_scope_post_apply_v1.py`:

| File / Area | Diff vs HEAD | Esito |
|---|---|---|
| `backend/routes/gvg.py` | 2 righe aggiunte (autorizzate) | ✅ |
| `backend/battle_engine.py` | nessuno | ✅ |
| `backend/battle_core.py` | nessuno | ✅ |
| `frontend/app/combat.tsx` | nessuno | ✅ |
| `backend/routes/affinity_gift_spend.py` | nessuno | ✅ |
| `backend/routes/affinity_gifts.py` | nessuno | ✅ |
| `backend/routes/combat.py` | nessuno | ✅ |
| `backend/routes/equipment.py` | nessuno | ✅ |
| `backend/routes/forge.py` | nessuno | ✅ |
| `backend/routes/raids.py` | nessuno | ✅ (Raids-equipment preservato) |
| `backend/routes/unique_items.py` | nessuno | ✅ |
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
| `user_mail.insert_one` count in `gvg.py` | invariato (1) | ✅ |

---

## 15. Borea/Gaia Safety Result

- ✅ `primordial_gaia` HTTP = **404**.
- ✅ `borea`/`greek_borea` HTTP = **200** catalog-only inert.
- ✅ Nessuna attivazione runtime; Character Bible non toccata.
- ✅ Nessun cambiamento a banner/rates/pity/obtainable/roster.
- ✅ La patch riguarda solo creazione di `gvg_wars` (match guild vs guild): nessun impatto su roster/Borea/Gaia.

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

**Conclusione:** AF2-N **identico** allo stato pre-apply.

---

## 17. Known Drift Docs Status

🟡 **NON CORRETTI** per istruzione esplicita del guardrail. I 7 drift docs gacha/summon restano `DRIFT KNOWN, NON-BLOCKING`. Out of GVG_WAR_ONLY scope.

---

## 18. Remaining Risks

| Rischio | Severità | Mitigazione |
|---|---|---|
| 7 drift docs gacha/summon | bassa | Documentazione; runtime non impattato. |
| Documenti `gvg_wars` legacy senza `server_id` esplicito | informativa | Coperti da SLC-G `LEGACY_DEFAULT_SERVER_ID="s1"`. |
| `unique_items.py` insert+upsert non ancora patchati (audit candidate #2) | bassa | Disponibile come prossimo micro-batch sicuro identico pattern (markers già documentati). |
| `gvg.py:354 user_mail.insert_one` non patchato | informativa | AMBIGUOUS_DEFER per design (mail mixed origin); resta deferred. |
| Insert `user_equipment` in `combat.py` non patchati | bassa | Batch-4 future. |
| `heroes.py` user_heroes inserts (gacha claim) | bassa | GACHA_SUMMON_DEFER. |
| Redis rate-limit binary può crashare | media | `bash /app/ops/ensure_redis_rate_limit.sh` ripristina. |

Nessun rischio severità **alta**.

---

## 19. Recommended Next Step

🟢 **Prossimo job suggerito (audit candidate #2):**

### **SLC-F UNIQUE-ITEMS SCOPE**
- **Target:** `unique_items.py:277` (`db.unique_items_crafted.insert_one`) + `unique_items.py:303` (`db.unique_items_equipped.update_one(upsert=True)`)
- **Pattern:** Batch-1B-style con `$setOnInsert` per upsert
- **Expected diff:** +3 righe (1 import + 2 call)
- **Markers richiesti:** `SLC_F_UNIQUE_ITEMS_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=UNIQUE_ITEMS_ONLY`
- **Expected verdict:** `SLC_F_UNIQUE_ITEMS_SCOPE_APPLIED_SAFE`
- **Risk:** low (cost/rarity/UNIQUE_ITEMS catalog NON da toccare)

🔵 **Backlog (non in micro-batch):**
- Refactor strutturale `cosmetics.py` (split ownership/equipped).
- Refactor strutturale `economy.py` (split paid/free + isolate VIP + rimuovere legacy `/server/select`).
- Housekeeping drift docs gacha/summon.
- Batch-3 AF2-N routing.
- Batch-4 combat/battle (combat.py 9 surfaces).
- Gacha/summon dedicated scope task (heroes.py user_heroes).
- Character Bible / sanctuary split dedicato.
- SLC-H live wiring (post-economy refactor).

⚠️ **Esplicitamente NON raccomandato ora:**
- Apertura secondo server / `SERVER_PROFILES_RUNTIME_ENABLED`.
- Toccare `db.heroes` / Character Bible / Borea activation.
- Toccare gacha/summon/combat/battle/AF2-N routing.
- Implementare `/api/housing` runtime.

---

## 20. Updated Progress Estimate

| Fase | Stato pre-task | Stato post-task |
|---|---|---|
| SLC-F Batch-0/1, Batch-1B, Batch-2, Equipment-scope, Raids-equipment | ✅ done | ✅ done |
| SLC-F Minor Write Surfaces Audit (audit-only) | ✅ ready | ✅ ready |
| **SLC-F GVG War Insert Scope (REAL PATCH)** | 🟡 pending | ✅ **done** |
| SLC-F Unique-items scope micro-batch | 🟢 candidate #2 | 🟢 RECOMMENDED NEXT |
| SLC-F Cosmetics/Economy refactor | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 AF2-N routing | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 combat/battle | 🔵 backlog | 🔵 backlog |
| SLC-F gacha/summon scope task | 🔵 backlog | 🔵 backlog |
| SLC-F Character Bible / sanctuary split | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |
| Drift docs gacha/summon housekeeping | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **94% → ~95%** ✅ (suite master 347/347 PASS; patch reale minima applicata; un altro candidato safe identificato come next).

---

## 21. Markers di audit (riferimenti rapidi)

- `apply_id`: `slc_f_gvg_war_scope_20260523T192217Z_34999526`
- `applied_at_utc`: `2026-05-23T19:22:17+00:00`
- `git_head_before`: `1c991ec`
- `git_head_after`: `a3bc211`
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `slc_f_batch_1b_apply_id_preserved`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `slc_f_batch_2_apply_id_preserved`: `slc_f_batch_2_20260523T181752Z_b838601e`
- `slc_f_equipment_scope_apply_id_preserved`: `slc_f_equipment_scope_20260523T182939Z_d2afcc8a`
- `slc_f_raids_equipment_scope_apply_id_preserved`: `slc_f_raids_equipment_scope_20260523T184512Z_a46a6034`
- `slc_f_minor_audit_id_preserved`: `slc_f_minor_audit_20260523T190000Z_audit_only`
- `verdict_target`: `SLC_F_GVG_WAR_SCOPE_APPLIED_SAFE` → ✅ **RAGGIUNTO**

---

**FINE REPORT 111_SLC_F_GVG_WAR_SCOPE_EXTENSION.md**
