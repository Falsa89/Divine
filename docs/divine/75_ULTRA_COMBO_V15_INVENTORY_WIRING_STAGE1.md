# ULTRA-COMBO V15 — Stage1 Extended Monitoring + Inventory Wiring Activate (Safe Block) + K6 Install Prep + Safety Rollup J

**Stato finale**: ✅ PASS (42/42 check composite + 115/115 suite con `--include-baseline-diff`)
**Data**: 2026-05-17 (sessione V15)
**Modalità runtime**: `stage1_allowlist_active_no_broad_rollout` — Stage1 attivo (50 utenti, cap 500), Inventory wiring **READY_NOT_ACTIVATED** (safe block), Battle wiring NON live, Broad rollout NON autorizzato.
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` (PASS).

---

## 1) File creati in V15

| Path | Ruolo |
|---|---|
| `/app/backend/scripts/run_af2n_v15_preflight.py` | Runner preflight V15 (genera artefatto) |
| `/app/backend/scripts/validate_af2n_v15_preflight.py` | Validator preflight (34 check) |
| `/app/backend/scripts/run_af2n_stage1_extended_monitoring_v15.py` | Probe Stage1 extended monitoring (90 campioni × 6 probe = 540 chiamate) |
| `/app/backend/scripts/validate_af2n_stage1_extended_monitoring_v15.py` | Validator monitoring extended (24 check) |
| `/app/backend/scripts/apply_affinity_inventory_wiring_stage1.py` | Driver attivazione inventory wiring (con SAFE BLOCK path) |
| `/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py` | Script rollback flag inventory (con `--dry-run`) |
| `/app/backend/scripts/validate_affinity_inventory_wiring_stage1_apply_result.py` | Validator apply result (21 check) |
| `/app/backend/scripts/run_affinity_inventory_live_monitoring_stage1.py` | Inventory live monitoring (safe block oggi) |
| `/app/backend/scripts/validate_affinity_inventory_live_monitoring_stage1.py` | Validator live monitoring (29 check) |
| `/app/backend/scripts/audit_af2n_k6_live_install_readiness.py` | Audit install K6/Locust (no install esecuzione) |
| `/app/backend/scripts/run_af2n_v15_k6_fallback_probe.py` | Fallback Python probe (1500 req) |
| `/app/backend/scripts/validate_af2n_v15_k6_fallback_probe.py` | Validator probe fallback (44 check) |
| `/app/backend/scripts/validate_af2n_v15_rollback_readiness.py` | Validator + runner rollback readiness (esegue live dry-run su 2 script) |
| `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v10.py` | Validator Safety Rollup J (65 check) |
| `/app/backend/scripts/validate_ultra_combo_v15_inventory_activate_stage1.py` | Composite V15 (42 check) |
| `/app/data/design/affinity/af2n_v15_preflight_result_v1.json` | Artefatto preflight |
| `/app/data/design/affinity/af2n_stage1_extended_monitoring_v15_result.json` | Artefatto Stage1 extended monitoring |
| `/app/data/design/affinity/affinity_gift_inventory_live_contract_v1.json` | Contratto inventory wiring live (request flow order, idempotency, rollback contract, preconditions ≥7, abort triggers ≥13, safe block path) |
| `/app/data/design/affinity/affinity_inventory_wiring_stage1_apply_result_v1.json` | Apply result: `READY_NOT_ACTIVATED`, `blocked_by_missing_inventory_source=true` |
| `/app/data/design/affinity/affinity_inventory_live_monitoring_stage1_result_v1.json` | Live monitoring result: `PASS_SAFE_BLOCK` |
| `/app/data/design/affinity/af2n_k6_live_install_readiness_v1.json` | K6 install audit: `READY_NOT_INSTALLED` + install commands documentati |
| `/app/data/design/affinity/af2n_v15_k6_fallback_probe_result_v1.json` | Probe fallback: 1500 req, 0 5xx, ledger unchanged |
| `/app/data/design/affinity/af2n_v15_rollback_readiness_result_v1.json` | Rollback readiness: 3 target rollback, tutti dry-run PASS |
| `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v10.json` | Safety Rollup J (rollup v10) |
| `/app/backend/reports/ultra_combo_v15_validator_summary_v1.json` | Sommario composite V15 |
| `/app/backend/reports/suite_v15.json` | Sommario suite V15 |

## 2) File modificati in V15

| Path | Modifica |
|---|---|
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Aggiunto blocco `# ULTRA-COMBO V15` (8 nuovi task validator) nella sezione OPTIONAL, dopo il blocco V14. Nessun check pre-esistente indebolito. |

