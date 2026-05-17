# ULTRA-COMBO V14 — Stage1 Apply + Stage1 Monitoring + Inventory Shadow + K6 Prep3 + Safety Rollup I

**Stato finale**: ✅ PASS (40/40 check composite + 107/107 suite con `--include-baseline-diff`)
**Data**: 2026-05-17 (sessione V14)
**Modalità runtime**: `stage1_allowlist_active_no_broad_rollout` — AF2-N Stage1 applicato (50 utenti, cap 500); NESSUN broad rollout; NESSUNA inventory mutation live; NESSUN battle wiring.
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` (PASS).

---

## 1) File creati in V14

| Path | Ruolo |
|---|---|
| `/app/backend/scripts/validate_af2n_v14_preflight.py` | Validator preflight V14 (33 gate) |
| `/app/backend/scripts/apply_af2n_stage1_1pct_allowlist.py` | Script orchestratore di Stage1 apply (preflight → backup conf → riscrittura env → restart → smoke) |
| `/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py` | Script rollback Stage1 → V12 canary (con `--dry-run`) |
| `/app/backend/scripts/validate_af2n_stage1_1pct_apply_result.py` | Validator apply result |
| `/app/backend/scripts/run_af2n_stage1_monitoring_window.py` | Monitoring window probe Stage1 (60 campioni × 100ms, 7 probe ciascuno) |
| `/app/backend/scripts/validate_af2n_stage1_monitoring_window.py` | Validator monitoring window Stage1 |
| `/app/backend/data/affinity_gift_inventory_shadow_adapter.py` | Adapter inventory shadow/dry-run (`shadow_inventory_apply`) — inert, contratto di rollback documentato |
| `/app/backend/scripts/run_affinity_gift_inventory_shadow_probe.py` | Probe shadow su 9 scenari (Borea, insufficient_inv, ecc.) |
| `/app/backend/scripts/validate_affinity_gift_inventory_shadow_wiring.py` | Audit + validator shadow adapter (no import live, no DB write call sites) |
| `/app/loadtests/af2n_stage1_allowlist.k6.js` | Script K6 (NON eseguito oggi, k6 binary mancante) |
| `/app/loadtests/af2n_stage1_allowlist_locust.py` | Script Locust (NON eseguito oggi, locust mancante) |
| `/app/backend/scripts/validate_af2n_stage1_k6_live_test_plan.py` | Validator del piano K6 Live Prep3 |
| `/app/backend/scripts/run_af2n_stage1_k6_prep_probe.py` | Probe fallback Python (600 req) |
| `/app/backend/scripts/validate_af2n_stage1_k6_prep_probe.py` | Validator del result probe |
| `/app/backend/scripts/validate_af2n_stage1_rollback_readiness.py` | Validator rollback readiness (esegue live dry-run) |
| `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v9.py` | Validator Safety Rollup I |
| `/app/backend/scripts/validate_ultra_combo_v14_stage1_inventoryshadow.py` | Composite V14 (orchestratore + invarianti live + DB + git diff) |
| `/app/data/design/affinity/af2n_v14_preflight_result_v1.json` | Artefatto preflight |
| `/app/data/design/affinity/af2n_stage1_1pct_apply_result_v1.json` | Artefatto apply result |
| `/app/data/design/affinity/af2n_stage1_monitoring_window_result_v1.json` | Artefatto monitoring window |
| `/app/data/design/affinity/affinity_gift_inventory_shadow_wiring_result_v1.json` | Artefatto shadow probe |
| `/app/data/design/affinity/af2n_stage1_k6_live_test_plan_v1.json` | Piano K6 Prep3 |
| `/app/data/design/affinity/af2n_stage1_k6_prep_probe_result_v1.json` | Artefatto K6 fallback probe |
| `/app/data/design/affinity/af2n_stage1_rollback_readiness_result_v1.json` | Artefatto rollback readiness |
| `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v9.json` | Safety Rollup I (rollup v9) |
| `/app/backend/reports/ultra_combo_v14_validator_summary_v1.json` | Sommario composite V14 |
| `/app/backend/reports/suite_v14.json` | Sommario suite completa V14 |
| `/app/backups/backend.conf.pre-stage1.20260517T231412Z.bak` | Backup pre-Stage1 di `backend.conf` |

## 2) File modificati in V14

| Path | Modifica |
|---|---|
| `/etc/supervisor/conf.d/backend.conf` | `AFFINITY_GIFT_CANARY_ALLOWLIST`: 3 utenti → 50 utenti (`user_canary_001/002/003` + `stage1_qa_001…stage1_qa_047`). `AFFINITY_GIFT_CANARY_LEDGER_CAP`: 20 → 500. **Solo env vars; nessun cambio a `command`, `directory`, `autostart`, `autorestart`, log paths.** |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Aggiunto blocco `# ULTRA-COMBO V14` (9 nuovi task validator) nella sezione OPTIONAL. Nessun check pre-esistente indebolito. |

