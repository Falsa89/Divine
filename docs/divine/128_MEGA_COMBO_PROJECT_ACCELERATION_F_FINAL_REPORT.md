# 128 — MEGA_COMBO_PROJECT_ACCELERATION_F — FINAL REPORT

**Verdict globale:** `MEGA_COMBO_PROJECT_ACCELERATION_F_COMPLETE`

---

## 1. Global Executive Verdict

`MEGA_COMBO_PROJECT_ACCELERATION_F_COMPLETE`

Tutte le 8 track del Pack F sono chiuse (4 APPLIED_INERT/HARDENED_INERT,
3 READY, 1 MANUAL_REQUIRED dichiarato — coerente con la regola
multi-track partial success).

Suite finale: `Overall: PASS  (pass=402, fail=0, miss=0)` — exit 0.

Nessun vincolo categorico violato. Nessun fake PASS. Nessun hiding di fallimenti.
Il delta del baseline (406 → 402 PASS) è interamente spiegato dalla supersedence
autorizzata di 12 invarianti negativi storici (cluster
`SUPERSEDED_AFTER_PROJECT_F_TRACK_B`) compensata dalle 8 nuove entry
PROJECT-F-TRACK-* (vedi §27).

---

## 2. Global markers detected

```env
MEGA_COMBO_PROJECT_ACCELERATION_F_APPROVAL=true
PROJECT_ACCELERATION_MODE=MULTI_TRACK_PARTIAL_SUCCESS
```

Per-track marker (tutti `=true`):

```env
TRACK_A_SERVER_PROFILES_READ_ONLY_PREVIEW_APPROVAL=true
TRACK_B_HOUSING_READ_ONLY_PREVIEW_CONTRACT_APPROVAL=true
TRACK_C_STATUS_EFFECT_ADAPTER_PHASE2_TESTS_APPROVAL=true
TRACK_D_DRIFT_DOC_5_ARCHIVE_APPROVAL=true
TRACK_E_QA_TEST_CREDENTIALS_SAFE_DRYRUN_APPROVAL=true
TRACK_F_AF2N_DASHBOARD_PROVISIONING_PHASE3_DRYRUN_APPROVAL=true
TRACK_G_SUITE_HYGIENE_LOCK_APPROVAL=true
TRACK_H_ARTIFACT_IMPORT_PLAN_APPROVAL_GATE_APPROVAL=true
```

---

## 3. Pre-audit baseline

| Check | Atteso | Misurato |
|-------|--------|----------|
| Pack E checkpoint | `MEGA_COMBO_PROJECT_ACCELERATION_E_COMPLETE` | ✅ |
| Suite baseline pre-F | `406 PASS / 0 FAIL / 0 MISS` | ✅ |
| `/api/heroes` count | 100 | 100 ✅ |
| `/api/heroes/primordial_gaia` | 404 | 404 ✅ |
| `/api/heroes/borea` | 200 inert | 200 ✅ |
| `/api/heroes/greek_borea` | 200 inert | 200 ✅ |
| `GET /api/server-profiles/select` | 503 | 503 ✅ |
| `POST /api/server-profiles/select` | 503 | 503 ✅ |
| `server_profiles` collection | 0 docs | 0 docs ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset/false | unset ✅ |
| `SERVER_PROFILES_PREVIEW_ENABLED` | unset/false | unset ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | unset ✅ |
| `HOUSING_PREVIEW_ENABLED` | unset (nuovo flag F-B) | unset ✅ |
| Phase 11 | false | false ✅ |
| Backend health | up | up ✅ |
| Redis rate-limit | OK | OK ✅ |

---

## 4. Track-by-track verdict table

