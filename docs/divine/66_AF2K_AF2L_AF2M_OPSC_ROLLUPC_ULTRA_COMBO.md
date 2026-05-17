# 66. ULTRA-COMBO V8 — AF2-K · AF2-L · AF2-M · OPS-C · SAFETY-ROLLUP-C

> **Stato:** ✅ CHIUSO (PASS) — Suite **83/83 PASS**, combo validator **107/107 PASS**, baseline diff PASS auto-detect v6. **AF2-N esplicitamente NON consentito**.
>
> **Anchor baseline:** `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` (clean)

---

## 1. AF2-K summary
- Schema: `affinity_gift_transaction_ledger_schema_v1.json` (14 campi, 5 indexes incl. 1 partial unique).
- Script migration: `migrate_affinity_gift_transaction_ledger.py` — **default dry-run**, `--commit` richiede env `DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION=YES_I_UNDERSTAND` + è ulteriormente gated (nessun write reale eseguito da questo script).
- Risultato attuale: `dry_run=true`, `migration_applied=false`, `db_write=false`, `no_ledger_rows_inserted=true`, `no_inventory_mutation=true`, `no_affinity_points_mutation=true`, 5 indexes planned, 6 rollback steps.
- Rollback script: `rollback_affinity_gift_transaction_ledger_migration.py` (default dry-run).
- Validator: **55/55 PASS**.

## 2. AF2-L summary
- Probe: `run_affinity_gift_spend_disabled_load_probe.py` — 98 requests, **5xx=0, unexpected=0, p95=0.87 ms**.
- Probe behavior (no live spend):
  - empty/valid/dup_idem/missing_idem → **423** ognuno
  - borea/greek_borea/primordial_gaia → **404** ognuno
  - regressioni GET (gifts, summary, by-faction/greek, by-element/dark) → **200**
- Rollback rehearsal: `rehearse_affinity_gift_spend_rollback.py` → `dry_run=true`, `destructive_actions_performed=false`, 8 step.
- Validator: **42/42 PASS**.

## 3. AF2-M summary
- Package: `affinity_gift_runtime_operator_signoff_package_v1.json`.
- Tutti i 5 signoff (`product`, `engineering`, `qa`, `economy_balance`, `rollback_owner`) = **false**.
- `af2n_allowed: false`, `feature_flag_currently_enabled: false`.
- 12 preconditions, 6 immediate rollback triggers (5xx>1%, duplicate>0, borea_leak>0, inventory_mismatch>0, p95>800ms, unauthorized_writes>0).
- 5 rollout stages: solo stage0 (`internal_disabled`) `allowed_today=true`; tutti gli stage 1-4 = false.
- Gate: `user_explicit_approval_required=true`.
- Validator: **41/41 PASS**.

## 4. OPS-C summary
- Check + restore hook: `/app/ops/check_and_restore_start_expo_wrapper.sh` (idempotent, `cmp -s`, niente `rm -rf`, niente mongo, no app runtime modify, restart supervisor solo se non RUNNING).
- README: `/app/ops/README_START_EXPO_AUTORESTORE.md` con istruzioni manuali e raccomandazione di integrazione startup non-invasiva.
- Audit: **19/19 PASS** (`/usr/local/bin/start-expo.sh` aligned + executable, supervisor block riferisce wrapper, frontend `:3000 → 200`).

## 5. SAFETY-ROLLUP-C summary
- Report v3: `collection_affinity_runtime_activation_readiness_rollup_v3.json`.
- 7 layer READY (axis/ops/auth/idempotency/migration/load_probe/rollback_rehearsal).
- 4 gate ancora FALSE (`migration_applied`, `operator_signoff_ready`, `overall_runtime_activation_ready`, `AF2N_allowed`).
- `go_no_go_decision: NO_GO_RUNTIME`, `axis_layer_decision: GO_AXIS`.
- 8 no_go reasons, 4 AF2N_blockers, 12 invariants.
- Validator: **38/38 PASS**.

## 6. Borea safety
- `/api/heroes` = 100; borea / greek_borea / primordial_gaia **assenti**.
- POST gift-spend con qualunque Borea alias → **404**.
- `/api/affinity/gifts/by-faction/borea` → **404 forbidden**.
- AF2-L probe: 0 successful spend su Borea (0 spend in totale, endpoint disabled).
- Marchio Boreale leak in non-Borea 6★: **0**.

## 7. Validator results
| Task | PASS |
|---|---|
| AF2-K | 55/55 |
| AF2-L | 42/42 |
| AF2-M | 41/41 |
| OPS-C | 19/19 |
| SAFETY-ROLLUP-C | 38/38 |
| ULTRA-COMBO-V8 | **107/107** |

## 8. Suite / baseline results
```
run_hero_skill_kit_validator_suite.py --include-baseline-diff
Overall: PASS  (pass=83, fail=0, miss=0)
```
Baseline diff PASS con auto-detection `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`. JSON: `/tmp/ultra_combo_v8_suite.json`.

