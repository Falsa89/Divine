# ULTRA-COMBO V20 — STAGE4 INTERNAL BETA PLAN-ONLY + ROLLBACK DRILLS + SIGNOFFS V5 + LOCUST EXTENDED LOW-IMPACT + PUBLIC UI PREVIEW QA/A11Y AUDIT + SAFETY-ROLLUP-O

**Project**: Divine RPG / Divine Waifus
**Baseline anchor**: `hero_skill_kit_catalog_baseline_rm134b_axispatch_v6`
**Stato**: ✅ COMPLETATO — Stage4 **NON applicato**, plan + signoffs + drills + Locust ext + UI A11y completati. Suite 120/120 PASS.

---

## 1. File creati

### Scripts (`/app/backend/scripts/`)
- `validate_af2n_v20_preflight.py`
- `validate_af2n_stage4_internal_beta_plan.py`
- `run_af2n_v20_rollback_drills.py`
- `validate_af2n_v20_rollback_drill_result.py`
- `validate_af2n_stage4_signoff_package_v5.py`
- `run_af2n_v20_locust_extended_low_impact.py`
- `validate_af2n_v20_locust_extended_result.py`
- `audit_affinity_gifts_public_preview_qa_a11y.py`
- `validate_collection_affinity_runtime_activation_rollup_v15.py`
- `validate_ultra_combo_v20_stage4_readiness_drills.py`

### Locust
- `/app/loadtests/af2n_v20_stage3_extended_locustfile.py` (15 users / 40s, read-only + replay + reject paths, ZERO fresh spend)

### Design / safety JSON
- `/app/data/design/affinity/af2n_v20_preflight_result_v1.json`
- `/app/data/design/affinity/af2n_stage4_internal_beta_plan_v1.json`
- `/app/data/design/affinity/af2n_v20_rollback_drill_result_v1.json`
- `/app/data/design/affinity/af2n_stage4_signoff_package_v5.json`
- `/app/data/design/affinity/af2n_v20_locust_extended_result_v1.json`
- `/app/data/design/ui/affinity_gifts_public_preview_qa_a11y_audit_v1.json`
- `/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v15.json`

### Reports / docs
- `/app/backend/reports/suite_v20.json` (overall PASS, 120/120)
- `/app/backend/reports/ultra_combo_v20_validator_summary_v1.json`
- `/app/docs/divine/80_ULTRA_COMBO_V20_STAGE4_PLAN_DRILLS_SIGNOFFS_LOCUST_A11Y.md` (questo)

### Frontend (a11y improvements, read-only)
- `/app/frontend/app/affinity-gifts-preview.tsx` — aggiunti `accessibilityLabel` / `accessibilityRole` su header / scrollview / card / row / refresh / error box / info box / activity indicator. Aggiunto indicatore non-color-only (`✓ ` prefix per stati safe). Nessuna logica di mutazione introdotta.

---

## 2. File modificati

- `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` (registrati 8 nuovi validator V20)
- `/app/frontend/app/affinity-gifts-preview.tsx` (solo a11y attributes + checkmark prefix; nessun POST/mutation aggiunto)

**File esplicitamente NON modificati (invariante hard)**:
- `/app/backend/battle_engine.py`
- `/app/backend/battle_core.py`
- `/app/frontend/app/combat.tsx`
- `/app/backend/synergy_system.py`
- `/app/backend/game_systems.py`
- `/app/backend/routes/affinity_gift_spend.py` (zero modifiche in V20)
- `/etc/supervisor/conf.d/backend.conf` (zero modifiche; runtime invariato Stage3)
- **NESSUN** apply/rollback script Stage4 creato (PLAN-ONLY contract verificato in composite).

---

## 3. Preflight V20

**Status**: PASS. Tutti i gates verde, inclusi `locust_binary_present` + `locust_version_known` (locust v2.44.0), `ui_preview_present`, `ui_preview_no_spend_call`, `ui_preview_no_borea`, `suite_v19_pass`, `baseline_v6_diff_pass`.

Canary status snapshot al preflight: size=200, cap=2500, flag=on, inv=on, combat=off, battle=off, buffs=off.

---

## 4. Stage4 Internal Beta Plan

