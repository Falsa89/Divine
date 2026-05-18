# ULTRA-COMBO V17 — INVENTORY EXTENDED MONITORING + STAGE2 5-10% EXPANSION (APPLIED-GATED) + SUITE SUPERSEDED CLEANUP + K6/LOCUST READINESS + SAFETY-ROLLUP-L

**Project**: Divine RPG / Divine Waifus
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`
**Stato**: ✅ COMPLETATO — Stage2 APPLIED (allowlist 50→100, cap 500→1000) — Suite 104/104 PASS

---

## 1. File creati

### Scripts (`/app/backend/scripts/`)
- `validate_af2n_v17_preflight.py`
- `run_af2n_inventory_extended_monitoring_v17.py`
- `validate_af2n_inventory_extended_monitoring_v17.py`
- `apply_af2n_stage2_5_10pct_allowlist.py`
- `rollback_af2n_stage2_5_10pct_allowlist.py`
- `validate_af2n_stage2_5_10pct_apply_result.py`
- `run_af2n_stage2_monitoring_v17.py`
- `validate_af2n_stage2_monitoring_v17.py`
- `validate_validator_suite_supersedence_cleanup.py`
- `run_af2n_v17_k6_locust_readiness.py`
- `validate_af2n_v17_k6_locust_readiness.py`
- `run_af2n_v17_rollback_readiness.py`
- `validate_af2n_v17_rollback_readiness.py`
- `validate_collection_affinity_runtime_activation_rollup_v12.py`
- `validate_ultra_combo_v17_stage2_monitoring_cleanup_k6.py`

### Design / safety JSON
- `/app/data/design/affinity/af2n_v17_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_inventory_extended_monitoring_v17_result.json`
- `/app/data/design/affinity/af2n_stage2_5_10pct_plan_v1.json`
- `/app/data/design/affinity/af2n_stage2_5_10pct_apply_result_v1.json`
- `/app/data/design/affinity/af2n_stage2_monitoring_v17_result.json`
- `/app/data/design/affinity/af2n_v17_k6_locust_readiness_result_v1.json`
- `/app/data/design/affinity/af2n_v17_rollback_readiness_result_v1.json`
- `/app/data/design/system_safety/validator_suite_supersedence_cleanup_report_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v12.json`

### Reports / docs
- `/app/backend/reports/suite_v17.json` (overall PASS, 104/104)
- `/app/backend/reports/ultra_combo_v17_validator_summary_v1.json`
- `/app/docs/divine/VALIDATOR_SUITE_SUPERSEDENCE_POST_AF2N.md`
- `/app/docs/divine/77_ULTRA_COMBO_V17_STAGE2_MONITORING_CLEANUP_K6.md` (questo)

### Backup operativo
- `/app/ops/backups/backend.conf.v17_pre_stage2.20260518T002315Z.bak`

---

## 2. File modificati

- `/etc/supervisor/conf.d/backend.conf` (allowlist 50→100, ledger cap 500→1000; backup preservato)
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` (header doc V17 supersedence + bucket `SUPERSEDED_AFTER_STAGE2` + detection via API fallback; registrati 9 nuovi validator V17). Logica core invariata, copertura attiva NON ridotta.

**File esplicitamente NON modificati (invariante hard)**:
- `/app/backend/battle_engine.py`
- `/app/backend/battle_core.py`
- `/app/frontend/app/combat.tsx`
- `/app/backend/synergy_system.py`
- `/app/backend/game_systems.py`
- `/app/backend/routes/affinity_gift_spend.py` (nessuna modifica funzionale in V17; route già attiva da V16)

---

## 3. Preflight V17

**Status**: PASS. Tutti i 23 gates verde (api health, heroes=100, no-borea, canary flag on, inventory writes on, allowlist≥50, cap≥500, borea 404, non-allow 423, battle files unchanged, ugi/uas presenti, seed V16=50, no negative inventory, inv/aff mutation equal, no buffs/battle/borea ledger rows, rollback scripts presenti, V16 composite PASS, baseline v6 diff PASS, UI safety PASS, no shadow adapter leak).

---

## 4. Inventory Extended Monitoring (V17)