**Nessuna modifica** a: `server.py`, `battle_engine.py`, `battle_core.py`, `combat.tsx`, `game_systems.py`, `synergy_system.py`, `affinity_gift_spend.py`, cataloghi gacha/roster, `final_numbers`, `/etc/supervisor/conf.d/backend.conf` (nessun env nuovo applicato).

## 3) Preflight V15

- File: `/app/data/design/affinity/af2n_v15_preflight_result_v1.json`
- Validator (34 check) → **PASS**
- **23 gate** tutti verdi, fra cui:
  - `api_health_200`, `api_heroes_count_100`, `api_heroes_no_borea`
  - `canary_status_200`, `canary_flag_on`, `stage1_allowlist_50`, `stage1_cap_500`
  - `ledger_within_cap`, `canary_only_writes`
  - `gift_spend_borea_404`, `gift_spend_non_allowlist_423`, `no_5xx_observed`
  - `battle_files_unchanged`, `inventory_mutation_count_zero`, `affinity_points_mutation_count_zero`, `buffs_count_zero`, `battle_wiring_count_zero`, `borea_hero_count_zero`
  - `rollback_script_stage1_ready`, `rollback_script_canary_ready`
  - `baseline_v6_diff_pass`, `suite_post_af2n_pass`, `ui_safety_pass`
  - `user_gift_inventory_collection_present_or_safely_blocked`
- **`inventory_activation_path` = `ready_not_activated_blocked_by_missing_inventory_source`** (registrato per il successivo apply)

## 4) Stage1 extended monitoring (AF2-N-STAGE1-EXTENDED-MONITORING-V15)

- **Campioni**: 90 × 100ms (elapsed 9.5s)
- **Per ogni campione**: 6 probe (`/health`, `/heroes`, `canary-status`, POST Borea, POST non-allowlist, POST idempotent replay)
- **Totale chiamate API**: 540
- **HTTP codici osservati**:
  - `/health`, `/heroes`, `canary-status` → tutti 90×200
  - POST Borea → 90×404
  - POST non-allowlist → 90×423 (mai 200)
  - POST replay idempotente (`canary_idem_0001`/`user_canary_001`) → 90×200, `ledger_row_inserted=false` 90/90
- **5xx totali**: 0
- **Trigger di abort**: 0 / 0
- **Ledger pre/post monitoring**: 11 / 11 (delta = 0; gate `ledger_delta_le_5` PASS)
- **`overall_status`**: PASS
- Validator (24 check) → **PASS**

## 5) Inventory wiring apply summary (AF2-N-INVENTORY-WIRING ACTIVATE)

- **Stato attivazione**: `READY_NOT_ACTIVATED`
- **Activation applied**: `False`
- **Flag dedicato**: `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED` — **MAI impostato** in `backend.conf` (verificato via grep)
- **Blocked by**:
  - `user_gift_inventory_collection_present = false` (collection non esistente)
  - `user_affinity_state_collection_present = false` (collection non esistente)
- **`blocked_by_missing_inventory_source = true`**
- **Contratto V1 prodotto**: `/app/data/design/affinity/affinity_gift_inventory_live_contract_v1.json` con:
  - 12 step di request flow order (Borea 1°, runtime flag, allowlist, idempotency, gift existence, inventory check, multi-doc tx, dec/inc, commit, response)
  - 5 regole idempotency contract
  - 3 regole economy cap contract
  - 4 regole rollback/compensation contract
  - 8 required preconditions BEFORE activation
  - 13 abort triggers post-activation
  - safe-block path con 6 remediation steps documentati
- **Preconditions evaluated**: 7 totali, 5 pass + 2 fail (le due collection mancanti) → SAFE BLOCK attivato secondo contratto V1
- Validator (21 check) → **PASS**

