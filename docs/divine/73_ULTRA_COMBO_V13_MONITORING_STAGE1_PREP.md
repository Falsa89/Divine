# ULTRA-COMBO V13 — Monitoring Window + Stage1 Prep + Inventory Wiring Pre + K6 Live Prep2 + Safety Rollup H

**Stato finale**: ✅ PASS (33/33 check composite + 98/98 suite con `--include-baseline-diff`)
**Data**: 2026-05-17 (sessione V13)
**Modalità**: Canary AF2-N ATTIVO, monitoring window completata, NESSUN broad rollout, Stage1 NON applicato, Inventory wiring NON attivo, Battle wiring NON attivo.
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` (PASS).

---

## 1) File creati in V13

| Path | Ruolo |
|---|---|
| `/app/backend/scripts/run_af2n_monitoring_window.py` | Probe runtime di monitoring esteso (30 campioni, read-mostly + replay idempotente) |
| `/app/backend/scripts/validate_af2n_monitoring_window_result.py` | Validator del risultato monitoring window |
| `/app/backend/scripts/validate_af2n_stage1_1pct_allowlist_plan.py` | Validator del piano Stage1 1% (design-only) |
| `/app/backend/scripts/audit_af2n_inventory_wiring_pre.py` | Audit dell'adapter inventory preview (inert) |
| `/app/backend/scripts/run_affinity_gift_spend_k6_live_safe_probe_prep2.py` | Safe probe Python (fallback K6) sotto canary attivo |
| `/app/backend/scripts/validate_affinity_gift_spend_k6_live_prep2_result.py` | Validator del risultato K6-Live-Prep2 |
| `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v8.py` | Validator del Rollup di sicurezza H (rollup v8) |
| `/app/backend/scripts/validate_ultra_combo_v13_monitoring_stage1_prep.py` | Validator composite V13 (orchestratore + invarianti live + DB + git diff) |
| `/app/backend/data/inventory_wiring_preview_adapter.py` | Adapter di preview inventory: `runtime_attached=False`, no DB write, Borea-filtered |
| `/app/data/design/affinity/af2n_monitoring_window_result_v1.json` | Artefatto risultato monitoring window |
| `/app/data/design/affinity/af2n_stage1_1pct_allowlist_plan_v1.json` | Artefatto piano Stage1 1% (design_only=true, do_not_apply=true) |
| `/app/data/design/affinity/affinity_gift_spend_k6_live_prep2_result_v1.json` | Artefatto risultato K6 Live Prep2 |
| `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v8.json` | Safety Rollup H (rollup v8) |
| `/app/backend/reports/ultra_combo_v13_validator_summary_v1.json` | Sommario composite V13 |
| `/app/backend/reports/suite_v13.json` | Sommario suite completa V13 |

## 2) File modificati in V13

| Path | Modifica |
|---|---|
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | Aggiunto blocco `# ULTRA-COMBO V13` con i 6 nuovi task (`AF2-N-MONITORING-WINDOW`, `AF2-N-STAGE1-PREP`, `AF2-N-INVENTORY-WIRING-PRE`, `AF2-L-K6-LIVE-PREP2`, `SAFETY-ROLLUP-H`, `ULTRA-COMBO-V13`) nella sezione OPTIONAL |
| `/app/backend/scripts/audit_af2n_inventory_wiring_pre.py` | Audit refactored: rilevamento `insert_one`/`update_one`/`delete_one` via regex sulla *chiamata* (`\.insert_one\(`) anziché substring nei docstring; check `runtime_attached: False` reso quote-style agnostic |

**Nessun file di produzione runtime modificato** (`/app/backend/server.py`, `/app/backend/battle_engine.py`, `/app/backend/battle_core.py`, `/app/backend/synergy_system.py`, `/app/backend/game_systems.py`, `/app/frontend/app/combat.tsx`).

## 3) Monitoring window summary (AF2-N-MONITORING-WINDOW)