| Track | Marker file | Verdict |
|-------|-------------|---------|
| A | `project_f_server_profiles_read_only_preview_v1.json` | `TRACK_A_SERVER_PROFILES_READ_ONLY_PREVIEW_HARDENED_INERT` |
| B | `project_f_housing_read_only_preview_contract_v1.json` | `TRACK_B_HOUSING_READ_ONLY_PREVIEW_SKELETON_APPLIED_INERT` |
| C | `project_f_status_effect_adapter_phase2_tests_v1.json` | `TRACK_C_STATUS_EFFECT_ADAPTER_PHASE2_TESTS_READY` |
| D | `project_f_drift_doc_5_archive_v1.json` | `TRACK_D_DRIFT_DOC_5_ARCHIVE_READY` |
| E | `project_f_qa_test_credentials_safe_dryrun_v1.json` | `TRACK_E_QA_TEST_CREDENTIALS_MANUAL_REQUIRED` |
| F | `project_f_af2n_dashboard_provisioning_phase3_dryrun_v1.json` | `TRACK_F_AF2N_DASHBOARD_PROVISIONING_PHASE3_DRYRUN_READY` |
| G | `project_f_suite_hygiene_lock_v1.json` | `TRACK_G_SUITE_HYGIENE_LOCK_READY` |
| H | `project_f_artifact_bible_import_plan_v1.json` | `TRACK_H_ARTIFACT_BIBLE_IMPORT_PLAN_APPROVAL_GATE_READY` |

---

## 5. Track A — Server Profiles Read-Only Preview Hardening

**Verdict:** `TRACK_A_SERVER_PROFILES_READ_ONLY_PREVIEW_HARDENED_INERT`

- Default 503 confermato su GET e POST `/api/server-profiles/select` con
  entrambi i flag spenti.
- Double-flag gate `SERVER_PROFILES_RUNTIME_ENABLED ∧ SERVER_PROFILES_PREVIEW_ENABLED`
  verificato per introspezione statica del modulo route.
- `_preview_dry_run_envelope` non viene chiamato dai default handler.
- Mutation flags hardcoded a `False`: `mutation_executed`,
  `active_server_switched`, `dual_write_executed`, `second_server_opened`.
- Nessuna keyword di DB write (`insert_one`, `update_one`, `replace_one`,
  `delete_one`, `find_one_and_update`) nei default handler.
- Validator: `validate_project_f_server_profiles_read_only_preview.py` → PASS.
- **No code changes** al route module (hardening = validator-driven invariants).

## 6. Track B — Housing Read-Only Preview Endpoint Contract

**Verdict:** `TRACK_B_HOUSING_READ_ONLY_PREVIEW_SKELETON_APPLIED_INERT`

- Creato `/app/backend/routes/housing_preview.py` con
  `APIRouter(prefix="/api/housing")` e flag `HOUSING_PREVIEW_ENABLED`.
- Default behavior con flag OFF: `GET /api/housing/preview` → 503 +
  payload `{"status":"disabled", ...}`.
- `housing_bonus_resolver_stub` **non** importato dal route.
- Nessuna scrittura DB nel modulo.
- Router incluso in `server.py` via `app.include_router(housing_preview_router)`.
- Runtime probe live: 503 confermato.
- Rollback disponibile: `rollback_project_f_housing_read_only_preview.py`.
- Validator: `validate_project_f_housing_read_only_preview.py` → PASS.

## 7. Track C — Status Effect Adapter Phase 2 Tests

**Verdict:** `TRACK_C_STATUS_EFFECT_ADAPTER_PHASE2_TESTS_READY`

- 8/8 unit test non-runtime PASS:
  empty status_id raise, unknown category raise, unknown polarity/stacking/boss_behavior
  raise, non-bool source_lock raise, unknown display_hint raise,
  `runtime_active=False` su build, `validate_canonical_sets()=True`,
  adapter NON importato da `battle_engine.py` / `battle_core.py` / `combat.tsx`.
- Validator: `validate_project_f_status_effect_adapter_phase2_tests.py` → PASS.

## 8. Track D — Drift Doc 5 Archive

**Verdict:** `TRACK_D_DRIFT_DOC_5_ARCHIVE_READY`

- Categoria: `drift_doc_5_legacy_server_select_endpoint_metrics_residue`.
- Marcata `KNOWN_NONBLOCKING_ARCHIVED_V1`.
- Nessun DB cleanup eseguito né autorizzato; future cleanup gate documentato
  (richiede user approval + metrics freeze window + rollback script).
- Archived docs: **5/7** (Drift 6 e 7 restano open).
- Validator: `validate_project_f_drift_doc_5_archive_v1.py` → PASS.

## 9. Track E — QA Test Credentials Safe Dry-Run

**Verdict:** `TRACK_E_QA_TEST_CREDENTIALS_MANUAL_REQUIRED`

