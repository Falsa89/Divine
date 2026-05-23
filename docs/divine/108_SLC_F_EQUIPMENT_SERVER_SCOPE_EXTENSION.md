# 108 — SLC-F EQUIPMENT SERVER_SCOPE EXTENSION (gated micro-batch — SAFE NO-OP)

> **Verdict finale:** `SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION_APPLIED_SAFE`
> **Tipo apply:** **SAFE NO-OP** — `equipment.py` contiene esclusivamente `update_one` su documenti esistenti (zero `insert_one`, zero `upsert=True`). Patchare violerebbe la regola §4 "do not migrate existing DB docs in this task".
> **Progress globale:** **92% → ~93%**
> **Modalità:** GATED MICRO-BATCH — EQUIPMENT ONLY. Nessuna espansione di scope. AF2-N, Character Bible, combat/battle, gacha/summon, Housing completamente preservati.

---

## 1. Executive Verdict

✅ **PASS** — Il micro-batch SLC-F Equipment Server-Scope Extension è stato completato come **safe no-op apply**. L'audit pre-apply read-only ha rilevato che tutte e 4 le write surfaces in `/app/backend/routes/equipment.py` sono `update_one` su documenti esistenti (mutano un singolo campo `equipped_to` via `$set`/`$unset`). Nessuna è `insert_one` né `upsert=True`. Patchare con `ensure_server_scope` sarebbe stato un no-op semantico (con `$setOnInsert` senza upsert) oppure una migrazione DB inline (con `$set`), entrambi vietati. Decisione conforme al GUARDRAIL principale: "skipped > unsafe patch". Suite master verde 344/344.

| Voce | Atteso | Osservato | Esito |
|---|---|---|---|
| Authorization markers (`SLC_F_EQUIPMENT_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=EQUIPMENT_ONLY`) | presenti | presenti | ✅ |
| Suite master | PASS | **344/344 PASS** (era 343 + nuovo validator) | ✅ |
| Nuovo validator `SLC-F-EQUIPMENT-SCOPE-POST-APPLY` | PASS | PASS (errors=0) | ✅ |
| Pre-apply audit eseguito prima di qualunque code-change | sì | sì (zero code-change effettuati) | ✅ |
| Equipment route audit table prodotta | sì | sì (vedi §5) | ✅ |
| Rollback gated creato prima dell'apply | sì | sì (refuse exit=2 senza marker) | ✅ |
| Invarianti API runtime | preservati | preservati | ✅ |
| AF2-N canary state | preservato | identico (allowlist=2500, cap=50000) | ✅ |
| Diff vs HEAD su `equipment.py` | 0 righe | 0 righe | ✅ |

---

## 2. Authorization Markers Detected

```env
SLC_F_EQUIPMENT_SCOPE_APPLY_APPROVAL=true     ✅
SLC_F_APPLY_BATCH_SCOPE=EQUIPMENT_ONLY        ✅
```

Forniti dall'utente nel messaggio di task. Nessun marker spurio.

---

## 3. Previous SLC-F State Confirmation

| Checkpoint | Apply ID | Esito |
|---|---|---|
| `SLC_F_BATCH_0_1_APPLIED_SAFE` | `slc_f_batch_0_1_20260523T173754Z_27b1b737` | ✅ marker presente |
| `SLC_F_BATCH_1B_APPLIED_SAFE` | `slc_f_batch_1b_20260523T175058Z_2cf0584c` | ✅ marker presente |
| `SLC_F_BATCH_2_APPLIED_SAFE` (safe no-op) | `slc_f_batch_2_20260523T181752Z_b838601e` | ✅ marker presente |
| `SLC-G COMMIT-A` migration | `slc_g_commit_a_20260523T143803Z_4600ac04` (`migration_applied=True`) | ✅ preservato |
| Helper `backend/utils/server_scope.py` (export `ensure_server_scope` + `LEGACY_DEFAULT_SERVER_ID="s1"`) | — | ✅ presente |
| Suite baseline prima del task | **343 PASS / 0 FAIL / 0 MISS** | ✅ |