**Nessuna modifica** a: `server.py`, `battle_engine.py`, `battle_core.py`, `combat.tsx`, `game_systems.py`, `synergy_system.py`, `affinity_gift_spend.py`, cataloghi gacha/roster, file `final_numbers`.

## 3) Preflight V14

- File: `/app/data/design/affinity/af2n_v14_preflight_result_v1.json`
- Validator (33 check) → **PASS**
- Gate critici tutti OK:
  - `api_heroes_count_100`, `api_heroes_no_borea`
  - `canary_status_200`, `canary_flag_on`, `canary_ledger_within_cap`, `canary_only_writes`
  - `gift_spend_borea_404`, `gift_spend_non_allowlist_423`, `no_5xx_observed`
  - `battle_files_unchanged` (git diff vuoto su tutti i 5 file critici)
  - `stage1_plan_present`, `monitoring_window_pass`
  - `all_5_operator_signoffs_true`, `final_user_runtime_approval_present`
  - `inventory_mutation_count_zero`, `affinity_points_mutation_count_zero`, `buffs_count_zero`, `battle_wiring_count_zero`, `borea_hero_count_zero`
  - `rollback_script_ready`, `suite_post_af2n_pass`
- `explicit_user_stage1_approval=true` registrato (il messaggio V14 dell'utente è l'approvazione esplicita richiesta dal prerequisito V13).
- `stage1_apply_authorized=true`, `do_not_apply_today=false`.

## 4) Stage1 apply summary

- **Backup pre-Stage1**: `/app/backups/backend.conf.pre-stage1.20260517T231412Z.bak` (copia esatta di `backend.conf` PRIMA della modifica).
- **Modifica applicata** a `/etc/supervisor/conf.d/backend.conf`:
  - `AFFINITY_GIFT_CANARY_ALLOWLIST`: `"user_canary_001,user_canary_002,user_canary_003"` → `"user_canary_001,user_canary_002,user_canary_003,stage1_qa_001,…,stage1_qa_047"` (50 totali, tutti ID sintetici interni QA, **nessun utente reale**, **nessuna affiliazione Borea**)
  - `AFFINITY_GIFT_CANARY_LEDGER_CAP`: `"20"` → `"500"`
- **Restart**: `supervisorctl reread && update && restart backend`. Il client subprocess ha sforato il timeout di 20s (a causa del `startsecs=20` + `pip install` al boot) **ma supervisor ha completato correttamente il restart**; backend ripreso in RUNNING dopo ~28s. Nessun rollback richiesto.
- **Verifica live post-apply** (immediata):
  - `GET /api/affinity/gift-spend/canary-status` → `canary_allowlist_size=50, canary_ledger_cap=500, ledger_total_rows=11, feature_flag=true`
  - `GET /api/heroes` → 100 eroi, nessuna fuga Borea
  - `POST /api/affinity/gift-spend` (Borea) → **404** ✓
  - `POST /api/affinity/gift-spend` (non-allowlist) → **423** ✓
- Validator apply result (18 check) → **PASS**
- Stato globale: `overall_state="stage1_allowlist_active_no_broad_rollout"`.

## 5) Stage1 monitoring summary (AF2-N-STAGE1-MONITORING-WINDOW)

- **Campioni**: 60 × 100ms (elapsed 6.91s)
- **Per ogni campione**: 7 probe (`/health`, `/heroes`, `canary-status`, POST empty, POST Borea, POST non-allowlist, POST idempotent replay)
- **HTTP codici osservati**:
  - `/health`, `/heroes`, `canary-status` → 60×200 ciascuno
  - POST empty → 60×423
  - POST Borea → 60×404
  - POST non-allowlist → 60×423 (mai 200)
  - POST replay idempotente (`canary_idem_0001`/`user_canary_001`) → 60×200, **mai** una nuova riga ledger