**Status**: PASS — `af2n_stage4_internal_beta_plan_v1.json`.
- `design_only: true`, `runtime_attached: false`, `plan_only: true`, `stage4_applied: false`
- `broad_rollout_authorized: false`, `public_spend_ui: false`, `battle_wiring: false`
- `explicit_status`: `PLAN_ONLY_NOT_APPLIED_REQUIRES_FULL_SIGNOFF_AND_USER_AUTHORIZATION`
- Target: 500 utenti sintetici internal (`stage4_qa`, `internal_eng`, `internal_econ`, `internal_support`); hard cap 1000.
- Target allowlist totale post-apply: 700; hard cap totale 1500.
- Ledger cap raccomandato: 5000; hard cap 10000.
- **Rate-limit plan**: 30 req/user/min, 240 req/user/h, 60 req/ip/min, 200 req/s globale (enforcement_status: `NOT_IMPLEMENTED_YET`).
- **Abuse monitoring**: 9 metriche + 5 alerting thresholds + 3 dashboards.
- **Borea safety gates**, **economy caps** (max_q/tx=100, max_inv_balance/gift=1000, weekly cap/user=2000), **rollback plan** (rollback target → stage3_200_users_ledger_cap_2500).
- **9 gate** richiesti prima di apply (incluso `final_user_apply_approval_v5=true`, apply/rollback script creati e auditati, observation window 24-72h completa).
- 11 abort triggers documentati.

---

## 5. Rollback Drills

**Status**: PASS — `af2n_v20_rollback_drill_result_v1.json`.
- `mode: dry_run_only`, `no_actual_state_change: true`
- **7 drill** documentati:
  1. **Stage3 rollback dry-run** → exit 0 ✅
  2. **Stage2 rollback dry-run** → exit 0 ✅
  3. **Inventory flag rollback plan** (ops shell `/app/ops/rollback_af2n_canary.sh`) — 3 plan steps
  4. **Full AF2-N canary rollback plan** — 4 plan steps (clear allowlist, set caps=0, restart, verify)
  5. **UI preview rollback plan** — `rm /app/frontend/app/affinity-gifts-preview.tsx && rebuild`
  6. **Locust stop/abort plan** — `pkill -f locust`, verifica no lingering processes
  7. **DB backup/restore plan** — comandi `mongodump --db divine_waifus --collection user_gift_inventory|user_affinity_state|gift_transaction_ledger` (mongodump/mongorestore presenti)
- **0 failures** aggregati

---

## 6. Signoffs V5

**Status**: PASS (package draftato; **TUTTI i signoff PENDING**, apply DENIED).
- File: `af2n_stage4_signoff_package_v5.json`
- `stage4_apply_allowed: false`, `final_user_stage4_apply_approval: false`
- `explicit_status`: `PACKAGE_DRAFTED_ALL_SIGNOFFS_PENDING_APPLY_DENIED`
- 7 operator signoff: `product_v5`, `engineering_v5`, `qa_v5`, `economy_balance_v5`, `rollback_owner_v5`, `security_abuse_v5`, `support_ops_v5` → tutti `PENDING` con blockers espliciti
- 1 final user signoff: `final_user_apply_approval_v5` → `NOT_GRANTED`
- `global_status_summary.operator_signoffs_passed_count`: **0** / 7
- 8 `required_for_apply` clauses (`all_7_operator_signoffs_status_PASSED`, `final_user_apply_approval_v5_true`, `all_blockers_resolved`, `apply_script_for_stage4_created_and_audited`, `rollback_script_for_stage4_created_and_audited`, `db_backup_drill_executed_real_mongodump`, `rate_limit_middleware_implemented_or_explicit_acceptance`, `24_72h_observation_window_completed`)

**Apply RIMANE DENIED finché tutti i blockers non sono risolti e ottenuti tutti i signoff.**

---

## 7. Locust Extended Low-Impact