Verifica imports persistenti: tutti i file patchati in Batch-0/1 e Batch-1B contengono ancora `from utils.server_scope import ensure_server_scope` (`items`, `forge`, `achievements`, `level_sharing`, `social`, `soul_forge`, `artifacts`, `guild`).

---

## 4. Git Status Before / After

- **HEAD prima del task:** `fa44754`
- **HEAD dopo il task:** `b8f1715` (auto-commit triggerato per i NEW file: marker JSON + 2 script + report doc + suite runner edit)
- **Diff su `backend/routes/equipment.py` vs HEAD:** **0 righe** (file completamente intatto)
- **File codice runtime modificati:** **0** (zero patch su equipment.py o altro)
- **File aggiunti (non-codice runtime):**
  - `data/design/system_safety/slc_f_equipment_scope_apply_marker_v1.json`
  - `backend/scripts/rollback_slc_f_equipment_scope.py`
  - `backend/scripts/validate_slc_f_equipment_scope_post_apply_v1.py`
  - `docs/divine/108_SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION.md`
  - `data/design/server_lifecycle/_slc_f_equipment_scope_post_apply_v1_result.json` (output validator)
- **File suite runner modificato (+1 riga `OPTIONAL`):**
  - `backend/scripts/run_hero_skill_kit_validator_suite.py`

---

## 5. Equipment Route Audit Table

`/app/backend/routes/equipment.py` (51 righe) — write surfaces:

| ID | Line | Endpoint | Operation | Semantica | Crea nuovo doc? | Upsert? | Classification | Decisione |
|---|---|---|---|---|---|---|---|---|
| **EQ-W1** | 36 | `POST /api/equipment/equip` | `db.user_equipment.update_one` | `$unset equipped_to` su doc esistente (clear previous equip) | ❌ no | ❌ no | server_bound | **SKIP_UPDATE_ONLY_NO_NEW_DOC** |
| **EQ-W2** | 40 | `POST /api/equipment/equip` | `db.user_equipment.update_one` | `$unset equipped_to` su doc esistente in conflitto (swap slot) | ❌ no | ❌ no | server_bound | **SKIP_UPDATE_ONLY_NO_NEW_DOC** |
| **EQ-W3** | 41 | `POST /api/equipment/equip` | `db.user_equipment.update_one` | `$set equipped_to` su doc esistente (apply new equip target) | ❌ no | ❌ no | server_bound | **SKIP_UPDATE_ONLY_NO_NEW_DOC** |
| **EQ-W4** | 46 | `POST /api/equipment/unequip/{id}` | `db.user_equipment.update_one` | `$unset equipped_to` su doc esistente (unequip) | ❌ no | ❌ no | server_bound | **SKIP_UPDATE_ONLY_NO_NEW_DOC** |

**Sintesi:** 4/4 write surfaces → SKIP. Zero `insert_one`, zero `upsert=True`. La creazione dei documenti `user_equipment` avviene **al di fuori** di `equipment.py`.

### Dove vengono creati i documenti `user_equipment` (OUT OF SCOPE per EQUIPMENT_ONLY)

| File | Lines | Operation | Motivo OUT_OF_SCOPE |
|---|---|---|---|
| `backend/routes/combat.py` | 87, 140, 232 | `db.user_equipment.insert_one` | Batch-4 (combat/battle routing) — esplicitamente vietato dallo scope EQUIPMENT_ONLY. |
| `backend/routes/raids.py` | 150 | `db.user_equipment.insert_one` | server_bound ma non in EQUIPMENT_ONLY scope; differito a micro-batch raids/gvg dedicato se necessario. |

Patchare gli insert in `combat.py`/`raids.py` richiederebbe espansione di scope ⇒ vietato. Restano nel backlog Batch-4 / micro-batch dedicato.

---

## 6. Files Changed

### File di codice runtime patchati
- **NESSUNO.** Apply = SAFE NO-OP. `backend/routes/equipment.py` è 100% identico al pre-apply (`git diff` 0 righe).