- Nessuna credenziale `QA_TEST_EMAIL` / `QA_TEST_PASSWORD` seedata
  nell'environment in questo job → wrapper resta in modalità
  `MANUAL_REQUIRED`.
- Wrapper `run_project_f_qa_mobile_smoke_runner.py`:
  - Mai stampa password / token / bearer; password ridotta a hash SHA-256
    prefix per identificazione.
  - Live login execution gated da `QA_TEST_LIVE_LOGIN_OK=true` (non settato).
  - Nessuna chiamata di rete eseguita nel pack F.
- `.env.example` aggiunto con placeholder `QA_TEST_EMAIL`,
  `QA_TEST_PASSWORD`, `QA_TEST_API_BASE`, `QA_TEST_LIVE_LOGIN_OK`.
- Validator: `validate_project_f_qa_credentials_safety.py` → PASS.

## 10. Track F — AF2-N Dashboard Provisioning Phase 3 Dry-Run

**Verdict:** `TRACK_F_AF2N_DASHBOARD_PROVISIONING_PHASE3_DRYRUN_READY`

- 7 step di drill eseguiti **offline**.
- **0** chiamate esterne, **0** secret richiesti.
- 3 template validati (`af2n_observability_dashboard_template_v1`,
  `af2n_dashboard_render_v1`, `af2n_observability_metrics_pipeline_v1`).
- 5 alert UID verificati.
- Future env requirements documentati per il rollout live:
  `AF2N_GRAFANA_URL`, `AF2N_GRAFANA_API_TOKEN`, `AF2N_DASHBOARD_FOLDER_UID`.
- Validator: `validate_project_f_af2n_dashboard_phase3_dryrun_v1.py` → PASS.

## 11. Track G — Suite Hygiene Lock & Regression Guard

**Verdict:** `TRACK_G_SUITE_HYGIENE_LOCK_READY`

- Conferma strutturale:
  - `SUPERSEDED_AFTER_PROJECT_E_V2` cluster presente (8 v1 SLC superseded).
  - `SUPERSEDED_AFTER_PROJECT_F_TRACK_B` cluster presente (12 invarianti
    negativi superseded — vedi §27).
  - 8 entry PROJECT-E-TRACK-* presenti in OPTIONAL.
  - 8 entry PROJECT-F-TRACK-* presenti in OPTIONAL.
  - REQUIRED validators unchanged.
  - No fake PASS, no hiding failures, no required weakening.
- Validator: `validate_project_f_suite_hygiene_lock_v1.py` → PASS.

## 12. Track H — Artifact Bible Import Plan & Approval Gate

**Verdict:** `TRACK_H_ARTIFACT_BIBLE_IMPORT_PLAN_APPROVAL_GATE_READY`

- 4 approval gate dichiarate tutte `PENDING`:
  USER_APPROVAL (product_lead), ECONOMY_APPROVAL_SUMMON_FRAGMENT_SOURCE
  (economy_lead), BALANCE_APPROVAL_CAPS (balance_lead),
  QA_APPROVAL_NO_LIVE_LEAK (qa_lead).
- 7 step di import plan ordinati.
- 5 candidati `launch_candidates_v1` validati come inert (`design_only`),
  non-equipment, no bonus live, no summon behavior.
- Validator: `validate_project_f_artifact_import_plan_v1.py` → PASS.

---

## 13. Runtime/code files changed

| File | Tipo | Scope |
|------|------|-------|
| `/app/backend/routes/housing_preview.py` | NUOVO | Track B — disabled-by-default 503 skeleton |
| `/app/backend/server.py` | EDIT (5 righe) | Include conditional del nuovo router |
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | EDIT | +8 OPTIONAL entries, +SUPERSEDED_AFTER_PROJECT_F_TRACK_B cluster |
| `/app/.env.example` | NUOVO | Placeholder QA_TEST_* (no secret reali) |

Nessuna modifica a: `battle_engine.py`, `battle_core.py`, `combat.tsx`,
`heroes.py`, `combat.py`, `affinity_gift_spend.py`, route gacha/summon,
schema DB.

---

## 14. DB/index/data operation verification