**Status**: PASS — `af2n_v20_locust_extended_result_v1.json`.
- Locust v2.44.0 (reinstallato system-wide in V20 dopo che era stato purgato)
- Comando: `locust -f /app/loadtests/af2n_v20_stage3_extended_locustfile.py --headless -u 15 -r 5 -t 40s --host http://127.0.0.1:8001 --only-summary --csv /tmp/v20_locust_csv --csv-full-history`
- Exit code: **0**, durata ~40s
- Snapshot DB pre/post:
  - `delta.ledger_total` = **0** ✅ (zero crescita ledger)
  - `delta.borea_hero` = 0, `delta.buffs` = 0, `delta.battle_wiring` = 0, `delta.negative_inventory` = 0
- Triggers: **0**
- CSV summary salvato in `/tmp/v20_locust_csv_stats.csv`

**Nessuna crescita di stato dal load test reale**. Le authoritative safety checks sono exit_code==0 + delta DB == 0 (NON la parsificazione testuale fragile dell'aggregated row di Locust).

---

## 8. Public UI Preview QA / A11y Audit

**Status**: PASS (29/29) — `affinity_gifts_public_preview_qa_a11y_audit_v1.json`.
- ✅ File presente, no mutating HTTP methods, no Spend/Claim/Give text, no Borea alias string
- ✅ Etichette `Design only` + `Spend disabled` presenti
- ✅ Solo endpoint `/api/affinity/gift-spend/canary-status` (no altri `/api/affinity/*`)
- ✅ Sanitizzazione: NO `canary_allowlist_size`, NO `user_id`, NO `ledger_total_rows` (verificato escludendo commenti); usato count-only per hidden_aliases (`__hidden_aliases_blocked_count__`)
- ✅ Mobile layout: SafeAreaView, ScrollView, RefreshControl, StyleSheet, Platform
- ✅ **A11y labels**: 11 (>=5), **A11y roles**: 8 (>=4)
- ✅ Indicatore non-color-only: prefisso `✓ ` su stati safe (accessibilità per daltonici)
- ✅ No menu/Tabs/Link discoverability verso `/affinity-gifts-preview`
- ✅ `combat.tsx` invariato, backend battle files invariati
- ✅ Bilanciamento sintattico (braces/brackets/parens)

---

## 9. Safety Rollup O

**Status**: PASS (`collection_affinity_runtime_activation_readiness_rollup_v15.json`).
- `supersedes`: rollup_v14
- `runtime_state`: **`stage3_qa_active_no_broad_rollout`** (invariato rispetto a V19)
- `stage3_state`: APPLIED
- `stage4_internal_beta_plan_ready`: true
- `stage4_applied`: **false**
- `public_ui_preview_state`: **`READONLY_QA_A11Y_AUDITED`**
- `broad_rollout_authorized`: false, `public_spend_ui`: false, `battle_wiring_live`: false, `buffs_enabled`: false
- `Borea_hidden`: true, `inventory_live_scope`: `stage3_allowlist_only`
- `rollback_ready`: true
- `locust_extended_status.overall`: PASS, `delta_ledger`=0
- `signoff_v5_status.operator_signoffs_passed_count`: 0 / 7, `stage4_apply_allowed`: false
- `public_ui_preview_qa_a11y.overall`: PASS, 29 checks
- `next_decision`: **`stage4_apply_requires_user_approval`**

---

## 10. Borea Safety

- `/api/heroes` count = **100**, nessun id Borea/greek_borea/primordial_gaia
- POST `/api/affinity/gift-spend` con hero_id Borea → **HTTP 404** (verificato in preflight + locust + composite)
- Ledger query `hero_id IN [borea, greek_borea, primordial_gaia]` → **0 righe**
- Preview UI: zero stringhe alias (audit V20 PASS)
- Stage4 plan elenca `borea_safety_gates` come gate obbligatori

---

## 11. Validator Results

| Task | Status |
|---|---|
| V20-PREFLIGHT | ✅ PASS |
| AF2-N-STAGE4-INTERNAL-BETA-PLAN | ✅ PASS (PLAN-ONLY) |
| AF2-N-V20-ROLLBACK-DRILLS | ✅ PASS (7 drills, dry-run only) |
| AF2-N-STAGE4-SIGNOFF-PACKAGE-V5 | ✅ PASS (apply DENIED, tutti PENDING) |
| AF2-L-LOCUST-EXTENDED-LOW-IMPACT-V20 | ✅ PASS (exit 0, delta_ledger=0) |
| AF2-N-PUBLIC-UI-PREVIEW-QA-A11Y-V20 | ✅ PASS (29/29) |
| SAFETY-ROLLUP-O | ✅ PASS |
| ULTRA-COMBO-V20 composite (38 checks) | ✅ PASS |

---

## 12. Suite / Baseline

- `python3 backend/scripts/run_hero_skill_kit_validator_suite.py --include-baseline-diff --json-out /app/backend/reports/suite_v20.json`
- **Overall: PASS** — pass=120, fail=0, miss=0
- 5 frozenset SUPERSEDED: `SUPERSEDED_AFTER_AF2N`, `SUPERSEDED_AFTER_INV_WRITES`, `SUPERSEDED_AFTER_STAGE2`, `SUPERSEDED_AFTER_STAGE3`, `SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW`
- **RM1.32-PRE baseline diff**: PASS (`hero_skill_kit_catalog_baseline_rm134b_axispatch_v6` invariato)

---

## 13. API Smoke (post-V20)

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/health` | 200 | ✅ |
| `GET /api/heroes` | 100, no Borea | ✅ |
| `GET /api/affinity/gift-spend/canary-status` | 200, size=**200**, cap=**2500**, ledger=64, flag=on, inv=on, combat=off | ✅ (Stage3 unchanged, **Stage4 NOT applied**) |
| `POST gift-spend` Borea | 404 | ✅ 404 |
| `POST gift-spend` non-allowlist | 423 | ✅ 423 |
| `POST gift-spend` Stage3 user con inventory | 200 `applied_inventory_live` | ✅ verificato in Locust replay + extended runs |
| `POST gift-spend` idempotent replay | 200 `idempotent_replay` (no state change) | ✅ |

---

## 14. UI Safety

- ❌ Nessun bottone public spend.
- ❌ Nessun bottone claim/give.
- ❌ Nessuna mutazione UI (solo GET sanitizzato).
- ❌ Nessun runtime toggle in UI.
- ❌ Nessun battle wiring UI.
- ❌ Nessuna rivelazione Borea (audit V20 PASS — sanitizzazione robusta anche con commenti).
- ✅ Public UI preview rimane **READ-ONLY** con etichetta `Design only — Spend disabled`.
- ✅ A11y migliorato: 11 `accessibilityLabel`, 8 `accessibilityRole`, prefisso `✓ ` per stati safe (non-color-only).
- ✅ `combat.tsx` invariato.

---

## 15. Runtime / DB / Gacha / Roster / Catalog Safety

- **Runtime**: stato Stage3 **invariato** in V20 (allowlist 200, cap 2500, ledger 64). `applied_to_combat=false`, `battle_runtime_attached=false`, `buffs_enabled=false`.
- **DB**:
  - `gift_transaction_ledger`: 64 righe totali, tutte `canary=True`. inv/aff mut equal. 0 buffs, 0 battle wiring, 0 Borea heroes.
  - `user_gift_inventory`: 0 docs `quantity<0`. **0 docs con `metadata.seed_task=V20_STAGE4`** (verificato in composite: Stage4 NOT seeded).
- **Gacha / Roster / Character Bible / asset / skill catalogs / final_numbers**: NESSUNA modifica.
- **Supervisor.conf**: NESSUNA modifica.

---

## 16. Warnings

- **Locust install volatilità**: Locust era stato purgato dall'env tra V19 e V20 (probabilmente da supervisor restart con `pip install -r requirements.txt`). Reinstallato system-wide in V20. Future hardening: aggiungere `locust` a `requirements.txt` via `pip freeze` quando appropriato (P2 task).
- **Locust failure rate parsing**: la parsificazione testuale dell'aggregated row di Locust è risultata fragile (n_reqs/n_fails parsing inaffidabile tra versioni). Il runner V20 ora si affida esclusivamente a `exit_code` + delta DB + DB invariants come safety check authoritative; i campi parsati restano come informazione ops.
- **UI audit comment-aware**: l'audit QA/A11y V20 ora striscia commenti TS/JS prima dei content-leak check per evitare falsi positivi su commenti documentali legittimi (es. `// Sanitize: never display canary_allowlist_size, ...`).
- **k6** non installato — task gated separato.

---

## 17. Final Recommendation

**Recommendation**: **STAGE4_APPLY_REQUIRES_USER_APPROVAL**.

V20 ha consolidato la readiness completa per Stage4 senza applicare:
- Stage4 plan dettagliato e validato (PLAN-ONLY)
- 7 rollback drills dry-run PASS
- Signoff package V5 draftato con 7 operator + 1 final-user, tutti `PENDING` (apply DENIED)
- Locust extended low-impact PASS (15 vus, 40s, delta_ledger=0)
- Public UI preview READ-ONLY auditata QA/A11y (29/29) con miglioramenti accessibili
- Tutti gli invarianti hard tenuti: /api/heroes=100, Borea hidden/404, battle/combat files NON modificati, no public spend UI, no broad rollout, no battle wiring, no buffs, no gacha/roster/catalog mutation
- Stage3 runtime **invariato** (200 users, cap 2500, ledger 64)

Prossimo passo **richiede esplicita autorizzazione utente V5** PIÙ:
- Tutti i 7 operator signoffs PASSED (con blockers risolti)
- Apply + rollback script Stage4 creati e auditati
- DB backup drill con `mongodump` reale eseguito
- Rate-limit middleware implementato o esplicita acceptance
- Observation window 24-72h completata

**Broad rollout, public spend UI, STACK-G restano gated e NON autorizzati.**

---

## 18. Suggested Next Tasks

- **P1** `AF2-N-STAGE4-OPERATOR-SIGNOFF-EXECUTION` — raccolta signoff reali dai 7 owner; aggiornare statuses in `af2n_stage4_signoff_package_v5.json` con firma + data.
- **P1** `AF2-N-STAGE4-APPLY-SCRIPT` — creare `apply_af2n_stage4_internal_beta.py` (gated, con hard caps, backup, seed-before-flip, smoke verify) — **NON eseguire apply** senza signoffs+approval.
- **P1** `AF2-N-STAGE4-ROLLBACK-SCRIPT` — creare `rollback_af2n_stage4_internal_beta.py` (dry-run + execute pattern).
- **P1** `AF2-N-DB-BACKUP-DRILL-REAL` — eseguire `mongodump` reale per le 3 collezioni canary; conservare in `/app/ops/backups/dbdump_*`; testare `mongorestore` in ambiente isolato.
- **P1** `AF2-N-RATE-LIMIT-MIDDLEWARE` — implementare rate-limit middleware backend con env-driven thresholds (per-user/min, per-ip/min, global/sec).
- **P1** `AF2-N-STAGE3-OBSERVATION-24-72H` — completare la observation window con scheduled cron sui validator V19/V20.
- **P2** `AF2-L-LOCUST-RAMP-V21` — Locust scaling controllato (30 vus → 50 → 100) con caps espliciti, sempre read-only/replay/reject.
- **P2** `AF2-N-ABUSE-DASHBOARDS` — implementare le 3 dashboards (`affinity_canary_health`, `affinity_idempotency`, `affinity_economy_delta`).
- **P2** `OPS-F-LOCUST-IN-REQUIREMENTS` — aggiungere locust a requirements.txt via pip freeze controllato.
- **P3** `STACK-G-WIRING-FULL` — **deferred**.
- **P3** `PUBLIC_SPEND_UI` — **deferred**.

---

## Acceptance V20 — Checklist Finale

- [x] no broad rollout
- [x] Stage4 PLAN-ONLY (non applicato)
- [x] no public spend UI
- [x] Stage3 resta gated (200 users, cap 2500)
- [x] Locust extended safe (exit 0, delta_ledger=0)
- [x] rollback drills PASS (7 drills, dry-run only)
- [x] signoff package safe (apply DENIED, tutti PENDING)
- [x] no battle wiring
- [x] /api/heroes = 100
- [x] Borea hidden/404
- [x] no unauthorized spend
- [x] no 5xx critico
- [x] suite/baseline PASS (120/120, RM1.32-PRE PASS)
- [x] UI safety PASS (audit 29/29)
- [x] no battle/gacha/roster/catalog mutation

**ULTRA-COMBO V20 — COMPLETATO**
