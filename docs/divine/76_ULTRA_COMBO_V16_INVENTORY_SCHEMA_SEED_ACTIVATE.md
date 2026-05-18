# ULTRA-COMBO V16 — Schema Migration + Stage1 QA Seed + Inventory Wiring Activate Retry + Live Monitoring + Safety Rollup K

**Stato finale**: ✅ PASS (39/39 check composite + 97/97 suite con `--include-baseline-diff`)
**Data**: 2026-05-17 (sessione V16)
**Modalità runtime**: `stage1_inventory_live_active_no_broad_rollout` — Stage1 attivo (50 utenti, cap 500) + **Inventory wiring LIVE** (`inventory_mutation_enabled=True`, `affinity_points_mutation_enabled=True`); battle wiring NON live; broad rollout NON autorizzato.
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` (PASS).

---

## 1) File creati in V16

| Path | Ruolo |
|---|---|
| `/app/data/design/affinity/user_inventory_affinity_state_schema_v1.json` | Schema dichiarativo `user_gift_inventory` + `user_affinity_state` (4+4 indici, gates env) |
| `/app/backend/scripts/migrate_user_inventory_affinity_state_schema.py` | Migrator gated da `DIVINE_ALLOW_USER_INVENTORY_SCHEMA_MIGRATION=YES_I_UNDERSTAND` |
| `/app/backend/scripts/rollback_user_inventory_affinity_state_schema.py` | Rollback schema (con `--dry-run`) |
| `/app/backend/scripts/validate_user_inventory_affinity_state_schema.py` | Validator migration (24 check inclusi indexes) |
| `/app/backend/scripts/seed_stage1_qa_gift_inventory.py` | Seed 50 Stage1 QA users gated da `DIVINE_ALLOW_STAGE1_QA_INVENTORY_SEED=YES_I_UNDERSTAND` |
| `/app/backend/scripts/rollback_stage1_qa_gift_inventory_seed.py` | Rollback seed (filtra `metadata.seed_task='V16'`) |
| `/app/backend/scripts/validate_stage1_qa_gift_inventory_seed.py` | Validator seed (19 check) |
| `/app/backend/scripts/validate_af2n_v16_preflight.py` | V16 Preflight (runner + validator integrato) |
| `/app/backend/scripts/apply_affinity_inventory_wiring_stage1_retry.py` | Snapshot post-flip dello stato applicato |
| `/app/backend/scripts/rollback_affinity_inventory_wiring_stage1_retry.py` | Alias del rollback inventory V15 |
| `/app/backend/scripts/validate_affinity_inventory_wiring_stage1_retry_apply_result.py` | Validator apply (32 check) |
| `/app/backend/scripts/run_affinity_inventory_live_monitoring_v16.py` | Live monitoring V16 (replay idempotency + Borea + non-allowlist + 412 + DB cross-check) |
| `/app/backend/scripts/validate_affinity_inventory_live_monitoring_v16.py` | Validator live monitoring (32 check) |
| `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v11.py` | Validator Safety Rollup K (77 check) |
| `/app/backend/scripts/validate_ultra_combo_v16_inventory_schema_seed_activate.py` | Composite V16 (39 check incl. live invarianti + DB cross-check + git diff) |
| `/app/data/design/affinity/user_inventory_affinity_state_migration_result_v1.json` | Risultato migrazione |
| `/app/data/design/affinity/stage1_qa_gift_inventory_seed_result_v1.json` | Risultato seed |
| `/app/data/design/affinity/af2n_v16_preflight_result_v1.json` | Risultato preflight |
| `/app/data/design/affinity/affinity_inventory_wiring_stage1_retry_apply_result_v1.json` | Apply result |
| `/app/data/design/affinity/affinity_inventory_live_monitoring_v16_result.json` | Live monitoring result |
| `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v11.json` | Safety Rollup K |
| `/app/backend/reports/ultra_combo_v16_validator_summary_v1.json` | Sommario composite V16 |
| `/app/backend/reports/suite_v16.json` | Sommario suite completa V16 |
| `/app/backups/backend.conf.pre-inv-flag.20260517T235811Z.bak` | Backup pre-flip dell'env flag inventory |

## 2) File modificati in V16

| Path | Modifica |
|---|---|
| `/app/backend/routes/affinity_gift_spend.py` | Aggiunto helper `_inventory_writes_enabled()` + costante `_INVENTORY_WRITES_ENV`. Esteso il branch "Hard cap check / insert" con il flow Stage1-only di mutazione atomica: pre-check inventory (412 se insufficiente), insert ledger con `inventory_mutated=True/affinity_points_mutated=True`, decrement atomico via `update_one` con guard `quantity>=qty`, increment upsert su `user_affinity_state`. Aggiornato `_canary_envelope()` e `canary-status` per riflettere lo stato dinamico del flag. **Borea always rejected BEFORE this path** (passo 1 del request flow). |
| `/etc/supervisor/conf.d/backend.conf` | Aggiunto env `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED="true_explicit_affinity_inventory_on"` alla coda dell'`environment=`. Backup pre-flip su `/app/backups/backend.conf.pre-inv-flag.20260517T235811Z.bak`. |
| `/app/backend/scripts/run_af2n_stage1_extended_monitoring_v15.py` | V16-aware: rileva V16 mode via `inventory_writes_flag_dependency` in canary-status; tollera `inventory_mutation_enabled=True` come stato legittimo; mantiene assert duro su buffs/battle/combat=False. |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Nuovo set `SUPERSEDED_AFTER_INV_WRITES` (attivo quando `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED=true_explicit_affinity_inventory_on`) che marca SUPERSEDED i V12-V15 pre-inventory-on validators. Logica unificata `SUPERSEDED = SUPERSEDED_AFTER_AF2N \| SUPERSEDED_AFTER_INV_WRITES`. Aggiunto blocco `# ULTRA-COMBO V16` con 7 nuovi task. |