## 9. API smoke
| Endpoint | Esito |
|---|---|
| `/api/heroes` count=100, Borea hidden | ✅ |
| `/api/affinity/gifts` | ✅ 200 |
| `/api/affinity/gifts/by-faction/greek` | ✅ 200 |
| `/api/affinity/gifts/by-faction/tides` | ✅ 404 deferred_not_live |
| `/api/affinity/gifts/by-element/dark` | ✅ 200 |
| `/api/affinity/gifts/by-element/darkness` | ✅ 200 alias_applied=true |
| `/api/affinity/gifts/by-element/tides` | ✅ 404 axis_type_mismatch |
| `POST /api/affinity/gift-spend` empty | ✅ 423 |
| `POST /api/affinity/gift-spend` borea/greek_borea/primordial_gaia | ✅ 404 / 404 / 404 |

## 10. UI safety
`grep -rnE "gift_spend|GiftSpendButton|gift_transaction_ledger|AFFINITY_GIFT_RUNTIME_ENABLED|RuntimeToggle|IdempotencyKey|operator_signoff"` in `/app/frontend/app/*.tsx` → **0 hit**.

## 11. Runtime / DB / gacha / roster / catalog safety
- `battle_engine.py`, `battle_core.py`, `combat.tsx`: 0 reference a 9 nuovi token chiave (schema, result, probe, rehearsal, signoff, rollup_v3, env flag, OPS-C check, runtime flag).
- 0 DB write nel codice route (6 pattern verificati).
- Gacha / roster / heroes_master / heroes_kits / Character Bible / skill kit / DW / status / baseline / assets → **non toccati**.
- `feature_flag_currently_enabled: false` su envelope live.
- AF2-K migration: dry-run, 0 collection created, 0 row inserted.

## 12. Warning / discrepanze
1. ⚠️ `/usr/local/bin/start-expo.sh` era allineato all'avvio del task (OPS-C `cmp -s` check OK).
2. ⚠️ Nessun altro warning. Tutti i validator PASS.

## 13. Final recommendation
✅ **ACCETTARE**. Tutte le condizioni di accettazione sono soddisfatte:
- AF2-K migration foundation PASS (dry-run, no spend) ✅
- AF2-L load probe PASS (0 5xx, 0 unexpected, 0 writes) ✅
- AF2-L rollback rehearsal PASS dry-run ✅
- AF2-M signoff package creato, tutti i signoff false, AF2-N blocked ✅
- OPS-C audit PASS ✅
- SAFETY-ROLLUP-C dice runtime NO_GO, AF2-N not allowed ✅
- Suite 83/83 PASS con baseline diff PASS sotto v6 ✅
- `/api/heroes = 100`, Borea hidden ✅
- gift-spend disabled / no-write ✅
- zero battle_engine/combat mutation ✅
- zero gacha/roster/catalog mutation ✅
- UI safety PASS ✅

**AF2-N non eseguito** come richiesto.

## 14. Suggested next tasks
- 🟡 **AF2-M-SIGN-PRODUCT** — primo signoff (`product_signoff=true`) dopo review approvazione esplicita utente.
- 🟡 **AF2-K-COMMIT** — runner reale `pymongo` per migration AF2-K-MIG-001 dietro `DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION=YES_I_UNDERSTAND` + approval (separato).
- 🟢 **AF2-L-FULL** — load test reale con k6/Locust dopo migration commit.
- 🟢 **AF2-N** — flip `AFFINITY_GIFT_RUNTIME_ENABLED` **solo dopo** tutti 5 signoff true + user explicit approval.
- 🟢 **STACK-G** — connettere `global_modifier_cap_resolver` al battle (gated, no-write).
- 🟢 **OPS-C-WIRING** — aggiungere `bash /app/ops/check_and_restore_start_expo_wrapper.sh || true` al boot script (1 riga, non-invasiva).
- 🟢 **AXIS-G** — read-only routes combinate `by-element/{e}+by-faction/{f}`.

---

## File creati
- `/app/data/design/affinity/affinity_gift_transaction_ledger_schema_v1.json`
- `/app/data/design/affinity/affinity_gift_transaction_ledger_migration_result_v1.json`
- `/app/data/design/affinity/affinity_gift_spend_disabled_load_probe_result_v1.json`
- `/app/data/design/affinity/affinity_gift_spend_rollback_rehearsal_result_v1.json`
- `/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v3.json`
- `/app/backend/scripts/migrate_affinity_gift_transaction_ledger.py`
- `/app/backend/scripts/rollback_affinity_gift_transaction_ledger_migration.py`
- `/app/backend/scripts/validate_affinity_gift_transaction_ledger_migration.py`
- `/app/backend/scripts/run_affinity_gift_spend_disabled_load_probe.py`
- `/app/backend/scripts/rehearse_affinity_gift_spend_rollback.py`
- `/app/backend/scripts/validate_affinity_gift_spend_load_and_rollback_results.py`
- `/app/backend/scripts/validate_affinity_gift_runtime_operator_signoff.py`
- `/app/backend/scripts/audit_ops_start_expo_autorestore.py`
- `/app/backend/scripts/validate_collection_affinity_runtime_activation_rollup_v3.py`
- `/app/backend/scripts/validate_af2k_af2l_af2m_opsc_safetyc_combo.py`
- `/app/ops/check_and_restore_start_expo_wrapper.sh`
- `/app/ops/README_START_EXPO_AUTORESTORE.md`
- `/app/docs/divine/66_AF2K_AF2L_AF2M_OPSC_ROLLUPC_ULTRA_COMBO.md` (questo doc)

## File modificati
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunti 6 entry OPTIONAL (AF2-K, AF2-L, AF2-M, OPS-C, SAFETY-ROLLUP-C, ULTRA-COMBO-V8).