## 6) Inventory live monitoring / blocked summary (AF2-N-INVENTORY-LIVE-MONITORING)

- **Stato monitoring**: `PASS_SAFE_BLOCK` (path safe-block atteso)
- **Activation state recorded**: `READY_NOT_ACTIVATED`
- **Flag currently set**: `False`
- **Probe live osservate**:
  - canary-status: `inventory_mutation_enabled=False`, `affinity_points_mutation_enabled=False`, `buffs_enabled=False`, `battle_runtime_attached=False`
  - `/api/heroes` count = 100
  - POST Borea → 404
  - POST non-allowlist → 423
- **DB check**:
  - `ledger_inventory_mutated_rows = 0`
  - `ledger_affinity_points_mutated_rows = 0`
  - `ledger_buffs_activated_rows = 0`
  - `ledger_battle_wiring_rows = 0`
- **Triggers fired**: 0 / 0
- Validator (29 check) → **PASS**

## 7) K6 install prep / fallback summary

- **K6 binary present**: `False` (`shutil.which('k6')` = None)
- **Locust binary present**: `False`
- **`overall_status` audit**: `READY_NOT_INSTALLED`
- **Install commands documentati (NON eseguiti, network/permessi)**:
  - K6 via apt: gpg key + keyring + repo + apt install (5 step)
  - Locust via pip: `pip3 install locust==2.31.5`
- **Safety notes (4)**: non installare auto, approva install in task ops separato, verifica versione, mantieni fallback Python.
- **Test script K6/Locust presenti**: `/app/loadtests/af2n_stage1_allowlist.k6.js` e `_locust.py` (da V14).
- **Fallback Python probe**: 1500 richieste (150 × 10 label):
  - `empty`/`no_idem`/`malformed_idem`/`negative_qty`/`huge_qty`/`stage1_qa_blocked_path` → tutti 150×423 ✓
  - `borea`/`greek_borea`/`primordial_gaia` → tutti 150×404 ✓
  - `idempotent_replay` → 150×200, `ledger_row_inserted=false` 150/150
- **5xx totali**: 0, **codici inattesi**: 0, **duplicate inserts**: 0
- **Ledger pre/post probe**: 11 / 11 (`ledger_row_count_unchanged=true`)
- **Regression GET (7 endpoint)**: tutti `ok=true`
- Validator (44 check) → **PASS**

## 8) Rollback readiness V15

- File: `/app/data/design/affinity/af2n_v15_rollback_readiness_result_v1.json`
- **Stage1-specific rollback** (`rollback_af2n_stage1_1pct_allowlist.py`) → dry-run **exit 0**, ripristina V12 canary (3/20)
- **Inventory wiring rollback** (`rollback_affinity_inventory_wiring_stage1.py`) → dry-run **exit 0** (oggi è no-op poiché flag mai impostato; pronto a strip-and-restart quando attivato)
- **Canary fallback rollback** (`/app/ops/rollback_af2n_canary.sh`) → presente
- **Pre-stage1 backups presenti**: True (backup V14: `backend.conf.pre-stage1.20260517T231412Z.bak`)
- **`can_disable_inventory_flag_without_disabling_stage1 = true`** (script inventory tocca solo il proprio env, lascia intatti `AFFINITY_GIFT_CANARY_ALLOWLIST` e `AFFINITY_GIFT_CANARY_LEDGER_CAP`)
- **`overall_status`**: PASS (7/7 check)
- `rollback_executed=false`

## 9) Safety Rollup J (rollup v10)