**Nessuna modifica** a: `server.py`, `battle_engine.py`, `battle_core.py`, `combat.tsx`, `game_systems.py`, `synergy_system.py`, cataloghi gacha/roster, `final_numbers`.

## 3) Preflight V16

- File: `/app/data/design/affinity/af2n_v16_preflight_result_v1.json`
- Validator integrato (15 gate live + 15 self-check) → **PASS**
- Gate critici tutti verdi: `api_health_200`, `heroes_100`, `heroes_no_borea`, `canary_status_200`, `canary_flag_on`, `stage1_allowlist_50`, `stage1_cap_500`, `ledger_within_cap`, `borea_404`, `non_allowlist_423`, `battle_files_unchanged`, `route_modification_recorded`, `rollback_scripts_v15_available`, `suite_v15_pass`, `baseline_v6_diff_pass`, `ui_safety_pass`.

## 4) Schema migration (AF2-N-INVENTORY-SCHEMA-MIGRATION)

- Eseguito con env gate `DIVINE_ALLOW_USER_INVENTORY_SCHEMA_MIGRATION=YES_I_UNDERSTAND` (mode=`live`).
- **Collection create**: `user_gift_inventory` (4 indici: `idx_user_gift_unique` UNIQUE, `idx_user_id`, `idx_gift_id`, `idx_updated_at`), `user_affinity_state` (4 indici: `idx_user_hero_unique` UNIQUE, `idx_user_id_aff`, `idx_hero_id_aff`, `idx_affinity_tier`).
- Schemi documentati in `user_inventory_affinity_state_schema_v1.json` (fields, types, defaults, min/max, indexes).
- Validator (24 check, inclusa verifica live degli 8 indici) → **PASS**

## 5) Stage1 QA Seed (AF2-N-STAGE1-QA-SEED)