**Status**: PASS. 120 campioni, 0 trigger.
- 50 health 200 OK
- 20 /api/heroes count=100 OK
- 15 Borea POST tutti 404 (zero 423/200)
- 15 non-allowlist tutti 423
- 15 idempotent replay tutti 200 result=`idempotent_replay` con `inventory_unchanged` e `affinity_unchanged`
- 5 fresh spend Stage1 (`stage1_qa_006..010`) con delta inventory −1 e affinity +1 esatti
- inv_mut_delta == aff_mut_delta == 5
- 0 HTTP 5xx, 0 negative inventory, 0 buffs, 0 battle wiring

---

## 5. Stage2 Apply / Prep

**Status**: APPLIED_PASS (tutti i gate erano verde → apply commesso).

Espansione applicata in modo gated e con backup:
- Aggiunti 50 utenti sintetici QA: `stage2_qa_001`..`stage2_qa_050`
- Allowlist totale: **50 → 100** (Stage1 + Stage2)
- Ledger cap: **500 → 1000**
- Seed inventory: 50 docs `gift_test_001 x10` con `metadata.seed_task=V17_STAGE2`
- Backup supervisor.conf: `/app/ops/backups/backend.conf.v17_pre_stage2.20260518T002315Z.bak`
- Smoke verify post-restart: PASS (canary-status mostra size=100, cap=1000, flag on, inv on, combat off, battle off, buffs off)

Hard caps di sicurezza nello script di apply: total_allowlist ≤ 200, ledger_cap ≤ 1000, stage2_user_count ≤ 50.

---

## 6. Stage2 Monitoring (V17)

**Status**: PASS. ≥70 campioni, 0 trigger.
- Health/heroes/Borea/non-allowlist: tutti i bucket OK (borea_bad=0, non_allowlist_bad=0)
- 5 fresh spend Stage2 (`stage2_qa_001..005`) inventory −1 / affinity +1 esatti
- Idempotent replay Stage2 verificato: prima richiesta `applied_inventory_live`, replay `idempotent_replay` con stato invariato
- 0 HTTP 5xx, 0 negative inventory, 0 buffs, 0 battle wiring, inv_delta==aff_delta

---

## 7. Suite Supersedence Cleanup

**Status**: PASS. Refactor solo a livello metadati + bucket esplicito V17.

Bucket ufficiali documentati in `validator_suite_supersedence_cleanup_report_v1.json` e in `/app/docs/divine/VALIDATOR_SUITE_SUPERSEDENCE_POST_AF2N.md`:

1. **ACTIVE_REQUIRED**: 14 validator core (5-star, 6-star, divine weapon, balance foundation, numeric trim) — invariati.
2. **ACTIVE_OPTIONAL**: validator contestuali post-AF2-N (V16-aware + V17).
3. **SUPERSEDED_PRE_AF2N**: auto-marked quando `AFFINITY_GIFT_RUNTIME_ENABLED=on`.
4. **SUPERSEDED_PRE_INV_WRITES**: auto-marked quando `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED=on`.
5. **SUPERSEDED_AFTER_STAGE2** (nuovo): V16-PREFLIGHT, ULTRA-COMBO-V16 auto-marked quando allowlist>50 o cap>500.
6. **HISTORICAL_MANUAL**: apply/seed/rollback scripts NON cancellati.

Nessun validator `ACTIVE_REQUIRED` rimosso o indebolito. Nessuno script storico cancellato. Detection ora robusta tramite env var + API fallback (`/api/affinity/gift-spend/canary-status`).

---

## 8. K6 / Locust Readiness

**Status**: PASS.
- k6 NON installato, locust NON installato.
- Istruzioni di install esatte salvate in `af2n_v17_k6_locust_readiness_result_v1.json` (k6 via tarball + locust via pip3).
- **Python fallback probe**: 2000 richieste totali (800 health, 200 canary-status, 500 non-allowlist, 500 borea reject) — 0 HTTP 5xx, 0 borea_bad, 0 non_allowlist_bad, **~873 RPS sostenuti** (fully read-only / reject paths, ZERO mutazioni fresche).

**Raccomandazione**: AF2-L-K6-LIVE real install resta task gated separato; readiness V17 sufficiente per scope corrente.