- **5xx totali**: 0
- **Trigger di abort**: 0 / 0
- **Allowlist size verificato live**: **50** (`observed_allowlist_size_must_be_50=true`)
- **Ledger pre/post monitoring**: 11 / 11 (invariato, sempre `canary=true`)
- **`overall_status`**: PASS
- Validator (28 check) → **PASS**

## 6) Inventory shadow summary (AF2-N-INVENTORY-WIRING-SHADOW)

- Adapter `/app/backend/data/affinity_gift_inventory_shadow_adapter.py` con entry `shadow_inventory_apply(...)`.
- **Probe su 9 scenari**:
  - `normal_ok` → `would_decrement_inventory=1`, `would_increment_affinity=5`, `would_have_status='applied_shadow_only'`, `runtime_attached=False`, `db_write=False`, rollback_contract completo
  - `normal_zero_qty` → `applied_shadow_only`, dec=0
  - `insufficient_inv` (inv=2, qty=5) → `pre_check_pass=False`, `would_have_status='rejected_shadow_only'`, dec=0
  - `huge_qty`, `negative_qty` → gestiti correttamente
  - `borea`, `greek_borea`, `primordial_gaia` → tutti `borea_filtered=true`, dec=0, would_have_status='borea_filtered'
  - `stage1_qa_user` → applied_shadow_only ma sempre `db_write=False`
- **Invarianti**:
  - `ledger_unchanged`=true (pre/post probe identici)
  - `all_runtime_attached_false`=true
  - `all_shadow_only_true`=true
  - `all_db_write_false`=true (envelope dichiara `db_write:false` su tutti)
  - `borea_filtered_correctly`=true
  - `rollback_contract_present_all`=true (su tutti gli output)
  - `insufficient_inv_rejected`=true
  - `normal_ok_applied_shadow`=true
- **NESSUN** import dell'adapter da: `affinity_gift_spend.py`, `battle_engine.py`, `battle_core.py`, `combat.tsx` (verificato).
- **NESSUN** import `motor` / `pymongo`, **NESSUNA** chiamata `.insert_one(` / `.update_one(` / `.delete_one(` (regex su call sites).
- Audit + validator (33 check) → **PASS**

## 7) K6 prep summary (AF2-L-K6-PREP3)

- **Modalità**: `python_fallback_stage1_active` (k6/locust non installati; piano K6/Locust comunque generato).
- **File K6/Locust**: `/app/loadtests/af2n_stage1_allowlist.k6.js`, `/app/loadtests/af2n_stage1_allowlist_locust.py` (pronti per uso futuro).
- **Probe Python fallback**: 600 richieste totali (60 per 10 label):
  - `empty`, `no_idem`, `malformed_idem`, `negative_qty`, `huge_qty`, `stage1_qa_user_blocked_path` → tutti 60×423 ✓
  - `borea`, `greek_borea`, `primordial_gaia` → tutti 60×404 ✓
  - `idempotent_replay` (`canary_idem_0001`/`user_canary_001`) → 60×200, mai `ledger_row_inserted=true`
- **5xx totali**: 0
- **Codici inattesi totali**: 0
- **Duplicate inserts**: 0
- **Ledger pre/post probe**: 11 / 11 (`ledger_row_count_unchanged=true`)
- **Regression GET** (7 endpoint): tutti `ok=true`
- Validator plan (22 check) + validator probe (43 check) → entrambi **PASS**

> ⚠️ Nota tecnica: una prima esecuzione della probe K6 prep3 conteneva un label `stage1_qa_user_malformed` con payload accidentalmente valido per uno Stage1 QA user allowlisted, che ha creato 1 riga ledger spuria. Identificata immediatamente, la riga è stata rimossa (`delete_one` mirato su `idempotency_key='shortbad'`, `user_id='stage1_qa_007'`) e la probe è stata rifattorizzata in `stage1_qa_user_blocked_path` con body sempre invalido. Ledger riportato a 11. Documentato in sez. 15.

## 8) Rollback readiness (AF2-N-STAGE1-ROLLBACK-READINESS)