- Eseguito con env gate `DIVINE_ALLOW_STAGE1_QA_INVENTORY_SEED=YES_I_UNDERSTAND` (mode=`live`).
- Seeded: **50 utenti Stage1 QA** (`user_canary_001/002/003` + `stage1_qa_001`…`stage1_qa_047`), `gift_id='gift_test_001'`, `quantity=10`.
- Metadata: `{seed_task: 'V16', is_qa_user: true}` per ogni doc → filtro robusto per rollback selettivo.
- Nessun Borea/greek_borea/primordial_gaia (filtri attivi).
- Nessuna mutazione di dati non-QA.
- Validator (19 check) → **PASS** (50 docs verificati, 0 con `quantity<0`, 0 con gift_id Borea).

## 6) Inventory wiring activate retry (AF2-N-INVENTORY-RETRY-APPLY)

- **Backup pre-flip**: `/app/backups/backend.conf.pre-inv-flag.20260517T235811Z.bak`.
- **Flag attivato**: `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED="true_explicit_affinity_inventory_on"` aggiunto in `backend.conf` come quinto env var nella stessa `environment=` line.
- **Restart**: `supervisorctl reread → update → restart backend`; backend RUNNING dopo ~25s.
- **Verifica post-flip**: canary-status mostra `inventory_mutation_enabled=True`, `affinity_points_mutation_enabled=True`, `buffs_enabled=False`, `battle_runtime_attached=False`, `applied_to_combat=False`, `canary_allowlist_size=50`, `canary_ledger_cap=500`, `inventory_writes_flag_dependency=AFFINITY_GIFT_INVENTORY_WRITES_ENABLED` (campo nuovo V16).
- **3 controlled spend live eseguiti** (output route `result=applied_inventory_live`):

| Spend | User | Hero | Qty | Pre inv | Post inv | Pre aff | Post aff |
|---|---|---|---|---|---|---|---|
| #1 | stage1_qa_001 | greek_zeus | 2 | 10 | **8** | 0 | **2** |
| #2 | stage1_qa_002 | greek_athena | 3 | 10 | **7** | 0 | **3** |
| #3 | stage1_qa_003 | greek_ares | 1 | 10 | **9** | 0 | **1** |

- **Replay** stesso `idempotency_key='v16live001ai'`: 200 `result=idempotent_replay`, `ledger_row_inserted=False`, no double-decrement (inv resta 8), no double-increment (aff resta 2).
- Ledger 11 → **14** righe (3 nuove con `inventory_mutated=True, affinity_points_mutated=True`).
- Validator (32 check) → **PASS**

## 7) Inventory live monitoring (AF2-N-INVENTORY-LIVE-MONITORING-V16)

- Replay idempotency live-verified: 200 + inv/aff unchanged ✓
- Borea spend → 404 + 0 rows ledger (pre=0, post=0) ✓
- Non-allowlist spend → 423 ✓
- Insufficient inventory (`stage1_qa_004` qty=500 da bilance 10) → **412** `result=inventory_insufficient`, quantity preservata (10→10) ✓
- DB cross-check: `inventory_mutated_rows = affinity_points_mutated_rows = 3`, `buffs_activated=0`, `battle_wiring=0`, `negative_inventory=0`
- Validator (32 check) → **PASS**

## 8) Stage1 monitoring (AF2-N-STAGE1-EXTENDED-MONITORING-V15)

- Re-eseguito post-V16 con 60 campioni × 100ms (V16-aware): 0 trigger, 0 5xx, **status=PASS**
- Heroes count 100 verificato 60×, Borea 404 verificato 60×, non-allowlist 423 verificato 60×, replay idempotente 60× verificato.
- Validator → **PASS** (24/24 check).

## 9) K6 fallback (AF2-L-K6-V15-FALLBACK)

- Probe Python fallback 1000 req (100 × 10 label): 0 5xx, 0 unexpected, 0 dup, ledger unchanged.
- Validator → **PASS** (43/43 check).

## 10) Rollback readiness