### File di sicurezza/marker/script generati
- `data/design/system_safety/slc_f_equipment_scope_apply_marker_v1.json` (apply marker con `route_patch_applied=false`, `all_candidates_skipped=true`, `safe_no_op_apply=true`)
- `backend/scripts/rollback_slc_f_equipment_scope.py` (rollback gated)
- `backend/scripts/validate_slc_f_equipment_scope_post_apply_v1.py` (post-apply validator)
- `data/design/server_lifecycle/_slc_f_equipment_scope_post_apply_v1_result.json` (output validator, verdict `PASS`)
- `docs/divine/108_SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION.md` (questo report)
- `/tmp/slc_f_eq_suite.json` (suite master JSON report)

### Suite runner
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (+1 riga in `OPTIONAL` per `SLC-F-EQUIPMENT-SCOPE-POST-APPLY`).

---

## 7. Equipment Write Surfaces Patched

**NESSUNA.** Tutte e 4 le surfaces (EQ-W1..EQ-W4) sono state correttamente skipped perché sono `update_one` su documenti esistenti.

---

## 8. Equipment Write Surfaces Skipped and Why

| Surface | Decisione | Motivo dettagliato |
|---|---|---|
| EQ-W1 (line 36) | SKIP_UPDATE_ONLY_NO_NEW_DOC | `update_one` non crea documenti; non c'è metadata da iniettare. Iniettare `server_id` via `$set` sarebbe **migrazione DB inline** (vietata dalla §4 del prompt). Usare `$setOnInsert` senza `upsert=True` sarebbe no-op semantico. |
| EQ-W2 (line 40) | SKIP_UPDATE_ONLY_NO_NEW_DOC | Stessa motivazione di EQ-W1. |
| EQ-W3 (line 41) | SKIP_UPDATE_ONLY_NO_NEW_DOC | `update_one` con `$set equipped_to`; non crea doc; non rilevante per server-scope iniezione. |
| EQ-W4 (line 46) | SKIP_UPDATE_ONLY_NO_NEW_DOC | `update_one` con `$unset equipped_to`; non crea doc; non rilevante per server-scope iniezione. |

**Conferma del pattern:** anche `forge.py` (già patchato in Batch-1B) contiene `db.user_equipment.update_one` alle righe 205 e 249 e NON applica `ensure_server_scope` a quelle chiamate — il helper è applicato solo agli `insert/upsert` (es. righe 283, 300 su `rune`). La nostra decisione di SKIP per `equipment.py` è coerente con il pattern già adottato in Batch-1B.

---

## 9. Rollback Path

```bash
export SLC_F_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL=true
export SLC_F_EQUIPMENT_SCOPE_ROLLBACK_ID=slc_f_equipment_scope_20260523T182939Z_d2afcc8a
python3 /app/backend/scripts/rollback_slc_f_equipment_scope.py
```

Caratteristiche:
- **Gated**: rifiuta exit=2 senza entrambi i marker. Test verificato: senza marker risponde `REFUSED: SLC_F_EQUIPMENT_SCOPE_ROLLBACK_APPROVAL must be set to "true"`.
- **Marker-only revert**: apply è SAFE NO-OP, nessun file da ripristinare.
- **No-DB-touch**: nessuna scrittura su MongoDB.
- **Idempotente**: rieseguito è no-op.

---

## 10. Validators Run

| Validator | Esito |
|---|---|
| `validate_slc_f_equipment_scope_post_apply_v1.py` (nuovo) | ✅ PASS errors=0 |
| `validate_slc_f_batch_2_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_1b_post_apply_v1.py` | ✅ PASS |
| `validate_slc_f_batch_0_1_post_apply_v1.py` | ✅ PASS |
| SLC-G commit-A post-apply | ✅ PASS |
| Suite AF2-N V12–V30 (canary, inventory writes, rate-limit, stage1–4 apply/monitoring, soak, observability, signoff V8) | ✅ PASS (tutti) |
| Suite Character Bible (RM1.27, RM1.28, RM1.29, RM1.30, RM1.32) | ✅ PASS (tutti) |
| Suite SLC-C/D/G/H | ✅ PASS (tutti) |
| Suite Benchmark Canonical | ✅ PASS (tutti) |

---

## 11. Suite Result