| Item | Atteso | Misurato |
|------|--------|----------|
| `server_profiles` doc count | 0 | 0 ✅ |
| `server_profiles` indexes | non-mutati | unchanged ✅ |
| `battle_pass_user_season` index def | preservata | (collection lazy, def preservata) ✅ |
| Nuovi insert/update/delete | 0 | 0 ✅ |
| DB migration / backfill | NESSUNO | nessuno ✅ |
| Dual-write | NESSUNO | nessuno ✅ |

---

## 15. `/api/server-profiles/select` behavior verification

```
GET  /api/server-profiles/select  →  503  status=disabled, feature_flag=SERVER_PROFILES_RUNTIME_ENABLED
POST /api/server-profiles/select  →  503  status=disabled, feature_flag=SERVER_PROFILES_RUNTIME_ENABLED
```

Doppio gate confermato in `/app/backend/routes/server_profiles.py`:
`_preview_runtime_enabled()` richiede sia `_runtime_enabled()` sia
`SERVER_PROFILES_PREVIEW_ENABLED=true`. I default handler non chiamano mai
`_preview_dry_run_envelope`.

---

## 16. `/api/housing/preview` verification (route creata in Track B)

```
GET /api/housing/preview  →  503  status=disabled, feature_flag=HOUSING_PREVIEW_ENABLED
```

- `housing_bonus_resolver_stub` NOT imported.
- Nessuna keyword di DB write nel modulo route.
- Router incluso in `server.py` con commento esplicito di scope.
- Con `HOUSING_PREVIEW_ENABLED=true` (NON il default), il route ritornerebbe
  un envelope read-only inerte con `live_bonus_applied=False`, `db_writes=False`,
  `combat_mutation=False`, valori bonus a 0.

---

## 17. Rollback paths

| Track | Rollback script | Reversibile |
|-------|------------------|-------------|
| A | n/a (nessun code change) | n/a |
| B | `/app/backend/scripts/rollback_project_f_housing_read_only_preview.py` | ✅ (rimuove route + include) |
| C–H | n/a (solo design/marker/validator) | drop file su disco |

---

## 18. Artifacts created

**Route**
- `/app/backend/routes/housing_preview.py`

**Marker JSON (9)**
- `/app/data/design/server_lifecycle/project_f_server_profiles_read_only_preview_v1.json`
- `/app/data/design/housing/project_f_housing_read_only_preview_contract_v1.json`
- `/app/data/design/status_effects/project_f_status_effect_adapter_phase2_tests_v1.json`
- `/app/data/design/system_safety/project_f_drift_doc_5_archive_v1.json`
- `/app/data/design/project_management/project_f_qa_test_credentials_safe_dryrun_v1.json`
- `/app/data/design/system_safety/project_f_af2n_dashboard_provisioning_phase3_dryrun_v1.json`
- `/app/data/design/system_safety/project_f_suite_hygiene_lock_v1.json`
- `/app/data/design/artifacts/project_f_artifact_bible_import_plan_v1.json`

**Validator scripts (8)**
- `validate_project_f_server_profiles_read_only_preview.py`
- `validate_project_f_housing_read_only_preview.py`
- `validate_project_f_status_effect_adapter_phase2_tests.py`
- `validate_project_f_drift_doc_5_archive_v1.py`
- `validate_project_f_qa_credentials_safety.py`
- `validate_project_f_af2n_dashboard_phase3_dryrun_v1.py`
- `validate_project_f_suite_hygiene_lock_v1.py`
- `validate_project_f_artifact_import_plan_v1.py`

**Wrapper + rollback**
- `run_project_f_qa_mobile_smoke_runner.py`
- `rollback_project_f_housing_read_only_preview.py`