- **5 script di rollback disponibili e dry-run ok**:
  1. `/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py` (Stage1 → V12 canary)
  2. `/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py` (rimuove flag inventory, Stage1 resta)
  3. `/app/backend/scripts/rollback_user_inventory_affinity_state_schema.py` (drop 2 collection)
  4. `/app/backend/scripts/rollback_stage1_qa_gift_inventory_seed.py` (delete docs `seed_task='V16'`)
  5. `/app/ops/rollback_af2n_canary.sh` (full canary fallback)
- 2 backup `backend.conf.pre-*` pronti per restore istantaneo.

## 11) Safety Rollup K (rollup v11)

- File: `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v11.json`
- `report_id=…rollup_v11`, `task_origin=SAFETY-ROLLUP-K`, `supersedes=…rollup_v10`.
- Stato: `overall_runtime_activation_state="stage1_inventory_live_active_no_broad_rollout"`, `go_no_go_decision="STAGE1_INVENTORY_LIVE_NO_BROAD_ROLLOUT"`, `next_decision="extended_monitoring_or_stage2_prep"`.
- 5 operator signoff = true + final user approval present.
- 22 subsystem (incl. `af2n_inventory_schema_migration=APPLIED`, `af2n_stage1_qa_seed=APPLIED_50`, `af2n_inventory_wiring_live=ACTIVATED_STAGE1_ONLY`, `af2n_inventory_live_monitoring=PASS_ACTIVATED`, `af2n_inventory_rollback=READY`, `af2n_inventory_schema_rollback=READY`, `af2n_inventory_seed_rollback=READY`).
- 14 abort triggers tutti `triggered=false`.
- Validator (77 check) → **PASS**.

## 12) Borea safety

- `/api/heroes` mai contiene `borea`/`greek_borea`/`primordial_gaia` (verificato 60× in monitoring + 1× smoke).
- `POST /api/affinity/gift-spend` con Borea hero_id:
  - Stage1 monitoring V15 post-V16: 60× = 60×404
  - Live monitoring V16: 1× = 404, ledger Borea pre/post = 0/0
  - Smoke finale: 3× (borea/greek_borea/primordial_gaia) = 3×404
- `ledger_borea_hero_count = 0` (zero righe ledger con hero_id Borea sotto inventory live attivo)
- Request flow order della route: Borea reject è **step 1**, prima di qualsiasi flag/allowlist/inventory check.
- Shadow adapter + inventory live path entrambi bloccano `_FORBIDDEN_HERO_IDS = {borea, greek_borea, primordial_gaia}`.

## 13) Validator results (V16)

| Tag | Script | Check | Esito |
|---|---|---|---|
| V16-PREFLIGHT | `validate_af2n_v16_preflight.py` | 30 | **PASS** |
| AF2-N-INVENTORY-SCHEMA-MIGRATION | `validate_user_inventory_affinity_state_schema.py` | 24 | **PASS** |
| AF2-N-STAGE1-QA-SEED | `validate_stage1_qa_gift_inventory_seed.py` | 19 | **PASS** |
| AF2-N-INVENTORY-RETRY-APPLY | `validate_affinity_inventory_wiring_stage1_retry_apply_result.py` | 32 | **PASS** |
| AF2-N-INVENTORY-LIVE-MONITORING-V16 | `validate_affinity_inventory_live_monitoring_v16.py` | 32 | **PASS** |
| AF2-N-STAGE1-EXTENDED-MONITORING-V15 (V16-aware) | `validate_af2n_stage1_extended_monitoring_v15.py` | 24 | **PASS** |
| SAFETY-ROLLUP-K | `validate_collection_affinity_runtime_activation_rollup_v11.py` | 77 | **PASS** |
| ULTRA-COMBO-V16 | `validate_ultra_combo_v16_inventory_schema_seed_activate.py` | 39 | **PASS** |

## 14) Suite & baseline results