---

## 9. Rollback Readiness V17

**Status**: PASS.
- 6 rollback script presenti: stage1 1pct allowlist, inventory wiring stage1, inventory wiring stage1 retry, stage1 QA seed, **stage2 5-10pct allowlist (NEW V17)**, ops `rollback_af2n_canary.sh`.
- Directory backup supervisor (`/app/ops/backups/`) scrivibile.
- Dry-run Stage2 rollback eseguito OK.

---

## 10. Safety Rollup L

**Status**: PASS (`collection_affinity_runtime_activation_readiness_rollup_v12.json` generato).
- `supersedes`: rollup_v11
- `stage2_state`: **APPLIED**
- `inventory_live_stage1_or_stage2`: stage2
- `broad_rollout_authorized`: false
- `battle_wiring_live`: false
- `Borea_hidden`: true
- `canary_allowlist_size`: 100, `ledger_cap`: 1000
- `inventory_mutation_health.extended_monitoring_pass`: true
- `suite_cleanup_state.report_present`: true, 5 bucket
- `k6_readiness_state.python_fallback_probe_pass`: true, fb_requests_total=2000
- `rollback_readiness_state.all_scripts_present`: true
- `next_decision`: **continue_stage2_monitoring**

---

## 11. Borea Safety

- `/api/heroes` count = 100, nessun id Borea/greek_borea/primordial_gaia.
- POST `/api/affinity/gift-spend` con hero_id Borea → **HTTP 404** (PRE qualsiasi flag check).
- Ledger query `hero_id IN [borea, greek_borea, primordial_gaia]` → **0 righe**.
- Borea NON rivelato in nessun catalogo / route / UI.

---

## 12. Validator Results

| Task | Status |
|---|---|
| V17-PREFLIGHT | ✅ PASS |
| AF2-N-INVENTORY-EXTENDED-MONITORING-V17 | ✅ PASS |
| AF2-N-STAGE2-APPLY | ✅ PASS (APPLIED_PASS) |
| AF2-N-STAGE2-MONITORING-V17 | ✅ PASS |
| SUITE-SUPERSEDENCE-CLEANUP | ✅ PASS |
| AF2-L-K6-LOCUST-READINESS-V17 | ✅ PASS |
| V17-ROLLBACK-READINESS | ✅ PASS |
| SAFETY-ROLLUP-L | ✅ PASS |
| ULTRA-COMBO-V17 composite (39 checks) | ✅ PASS |

---

## 13. Suite / Baseline

- `python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff --json-out /app/backend/reports/suite_v17.json`
- **Overall: PASS** — pass=104, fail=0, miss=0
- Validator SUPERSEDED (auto-marked, per design): 25 (V15/V16 preflight + composite + relativi sotto-validator pre-inventory-on / pre-Stage2). Tutti documentati in `SUPERSEDED_AFTER_AF2N`, `SUPERSEDED_AFTER_INV_WRITES`, `SUPERSEDED_AFTER_STAGE2`.
- **RM1.32-PRE baseline diff**: PASS (catalog baseline anchor `rm134b_axispatch_v6` invariato).

---

## 14. API Smoke (post-Stage2)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | ✅ 200 |
| `GET /api/heroes` count | 100, no Borea | ✅ 100, no Borea |
| `GET /api/affinity/gift-spend/canary-status` | 200, size=100, cap=1000, flag on, inv on, combat off, battle off, buffs off | ✅ |
| `POST gift-spend` Borea | 404 | ✅ 404 |
| `POST gift-spend` non-allowlist | 423 | ✅ 423 |
| `POST gift-spend` Stage1 user | 200 `applied_inventory_live` | ✅ |
| `POST gift-spend` Stage2 user (es. `stage2_qa_010`) | 200 `applied_inventory_live`, inv decrement / aff increment esatto | ✅ inv 10→9, aff 0→1 |
| `POST gift-spend` idempotent replay | 200 `idempotent_replay`, no state change | ✅ |
| `GET runtime debug coverage` | invariato | ✅ |

---

## 15. UI Safety

