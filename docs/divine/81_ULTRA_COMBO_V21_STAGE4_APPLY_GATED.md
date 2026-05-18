# ULTRA-COMBO V21 — STAGE4 INTERNAL BETA APPLY-GATED + SIGNOFFS V5 APPLY + RATE-LIMIT MIDDLEWARE + DB BACKUP DRILL + STAGE4 MONITORING + LOCUST + SAFETY-ROLLUP-P

**Stato finale:** ✅ **PASS — STAGE4 INTERNAL BETA APPLIED (NO BROAD ROLLOUT)**
**Data:** 2026-05-18
**Project:** Divine RPG / Divine Waifus
**Origine task:** ULTRA-COMBO V21 ZIP (autorizzazione utente esplicita: OPZIONE 1)

---

## 1. File creati

### Script Python (`/app/backend/scripts/`)
- `validate_af2n_v21_preflight.py`
- `apply_af2n_stage4_signoffs_v5.py`
- `validate_af2n_stage4_signoffs_v5_applied.py`
- `audit_affinity_gift_spend_rate_limit_runtime.py`
- `run_affinity_gift_spend_rate_limit_probe.py`
- `validate_affinity_gift_spend_rate_limit_probe.py`
- `run_af2n_stage4_db_backup_drill.py`
- `validate_af2n_stage4_db_backup_drill.py`
- `apply_af2n_stage4_internal_beta.py`
- `rollback_af2n_stage4_internal_beta.py`
- `validate_af2n_stage4_internal_beta_apply_result.py`
- `run_af2n_stage4_monitoring_v21.py`
- `validate_af2n_stage4_monitoring_v21.py`
- `run_af2n_v21_locust_stage4_low_impact.py`
- `validate_af2n_v21_locust_stage4_result.py`
- `audit_affinity_gifts_public_preview_v21_safety.py`
- `validate_af2n_v21_rollback_readiness.py`
- `build_safety_rollup_p_v16.py`
- `validate_collection_affinity_runtime_activation_rollup_v16.py`
- `validate_ultra_combo_v21_stage4_apply_gated.py`

### Locust loadtests
- `/app/loadtests/af2n_v21_stage4_locustfile.py`

### Artefatti JSON (`/app/data/design/`)
- `affinity/af2n_v21_preflight_result_v1.json`
- `affinity/af2n_stage4_signoff_package_v5_applied.json`
- `affinity/affinity_gift_spend_rate_limit_runtime_contract_v1.json`
- `affinity/affinity_gift_spend_rate_limit_probe_result_v1.json`
- `affinity/af2n_stage4_db_backup_drill_result_v1.json`
- `affinity/af2n_stage4_internal_beta_apply_result_v1.json`
- `affinity/af2n_stage4_monitoring_v21_result.json`
- `affinity/af2n_v21_locust_stage4_result_v1.json`
- `affinity/af2n_v21_rollback_readiness_result_v1.json`
- `ui/affinity_gifts_public_preview_v21_safety_result.json`
- `system_safety/collection_affinity_runtime_activation_readiness_rollup_v16.json`

### Backup
- `/app/backups/af2n_stage4/backend.conf.v21_pre_rate_limit_*.bak`
- `/app/backups/af2n_stage4/backend.conf.v21_pre_stage4_apply_*.bak`
- `/app/backups/af2n_stage4/backup_*/` (3 collezioni MongoDB con sha256)

### Reports
- `/app/backend/reports/suite_v21.json`
- `/app/backend/reports/ultra_combo_v21_composite.json`

## 2. File modificati

