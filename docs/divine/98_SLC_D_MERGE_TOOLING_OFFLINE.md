# 98 · SLC-D — MERGE TOOLING OFFLINE SIMULATION

**Stato**: ✅ DESIGN-ONLY / DRY-RUN — TUTTI I VALIDATOR PASS
**Modalità**: Read-only / Audit-only / Offline-simulation
**Suite globale**: `RM1.31-B Hero Skill Kit Validator Suite` → **317 PASS / 0 FAIL / 0 MISS**
**Data esecuzione**: vedi `/app/backend/reports/slc_d_final_suite_run.json`

---

## 1. Obiettivo del task

SLC-D consolida l'intera **catena di strumenti di Merge tra server (offline-only)**
prima di qualsiasi futura esecuzione runtime. Tutto è prodotto come **contratti JSON
di design** e **validator/simulatori Python** che non scrivono mai sul database,
non toccano `battle_engine.py`, `combat.tsx`, gacha, roster o Character Bible,
e non modificano runtime, routing o auth.

Invarianti di sistema confermate dopo l'esecuzione completa della suite:

| Endpoint | Atteso | Osservato |
|---|---|---|
| `GET /api/heroes` (count) | **100** | **100** ✅ |
| `GET /api/heroes/primordial_gaia` | **404** | **404** ✅ |
| `GET /api/heroes/borea` | **200** (catalog-only inert) | **200** ✅ |
| `GET /api/heroes/greek_borea` | **200** (catalog-only inert) | **200** ✅ |

---

## 2. Artefatti generati

### 2.1 Contratti JSON di design (in `/app/data/design/server_lifecycle/`)

| File | Scopo |
|---|---|
| `server_merge_tooling_offline_plan_v1.json` | Piano master delle fasi tooling offline |
| `server_merge_eligibility_policy_v1.json` | Criteri di eleggibilità (estesi, retro-compatibili) |
| `server_merge_group_planning_contract_v1.json` | Contratto di pianificazione gruppi merge |
| `server_merge_conflict_resolution_contract_v1.json` | Risoluzione conflitti (ID, nomi, gilde, classifiche) |
| `server_merge_recovery_season_contract_v1.json` | Contratto stagione di recovery post-merge |
| `server_merge_calendar_harmonization_policy_v1.json` | Armonizzazione calendari live mode |
| `server_merge_dryrun_scenarios_v1.json` | Scenari dry-run canonici |
| `server_merge_risk_matrix_v1.json` | Matrice di rischio merge |
| `server_merge_abort_rollback_policy_v1.json` | Policy abort + rollback |
| `merge_recovery_season_policy_v1.json` | Policy recovery (pre-esistente, ri-verificata) |
| `merge_catch_up_pool_schema_v1.json` | Schema catch-up pool |

### 2.2 Validator / Simulator / Audit Python (in `/app/backend/scripts/`)

| Script | Tipo |
|---|---|
| `validate_slc_d_preflight_v1.py` | Preflight design-only |
| `validate_server_merge_tooling_offline_plan_v1.py` | Validator piano master |
| `validate_server_merge_eligibility_policy_v1.py` | Validator eleggibilità |
| `validate_server_merge_group_planning_contract_v1.py` | Validator gruppi |
| `validate_server_merge_conflict_resolution_contract_v1.py` | Validator conflitti |
| `validate_server_merge_recovery_season_contract_v1.py` | Validator stagione recovery |
| `validate_server_merge_recovery_policy_v1.py` | Validator policy recovery |
| `validate_server_merge_calendar_harmonization_policy_v1.py` | Validator armonizzazione calendari |
| `validate_server_merge_dryrun_scenarios_v1.py` | Validator scenari dry-run |
| `simulate_slc_d_merge_tooling_offline_v1.py` | Simulatore offline (PASS) |
| `validate_server_merge_risk_matrix_v1.py` | Validator matrice rischi |
| `validate_server_merge_abort_rollback_policy_v1.py` | Validator abort/rollback |
| `audit_slc_d_runtime_safety_v1.py` | Audit safety runtime (read-only) |
| `validate_slc_d_merge_tooling_offline_readiness_rollup_v1.py` | Roll-up readiness |
| `validate_slc_d_merge_tooling_combo_v1.py` | Combo orchestrator |