```
Overall: PASS  (pass=344, fail=0, miss=0)
Δ vs Batch-2 end-state: +1 PASS (validator equipment scope aggiunto)
JSON report: /tmp/slc_f_eq_suite.json
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
| `GET /api/equipment/templates` | **200** | read-only equipment templates intatti |
| `GET /api/user/equipment` | 401 | auth richiesta, no 5xx |
| `GET /api/affinity/gift-spend/canary-status` | 200 | AF2-N preservato (allowlist=2500, cap=50000) |

✅ Zero 5xx su equipment routes. Zero regressioni di auth. Zero mutazioni DB.

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
| Batch-0/1, Batch-1B, Batch-2 markers | preservati | preservati | ✅ |
| Phase 11 executed | false | false | ✅ |
| `equipment.py` diff vs HEAD | 0 | 0 | ✅ |

---

## 14. Forbidden Scope Verification

Verificato dal validator `validate_slc_f_equipment_scope_post_apply_v1.py`:

| File / Area | Diff vs HEAD | Esito |
|---|---|---|
| `backend/routes/equipment.py` | nessuno | ✅ SAFE NO-OP confermato |
| `backend/battle_engine.py` | nessuno | ✅ |
| `backend/battle_core.py` | nessuno | ✅ |
| `frontend/app/combat.tsx` | nessuno | ✅ |
| `backend/routes/affinity_gift_spend.py` | nessuno | ✅ |
| `backend/routes/affinity_gifts.py` | nessuno | ✅ |
| `backend/routes/forge.py` | nessuno | ✅ (Batch-1B preservato) |
| `backend/routes/cosmetics.py` | nessuno | ✅ |
| `backend/routes/economy.py` | nessuno | ✅ |
| `backend/routes/push_notifications.py` | nessuno | ✅ |
| `backend/routes/game_data.py` | nessuno | ✅ |
| `backend/routes/heroes.py` | nessuno | ✅ |
| `backend/routes/combat.py` | nessuno | ✅ (Batch-4 future) |
| `backend/routes/raids.py` | nessuno | ✅ |
| `backend/routes/sanctuary.py` | nessuno | ✅ (Character Bible) |
| `backend/routes/player_faction_v2.py` | nessuno | ✅ |
| Route `/api/housing` | non presente | ✅ |
| Route `/api/account/server-profiles` | non presente | ✅ |
| Route `/api/account/active-server` | non presente | ✅ |
| Frontend `/app/frontend/app/*` | nessuna modifica | ✅ |
| SLC-H runtime endpoints | non implementati | ✅ |
| STACK-G | non toccato | ✅ |

**Verifica anti-falso-positivo:** il validator controlla che `equipment.py` **NON contenga** `from utils.server_scope import ensure_server_scope` né chiamate `ensure_server_scope(`. Entrambi i check passano ⇒ skip reale, non patch silente.

---

## 15. Borea/Gaia Safety Result

- ✅ `primordial_gaia` HTTP = **404** (esclusione storica preservata).
- ✅ `borea` HTTP = **200**, `greek_borea` HTTP = **200**, entrambi catalog-only inert:
  - presenti nel catalogo;
  - nessuna attivazione runtime;
  - nessun kit attivo, nessun trigger, nessun flag `BOREA_ACTIVATION_*` introdotto;
  - non summonabili, non visibili in pool obtainable, non in roster pubblico;
  - **Character Bible (`sanctuary.py`, `db.heroes`) NON toccata**.
- ✅ Nessun cambiamento a banner/rates/pity/obtainable/fragments/roster visibility (l'apply equipment-only non ha toccato gacha/summon/heroes).

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

**Conclusione:** AF2-N **identico** allo stato pre-apply. Nessuna interferenza. STACK-G non toccato. Public spend UI non implementata.

---

## 17. Known Drift Docs Status

I 7 documenti di drift `user_heroes` da gacha/summon restano in stato **DRIFT KNOWN, NON-BLOCKING, NON CORRETTI** per istruzione esplicita del guardrail del pack:

> *"The 7 drift docs in user_heroes from gacha/summon are known. Do not fix them here. Do not patch gacha/summon. Report them as deferred."*

Deferito a job housekeeping documentale dedicato.

---

## 18. Remaining Risks

| Rischio | Severità | Mitigazione |
|---|---|---|
| 7 drift docs gacha/summon non corretti | bassa | Documentazione; runtime non impattato; coperto da SLC-G commit-A legacy `s1` policy. |
| Insert `user_equipment` in `combat.py` (linee 87/140/232) non patchati | bassa | Batch-4 future (combat/battle); copertura SLC-G legacy `s1`. |
| Insert `user_equipment` in `raids.py` (line 150) non patchato | bassa | Out of EQUIPMENT_ONLY scope; potenziale micro-batch dedicato. |
| Documenti `user_equipment` esistenti senza `server_id` esplicito | informativa | Comportamento legacy: SLC-G commit-A define `LEGACY_DEFAULT_SERVER_ID="s1"` come fallback compatibile. Nessuna regressione runtime. |
| Redis rate-limit binary può crashare nel container | media | `bash /app/ops/ensure_redis_rate_limit.sh` ripristina; SAFETY-ROLLUP T/U/V/W/X/Y restano PASS. |

Nessun rischio severità **alta** identificato.

---

## 19. Recommended Next Step

🔵 **Prossimi job possibili (NON in questo apply):**

1. **(P2) Micro-batch raids.py** — patchare l'`insert_one user_equipment` in `raids.py:150` con `ensure_server_scope` (server_bound, basso rischio simile a Batch-1B). Richiederà nuovi marker `SLC_F_RAIDS_SCOPE_APPLY_APPROVAL=true`, `SLC_F_APPLY_BATCH_SCOPE=RAIDS_ONLY`.
2. **(P2) Refactoring strutturale `cosmetics.py`** — split `user_cosmetics` in ownership (account_wide) + equipped (server_bound).
3. **(P2) Refactoring strutturale `economy.py`** — split paid/free currency, isolate VIP, rimuovere legacy `/server/select`.
4. **(P2) Housekeeping drift docs gacha/summon** — job indipendente, metadata-only.
5. **(P3) SLC-F APPLY BATCH-3 ONLY (AF2-N routing)** — gated, solo post-broad-rollout signoff V8.
6. **(P3) SLC-F APPLY BATCH-4 ONLY (combat/battle)** — include gli insert `user_equipment` in `combat.py`; richiederà attento audit.
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
| **SLC-F Equipment server-scope extension (safe no-op)** | 🟡 pending | ✅ **done (no-op safe)** |
| SLC-F Raids/GvG micro-batch (insert `user_equipment` in raids.py) | 🔵 backlog | 🔵 backlog |
| SLC-F Cosmetics/Economy refactor strutturale | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-3 (AF2-N routing) | 🔵 backlog | 🔵 backlog |
| SLC-F Batch-4 (combat/battle, include insert user_equipment) | 🔵 backlog | 🔵 backlog |
| SLC-H live wiring | 🔵 design-only | 🔵 design-only |
| Phase 11 / Second server / Broad rollout | 🔵 backlog | 🔵 backlog |
| Drift docs gacha/summon housekeeping | 🔵 backlog | 🔵 backlog |

**Progress estimate:**

> **92% → ~93%** ✅ (suite master 344/344 PASS; safe no-op apply correttamente registrato).

---

## 21. Markers di audit (riferimenti rapidi)

- `apply_id`: `slc_f_equipment_scope_20260523T182939Z_d2afcc8a`
- `applied_at_utc`: `2026-05-23T18:29:39+00:00`
- `git_head_before`: `fa44754`
- `git_head_after`: `b8f1715` (auto-commit per i NEW marker/script/doc; zero diff su file di codice runtime)
- `slc_g_migration_id_preserved`: `slc_g_commit_a_20260523T143803Z_4600ac04`
- `slc_f_batch_0_1_apply_id_preserved`: `slc_f_batch_0_1_20260523T173754Z_27b1b737`
- `slc_f_batch_1b_apply_id_preserved`: `slc_f_batch_1b_20260523T175058Z_2cf0584c`
- `slc_f_batch_2_apply_id_preserved`: `slc_f_batch_2_20260523T181752Z_b838601e`
- `verdict_target`: `SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION_APPLIED_SAFE` → ✅ **RAGGIUNTO (SAFE NO-OP)**

---

**FINE REPORT 108_SLC_F_EQUIPMENT_SERVER_SCOPE_EXTENSION.md**