- File: `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v10.json`
- `report_id=collection_affinity_runtime_activation_readiness_rollup_v10`, `task_origin=SAFETY-ROLLUP-J`, `supersedes=…rollup_v9`.
- Stato globale: `overall_runtime_activation_state="stage1_allowlist_active_no_broad_rollout"`, `go_no_go_decision="STAGE1_ONLY_NO_BROAD_ROLLOUT"`.
- `next_decision="inventory_activate_retry"`.
- 5 operator signoff = true + `final_user_runtime_approval_present=true`.
- `AF2N_executed=true`, `AF2N_stage1_status="APPLIED_PASS"`, `AF2N_stage1_extended_monitoring_status="PASS"`, `inventory_wiring_state="ready_not_activated"`, `AF2N_inventory_blocked_by_missing_inventory_source=true`, `AF2N_inventory_live_monitoring_status="PASS_SAFE_BLOCK"`, `k6_live_install_readiness_status="READY_NOT_INSTALLED"`, `k6_v15_fallback_probe_status="PASS"`, `v15_rollback_readiness_status="PASS"`.
- **21 subsystem**, tutti con status atteso.
- **16 abort trigger** documentati, tutti `triggered=false`.
- Validator (65 check) → **PASS**.

## 10) Borea safety

- `/api/heroes` non contiene `borea`, `greek_borea`, `primordial_gaia` (verificato 90× extended monitoring + 1× smoke finale).
- `POST /api/affinity/gift-spend` con `hero_id ∈ {borea, greek_borea, primordial_gaia}`:
  - Extended monitoring V15: 90× Borea = 90×404
  - K6 fallback V15: 150× Borea + 150× greek_borea + 150× primordial_gaia = 450×404
  - Smoke finale: 3×404
  - **Totale V15: 543 risposte Borea, tutte 404, zero fughe**
- `GET /api/affinity/gifts/by-element/dark/by-faction/borea` → 404 (smoke).
- `ledger_borea_hero_count = 0` (zero righe ledger con hero_id Borea).
- Adapter shadow + contratto inventory live entrambi includono `hidden_aliases_blocked=['borea','greek_borea','primordial_gaia']`.
- Request flow order del contratto V1 inserisce "Reject Borea hero_id (404) BEFORE any other check" come **passo 1**.

## 11) Validator results (V15)

| Tag | Script | Check | Esito |
|---|---|---|---|
| V15-PREFLIGHT | `validate_af2n_v15_preflight.py` | 34 | **PASS** |
| AF2-N-STAGE1-EXTENDED-MONITORING-V15 | `validate_af2n_stage1_extended_monitoring_v15.py` | 24 | **PASS** |
| AF2-N-INVENTORY-WIRING-APPLY | `validate_affinity_inventory_wiring_stage1_apply_result.py` | 21 | **PASS** |
| AF2-N-INVENTORY-LIVE-MONITORING | `validate_affinity_inventory_live_monitoring_stage1.py` | 29 | **PASS** |
| AF2-L-K6-V15-FALLBACK | `validate_af2n_v15_k6_fallback_probe.py` | 44 | **PASS** |
| V15-ROLLBACK-READINESS | `validate_af2n_v15_rollback_readiness.py` | 7 | **PASS** |
| SAFETY-ROLLUP-J | `validate_collection_affinity_runtime_activation_rollup_v10.py` | 65 | **PASS** |
| ULTRA-COMBO-V15 | `validate_ultra_combo_v15_inventory_activate_stage1.py` | 42 | **PASS** |

## 12) Suite & baseline results

- Comando: `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on python3 run_hero_skill_kit_validator_suite.py --include-baseline-diff`
- Risultato: **Overall: PASS** — `pass=115, fail=0, miss=0`
- Tutti gli 8 nuovi validator V15 aggiunti in `OPTIONAL` con status PASS.
- I pre-AF2N validator (V6→V11) restano correttamente `[SUPERSEDED]`.
- `RM1.32-PRE` (baseline diff vs `rm134b_axispatch_v6`) → **PASS** (nessuna deriva).
- Sommario JSON: `/app/backend/reports/suite_v15.json`.