---

## 3. Registrazione nella suite master

I 15 task SLC-D sono stati registrati nella sezione **OPTIONAL** di
`/app/backend/scripts/run_hero_skill_kit_validator_suite.py` con prefisso `SLC-D-*`:

```
SLC-D-PREFLIGHT
SLC-D-TOOLING-OFFLINE-PLAN
SLC-D-ELIGIBILITY-POLICY
SLC-D-GROUP-PLANNING-CONTRACT
SLC-D-CONFLICT-RESOLUTION-CONTRACT
SLC-D-RECOVERY-SEASON-CONTRACT
SLC-D-RECOVERY-POLICY
SLC-D-CALENDAR-HARMONIZATION-POLICY
SLC-D-DRYRUN-SCENARIOS
SLC-D-OFFLINE-SIMULATION
SLC-D-RISK-MATRIX
SLC-D-ABORT-ROLLBACK-POLICY
SLC-D-RUNTIME-SAFETY-AUDIT
SLC-D-READINESS-ROLLUP
SLC-D-COMBO
```

Tutti riportano `[PASS]` con exit code `0` nell'ultima esecuzione master.

---

## 4. Risultato suite globale

```
RM1.31-B — Hero Skill Kit Validator Suite Runner
Overall: PASS  (pass=317, fail=0, miss=0)
JSON report: /app/backend/reports/slc_d_final_suite_run.json
```

**Delta vs baseline pre-SLC-D**: +15 OPTIONAL (302 → 317). Nessun task pre-esistente
è stato indebolito, supersedato o rimosso.

---

## 5. Issue rilevata e risolta durante l'integrazione

Durante l'esecuzione iniziale della suite master, due validator pre-esistenti
(`SERVER-LIFECYCLE-POLICIES-A` e `SERVER-LIFECYCLE-COMBO-A`) hanno fallito con
errore `merge:age_threshold_too_low`.

**Causa**: lo ZIP SLC-D ha sovrascritto `server_merge_eligibility_policy_v1.json`
con uno schema nuovo (`eligibility_criteria`) eliminando lo schema legacy
(`eligibility_inputs`) atteso dal validator pre-esistente.

**Risoluzione (non indebolente)**: il blocco legacy `eligibility_inputs` è stato
**ripristinato verbatim** dal commit pre-SLC-D, in coesistenza additiva con il
nuovo blocco `eligibility_criteria` SLC-D. Nessun valore è stato abbassato
(soglia `server_age_threshold_days_min=90` mantenuta). Vedi nota inline
nel JSON.

Post-fix: entrambi i validator passano nuovamente, e il combo SLC-D continua
a passare.

---

## 6. Guardrail rispettati

- ✅ **NO** DB write / migration / index creation
- ✅ **NO** route runtime / auth / server selection modificati
- ✅ **NO** modifiche a `battle_engine.py`, `battle_core.py`, `combat.tsx`
- ✅ **NO** modifiche a `affinity_gift_spend.py`, AF2-N, Stage4, Redis runtime
- ✅ **NO** modifiche a gacha, roster, Character Bible, cataloghi, asset
- ✅ **NO** apertura secondo server
- ✅ **NO** indebolimento test esistenti

`merge_execution_allowed=false` e `db_write=false` in TUTTI i JSON SLC-D.
L'audit `audit_slc_d_runtime_safety_v1.py` conferma che nessuna scrittura runtime
è attaccata.

---

## 7. Prossimi passi (gated, NON eseguiti)

- **SLC-G** (P1): default S1 migration commit — strettamente dry-run gated
- **SLC-H** (P1): server selection endpoint — design-only
- **COSMETIC-B/C/D/E** (P2): read-only/inert
- **Managed Redis Live / Alerting Sink Live** (P3): pendono env vars
- **Broad Rollout / Public Spend UI / STACK-G** (P4): strettamente OFF

Nessuno di questi è stato toccato in questa fase.

---

**Verdict finale**: ✅ **SLC-D COMPLETE — READY_NOT_APPLIED**