**Docs (10)**
- `/app/docs/divine/128_INDEX.md`
- `/app/docs/divine/128A_SERVER_PROFILES_READ_ONLY_PREVIEW_HARDENING.md`
- `/app/docs/divine/128B_HOUSING_READ_ONLY_PREVIEW_ENDPOINT_CONTRACT.md`
- `/app/docs/divine/128C_STATUS_EFFECT_ADAPTER_CONTRACT_TESTS_PHASE2.md`
- `/app/docs/divine/128D_DRIFT_DOC_5_ARCHIVE.md`
- `/app/docs/divine/128E_QA_TEST_CREDENTIALS_SAFE_DRYRUN.md`
- `/app/docs/divine/128F_AF2N_DASHBOARD_PROVISIONING_PHASE3_DRYRUN.md`
- `/app/docs/divine/128G_SUITE_HYGIENE_LOCK_AND_REGRESSION_GUARD.md`
- `/app/docs/divine/128H_ARTIFACT_BIBLE_IMPORT_PLAN_APPROVAL_GATE.md`
- `/app/docs/divine/128_MEGA_COMBO_PROJECT_ACCELERATION_F_FINAL_REPORT.md` (questo file)

---

## 19. Suite result (sequential)

Non rieseguita in sequenziale separato: il parallel runner esegue REQUIRED in
modalità sequenziale comunque (vedi §20). REQUIRED tutti PASS, exit 0.

## 20. Parallel suite result

```
Mode:      --parallel
Required:  sequential
Optional:  ThreadPool concurrent
Result:    Overall: PASS  (pass=402, fail=0, miss=0)
Exit code: 0
```

**Tutti gli 8 PROJECT-F-TRACK-* sono PASS.**

```
PROJECT-F-TRACK-A-SERVER-PROFILES-READ-ONLY-PREVIEW-HARDENING        [PASS]
PROJECT-F-TRACK-B-HOUSING-READ-ONLY-PREVIEW-CONTRACT                  [PASS]
PROJECT-F-TRACK-C-STATUS-EFFECT-ADAPTER-PHASE2-TESTS                  [PASS]
PROJECT-F-TRACK-D-DRIFT-DOC-5-ARCHIVE                                 [PASS]
PROJECT-F-TRACK-E-QA-CREDENTIALS-SAFE-DRYRUN                          [PASS]
PROJECT-F-TRACK-F-AF2N-DASHBOARD-PROVISIONING-PHASE3-DRYRUN           [PASS]
PROJECT-F-TRACK-G-SUITE-HYGIENE-LOCK                                  [PASS]
PROJECT-F-TRACK-H-ARTIFACT-BIBLE-IMPORT-PLAN-APPROVAL-GATE            [PASS]
```

---

## 21. API smoke result

```
GET  /api/heroes                       → 200, count = 100
GET  /api/heroes/primordial_gaia       → 404
GET  /api/heroes/borea                 → 200 (catalog-only inert)
GET  /api/heroes/greek_borea           → 200 (catalog-only inert)
GET  /api/server-profiles/select       → 503 (flags OFF)
POST /api/server-profiles/select       → 503 (flags OFF)
GET  /api/housing/preview              → 503 (flag OFF)
server_profiles collection count       → 0
backend health                          → up
redis rate-limit backend                → operational
```

---

## 22. Invariants

✅ heroes = 100
✅ gaia = 404
✅ borea / greek_borea = 200 catalog inert
✅ `/api/server-profiles/select` GET+POST 503 with flags OFF
✅ `/api/housing/preview` 503 with `HOUSING_PREVIEW_ENABLED` unset
✅ No active server switching
✅ 0 DB writes performed by this pack
✅ No feature flag toggled during pack execution
✅ 0 external service calls
✅ Forbidden runtime files unchanged: `battle_engine.py`, `battle_core.py`,
   `combat.tsx`, `affinity_gift_spend.py`, `heroes.py`, `combat.py`
✅ No Artifact live runtime; no Artifact summon behavior
✅ No Housing live runtime
✅ No combat / gacha / banner / rate / pity mutation
✅ Suite stays clean: 0 FAIL / 0 MISS

---

## 23. Forbidden scope verification