- File: `/app/data/design/affinity/af2n_stage1_rollback_readiness_result_v1.json`
- **Script primario**: `/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py` (ripristina backup pre-Stage1, restart backend)
- **Script fallback**: `/app/ops/rollback_af2n_canary.sh` (rollback completo a pre-AF2-N)
- **Backup presente e leggibile**: `/app/backups/backend.conf.pre-stage1.20260517T231412Z.bak`
- **Dry-run eseguito live**: `python3 rollback_af2n_stage1_1pct_allowlist.py --dry-run` → exit 0, `has_allowlist_env=True, has_cap_env=True, backup_readable=True`, **verdict=PASS**
- **Abort trigger documentati (≥12)**: 5xx>0.5%, Borea≠404, non-allowlist=200, replay duplicate insert, ledger>500, p95>800ms, inventory/points/buffs/battle mutation, hero_id Borea in ledger, battle file diff
- **Rollback procedure documentata (7 step)**: rollback script → wait health → verify allowlist=3, cap=20 → heroes=100 → Borea=404 → non-allowlist=423 → fallback canary rollback se fallisce
- `rollback_executed=false` (tutti i gate V14 PASS)
- Validator (19 check) → **PASS**

## 9) Safety Rollup I (rollup v9)

- File: `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v9.json`
- `report_id=collection_affinity_runtime_activation_readiness_rollup_v9`, `task_origin=SAFETY-ROLLUP-I`, `supersedes=…rollup_v8`.
- Stato globale: `overall_runtime_activation_state="stage1_allowlist_active_no_broad_rollout"`, `go_no_go_decision="STAGE1_ONLY_NO_BROAD_ROLLOUT"`.
- 5 operator signoff = true + `final_user_runtime_approval_present=true`.
- `AF2N_executed=true`, `AF2N_canary_status="PASS"`, `AF2N_stage1_status="APPLIED_PASS"`, `AF2N_monitoring_window_status="PASS"`, `AF2N_stage1_monitoring_window_status="PASS"`, `AF2N_inventory_wiring_state="SHADOW_ADAPTER_READY_NOT_WIRED"`, `k6_live_prep3_status="PASS"`, `stage1_rollback_readiness_status="PASS"`.
- **14 subsystem**, tutti con status atteso (APPLIED_PASS / PASS / PASS_SHADOW_READY_NOT_WIRED / READY / NO_GO per battle / GO per borea).
- **13 abort trigger** documentati, tutti `triggered=false`.
- `rollback_executed=false`.
- Validator (65 check) → **PASS**

## 10) Borea safety

- `/api/heroes` non contiene `borea`, `greek_borea`, `primordial_gaia` (verificato 60× in Stage1 monitoring + 1× in smoke finale).
- `POST /api/affinity/gift-spend` con `hero_id ∈ {borea, greek_borea, primordial_gaia}`:
  - V14 Stage1 monitoring: 60× Borea = 60×404
  - V14 K6 prep3: 60× Borea + 60× greek_borea + 60× primordial_gaia = 180×404
  - V14 smoke finale: 3× = 3×404
  - **Totale V14: 243 risposte Borea, tutte 404, zero fughe**
- `GET /api/affinity/gifts/by-element/dark/by-faction/borea` → 404, `/by-element/tides/by-faction/greek` → 404 (smoke + K6 prep3).
- `ledger_borea_hero_count = 0` (zero righe ledger con hero_id Borea).
- Adapter shadow gestisce `borea`/`greek_borea`/`primordial_gaia` con `borea_filtered=true`, `would_decrement_inventory=0`, `would_increment_affinity=0`.
- `hidden_aliases_blocked=['borea','greek_borea','primordial_gaia']` in ogni artefatto V14.

## 11) Validator results (V14)