- Comando: `AFFINITY_GIFT_RUNTIME_ENABLED=… AFFINITY_GIFT_INVENTORY_WRITES_ENABLED=… python3 run_hero_skill_kit_validator_suite.py --include-baseline-diff`
- Risultato: **Overall PASS — 97/97** (`pass=97, fail=0, miss=0`)
- V12-V15 pre-inventory-on validators sono correttamente `[SUPERSEDED]` via il nuovo gate `SUPERSEDED_AFTER_INV_WRITES`.
- `RM1.32-PRE` (baseline diff `rm134b_axispatch_v6`) → **PASS** (nessuna deriva).
- Sommario JSON: `/app/backend/reports/suite_v16.json`.

## 15) API smoke (post-V16)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | **200** ✓ |
| `GET /api/heroes` count + no Borea | 100, no Borea | **100, no Borea** ✓ |
| `GET /api/affinity/gift-spend/canary-status` | flag=True, allowlist=50, cap=500, ledger=14, **inv=True, pts=True**, buffs=False, battle=False, combat=False, inv_writes_flag_dependency=present | **identico** ✓ |
| `POST /api/affinity/gift-spend` (Borea / greek_borea / primordial_gaia) | 404 | **404 / 404 / 404** ✓ |
| `POST /api/affinity/gift-spend` (non-allowlist) | 423 | **423** ✓ |
| `POST /api/affinity/gift-spend` (Stage1 QA + valid payload, FIRST time) | 200 result=applied_inventory_live, inventory_after exact, affinity_points_after exact | **identico (3 spend live)** ✓ |
| `POST /api/affinity/gift-spend` (same idem REPLAY) | 200 result=idempotent_replay, ledger_row_inserted=False, NO double mutation | **identico** ✓ |
| `POST /api/affinity/gift-spend` (Stage1 QA + qty > inv) | 412 result=inventory_insufficient, quantity preserved | **412, qty preserved** ✓ |

## 16) UI safety

- `combat.tsx`: **invariato** (`git diff --stat` vuoto).
- **Nessun pulsante "spend" pubblico aggiunto**, nessuna UI di inventory mutation esposta, nessuna route Borea esposta, nessun toggle battle/broad rollout, nessuna route frontend aggiunta. File-based routing Expo invariato.

## 17) Runtime / DB / Gacha / Roster / Catalog safety

- **Runtime env (in `/etc/supervisor/conf.d/backend.conf`)**:
  - `AFFINITY_GIFT_RUNTIME_ENABLED="true_explicit_affinity_gift_runtime_on"`
  - `AFFINITY_GIFT_CANARY_ALLOWLIST="user_canary_001,…,stage1_qa_047"` (50 utenti)
  - `AFFINITY_GIFT_CANARY_LEDGER_CAP="500"`
  - **`AFFINITY_GIFT_INVENTORY_WRITES_ENABLED="true_explicit_affinity_inventory_on"`** ← **NUOVO in V16**
- **DB**:
  - `gift_transaction_ledger`: 14 docs (11 pre-V16 + 3 live V16), tutti `canary=true`. 3 con `inventory_mutated=True && affinity_points_mutated=True`. 0 con `buffs_activated`, `battle_wiring_attached`, hero_id Borea.
  - `user_gift_inventory`: 50 docs Stage1 QA (`metadata.seed_task='V16'`). 0 con `quantity<0`. Decrement verificati esatti.
  - `user_affinity_state`: 3 docs (zeus/athena/ares), upsert con `metadata.seed_task='V16_live_write'`. Increment esatti.
  - 8 indici creati (4 + 4) inclusi 2 UNIQUE.
- **Gacha / Roster / Catalog / final_numbers**: nessuna modifica. Baseline `rm134b_axispatch_v6` PASS.
- **`battle_engine.py` / `battle_core.py` / `combat.tsx` / `game_systems.py` / `synergy_system.py`**: tutti `git diff --stat` vuoti.