- Nessun pulsante public spend creato.
- Nessuna rivelazione di Borea.
- Nessun toggle runtime esposto.
- Nessun rollout UI broad.
- Nessuna wiring battle UI.
- `combat.tsx` NON modificato.

---

## 16. Runtime / DB / Gacha / Roster / Catalog Safety

- **Runtime**: feature flag e inventory writes ATTIVI (Stage1 + Stage2 allowlist 100). `applied_to_combat=false`, `battle_runtime_attached=false`, `buffs_enabled=false`.
- **DB**:
  - `gift_transaction_ledger`: tutte le righe `canary=True`, count entro cap (1000). `inventory_mutated` count == `affinity_points_mutated` count. 0 righe `buffs_activated`, 0 `battle_wiring_attached`, 0 `hero_id` Borea.
  - `user_gift_inventory`: 100 docs totali (50 V16 + 50 V17_STAGE2 + entries V16 spend). 0 docs con `quantity<0`.
  - `user_affinity_state`: incrementi esatti per ogni spend.
- **Gacha / Roster / Character Bible / asset / skill catalogs / final_numbers**: NESSUNA modifica. Solo collezioni runtime affinity/inventory toccate (per design).

---

## 17. Warnings

- `k6` / `locust` non disponibili nel container: usato Python fallback (2000 req @ ~873 RPS), già ammesso dal task. Install istruzioni esatte fornite per future ops.
- File V13/V14/V15/V16 preflight ora marcati `SUPERSEDED` quando Stage2 applicato — comportamento atteso e documentato.

---

## 18. Final Recommendation

**Recommendation**: **CONTINUE_STAGE2_MONITORING**.

Stage2 5-10% allowlist espansione APPLICATA in modo sicuro (50 → 100 utenti QA sintetici, cap 500 → 1000). Inventory live writes operativi su 100 utenti allowlist con invarianti hard tutti tenuti:
- /api/heroes = 100, Borea hidden/404
- 0 HTTP 5xx, 0 unauthorized spend, 0 negative inventory, 0 buffs, 0 battle wiring
- 0 modifiche a battle_engine.py / battle_core.py / combat.tsx / synergy_system.py / game_systems.py
- Rollback Stage2 dry-run OK, backup supervisor.conf disponibile

Prossimo prudente: 24-72h di osservazione estesa Stage2 sotto carico QA reale.

**Broad rollout, STACK-G full wiring e public spend UI restano gated tasks separate, NON autorizzati.**

---

## 19. Suggested Next Tasks

- **P1** `AF2-N-STAGE2-EXTENDED-MONITORING` — 24-72h observation window Stage2 sotto carico QA real.
- **P1** `AF2-N-STAGE3-PREP` — pianificazione (DESIGN_ONLY) eventuale espansione Stage3 controllata, gated.
- **P2** `AF2-L-K6-LIVE-REAL` — install reale k6/locust nel container (`apt-get` o tarball) + smoke probe LIVE su path read-only.
- **P2** `OPS-C-SUPERVISOR-APPLY-AUTOMATION` — automazione idempotente del flip supervisor.conf.
- **P2** `SUITE_RUNNER_HISTORICAL_REGISTRY_EXPORT` — esportazione formale del registry (4+1 bucket) in JSON consumabile da dashboards.
- **P3** `STACK-G-WIRING-FULL` — collegamento `affinity_state` → `battle_engine.py`/`combat.tsx`. **Strettamente deferred fino a Stage3+ con nuova approvazione esplicita**.
- **P3** `PUBLIC_SPEND_UI` — UI pubblica per gift-spend. **Strettamente deferred**.

---

## Acceptance V17 — Checklist Finale

- [x] no broad rollout
- [x] Stage2 applicato in modo safe/gated con backup + rollback ready
- [x] inventory/affinity mutation esatta e idempotente (Stage1 + Stage2)
- [x] no battle wiring
- [x] /api/heroes = 100
- [x] Borea hidden/404
- [x] no unauthorized spend success
- [x] no 5xx
- [x] rollback readiness PASS
- [x] suite/baseline PASS (104/104, RM1.32-PRE PASS)
- [x] no battle/gacha/roster/catalog mutation
- [x] UI safety PASS

**ULTRA-COMBO V17 — COMPLETATO**