| Tag | Script | Check | Esito |
|---|---|---|---|
| V14-PREFLIGHT | `validate_af2n_v14_preflight.py` | 33 | **PASS** |
| AF2-N-STAGE1-APPLY | `validate_af2n_stage1_1pct_apply_result.py` | 18 | **PASS** |
| AF2-N-STAGE1-MONITORING | `validate_af2n_stage1_monitoring_window.py` | 28 | **PASS** |
| AF2-N-INVENTORY-WIRING-SHADOW | `validate_affinity_gift_inventory_shadow_wiring.py` | 33 | **PASS** |
| AF2-L-K6-PREP3-PLAN | `validate_af2n_stage1_k6_live_test_plan.py` | 22 | **PASS** |
| AF2-L-K6-PREP3-PROBE | `validate_af2n_stage1_k6_prep_probe.py` | 43 | **PASS** |
| AF2-N-STAGE1-ROLLBACK-READY | `validate_af2n_stage1_rollback_readiness.py` | 19 | **PASS** |
| SAFETY-ROLLUP-I | `validate_collection_affinity_runtime_activation_rollup_v9.py` | 65 | **PASS** |
| ULTRA-COMBO-V14 | `validate_ultra_combo_v14_stage1_inventoryshadow.py` | 40 | **PASS** |

## 12) Suite & baseline results

- Comando: `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on python3 run_hero_skill_kit_validator_suite.py --include-baseline-diff`
- Risultato: **Overall: PASS** — `pass=107, fail=0, miss=0`
- Tutti i 9 nuovi validator V14 presenti in `OPTIONAL` con status PASS.
- I pre-AF2N validator (V6→V11) restano correttamente `[SUPERSEDED]`.
- `RM1.32-PRE` (baseline diff) → **PASS** (nessuna deriva da `rm134b_axispatch_v6`).
- Sommario JSON: `/app/backend/reports/suite_v14.json`.

## 13) API smoke (post-V14)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | **200** ✓ |
| `GET /api/heroes` count | 100, no Borea | **100, no Borea** ✓ |
| `GET /api/affinity/gifts` | 200 | **200** ✓ |
| `GET /api/affinity/gift-spend/canary-status` | flag=True, allowlist=50, cap=500, ledger=11, combat=False, battle=False, inv=False, pts=False, buf=False | **identico** ✓ |
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
- Nessun import nell'UI di: `affinity_gift_inventory_shadow_adapter`, `inventory_wiring_preview_adapter`, `global_modifier_cap_resolver`, `global_modifier_cap_battle_preview_adapter`.
- **Nessun pulsante "spend" pubblico aggiunto**, nessuna UI di inventory mutation, nessuna route Borea aggiunta, nessun toggle di battle runtime, nessun toggle di broad rollout.
- Nessuna route frontend nuova aggiunta. Il file-based routing Expo (`/app/frontend/app/`) è invariato.

## 15) Runtime / DB / Gacha / Roster / Catalog safety

- **Runtime** (env vars in supervisord):
  - `AFFINITY_GIFT_RUNTIME_ENABLED="true_explicit_affinity_gift_runtime_on"` (immutato da V12)
  - `AFFINITY_GIFT_CANARY_ALLOWLIST="user_canary_001,…,stage1_qa_047"` (50 utenti, **modificato in V14**)
  - `AFFINITY_GIFT_CANARY_LEDGER_CAP="500"` (**modificato in V14**)
- **DB**:
  - Collection `gift_transaction_ledger`: 11 documenti, **tutti** con `canary=true` (stato V12, stabile attraverso V13 e V14)
  - `inventory_mutated:true` → 0 doc, `affinity_points_mutated:true` → 0 doc, `buffs_activated:true` → 0 doc, `battle_wiring_attached:true` → 0 doc, `hero_id ∈ {borea/greek_borea/primordial_gaia}` → 0 doc.
- **Gacha / Roster / Catalog / final_numbers**: nessuna modifica. Baseline `rm134b_axispatch_v6` PASS. `validate_hero_skill_kit_catalog_baseline_diff.py` PASS.
- **`battle_engine.py` / `battle_core.py` / `combat.tsx` / `game_systems.py` / `synergy_system.py`**: tutti `git diff --stat` vuoti.

## 16) Warning / discrepanze