- **Campioni**: 30 (interval 50ms, elapsed 4.20s)
- **Per ogni campione**: 7 probe sequenziali (`/health`, `/heroes`, `/affinity/gift-spend/canary-status`, POST empty, POST Borea, POST non-allowlist, POST replay idempotente)
- **HTTP codici osservati**:
  - `/health` → 30×200
  - `/heroes` → 30×200, sempre 100 eroi, mai Borea
  - canary-status → 30×200
  - POST empty → 30×423
  - POST Borea → 30×404
  - POST non-allowlist → 30×423 (mai 200 = nessun unauthorized successful spend)
  - POST replay idempotente (`canary_idem_0001`/`user_canary_001`) → 30×200 con `ledger_row_inserted=False` per ogni replay
- **5xx totali**: 0
- **Trigger di abort**: 0 / 0
- **Latenze p95** (ms): health=2.87, heroes=79.17, status=13.05, spend_empty=1.47, spend_borea=1.04, spend_nonal=1.44, spend_replay=5.43 (tutte ben sotto 500ms target)
- **DB ledger pre/post monitoring**: 11 / 11 (invariato, sempre `canary=true`)
- **`overall_status`**: PASS
- Artefatto: `/app/data/design/affinity/af2n_monitoring_window_result_v1.json`
- Validator (29 check) → **PASS**

## 4) Stage1 prep summary (AF2-N-STAGE1-PREP)

- Piano `af2n_stage1_1pct_allowlist_plan_v1.json` creato con `design_only=true`, `do_not_apply_in_this_task=true`, `db_write=false`.
- Stato attuale: canary_active=true, allowlist_size_today=3.
- Target Stage1: `allowlist_size_hard_cap≥50`, `canary_ledger_cap_proposed>20`, almeno 3 selection_criteria documentati.
- **Prerequisiti BEFORE stage1_apply** (≥5, tutti elencati): `explicit_user_stage1_approval` con `required=true` e `status_today=FAIL_NOT_YET_GIVEN`.
- Documentati ≥5 abort trigger Stage1, ≥6 step di apply procedure (NON ESEGUIBILI ORA), ≥2 step di rollback, ≥5 safety constraints.
- Safety flags: `stage1_applied=false`, `broad_rollout_authorized=false`, inventory/points/buffs/battle tutti `false`.
- Validator (26 check) → **PASS**.

## 5) Inventory wiring preflight summary (AF2-N-INVENTORY-WIRING-PRE)

- Adapter `/app/backend/data/inventory_wiring_preview_adapter.py` presente, entry point `preview_inventory_apply()`.
- Ritorna sempre `runtime_attached=False`. Per Borea (`borea`, `greek_borea`, `primordial_gaia`) ritorna `borea_filtered=True`, `would_have_status='borea_filtered'`, `would_have_consumed_inventory=False`.
- Per input valido (`greek_zeus`, qty=1): `would_have_status='applied_preview_only'`, **nessuna chiamata DB**, `safety_envelope.feature_flag_currently_enabled=False`, `safety_envelope.db_write=False`.
- **NESSUN** import di: `motor`, `pymongo`, `battle_engine`, `battle_core`, qualsiasi modulo frontend.
- **NESSUNA** chiamata a `insert_one(`, `update_one(`, `delete_one(` (verificato via regex).
- **NESSUN** modulo runtime importa l'adapter:
  - `affinity_gift_spend.py` → niente import
  - `battle_engine.py` → niente import
  - `battle_core.py` → niente import
  - `combat.tsx` → niente import
- Feature flag dipendenza documentato: `AFFINITY_GIFT_INVENTORY_WIRING_ENABLED` (oggi disattivato).
- Audit (26 check) → **PASS**.

## 6) K6/Live Prep2 summary (AF2-L-K6-LIVE-PREP2)