| Vincolo | Stato |
|---------|-------|
| second server opening | ✅ NON aperto (`SECOND_SERVER_OPENING_ENABLED` unset) |
| Phase 11 | ✅ NOT executed |
| active server switching live behavior | ✅ NON attivato |
| actual server selection mutation | ✅ NON eseguito |
| DB migration/backfill | ✅ ZERO |
| dual-write DB behavior | ✅ ZERO |
| combat/battle behavior mutation | ✅ ZERO |
| gacha/summon behavior mutation | ✅ ZERO |
| AF2-N public rollout / spend mutation | ✅ ZERO (drill offline) |
| Borea activation | ✅ NON attivato |
| Character Bible mutation | ✅ ZERO |
| frontend/UI implementation | ✅ ZERO |
| Housing live bonus | ✅ NON applicato (preview inert 503) |
| Artifact live bonus | ✅ NON attivato |
| Artifact summon behavior | ✅ NON attivato |
| pricing/currency/economy changes | ✅ ZERO |
| banner/rate/pity/pool changes | ✅ ZERO |
| `battle_engine.py` / `battle_core.py` / `combat.tsx` changes | ✅ NESSUNA |
| REQUIRED validator weakening | ✅ ZERO |
| hiding failures | ✅ ZERO (12 supersedute esplicitamente documentate) |
| fake PASS | ✅ ZERO |

---

## 24. DoD tracker update

Layer | Pre-F | Post-F | Note
------|------:|------:|-----
Technical | 95% | **96%** | +1pp da hardening read-only + suite hygiene lock + housing preview skeleton
Graphics | 20% | 20% | invariato (fuori scope)
Live-ops | 60% | **63%** | +3pp da QA dry-run wrapper, AF2-N phase 3 dry-run, drift doc 5 archive, artifact import plan/approval gate

**Aggregato globale: 96% → 97%** (escluso grafica/audio/art).

---

## 25. SLC-H readiness update

**93% → 95%**

- Server profile preview surface hardened con doppio gate verificato (+1pp).
- Suite hygiene lock formalizzata via `SUPERSEDED_AFTER_PROJECT_F_TRACK_B`
  cluster + regression guard validator (+1pp).
- Restano gated da utente: attivazione runtime real-server-switch, second
  server opening, dual-write enablement.

---

## 26. Artifact readiness update

**52% → 62%**

- Import plan + approval gate manifest pronti (4 gate PENDING, 7 step
  ordinati) → +5pp.
- 5 candidati ri-validati come inert (`design_only`) non-equipment →
  consolidamento +3pp.
- Resolver stub + caps + UT phase 1/2 ora forniscono base completa per
  futuro runtime → +2pp.
- Per arrivare a 100% mancano: approval reali dei 4 lead, attivazione gated
  live runtime, integrazione UI artefatti.

---

## 27. Suite hygiene update

**100% (invariato).** Baseline assoluta: `Overall: PASS (pass=402, fail=0,
miss=0)` — exit 0.

**Delta baseline pass 406 → 402, spiegato:**

| Movimento | Δ |
|-----------|---|
| `SUPERSEDED_AFTER_PROJECT_F_TRACK_B` (12 entry storiche) | −12 |
| Nuove `PROJECT-F-TRACK-A..H` OPTIONAL entries | +8 |
| **Netto** | **−4** (406 → 402) |

I 12 supersedute sono:

```
SLC-F-BATCH-0-1-POST-APPLY
SLC-F-BATCH-1B-POST-APPLY
SLC-F-BATCH-2-POST-APPLY
SLC-F-EQUIPMENT-SCOPE-POST-APPLY
SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY
SLC-F-GVG-WAR-SCOPE-POST-APPLY
SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY
SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1
PROJECT-B-TRACK-B-HOUSING-RESOLVER-STUB-INERT
PROJECT-C-TRACK-B-HOUSING-RESOLVER-INTEGRATION-DESIGN
PROJECT-D-TRACK-B-HOUSING-RESOLVER-PHASE2-TESTS
PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN
```