- ⚠️ **K6/Locust ancora non installati nell'ambiente**: il piano K6 Prep3 + gli script `.k6.js` e `_locust.py` sono pronti per esecuzione futura, ma il probe reale è stato eseguito in Python fallback (600 req). Task P2 futuro `AF2-L-K6-LIVE real`.
- ⚠️ **Restart subprocess timeout**: lo `subprocess.run(['sudo','supervisorctl','restart','backend'], timeout=20)` ha sforato 20s a causa di `startsecs=20 + pip install` al boot; supervisor però ha completato correttamente il restart e backend è tornato `RUNNING` dopo ~28s. L'artefatto apply result è stato finalizzato post-restart con dati live. Lo script è già stato aggiornato per usare un timeout di 60s sul restart (effetto sui prossimi run).
- ⚠️ **Riga ledger spuria temporanea durante K6 prep3**: la prima versione del probe aveva un label che usava `user_id='stage1_qa_007'` (allowlisted) con payload valido. Ha generato 1 riga ledger. Identificata, rimossa via `delete_one({idempotency_key:'shortbad',user_id:'stage1_qa_007'})`, e label rifattorizzato a `stage1_qa_user_blocked_path` (body sempre invalido). Probe ri-eseguita, **ledger ripristinato a 11**. Tutti gli invarianti finali rispettati.
- ⚠️ **Supervisor wiring**: ancora `READY_NOT_APPLIED` come da V12-V13. Task P2 futuro.
- ⚠️ **Supersedence env var**: per ottenere `Overall: PASS` nella suite occorre esportare `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on` nella shell (è già in `backend.conf` per il backend ma la suite gira fuori da supervisor).

## 17) Final recommendation

✅ **ULTRA-COMBO V14 COMPLETATO con stato PASS** su tutte le 9 sub-task + composite + suite completa + baseline diff.

- **Stage1 1% allowlist è LIVE e stabile**: 3 → 50 utenti (sintetici interni QA), cap 20 → 500. Tutti i gate critici PASS prima dell'apply, monitoring window 60×7 probe = 420 chiamate API senza una sola anomalia, K6 prep3 600 chiamate aggiuntive senza fughe.
- **Inventory wiring shadow adapter pronto e contrattualizzato** (con rollback/compensation steps documentati), ma **strettamente NON wired** in alcun modulo runtime.
- **Tutti gli invarianti hard sono mantenuti**: `/api/heroes`=100, Borea=404 ovunque (243 risposte V14), ledger=11≤500, nessuna mutazione inventory/points/buffs/battle, file battle/combat/synergy/game invariati, broad rollout NOT authorized, nessun pulsante spend pubblico, nessuna route Borea esposta.
- **Rollback readiness PASS**: backup pre-Stage1 presente, script rollback dry-run PASS, fallback canary rollback presente.
- **Nessun abort trigger scattato**.

Il sistema è in stato `stage1_allowlist_active_no_broad_rollout` come da decisione `STAGE1_ONLY_NO_BROAD_ROLLOUT`.

## 18) Suggested next tasks (richiedono approvazione esplicita)

### P1 — Estensione post-Stage1
1. **AF2-N-STAGE1-EXTENDED-MONITORING (24-72h)**: finestra di monitoring estesa multi-ora sotto Stage1 prima di considerare ulteriori espansioni. Prerequisito: nuova approvazione utente esplicita.
2. **AF2-N-INVENTORY-WIRING ACTIVATE**: promuovere lo shadow adapter a live sotto nuovo feature flag `AFFINITY_GIFT_INVENTORY_WIRING_ENABLED=true_explicit_inventory_wiring_on`. Prerequisito: nuova approvazione esplicita + smoke test dedicato + estensione del ledger con `inventory_mutated` field + auto-rollback wired sui trigger di inventory mismatch.
3. **AF2-N-STAGE2-EXPANSION** (es. 5-10% allowlist): solo dopo che l'extended monitoring è stabile e l'inventory wiring è live verified. Richiede nuova approvazione esplicita.

### P2 — Infrastruttura
4. **AF2-L-K6-LIVE real**: installare k6 e/o locust nell'ambiente e ri-eseguire `AF2-L-K6-LIVE` con i piani esistenti (`/app/loadtests/af2n_stage1_allowlist.k6.js` + `_locust.py`).
5. **OPS-C-SUPERVISOR-APPLY**: applicare la wiring auto-rollback del supervisor (oggi `READY_NOT_APPLIED`).

### P3 — Battle wiring
6. **STACK-G full wiring**: collegare il `global_modifier_cap_resolver` al `battle_engine.py` live. **Strettamente deferred** finché Stage1 extended monitoring non è verde e l'inventory wiring non è live verified.

---

**Fine report ULTRA-COMBO V14.**