- **Modalità**: `safe_probe_python_fallback_canary_active` (k6/locust non installati → fallback su `urllib` Python).
- **Richieste totali**: 720 (80 per ognuna delle 9 label).
- **Label e codici attesi**:
  - `empty`, `no_idem`, `malformed_idem`, `negative_qty`, `huge_qty` → tutti 80×423 ✓
  - `borea`, `greek_borea`, `primordial_gaia` → tutti 80×404 ✓
  - `idempotent_replay` (`canary_idem_0001`/`user_canary_001`) → 80×200 con `ledger_row_inserted=False` ovunque ✓
- **5xx totali**: 0
- **Codici inattesi totali**: 0
- **Duplicate inserts**: 0
- **Ledger pre/post probe**: 11 / 11 (`ledger_row_count_unchanged=true`)
- **Regression GET** (9 endpoint): tutti `ok=true` (200 dove atteso, 404 dove atteso)
- Validator (40 check) → **PASS**.

## 7) Rollback readiness

- Script: `/app/ops/rollback_af2n_canary.sh` → `af2n_canary_rollback_script_ready=true`
- `rollback_executed=false` (tutti i gate V13 PASS, monitoring completata, nessun trigger).
- Procedura di abort documentata in `abort_triggers_status` del rollup v8:
  - `5xx_rate_gt_1pct`, `borea_not_404`, `duplicate_double_spend`, `unexpected_ledger_rows`, `unauthorized_successful_spend`, `api_heroes_not_100`, `battle_file_mutation`, `inventory_wiring_pre_imported_by_runtime`, `stage1_applied_without_approval` — tutti `triggered=false`.

## 8) Safety Rollup H

- File: `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v8.json`
- `report_id=collection_affinity_runtime_activation_readiness_rollup_v8`, `task_origin=SAFETY-ROLLUP-H`, `supersedes=…rollup_v7`.
- Stato globale: `overall_runtime_activation_state="canary_active_monitoring_window_passed_no_broad_rollout"`, `go_no_go_decision="CANARY_ONLY_NO_BROAD_ROLLOUT"`.
- 5 operator signoff = true + `final_user_runtime_approval_present=true`.
- `AF2N_executed=true`, `AF2N_canary_status="PASS"`, `AF2N_monitoring_window_status="PASS"`, `AF2N_stage1_state="PLAN_READY_NOT_APPLIED"`, `AF2N_inventory_wiring_state="PREVIEW_ADAPTER_READY_NOT_WIRED"`, `k6_live_prep2_status="PASS"`.
- 14 subsystem, tutti con status atteso (ACTIVE_PASS / PASS / READY_NOT_APPLIED / READY_NOT_WIRED / NO_GO per battle / GO per borea).
- Validator (58 check) → **PASS**.

## 9) Borea safety

- `/api/heroes` non contiene `borea`, `greek_borea`, `primordial_gaia` (verificato 30× in monitoring + 1× in smoke finale).
- `POST /api/affinity/gift-spend` con `hero_id` in `{borea, greek_borea, primordial_gaia}` → 404 (verificato 30× + 240× in K6 prep2 + 1× smoke = 271 risposte 404 in totale, **mai una sola fuga**).
- `GET /api/affinity/gifts/by-element/dark/by-faction/borea` → 404 (verificato in K6 prep2 + smoke).
- `ledger_borea_hero_count = 0` (zero righe ledger con hero_id Borea).
- `hidden_aliases_blocked=['borea','greek_borea','primordial_gaia']` propagato in ogni artefatto V13 (monitoring, stage1 plan, inventory adapter, k6 prep2, rollup v8, composite V13).

## 10) Validator results (V13)