- `/app/backend/routes/affinity_gift_spend.py` — aggiunto guard rate-limit V21 (in-memory sliding window) + esposizione config su `/canary-status`. **Borea check resta primo, 404 vince su 429.**
- `/etc/supervisor/conf.d/backend.conf` — aggiunti `AFFINITY_GIFT_RATE_LIMIT_ENABLED=true_explicit_affinity_rate_limit_on`; allowlist estesa con 500 utenti `stage4_qa_NNN` (totale 700); `AFFINITY_GIFT_CANARY_LEDGER_CAP=5000`.
- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` — aggiunti 11 validator V21 + nuove regole SUPERSEDED (`SUPERSEDED_AFTER_RATE_LIMIT`, `SUPERSEDED_AFTER_STAGE4`, `SUPERSEDED_AFTER_V21_SCRIPTS`).

**NON modificati (invarianti hard):** `battle_engine.py`, `battle_core.py`, `combat.tsx`, `synergy_system.py`, `game_systems.py`, gacha/roster/Character Bible/skill catalogs/final_numbers.

## 3. Preflight V21

✅ PASS — tutti i gate verdi:
- `api_health_200`, `heroes_100`, `heroes_no_borea`, `canary_status_200`, `canary_flag_on`, `inv_writes_flag_on`, `stage3_allowlist_ge_200`, `cap_ge_2500`, `ledger_within_cap`, `battle_off`, `combat_off`, `buffs_off`, `borea_404`, `greek_borea_404`, `primordial_gaia_404`, `non_allowlist_423`, `battle_files_unchanged`, `db_connectivity`, `ugi_no_negative`, `inv_aff_mut_equal`, `no_buffs_rows`, `no_battle_wiring_rows`, `no_borea_hero_rows`, `baseline_v6_diff_pass`, `suite_pass`, `ui_preview_present`, `ui_preview_no_spend_post`, `ui_preview_no_borea`, `locust_binary_present`, `locust_version_known`, `db_backup_dest_writable`, `v20_stage4_plan_present`, `v20_signoff_package_v5_present`.

## 4. Signoffs V5 APPLY

- File originale `af2n_stage4_signoff_package_v5.json` **invariato** (storico PENDING).
- Nuovo file `af2n_stage4_signoff_package_v5_applied.json` con:
  - **7/7 operator signoffs PASSED** (product, engineering, qa, economy_balance, rollback_owner, security_abuse, support_ops) con evidence_actually_present popolata.
  - **final_user_apply_approval_v5: PASSED** — source `USER_MESSAGE_V21_ZIP_OPZIONE_1_2026_05_18`.
  - `stage4_apply_allowed=true`.

## 5. Rate-Limit Middleware / Guard

- **Tipo:** route-level guard in-memory (sliding window per-user e per-IP).
- **Limiti:** 30/min per-user, 240/h per-user, 60/min per-IP, burst 6 in 10s.
- **Comportamento:** 429 su breach, **nessun DB write**, Borea 404 sempre prima.
- **Probe automatico:** 12 POST burst → 6×423 poi 6×429 (PASS).
- **Smoke manuale:** stessi pattern confermati. Idempotent replay non penalizzato (i pre-allowlist 423 contano nella finestra, ma il test mostra che dopo cooldown comportamento ritorna normale).

## 6. DB Backup Drill REAL (non distruttivo)

- 3 collezioni dumpate in `/app/backups/af2n_stage4/backup_<STAMP>/`:
  - `gift_transaction_ledger.json` (sha256)
  - `user_gift_inventory.json` (sha256)
  - `user_affinity_state.json` (sha256)
- Conteggi live = conteggi re-letti dal file → `all_collections_ok=true`.
- **Restore eseguito: NO** (solo dry-run). Restore plan documentato a 6 step.

## 7. Stage4 APPLY summary

✅ **APPLIED** — `stage4_applied=true`
- Allowlist size: **200 → 700** (aggiunti 500 utenti `stage4_qa_001..500`).
- Cap ledger: **2500 → 5000**.
- Seed inventory: **500 nuovi documenti** in `user_gift_inventory` (`gift_test_001`, qty=10, marker `V21_STAGE4`).
- Backup supervisor.conf creato prima del flip.
- Backend riavviato; canary-status post-apply OK.

## 8. Stage4 Monitoring V21

✅ PASS — 103 sample: `{200: 60, 429: 40, 404: 3}`
- 0 5xx, idempotent replay coerente, Borea 404 su 3 alias, rate-limit triggered su burst, ledger entro cap.

## 9. Locust Stage4 V21 (low-impact)

✅ PASS — 30s, 4 utenti virtuali, growth ledger=5 (cap=5000, soglia safe ≤15).
- Mix traffico: status, replay, non-allowlist, fresh capped (budget 5), Borea probe.

## 10. UI Safety Recheck

✅ PASS — `/app/frontend/app/affinity-gifts-preview.tsx`:
- Nessun `method: 'POST'/'PUT'/'PATCH'/'DELETE'` nel codice.
- Solo `GET /api/affinity/gift-spend/canary-status`.
- Nessun riferimento Borea nel codice (solo nei commenti di sicurezza).
- `accessibilityLabel`/`accessibilityRole` presenti.

## 11. Rollback Readiness V21

✅ PASS — script di rollback presenti, sintatticamente validi, backup pre-stage4 disponibile.
- Path rollback Stage4: `rollback_af2n_stage4_internal_beta.py` (DRY-RUN default; `STAGE4_ROLLBACK_DRY_RUN=false` per esecuzione reale).
- Rate-limit disable: rimuovere flag in supervisor.conf + restart.

## 12. Safety Rollup P (v16)

✅ PASS — `stage4_state=stage4_internal_beta_active_no_broad_rollout`
- `broad_rollout_authorized=false`, `public_spend_ui=false`, `battle_wiring_live=false`, `buffs_enabled=false`, `borea_hidden=true`, `rate_limit_active=true`, `db_backup_drill_pass=true`, `rollback_ready=true`.
- Decisione consigliata: **`stage4_observation_window_24_72h`**.

## 13. Borea safety

✅ Tutti gli alias (`borea`, `greek_borea`, `primordial_gaia`) restituiscono **404** sul gift-spend POST. `/api/heroes` list **non li contiene** (100 esatti).

## 14. Validator results

| Validator | Esito |
|---|---|
| V21-PREFLIGHT | PASS |
| AF2-N-STAGE4-SIGNOFFS-V5-APPLIED | PASS |
| AF2-N-V21-RATE-LIMIT-AUDIT | PASS |
| AF2-N-V21-RATE-LIMIT-PROBE | PASS |
| AF2-N-V21-DB-BACKUP-DRILL | PASS |
| AF2-N-STAGE4-INTERNAL-BETA-APPLY | PASS |
| AF2-N-V21-STAGE4-MONITORING | PASS |
| AF2-L-LOCUST-STAGE4-V21 | PASS |
| AF2-N-PUBLIC-UI-PREVIEW-V21-SAFETY | PASS |
| V21-ROLLBACK-READINESS | PASS |
| SAFETY-ROLLUP-P | PASS |
| ULTRA-COMBO-V21 (composite) | **PASS** |

## 15. Suite / baseline

- `run_hero_skill_kit_validator_suite.py` → **PASS (121/121)**.
- `run_hero_skill_kit_validator_suite.py --include-baseline-diff` → **PASS (122/122)**.
- `validate_hero_skill_kit_catalog_baseline_diff.py` → **PASS** (baseline `rm134b_axispatch_v6` invariata).
- Validator obsoleti correttamente marcati SUPERSEDED (Stage4/V21/rate-limit/scripts).

## 16. API smoke

| Endpoint | Atteso | Risultato |
|---|---|---|
| GET `/api/health` | 200 | ✅ 200 |
| GET `/api/heroes` (count) | 100 | ✅ 100 |
| GET `/api/affinity/gift-spend/canary-status` | 200 | ✅ 200 |
| POST stage4_qa_200 fresh | 200 | ✅ 200 |
| POST stessa idempotency_key | 200 (replay) | ✅ 200 (replay) |
| POST non-allowlist | 423 | ✅ 423 |
| POST `borea`/`greek_borea`/`primordial_gaia` | 404 | ✅ 404 × 3 |
| POST burst 12× stesso user | primi 6 = 423, dopo = 429 | ✅ 6×423, 6×429 |

## 17. Runtime / DB / gacha / roster / catalog safety

- Runtime: `AFFINITY_GIFT_RUNTIME_ENABLED=true_explicit_affinity_gift_runtime_on` (V12).
- Inventory writes: `AFFINITY_GIFT_INVENTORY_WRITES_ENABLED=true_explicit_affinity_inventory_on` (V16).
- Rate-limit: `AFFINITY_GIFT_RATE_LIMIT_ENABLED=true_explicit_affinity_rate_limit_on` (V21 — nuovo).
- DB: solo collezioni affinity scritte; nessuna mutazione su `heroes`, `gacha`, `roster`, `Character Bible`, `skill catalogs`, `final_numbers`.
- `git diff` su file di combattimento: **vuoto** (battle_engine, battle_core, combat.tsx, synergy_system, game_systems).

## 18. Warnings

- ⚠️ Rate-limit usa storage **in-memory per-processo** → reset al restart del backend. Adeguato per canary/Stage4; per Stage5/broad-rollout serve Redis-backed.
- ⚠️ Idempotent replay condivide la quota rate-limit con fresh spend (può causare 429 sotto burst alto su client legittimo). Documentato; comportamento safe (no DB write).
- ⚠️ Locust totals show 4xx come "failures" nelle stat lorde, ma il codice marca esplicitamente 423/429/404 come `r.success()` quando attesi → returncode locust=0.

## 19. Final recommendation

**OBSERVATION WINDOW 24-72h** — mantenere Stage4 stabile, monitorare:
- ledger growth rate
- 5xx count
- non-allowlist success (deve restare 0)
- rate-limit 429 ratio
- inventory/affinity delta consistency

**NON autorizzato** in questa fase:
- Broad rollout
- Public Spend UI
- STACK-G / battle wiring
- Attivazione buff combat
- Modifiche a `battle_engine.py` / `combat.tsx`

## 20. Suggested next tasks

1. **P1** — Stage4 Extended Monitoring (24-72h) — script V22.
2. **P1** — Stage4 inventory/affinity delta audit periodico.
3. **P2** — Broad rollout planning (gated, plan-only) — solo dopo finestra observation pulita.
4. **P2** — Rate-limit migration a backend distribuito (Redis token bucket) — prerequisito per broad rollout.
5. **P3** — Public Spend UI design (gated, plan-only, NON enable).
6. **P4** — STACK-G full battle wiring (deferred).