## 13) API smoke (post-V15)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | **200** ✓ |
| `GET /api/heroes` count + no Borea | 100, no Borea | **100, no Borea** ✓ |
| `GET /api/affinity/gifts` | 200 | **200** ✓ (via regression V15) |
| `GET /api/affinity/gift-spend/canary-status` | flag=True, allowlist=50, cap=500, ledger=11, **inv/pts/buffs/battle=False** | **identico** ✓ |
| `POST /api/affinity/gift-spend` (Borea) | 404 | **404** ✓ |
| `POST /api/affinity/gift-spend` (greek_borea) | 404 | **404** ✓ |
| `POST /api/affinity/gift-spend` (primordial_gaia) | 404 | **404** ✓ |
| `POST /api/affinity/gift-spend` (non-allowlist) | 423 | **423** ✓ |
| `POST /api/affinity/gift-spend` (canary user idempotent replay) | 200 result=idempotent_replay, no new row | **200 idempotent_replay, ledger_row_inserted=False, tx=tx_canary_34fb3539a8164210** ✓ |
| `GET /api/affinity/gifts/by-element/dark/by-faction/greek` | 200 | **200** ✓ |
| `GET /api/affinity/gifts/by-element/dark/by-faction/borea` | 404 | **404** ✓ |
| `GET /api/affinity/gifts/by-element/tides/by-faction/greek` | 404 | **404** ✓ |

## 14) UI safety

- `combat.tsx`: **invariato** (`git diff --stat` vuoto).
- UI safety grep (V15 preflight): nessun `borea` literal, nessun `gift-spend.*onPress`, nessun `spend_gift_button`, nessun `broad_rollout`, nessun `battle_runtime_toggle` in tutti i `.tsx` di `/app/frontend/app/`.
- **Nessun pulsante "spend" pubblico aggiunto**, nessuna UI di inventory mutation, nessuna route Borea esposta, nessun toggle di battle runtime, nessun toggle di broad rollout.
- Nessuna route frontend nuova aggiunta. File-based routing Expo invariato.

## 15) Runtime / DB / Gacha / Roster / Catalog safety

- **Runtime** (env vars in supervisord, **invariati da V14**):
  - `AFFINITY_GIFT_RUNTIME_ENABLED="true_explicit_affinity_gift_runtime_on"`
  - `AFFINITY_GIFT_CANARY_ALLOWLIST="user_canary_001,…,stage1_qa_047"` (50 utenti)
  - `AFFINITY_GIFT_CANARY_LEDGER_CAP="500"`
  - **`AFFINITY_GIFT_INVENTORY_WRITES_ENABLED` NON impostato** (verificato via grep — flag inventory OFF)
- **DB**:
  - `gift_transaction_ledger`: **11 documenti**, **tutti** `canary=true` (stato V12, stabile attraverso V13/V14/V15)
  - `inventory_mutated:true` → 0 doc, `affinity_points_mutated:true` → 0 doc, `buffs_activated:true` → 0 doc, `battle_wiring_attached:true` → 0 doc, `hero_id ∈ {borea/greek_borea/primordial_gaia}` → 0 doc
  - **`user_gift_inventory` collection NON presente** → safe-block path obbligatorio onorato
  - **`user_affinity_state` collection NON presente** → idem
  - `inventory` collection generica (10 docs) presente ma con schema `{item_id, user_id, quantity}` incompatibile col contratto V1; **NON usata** dal route live
- **Gacha / Roster / Catalog / final_numbers**: nessuna modifica. Baseline `rm134b_axispatch_v6` PASS.
- **`battle_engine.py` / `battle_core.py` / `combat.tsx` / `game_systems.py` / `synergy_system.py` / `affinity_gift_spend.py`**: tutti `git diff --stat` vuoti.

## 16) Warning / discrepanze

- ⚠️ **Inventory wiring NON attivato (SAFE BLOCK intenzionale)**: i prerequisiti del contratto V1 richiedono le collection `user_gift_inventory` e `user_affinity_state` che non esistono in MongoDB. Il path safe-block è esplicitamente permesso dal `ULTRA_COMBO_PROMPT_EMERGENT.txt` V15: «If activation unsafe, produce READY_NOT_ACTIVATED report and keep flag OFF». Per attivare nel futuro serve un task `SCHEMA-MIGRATION-USER-INVENTORY` + seed di Stage1 QA users.
- ⚠️ **K6/Locust ancora non installati**: audit `READY_NOT_INSTALLED`; install commands documentati ma non eseguiti per evitare rischio network/permessi. Fallback Python probe da 1500 req copre lo stesso surface funzionalmente.
- ⚠️ **Supervisor wiring**: ancora `READY_NOT_APPLIED` come da V12-V14. Task P2 futuro `OPS-C-SUPERVISOR-APPLY`.
- ⚠️ **Supersedence env var**: per ottenere `Overall: PASS` nella suite occorre esportare `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on` nella shell (è già in `backend.conf` ma la suite gira fuori dal contesto supervisord).

