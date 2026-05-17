# ULTRA-COMBO V9 — Report Finale

**Task**: `AF2-K-COMMIT + AF2-L-FULL + AF2-M-SIGN-PRE + AXIS-G + OPS-C-WIRING + SAFETY-ROLLUP-D`  
**Stato**: ✅ **PASS COMPLETO** (90/90 suite + 32/32 combo + invariants live OK)  
**Modalità**: Inerte / read-only / no-runtime / no-Borea-activation  
**Baseline ancorata**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`

---

## 1. AF2-K-COMMIT — Migration ledger (schema + indici)

| Aspetto | Risultato |
| --- | --- |
| Env gate richiesto | `DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION=YES_I_UNDERSTAND` ✅ presente |
| Collection creata | `gift_transaction_ledger` ✅ |
| Indici creati | `idx_idem_key_user_window` (unique), `idx_tx_id_unique` (unique), `idx_user_created_desc`, `idx_gift_hero`, `idx_status_created` (5 + `_id_`) ✅ |
| Righe inserite | **0** ✅ (gate `final_rows != 0` esplicito che abortirebbe la migration) |
| `gift-spend` post-commit | HTTP **423** ✅ (no-write preservato) |
| Borea alias post-commit | HTTP **404** ✅ |
| `runtime_attached` | `false` ✅ |
| `db_write` (data) | `false` ✅ |
| `schema_index_write` | `true` (solo metadata MongoDB, no righe) |
| Validator | `validate_affinity_gift_transaction_ledger_commit_result.py` → **PASS 32/32** |

**File chiave**: 
- `/app/backend/scripts/migrate_affinity_gift_transaction_ledger.py` (aggiornato: percorso commit reale via `pymongo`, sotto env gate, con pre-check `rows==0` e post-check `rows==0` come safety net)
- `/app/data/design/affinity/affinity_gift_transaction_ledger_migration_commit_result_v1.json` (rigenerato)

**Note di sicurezza**: il filtro parziale `created_at_utc_within_hours: 24` del design schema non è esprimibile nativamente come `partialFilterExpression` MongoDB → l'indice unique è stato creato **senza** filtro parziale, ovvero in modalità **strettamente più rigida** (vincolo unique globale su `(user_id, idempotency_key, created_at_utc)`). Nessuna riga inserita ⇒ nessun conflitto possibile finché AF2-N resta bloccato.

---

## 2. AF2-L-FULL — Disabled load probe (full)

| Metrica | Valore |
| --- | --- |
| Richieste totali | 297 |
| 5xx | **0** |
| Risposte inattese | **0** |
| p50 latency | ~0.5 ms |
| p95 latency | **0.98 ms** (target < 500 ms) |
| Probe ID | `AF2-L-FULL-PROBE-001` |
| Rollback rehearsal | **PASS_DRY_RUN** (4/4 step simulati, 0 DB write) |

**Etichette coperte** (con expected status): empty 423, valid 423, no_idem 423, dup_idem 423, malformed_idem 423, negative_qty 423, huge_qty 423, stale_gift 423, borea 404, greek_borea 404, primordial_gaia 404.

---

## 3. AF2-M-SIGN-PRE — Operator sign-off package V2

- **5 sign-off** (product, engineering, qa, economy_balance, rollback_owner) → tutti **`false`** ✅
- **AF2-N**: `af2n_allowed = false` ✅ **BLOCCATO**
- `feature_flag_currently_enabled = false`
- Preconditions ora aggiornate post-V9:
  - `af2k_commit_safe`: `BLOCKED_BY_MISSING_ENV` (riferito al precedente run senza env gate; AF2-K-COMMIT con env gate è ora applicato e validato)
  - `af2l_full_load_probe_pass`: `PASS`
  - `axis_g_routes_pass`: `PASS`
  - `ops_c_wiring_pass`: `PASS`
- Validator `validate_affinity_gift_runtime_operator_signoff_v2.py` → **PASS 38/38**

---

## 4. AXIS-G — Route combinate read-only

**Aggiunte a `/app/backend/routes/affinity_gifts.py`** (read-only, NO 423, NO DB write):

| Route | Comportamento |
| --- | --- |
| `GET /api/affinity/gifts/by-element/{e}/by-faction/{f}` | combinazioni valide → 200 |
| `GET /api/affinity/gifts/by-faction/{f}/by-element/{e}` | stesso payload (ordine inverso) → 200 |

**Semantica risposta**:
- `dark + greek` → **200** (`canonical_element=dark`, `alias_applied=false`)
- `darkness + greek` → **200** (`canonical_element=dark`, `alias_applied=true`)
- `fire + greek` → **200**
- `greek + fire` (ordine inverso) → **200**
- `dark + tides` → **404 `deferred_not_live`**
- `dark + borea` / `dark + greek_borea` → **404 `forbidden alias`**
- `tides + greek` (token-faction in slot-element) → **404 `axis_type_mismatch`**
- `POST/PUT/PATCH/DELETE` su queste route → **405**

**Audit**: `audit_affinity_gifts_combined_axis_routes.py` → **PASS 23/23**

---

## 5. OPS-C-WIRING — Boot hook safe non-invasivo

**Strategia adottata** (come da richiesta utente: preferenza scripts/audit/doc, NO modifiche invasive a supervisor):

| Layer | Status | Note |
| --- | --- | --- |
| Scripts `/app/ops/*.sh` | ✅ DONE | `startup_check.sh`, `check_and_restore_start_expo_wrapper.sh`, `restore_start_expo_wrapper.sh`, `start-expo.sh` (tutti `chmod +x`) |
| Hook FastAPI startup (V9) | ✅ DONE | `@app.on_event("startup")` in `/app/backend/server.py` → `subprocess.Popen(["bash", "/app/ops/startup_check.sh"])` (background, non-bloccante, idempotente) |
| Kill-switch | ✅ DONE | `DISABLE_OPS_C_WIRING=1` env var disattiva il hook |
| Audit dedicato | ✅ DONE | `audit_ops_start_expo_boot_wiring.py` → **PASS 13/13** |
| Documento | ✅ DONE | `/app/ops/README_BOOT_WIRING.md` (aggiornato con tabella stato wiring) |
| **Supervisor oneshot** | ⚠️ **MANUAL NEXT STEP** | NON applicato. Template fornito in README per applicazione manuale futura su approvazione esplicita. |

**Garanzie** (audit `[OK]` su tutti i punti):
- nessuna `rm -rf`, nessun riferimento a `mongo/pymongo` negli script ops
- nessuna mutazione `/app/backend/` o `/app/frontend/`
- HMR Metro preservato (nessun `CI=1`)
- backend boot **mai bloccato dal hook** (`try/except` + `subprocess.Popen` con `start_new_session=True`)
- frontend `http://127.0.0.1:3000` raggiungibile (200 OK) post-restart

---

## 6. SAFETY-ROLLUP-D — Runtime NO_GO rollup v4

| Campo | Valore |
| --- | --- |
| `report_id` | `collection_affinity_runtime_activation_readiness_rollup_v4` |
| `supersedes` | `collection_affinity_runtime_activation_readiness_rollup_v3` |
| `go_no_go_decision` | **`NO_GO_RUNTIME`** ✅ |
| `axis_layer_decision` | `GO_AXIS` (axis/AXIS-F/AXIS-G pronti) |
| `AF2N_allowed` | **`false`** ✅ |
| `overall_runtime_activation_ready` | **`false`** ✅ |
| `migration_applied` | `false` (a livello rollup file V8; AF2-K-COMMIT V9 ha applicato schema+indici a DB ma rollup file resta come stato pre-AF2-N) |
| `runtime_no_go_reasons` | 8 motivi documentati |
| `AF2N_blockers` | 4 blocker documentati |
| `invariants_currently_holding` | 12 invarianti, tutte verificate live |

Validator `validate_collection_affinity_runtime_activation_rollup_v4.py` → **PASS 36/36**.

---

## 7. ULTRA-COMBO V9 Composite Validator

`validate_af2k_commit_af2l_full_af2m_signpre_axisg_opsc_wiring_safety_rollup_d_combo.py`:

- **32 check totali** (7 subtask + 25 invarianti live, DB e file)
- **0 failure**
- Report JSON: `/app/backend/reports/ultra_combo_v9_validator_summary_v1.json`

### Aggiunte alla Suite

Aggiornata `run_hero_skill_kit_validator_suite.py` con block V9:
```
AF2-K-COMMIT, AF2-L-FULL, AF2-M-SIGN-PRE,
AXIS-G, OPS-C-WIRING, SAFETY-ROLLUP-D,
ULTRA-COMBO-V9
```

**Suite completa**: `python3 run_hero_skill_kit_validator_suite.py --include-baseline-diff` →  
**PASS 90/90** (pass=90, fail=0, miss=0, baseline-diff PASS).

---

## 8. Smoke API live (post-implementazione V9)

| Endpoint | Atteso | Ottenuto |
| --- | --- | --- |
| `GET /api/heroes` count | 100 | **100** ✅ |
| Borea/greek_borea/primordial_gaia in `/api/heroes` | hidden | **hidden** ✅ |
| `POST /api/affinity/gift-spend` (empty) | 423 | **423** ✅ |
| `POST /api/affinity/gift-spend` (borea) | 404 | **404** ✅ |
| `POST /api/affinity/gift-spend` (greek_borea) | 404 | **404** ✅ |
| `POST /api/affinity/gift-spend` (primordial_gaia) | 404 | **404** ✅ |
| `GET /affinity/gifts/by-element/dark/by-faction/greek` | 200 | **200** ✅ |
| `GET /affinity/gifts/by-element/darkness/by-faction/greek` (alias) | 200 alias_applied | **200 alias_applied=true** ✅ |
| `GET /affinity/gifts/by-faction/greek/by-element/fire` (ordine inverso) | 200 | **200** ✅ |
| `GET /affinity/gifts/by-element/dark/by-faction/tides` | 404 deferred | **404 deferred** ✅ |
| `GET /affinity/gifts/by-element/dark/by-faction/borea` | 404 forbidden | **404 forbidden** ✅ |
| `GET /affinity/gifts/by-element/tides/by-faction/greek` (axis mismatch) | 404 | **404 axis_type_mismatch** ✅ |
| `POST /affinity/gifts/by-element/dark/by-faction/greek` (mutation) | 405 | **405** ✅ |

---

## 9. Stato DB live

```text
db.gift_transaction_ledger.count_documents({}) == 0      ✅
db.gift_transaction_ledger.list_indexes() == [
  _id_, idx_idem_key_user_window (UNIQUE),
  idx_tx_id_unique (UNIQUE),
  idx_user_created_desc, idx_gift_hero, idx_status_created
]                                                          ✅
```

---

## 10. Invarianti non negoziabili — tutte rispettate ✅

| Invariante | Stato |
| --- | --- |
| AF2-N **non eseguito** | ✅ |
| `AFFINITY_GIFT_RUNTIME_ENABLED` **OFF** | ✅ |
| `/api/heroes` **= 100** | ✅ |
| `borea / greek_borea / primordial_gaia` **hidden** | ✅ |
| `POST /affinity/gift-spend` **= 423 no-write** | ✅ |
| Borea aliases su spend **= 404** | ✅ |
| **0 righe inserite** in `gift_transaction_ledger` (a runtime) | ✅ |
| **0 mutazioni inventory** | ✅ |
| **0 mutazioni affinity_points** | ✅ |
| `battle_engine.py` **immutato** | ✅ (no diff) |
| `battle_core.py` **immutato** | ✅ (no diff) |
| `combat.tsx` **immutato** | ✅ (no diff) |
| `game_systems.py` / `synergy_system.py` **immutati** | ✅ (no diff) |
| **gacha / roster / catalog** immutati | ✅ |
| **baseline v6 clean** | ✅ (suite --include-baseline-diff PASS) |
| **UI safety PASS** (no spend button live) | ✅ (nessuna route runtime UI nuova) |

---

## 11. File modificati / aggiunti in V9

**Modificati**:
- `/app/backend/routes/affinity_gifts.py` (+ AXIS-G route combinate)
- `/app/backend/scripts/migrate_affinity_gift_transaction_ledger.py` (commit reale gated)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` (block V9)
- `/app/backend/server.py` (hook OPS-C-WIRING non-invasivo)
- `/app/ops/README_BOOT_WIRING.md`
- `/app/ops/startup_check.sh` (+x)
- `/app/data/design/affinity/affinity_gift_transaction_ledger_migration_commit_result_v1.json` (rigenerato)
- `/app/data/design/affinity/affinity_gift_transaction_ledger_migration_result_v1.json` (rigenerato)
- `/app/data/design/affinity/affinity_phase2_rollback_rehearsal_result_v1.json` (re-run rehearsal)
- `/app/data/design/affinity/affinity_gift_spend_full_disabled_load_result_v1.json` (re-run probe)

**Aggiunti**:
- `/app/backend/scripts/validate_af2k_commit_af2l_full_af2m_signpre_axisg_opsc_wiring_safety_rollup_d_combo.py`
- `/app/backend/reports/ultra_combo_v9_validator_summary_v1.json`
- `/app/docs/divine/67_ULTRA_COMBO_V9_AF2K_COMMIT_AF2L_FULL_AF2M_SIGNPRE_AXISG_OPSC_WIRING_SAFETY_ROLLUP_D.md` (questo report)

---

## 12. Prossimi punti manuali (NON eseguiti, in attesa di approvazione utente)

| ID | Cosa | Pre-requisito |
| --- | --- | --- |
| Supervisor wiring | Aggiungere `[program:startup_check]` a `/etc/supervisor/conf.d/` (template in `/app/ops/README_BOOT_WIRING.md`) | Approvazione esplicita utente |
| AF2-M-SIGN-PRODUCT | Step 1 di sign-off effettivo (product, engineering, qa, economy_balance, rollback_owner → tutti `true`) | Tutti i sign-off owner identificati + approvazione |
| AF2-L-FULL real K6/Locust | Esecuzione vera load test (oltre il probe interno 300 reqs) | Richiesta esplicita utente |
| AF2-N (flip runtime) | **STRETTAMENTE VIETATO** finché non sono tutti `true` i sign-off + approvazione utente esplicita | tutti i precedenti |
| STACK-G | Collegare `global_modifier_cap_resolver` a `battle_engine` (gated, no-write) | task separato |

---

## 13. Conclusioni

✅ **ULTRA-COMBO V9 completato con successo**, ZERO failure, ZERO mock attivati, ZERO mutazione runtime/battle/gacha/roster, ZERO riga ledger inserita dal runtime, infrastruttura DB pronta per attivazione futura sotto controllo manuale dell'utente, route AXIS-G combinate live e validate, hook OPS-C-WIRING safe e attivo, sign-off package V2 pronto, runtime confermato **NO_GO**, AF2-N **BLOCCATO**.

Tutte le invarianti di sicurezza richieste dall'utente sono mantenute e validate live.