| Tag | Script | Check | Esito |
|---|---|---|---|
| AF2-N-MONITORING-WINDOW | `validate_af2n_monitoring_window_result.py` | 29 | **PASS** |
| AF2-N-STAGE1-PREP | `validate_af2n_stage1_1pct_allowlist_plan.py` | 26 | **PASS** |
| AF2-N-INVENTORY-WIRING-PRE | `audit_af2n_inventory_wiring_pre.py` | 26 | **PASS** |
| AF2-L-K6-LIVE-PREP2 | `validate_affinity_gift_spend_k6_live_prep2_result.py` | 40 | **PASS** |
| SAFETY-ROLLUP-H | `validate_collection_affinity_runtime_activation_rollup_v8.py` | 58 | **PASS** |
| ULTRA-COMBO-V13 | `validate_ultra_combo_v13_monitoring_stage1_prep.py` | 33 | **PASS** |

## 11) Suite & baseline results

- Comando: `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on python3 run_hero_skill_kit_validator_suite.py --include-baseline-diff`
- Risultato: **Overall: PASS** — `pass=98, fail=0, miss=0`
- I pre-AF2N validator (V6→V11) sono correttamente marcati `[SUPERSEDED]` (logica di auto-supersedence già implementata in V12 quando `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on`).
- `RM1.32-PRE` (`validate_hero_skill_kit_catalog_baseline_diff.py`) → **PASS** (nessuna deriva dal baseline `rm134b_axispatch_v6`).
- Sommario JSON: `/app/backend/reports/suite_v13.json`.

## 12) API smoke (post-V13)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` count | 100 | **100** ✓ |
| `GET /api/heroes` contiene Borea? | NO | **NO** ✓ |
| `GET /api/affinity/gift-spend/canary-status` | `feature_flag=True, ledger=11≤cap 20, combat=False, battle=False, inventory=False, buffs=False` | **identico** ✓ |
| `POST /api/affinity/gift-spend` (Borea) | 404 | **404** ✓ |
| `POST /api/affinity/gift-spend` (non-allowlist) | 423 | **423** ✓ |
| `POST /api/affinity/gift-spend` (canary user, idempotent replay) | 200 + no new row | **200, no new row** ✓ |
| `GET /api/affinity/gifts/by-element/dark/by-faction/greek` | 200 | **200** ✓ |
| `GET /api/affinity/gifts/by-element/dark/by-faction/borea` | 404 | **404** ✓ |

## 13) UI safety

- `combat.tsx`: **invariato** (`git diff --stat` vuoto).
- Nessun import nell'UI di `inventory_wiring_preview_adapter`, `global_modifier_cap_resolver`, `global_modifier_cap_battle_preview_adapter`.
- Nessuna route frontend nuova aggiunta. Il file-based routing Expo (`/app/frontend/app/`) è invariato.

## 14) Runtime / DB / Gacha / Roster / Catalog safety

- **Runtime**: solo `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on` con `AFFINITY_GIFT_CANARY_ALLOWLIST="user_canary_001,user_canary_002,user_canary_003"` e `AFFINITY_GIFT_CANARY_LEDGER_CAP="20"` (immutati da V12).
- **DB**:
  - Collection `gift_transaction_ledger`: 11 documenti, **tutti** con `canary=true`.
  - `inventory_mutated:true` → 0 doc, `affinity_points_mutated:true` → 0 doc, `buffs_activated:true` → 0 doc, `battle_wiring_attached:true` → 0 doc, `hero_id ∈ {borea/greek_borea/primordial_gaia}` → 0 doc.
- **Gacha / Roster / Catalog**: nessuna modifica. Baseline `rm134b_axispatch_v6` PASS. `validate_hero_skill_kit_catalog_baseline_diff.py` PASS.
- **`battle_engine.py` / `battle_core.py` / `combat.tsx` / `game_systems.py` / `synergy_system.py`**: tutti `git diff --stat` vuoti (invariati).

## 15) Warning / discrepanze