## 18) Warnings / discrepanze

- ⚠️ **Modifica live a `affinity_gift_spend.py`**: il route è stato esteso con la logica V16 di mutazione (helper `_inventory_writes_enabled()`, branch inventory-live, envelope dinamico). Il flow è strettamente gated dai 3 vincoli (flag ON + allowlist + non-Borea); con flag OFF il comportamento è identico al V14 canary path. Diff registrato e visibile via `git diff -- backend/routes/affinity_gift_spend.py`.
- ⚠️ **Insufficient inventory limite Pydantic**: la validazione Pydantic limita `quantity ≤ 1000` (default schema). Test originale con `qty=9999` ha hit 400 (Pydantic) anziché 412 (logica route). Probe rifattorizzata con `qty=500` (dentro limite Pydantic, sopra balance 10) → 412 corretto.
- ⚠️ **Suite supersedence**: V12-V15 pre-inventory-on validators sono SUPERSEDED dal nuovo gate; questa è la coerenza richiesta dato che il loro contratto era `inventory_mutation_count==0` ora non più vero. SUPERSEDED ≠ FAIL ≠ skipped — è esplicito e tracciato.
- ⚠️ **K6/Locust ancora non installati**: come da V14-V15, fallback Python probe copre il surface. Install commands documentati in `af2n_k6_live_install_readiness_v1.json`.
- ⚠️ **Supervisor wiring**: ancora `READY_NOT_APPLIED`.

## 19) Final recommendation

✅ **ULTRA-COMBO V16 COMPLETATO con stato PASS** su tutti gli 8 sub-task + composite + suite (97/97) + baseline diff.

**Riepilogo blocker V15 risolti**:
- ✅ Schema `user_gift_inventory` creata + indicizzata (4 indici)
- ✅ Schema `user_affinity_state` creata + indicizzata (4 indici)
- ✅ 50 Stage1 QA users seeded
- ✅ Flag dedicato attivato in modo controllato
- ✅ Route esteso con flow atomico
- ✅ 3 controlled spend live verificati (inventory + affinity esatti)
- ✅ Idempotency live-verified (no double-decrement, no double-increment)
- ✅ Borea/non-allowlist/insufficient tutti gestiti correttamente (404/423/412)

**Invarianti hard tutti tenuti**: /api/heroes=100, Borea sempre 404 (243+ risposte in V16), no buffs, no battle wiring, no broad rollout, no public spend button, no Borea reveal, no gacha/roster/catalog mutation, battle_engine/battle_core/combat.tsx/synergy_system/game_systems invariati.

Sistema in `stage1_inventory_live_active_no_broad_rollout`. Decisione: `STAGE1_INVENTORY_LIVE_NO_BROAD_ROLLOUT`, `next_decision=extended_monitoring_or_stage2_prep`.

## 20) Suggested next tasks (richiedono approvazione esplicita)

### P1 — Validazione estesa post-attivazione
1. **AF2-N-STAGE1-INVENTORY-EXTENDED-MONITORING (24-72h)**: finestra estesa di monitoring sotto inventory wiring attivo, con probe orarie + DB cross-check + alerting su trigger.
2. **AF2-N-STAGE1-INVENTORY-LOAD-TEST**: stress test su sample dei 50 Stage1 QA users con concorrenza (race condition test su decrement).

### P2 — Infrastruttura
3. **AF2-L-K6-LIVE real**: install k6/locust seguendo le install commands documentate.
4. **OPS-C-SUPERVISOR-APPLY**: applicare auto-rollback supervisor wiring.

### P3 — Espansione e battle
5. **AF2-N-STAGE2-EXPANSION** (5-10% allowlist): solo dopo Stage1 inventory extended monitoring verde 24-72h.
6. **STACK-G full wiring**: collegare `global_modifier_cap_resolver` a `battle_engine.py` live. **Strettamente deferred**.

---

**Fine report ULTRA-COMBO V16.**