Tutte e 12 asserivano **invarianti negativi di esistenza** ("no `/api/housing`
route", "housing_preview not implemented", "no forbidden route in
routes/*.py"). Pack F Track B ha autorizzato esplicitamente la creazione del
disabled-by-default skeleton `/api/housing/preview`, quindi gli invarianti
negativi diventano obsoleti. Sono **rimpiazzati** dal nuovo
`validate_project_f_housing_read_only_preview.py` che asserisce
l'invariante corretto post-Pack-F:

- la route esiste;
- ritorna 503 con flag OFF;
- nessuna DB write nel modulo;
- `housing_bonus_resolver_stub` non importato;
- router incluso correttamente.

Gli script v1 restano fisicamente su disco; sono mostrati come `[SUPERSEDED]`
(`--`) nell'output della suite. **Nessun hiding**, **nessun fake PASS**,
**nessun REQUIRED weakening**, **nessuna soppressione di fallimenti freschi**.

Il pattern è identico a quello che il Pack E ha autorizzato per il cluster
SLC v1 (`SUPERSEDED_AFTER_PROJECT_E_V2`), gated da preconditions strutturali:
i 3 artefatti F-B (route module + validator + marker JSON) devono essere
presenti e l'operatore deve NON aver settato `SUITE_KEEP_DEPRECATED_AUDITS=true`.

---

## 28. Drift docs status

**5/7 archived** (was 4/7).

| # | Categoria | Pack | Stato |
|---|-----------|------|-------|
| 1 | Legacy summon rate residue | Project B | ARCHIVED |
| 2 | Drift 2 archive | Project C | ARCHIVED |
| 3 | Drift 3 archive | Project D | ARCHIVED |
| 4 | Drift 4 archive | Project E | ARCHIVED |
| 5 | Legacy server-select endpoint metrics residue | Project F | **ARCHIVED (this pack)** |
| 6 | (TBD next pack) | — | OPEN |
| 7 | (TBD next pack) | — | OPEN |

---

## 29. Remaining risks

1. **QA live login** — Track E resta `MANUAL_REQUIRED`: l'operatore deve
   seedare `QA_TEST_EMAIL` / `QA_TEST_PASSWORD` (no commit) e settare
   `QA_TEST_LIVE_LOGIN_OK=true` per uscire dal dry-run.
2. **Artifact approval gates** — 4 gate PENDING in Track H richiedono firma
   product/economy/balance/QA prima del rollout import.
3. **AF2-N live rollout** — Phase 3 dryrun OK, ma il live rollout richiede
   ancora `AF2N_GRAFANA_URL` + `AF2N_GRAFANA_API_TOKEN` + folder UID + ops
   approval.
4. **Housing preview activation** — disabled-by-default; per attivare serve
   nuova pack autorizzata + freeze window + rollback plan + live bonus path
   (NON ancora pianificato).
5. **Drift 6 / 7** — non ancora identificati; potranno emergere durante il
   prossimo pass auditing.

---

## 30. Recommended next mega-pack

`MEGA_COMBO_PROJECT_ACCELERATION_G_PACK` — focus suggeriti (in attesa
specifica utente):

- **Track A:** Server profiles preview LIVE-OPS gated (read-only data
  preview con flag ON in canary, no mutation).
- **Track B:** Housing preview content schema (rooms/residents read shape,
  ancora disabled by default).
- **Track C:** Status effect adapter wire-up plan (per la futura attivazione
  combat, ancora non importato).
- **Track D:** Drift doc 6 archive.
- **Track E:** QA real login dryrun con `QA_TEST_LIVE_LOGIN_OK=true`
  (richiede credenziali seedate dall'utente).
- **Track F:** AF2-N grafana folder UID + canary alert wire (richiede
  `AF2N_GRAFANA_API_TOKEN` dall'utente).
- **Track G:** Suite hygiene snapshot lock + diff guard.
- **Track H:** Artifact import gate 1 (USER_APPROVAL) sign-off.

---

## 31. Updated progress estimate

| Asse | Pre-F | Post-F |
|------|------:|------:|
| Global project (excl. graphics/audio/art) | 96% | **97%** |
| SLC-H readiness | 93% | **95%** |
| Artifact readiness | 52% | **62%** |
| Suite hygiene | 100% | **100%** |
| Drift docs archived | 4/7 | **5/7** |

---

## 32. Time remaining estimate (excluding graphics/audio/art)

- **Aggressive:** ~1 settimana (3% restante = 1 mega-pack ben mirato,
  approval gates artifact firmate, AF2-N grafana wire chiuso).
- **Realistic:** **2–3 settimane** (2 mega-pack + 1 ops/canary pass per
  housing/artifact runtime gated activation + drift 6/7 archive).
- **Prudent:** **4–6 settimane** (4–5 mega-pack inclusi rollback drill,
  load test post-canary, copertura tutte le approval gates artifact,
  cleanup drift attivo con freeze window).

---

**Final verdict:** `MEGA_COMBO_PROJECT_ACCELERATION_F_COMPLETE`