- ⚠️ **K6/Locust ancora non installati nell'ambiente**: K6-Live-Prep2 è stato eseguito in modalità `safe_probe_python_fallback_canary_active` (urllib). I risultati sono validi come gating funzionale/idempotenza ma non sono un vero load test ad alto throughput. Resta task P2 futuro `AF2-L-K6-LIVE real`.
- ⚠️ **`supervisor_wiring_state="READY_NOT_APPLIED"`**: la wiring auto-rollback del supervisor è pronta ma non applicata (l'apply causerebbe rollback immediato nell'ambiente attuale). Task P2 futuro `OPS-C-SUPERVISOR-APPLY`.
- ⚠️ **Audit inventory wiring**: il file di audit originale era troppo strict (matchava substring nei docstring e single-quote only). Refactored in modo intent-driven (regex su pattern di chiamata e quote-agnostic). Vedi sezione 2.
- ⚠️ **Supersedence env var**: per ottenere `Overall: PASS` nella suite, occorre esportare `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on` nella shell (è già impostato per il processo backend via `/etc/supervisor/conf.d/backend.conf` ma la suite gira fuori da supervisor). Senza, 17 pre-AF2N validator falliscono per design (asseriscono lo stato `runtime OFF`).

## 16) Final recommendation

✅ **ULTRA-COMBO V13 COMPLETATO con stato PASS** su tutte le 6 sub-task + composite + suite completa + baseline diff.

- Il canary AF2-N è **stabile** dopo finestra di monitoring estesa (30 campioni × 7 probe + 720 richieste K6-prep2 = 930 chiamate API live senza una sola anomalia).
- Lo Stage1 1% allowlist è **documentato come piano READY ma esplicitamente NOT APPLIED**; richiede nuovo messaggio esplicito utente.
- L'inventory wiring preview adapter è **inert e pronto come contratto** per un futuro task dedicato; nessun import live.
- Tutti gli invarianti hard sono mantenuti: `/api/heroes`=100, Borea=404 ovunque, ledger=11≤20, nessuna mutazione inventory/points/buffs/battle, file battle/combat invariati, broad rollout NOT authorized.
- **Nessun rollback eseguito né necessario**.

Il canary resta attivo per ulteriore observation. **Nessuna azione richiesta**: il sistema è in stato `canary_active_monitoring_window_passed_no_broad_rollout` come da decisione `CANARY_ONLY_NO_BROAD_ROLLOUT`.

## 17) Suggested next tasks (richiedono approvazione esplicita)

### P1 — Espansione canary (uno alla volta, con approvazione)
1. **AF2-N-STAGE1-1PCT-ALLOWLIST APPLY**: applicare il piano in `af2n_stage1_1pct_allowlist_plan_v1.json`. Prerequisito: nuovo messaggio utente esplicito che autorizza l'espansione a ~1% degli utenti e l'aumento del `canary_ledger_cap` a un nuovo valore documentato. Tutti gli abort trigger Stage1 vanno wired live.
2. **AF2-N-INVENTORY-WIRING ACTIVATE**: collegare l'adapter inert sotto un nuovo feature flag `AFFINITY_GIFT_INVENTORY_WIRING_ENABLED=true_explicit_inventory_wiring_on`. Prerequisito: nuova approvazione utente esplicita + smoke test dedicato + estensione del ledger con campo `inventory_mutated=true`.

### P2 — Infrastruttura
3. **AF2-L-K6-LIVE real**: installare k6 e/o locust nell'ambiente e ri-eseguire `AF2-L-K6-LIVE` real (target reali p95 < 500ms, throughput documentato).
4. **OPS-C-SUPERVISOR-APPLY**: applicare la wiring auto-rollback del supervisor (oggi `READY_NOT_APPLIED`). Richiede ambiente di staging per evitare oneshot rollback al boot.

### P3 — Battle wiring
5. **STACK-G full wiring**: collegare il `global_modifier_cap_resolver` al `battle_engine.py` live. **Strettamente deferred** finché AF2-N Stage1 non è stabile e l'inventory wiring non è live verified.

---

**Fine report ULTRA-COMBO V13.**