## 17) Final recommendation

✅ **ULTRA-COMBO V15 COMPLETATO con stato PASS** su tutti gli 8 sub-task + composite V15 + suite completa (115/115) + baseline diff.

- **Stage1 stabile dopo extended monitoring**: 90 campioni × 6 probe = 540 chiamate live + 1500 K6 fallback + smoke = >2050 chiamate API in V15 senza una singola anomalia.
- **Inventory wiring**: contratto live `affinity_gift_inventory_live_contract_v1.json` completo (12 step request flow + idempotency + economy caps + rollback/compensation + 8 preconditions + 13 abort triggers + safe block path). Apply driver ha correttamente eseguito il path **READY_NOT_ACTIVATED** perché le collection `user_gift_inventory` + `user_affinity_state` mancano. Flag dedicato `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED` **MAI impostato**.
- **Inventory live monitoring**: `PASS_SAFE_BLOCK` conferma che lo stato live continua a riportare `inventory/pts/buffs/battle = False` e il ledger non ha mutazioni di alcun tipo.
- **K6**: install plan documentato + 1500-req fallback PASS.
- **Rollback readiness V15 PASS**: 3 target rollback documentati e dry-runnabili, possibilità di disabilitare solo il flag inventory senza toccare Stage1.
- **Tutti gli invarianti hard tenuti**: `/api/heroes`=100, Borea=404 ovunque (543 risposte V15), ledger=11≤500, no inventory/points/buffs/battle mutation, file battle/combat/synergy/game/route invariati, broad rollout NOT authorized, nessun pulsante spend pubblico.
- **Nessun abort trigger scattato**.

Sistema in stato `stage1_allowlist_active_no_broad_rollout` con `inventory_wiring_state=ready_not_activated`. Decisione: `STAGE1_ONLY_NO_BROAD_ROLLOUT`, `next_decision=inventory_activate_retry`.

## 18) Suggested next tasks (richiedono approvazione esplicita)

### P1 — Sblocco inventory activation
1. **SCHEMA-MIGRATION-USER-INVENTORY**: creare le collection MongoDB `user_gift_inventory` (`{user_id, gift_id, quantity, updated_at_utc}`) e `user_affinity_state` (`{user_id, hero_id, affinity_points, updated_at_utc}`); seedare i 50 Stage1 QA users con bilanci realistici; verificare il supporto di multi-document transactions sul cluster MongoDB. Prerequisito: nuovo messaggio utente esplicito.
2. **AF2-N-INVENTORY-WIRING ACTIVATE retry** (post-#1): ri-eseguire `apply_affinity_inventory_wiring_stage1.py`; se tutti i preconditions verdi, **flippare** il flag `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED=true_explicit_affinity_inventory_on` in `backend.conf` (con backup pre-flip), aggiornare `affinity_gift_spend.py` per implementare i 12 step del request flow order del contratto V1 in transazione atomica, e validare con `run_affinity_inventory_live_monitoring_stage1.py` su 1-3 controlled spends.
3. **AF2-N-STAGE1-EXTENDED-MONITORING-24-72H**: finestra di monitoring estesa (multi-ora) prima di Stage2.

### P2 — Infrastruttura
4. **AF2-L-K6-LIVE real**: install k6/locust seguendo le install commands documentate in `af2n_k6_live_install_readiness_v1.json`; eseguire `af2n_stage1_allowlist.k6.js` real load test.
5. **OPS-C-SUPERVISOR-APPLY**: applicare auto-rollback supervisor wiring (oggi `READY_NOT_APPLIED`).

### P3 — Espansione / Battle
6. **AF2-N-STAGE2-EXPANSION** (~5-10% allowlist): solo dopo Stage1 extended 24-72h verde + inventory live verified.
7. **STACK-G full wiring**: collegare `global_modifier_cap_resolver` a `battle_engine.py` live. **Strettamente deferred**.

---

**Fine report ULTRA-COMBO V15.**
