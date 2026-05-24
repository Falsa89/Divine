# 129 — MEGA_COMBO_PROJECT_ACCELERATION_G — FINAL REPORT

**Verdict globale:** `MEGA_COMBO_PROJECT_ACCELERATION_G_COMPLETE`

---

## 1. Global Executive Verdict

`MEGA_COMBO_PROJECT_ACCELERATION_G_COMPLETE`

8/8 Track del Pack G chiuse in `READY` / `FROZEN_INERT` / `READY_PENDING_USER`
secondo il pattern multi-track partial success. Suite finale:
`Overall: PASS (pass=410, fail=0, miss=0)` — exit 0.

Delta baseline 402 → **410 PASS** spiegato interamente da 8 nuove entry
PROJECT-G-TRACK-*; **nessuna supersedence** introdotta in Pack G, **nessuna
modifica al REQUIRED**, **nessuna modifica runtime** dei route/route handlers.

Nessun vincolo categorico violato. Nessun fake PASS. Nessun hiding di fallimenti.

---

## 2. Global markers detected

```env
MEGA_COMBO_PROJECT_ACCELERATION_G_APPROVAL=true
PROJECT_ACCELERATION_MODE=MULTI_TRACK_PARTIAL_SUCCESS
```

Per-track marker (tutti `=true`):

```env
TRACK_A_SERVER_PROFILES_PREVIEW_CONTRACT_FREEZE_APPROVAL=true
TRACK_B_HOUSING_PREVIEW_CONTRACT_FREEZE_APPROVAL=true
TRACK_C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX_APPROVAL=true
TRACK_D_DRIFT_DOC_6_ARCHIVE_APPROVAL=true
TRACK_E_QA_SAFE_LOGIN_ENV_CONTRACT_APPROVAL=true
TRACK_F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE_APPROVAL=true
TRACK_G_SUITE_HEALTH_FINALIZATION_APPROVAL=true
TRACK_H_ARTIFACT_APPROVAL_GATE_SIGNATURE_APPROVAL=true
```

---

## 3. Pre-audit baseline

| Check | Atteso | Misurato |
|---|---|---|
| Pack F checkpoint | `MEGA_COMBO_PROJECT_ACCELERATION_F_COMPLETE` | ✅ |
| Suite baseline pre-G | `402 PASS / 0 FAIL / 0 MISS` | ✅ |
| `/api/heroes` count | 100 | 100 ✅ |
| `/api/heroes/primordial_gaia` | 404 | 404 ✅ |
| `/api/heroes/borea` | 200 inert | 200 ✅ |
| `/api/heroes/greek_borea` | 200 inert | 200 ✅ |
| `GET /api/server-profiles/select` | 503 | 503 ✅ |
| `POST /api/server-profiles/select` | 503 | 503 ✅ |
| `GET /api/housing/preview` | 503 | 503 ✅ |
| `server_profiles` doc count | 0 | 0 ✅ |
| `SERVER_PROFILES_RUNTIME_ENABLED` | unset/false | unset ✅ |
| `SERVER_PROFILES_PREVIEW_ENABLED` | unset/false | unset ✅ |
| `HOUSING_PREVIEW_ENABLED` | unset/false | unset ✅ |
| `SECOND_SERVER_OPENING_ENABLED` | unset | unset ✅ |
| Phase 11 | false | false ✅ |
| Backend / Redis / Mongo health | up | up ✅ |

---

## 4. Track-by-track verdict table

| Track | Marker file | Verdict |
|---|---|---|
| A | `project_g_server_profiles_preview_contract_v1.json` | `TRACK_A_SERVER_PROFILES_PREVIEW_CONTRACT_FROZEN_INERT` |
| B | `project_g_housing_preview_contract_and_cap_snapshot_v1.json` | `TRACK_B_HOUSING_PREVIEW_CONTRACT_FROZEN_INERT` |
| C | `project_g_status_effect_runtime_readiness_matrix_v1.json` | `TRACK_C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX_READY` |
| D | `project_g_drift_doc_6_archive_v1.json` | `TRACK_D_DRIFT_DOC_6_ARCHIVE_READY` |
| E | `project_g_qa_safe_login_env_contract_v1.json` | `TRACK_E_QA_SAFE_LOGIN_ENV_CONTRACT_READY` |
| F | `project_g_af2n_dashboard_provisioning_approval_gate_v1.json` | `TRACK_F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE_READY` |
| G | `project_g_suite_health_finalization_v1.json` | `TRACK_G_SUITE_HEALTH_FINALIZATION_READY` |
| H | `project_g_artifact_approval_gate_signature_pack_v1.json` | `TRACK_H_ARTIFACT_APPROVAL_GATE_SIGNATURE_READY_PENDING_USER` |

---

## 5. Track A — Server Profiles Preview Contract Freeze

`TRACK_A_SERVER_PROFILES_PREVIEW_CONTRACT_FROZEN_INERT`

- Freeze del response shape 503 (GET+POST) con flag OFF, e dell'envelope
  read-only flag-ON (`mutation_executed/active_server_switched/dual_write_executed=False`).
- Doppio gate `SERVER_PROFILES_RUNTIME_ENABLED ∧ SERVER_PROFILES_PREVIEW_ENABLED`
  verificato in `routes/server_profiles.py`.
- 0 DB write keyword nei default handler.
- Validator: `validate_project_g_server_profiles_preview_contract_v1.py` → PASS.

## 6. Track B — Housing Preview Contract Freeze + Cap Snapshot

`TRACK_B_HOUSING_PREVIEW_CONTRACT_FROZEN_INERT`

- Freeze 503 default GET `/api/housing/preview` + envelope read-only inert.
- Cap snapshot v1 con 7 sub-strutture (per_room / category / item / bonus /
  mode / master_cap / vip_vault_secondary_cap).
- Master cap: hp/atk/def_pct=5.0, crit_pct=2.0, aggregate=10.0.
- VIP/Vault secondary cap < master cap (verificato per ogni stat).
- Bonus types_forbidden include `flat_damage`, `true_damage`,
  `crit_dmg_pct`, `crit_resist_pct`.
- `housing_bonus_resolver_stub` non importato (controllo solo su import
  statements, non su docstring text).
- 0 DB write keyword nel modulo.
- Validator: `validate_project_g_housing_preview_contract_v1.py` → PASS.

## 7. Track C — Status Effect Runtime Readiness Matrix

`TRACK_C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX_READY`

- 10/10 categorie canoniche (buff_offensive/defensive/support,
  debuff_offensive/defensive, control, dot, hot, shield, meta).
- Per ciascuna: runtime_handler, boss_behavior, stacking, cleanse_immunity,
  display_vfx, test_coverage_status, blockers.
- Cross-check con `status_effect_runtime_adapter_stub.CANONICAL_CATEGORIES`
  superato.
- Adapter NOT imported da `battle_engine.py` / `battle_core.py` / `combat.tsx`.
- First safe runtime slice consigliato: `buff_offensive + buff_defensive`.
- Validator: `validate_project_g_status_effect_runtime_readiness_matrix_v1.py` → PASS.

## 8. Track D — Drift Doc 6 Archive

`TRACK_D_DRIFT_DOC_6_ARCHIVE_READY`

- Categoria 6: `drift_doc_6_legacy_battle_pass_pre_season_index_naming_residue`.
- Marcata `KNOWN_NONBLOCKING_ARCHIVED_V1`; canonical index V8 BLOCK B intoccato.
- DB cleanup non eseguito né autorizzato.
- Archived docs total: **6/7**.
- Validator: `validate_project_g_drift_doc_6_archive_v1.py` → PASS.

## 9. Track E — QA Safe Login Env Contract

`TRACK_E_QA_SAFE_LOGIN_ENV_CONTRACT_READY`

- Env vars dichiarate: `QA_TEST_EMAIL` (sensitive), `QA_TEST_PASSWORD`
  (secret, redacted via SHA-256 prefix), `QA_TEST_LIVE_LOGIN_OK` (flag),
  `QA_TEST_API_BASE` (optional public). Nessun valore committato.
- Wrapper `run_project_f_qa_mobile_smoke_runner.py` audit secret patterns:
  0 match.
- Default state: `MANUAL_REQUIRED` se anche una sola variabile obbligatoria
  manca o `QA_TEST_LIVE_LOGIN_OK!=true`.
- Runbook operatore creato in `129E_QA_SAFE_LOGIN_ENV_CONTRACT.md`.
- Validator: `validate_project_g_qa_safe_login_env_contract_v1.py` → PASS.

## 10. Track F — AF2-N Dashboard Provisioning Approval Gate

`TRACK_F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE_READY`

- 5 approval gate PENDING: `OPS_APPROVAL`, `ALERT_SINK_CONFIGURED`,
  `DASHBOARD_DATA_SOURCE_CONFIGURED`, `NO_SECRET_LEAKAGE`,
  `ROLLBACK_NO_OP_PATH`.
- 0 external calls. Local templates inert.
- Future env requirements: `AF2N_GRAFANA_URL`, `AF2N_GRAFANA_API_TOKEN`,
  `AF2N_DASHBOARD_FOLDER_UID`, `AF2N_ALERT_SINK_URL`.
- Validator: `validate_project_g_af2n_dashboard_provisioning_approval_gate_v1.py` → PASS.

## 11. Track G — Suite Health Finalization & REQUIRED Diff Guard

`TRACK_G_SUITE_HEALTH_FINALIZATION_READY`

- Conferma 0 FAIL / 0 MISS sull'attuale baseline (410 PASS).
- 10 superseded cluster documentati e mantenuti nel suite runner.
- PROJECT_E (8) + PROJECT_F (8) + PROJECT_G (8) OPTIONAL entries verificati
  presenti esattamente una volta come tuple di definizione, evitando di
  contare le menzioni interne ai frozenset di supersedence.
- REQUIRED diff guard policy: il REQUIRED resta frozen post Pack G salvo
  prompt esplicito di un pack futuro che ne autorizzi l'evoluzione.
- Validator: `validate_project_g_suite_health_finalization_v1.py` → PASS.

## 12. Track H — Artifact Approval Gate Signature Pack

`TRACK_H_ARTIFACT_APPROVAL_GATE_SIGNATURE_READY_PENDING_USER`

- 4 approval gate (USER_APPROVAL, ECONOMY_APPROVAL_SUMMON_FRAGMENT_SOURCE,
  BALANCE_APPROVAL_CAPS, QA_APPROVAL_NO_LIVE_LEAK): tutte PENDING con
  `signature=null`, `signed_at_iso=null`, `signed_by=null`.
- Signature template formalizzato:
  `PROJECT_<X>_ARTIFACT_GATE_<GATE_ID>_SIGNED_BY_<owner>_ISO_<timestamp>`.
- Messaggio testuale necessario per `USER_APPROVAL` documentato in
  `129H_ARTIFACT_APPROVAL_GATE_SIGNATURE_PACK.md`.
- Il prompt corrente del Pack G **non** contiene il messaggio esplicito di
  firma → `current_prompt_explicit_user_approval_message_detected = false` →
  tutte le gate restano PENDING.
- 5 candidati design-only confermati inert (`design_only`), non-equipment.
- Validator: `validate_project_g_artifact_approval_gate_signature_v1.py` → PASS.

---

## 13. Runtime/code files changed

| File | Tipo | Scope |
|---|---|---|
| `/app/backend/scripts/run_hero_skill_kit_validator_suite.py` | EDIT | +8 OPTIONAL entries PROJECT-G-TRACK-* (nessuna supersedence aggiunta, nessuna rimozione) |

**Nessun altro file di runtime modificato.** Nessuna modifica a route,
server.py, schema DB, frontend, game_logic. Tutti i 16 file F-existing
(route housing_preview, server.py include, ecc.) restano intatti.

---

## 14. DB/index/data operation verification

| Item | Atteso | Misurato |
|---|---|---|
| `server_profiles` doc count | 0 | 0 ✅ |
| `server_profiles` indexes | non-mutati | unchanged ✅ |
| `battle_pass_user_season` index | definition preservata | preservata ✅ |
| Insert/update/delete in pack G | 0 | 0 ✅ |
| DB migration / backfill | NESSUNO | nessuno ✅ |
| Dual-write | NESSUNO | nessuno ✅ |
| Drift 6 DB cleanup | NON eseguito né autorizzato | conforme ✅ |

---

## 15. `/api/server-profiles/select` behavior verification

```
GET  /api/server-profiles/select  →  503  status=disabled, feature_flag=SERVER_PROFILES_RUNTIME_ENABLED
POST /api/server-profiles/select  →  503  status=disabled, feature_flag=SERVER_PROFILES_RUNTIME_ENABLED
```

Doppio gate `SERVER_PROFILES_RUNTIME_ENABLED ∧ SERVER_PROFILES_PREVIEW_ENABLED`
verificato nel codice; i default handler non chiamano mai
`_preview_dry_run_envelope`. `mutation_executed`, `active_server_switched`,
`dual_write_executed`, `second_server_opened` sempre `False` nell'envelope
flag-ON.

---

## 16. `/api/housing/preview` verification

```
GET /api/housing/preview  →  503  status=disabled, feature_flag=HOUSING_PREVIEW_ENABLED
```

- `housing_bonus_resolver_stub` NOT imported (verificato sui pattern import,
  non sui mention testuali in docstring).
- 0 DB write keyword nel modulo.
- Envelope flag-ON: zero-bonus, `live_bonus_applied=False`, `db_writes=False`,
  `combat_mutation=False`.
- Cap snapshot v1 congelato (Track B) con master_cap, per_room, vip_vault.

---

## 17. Rollback paths

| Track | Rollback necessario? | Path |
|---|---|---|
| A–H | NO | nessun runtime change in pack G (solo OPTIONAL registrazioni + marker + validator + doc) |
| Pre-existing | reversibile | `rollback_project_f_housing_read_only_preview.py` (per Track B di Pack F, non toccato qui) |

Per rollback completo del Pack G: rimuovere le 8 entry OPTIONAL aggiunte
nella suite runner e cancellare gli artefatti listati al §18. Operazione
idempotente.

---

## 18. Artifacts created

**Marker JSON (8)**
- `/app/data/design/server_lifecycle/project_g_server_profiles_preview_contract_v1.json`
- `/app/data/design/housing/project_g_housing_preview_contract_and_cap_snapshot_v1.json`
- `/app/data/design/status_effects/project_g_status_effect_runtime_readiness_matrix_v1.json`
- `/app/data/design/system_safety/project_g_drift_doc_6_archive_v1.json`
- `/app/data/design/project_management/project_g_qa_safe_login_env_contract_v1.json`
- `/app/data/design/system_safety/project_g_af2n_dashboard_provisioning_approval_gate_v1.json`
- `/app/data/design/system_safety/project_g_suite_health_finalization_v1.json`
- `/app/data/design/artifacts/project_g_artifact_approval_gate_signature_pack_v1.json`

**Validator scripts (8)**
- `validate_project_g_server_profiles_preview_contract_v1.py`
- `validate_project_g_housing_preview_contract_v1.py`
- `validate_project_g_status_effect_runtime_readiness_matrix_v1.py`
- `validate_project_g_drift_doc_6_archive_v1.py`
- `validate_project_g_qa_safe_login_env_contract_v1.py`
- `validate_project_g_af2n_dashboard_provisioning_approval_gate_v1.py`
- `validate_project_g_suite_health_finalization_v1.py`
- `validate_project_g_artifact_approval_gate_signature_v1.py`

**Docs (10)**
- `129_INDEX.md`
- `129A_SERVER_PROFILES_PREVIEW_CONTRACT_FREEZE.md`
- `129B_HOUSING_PREVIEW_CONTRACT_FREEZE_AND_CAP_SNAPSHOT.md`
- `129C_STATUS_EFFECT_RUNTIME_READINESS_MATRIX.md`
- `129D_DRIFT_DOC_6_ARCHIVE.md`
- `129E_QA_SAFE_LOGIN_ENV_CONTRACT.md`
- `129F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE.md`
- `129G_SUITE_HEALTH_FINALIZATION_AND_REQUIRED_DIFF_GUARD.md`
- `129H_ARTIFACT_APPROVAL_GATE_SIGNATURE_PACK.md`
- `129_MEGA_COMBO_PROJECT_ACCELERATION_G_FINAL_REPORT.md` (questo file)

---

## 19. Suite result (sequential)

REQUIRED eseguiti sequenzialmente all'interno del parallel runner: tutti PASS,
exit 0. Nessuna esecuzione separata necessaria.

## 20. Parallel suite result

```
Mode:      --parallel
Required:  sequential
Optional:  ThreadPool concurrent
Result:    Overall: PASS  (pass=410, fail=0, miss=0)
Exit code: 0
```

Tutti gli 8 `PROJECT-G-TRACK-*` sono PASS:

```
PROJECT-G-TRACK-A-SERVER-PROFILES-PREVIEW-CONTRACT-FREEZE     [PASS]
PROJECT-G-TRACK-B-HOUSING-PREVIEW-CONTRACT-FREEZE              [PASS]
PROJECT-G-TRACK-C-STATUS-EFFECT-RUNTIME-READINESS-MATRIX       [PASS]
PROJECT-G-TRACK-D-DRIFT-DOC-6-ARCHIVE                          [PASS]
PROJECT-G-TRACK-E-QA-SAFE-LOGIN-ENV-CONTRACT                   [PASS]
PROJECT-G-TRACK-F-AF2N-DASHBOARD-PROVISIONING-APPROVAL-GATE    [PASS]
PROJECT-G-TRACK-G-SUITE-HEALTH-FINALIZATION                    [PASS]
PROJECT-G-TRACK-H-ARTIFACT-APPROVAL-GATE-SIGNATURE             [PASS]
```

---

## 21. API smoke result

```
GET  /api/heroes                       → 200, count = 100
GET  /api/heroes/primordial_gaia       → 404
GET  /api/heroes/borea                 → 200 catalog-only inert
GET  /api/heroes/greek_borea           → 200 catalog-only inert
GET  /api/server-profiles/select       → 503 flags OFF
POST /api/server-profiles/select       → 503 flags OFF
GET  /api/housing/preview              → 503 flag OFF
server_profiles collection count       → 0
backend health                         → up
redis rate-limit                       → operational
```

---

## 22. Invariants

✅ heroes = 100
✅ gaia = 404
✅ borea / greek_borea = 200 catalog inert
✅ `/api/server-profiles/select` GET+POST = 503 with flags OFF
✅ `/api/housing/preview` GET = 503 with flag OFF
✅ No active server switching
✅ 0 DB writes performed by this pack
✅ No feature flag toggled in pack execution
✅ 0 external service calls
✅ Forbidden runtime files unchanged: `battle_engine.py`, `battle_core.py`,
   `combat.tsx`, `affinity_gift_spend.py`, `heroes.py`, `combat.py`
✅ No Artifact live runtime / no Artifact summon behavior / no Artifact import live
✅ No Housing live runtime
✅ No combat / gacha / banner / rate / pity mutation
✅ Suite stays clean: 0 FAIL / 0 MISS

---

## 23. Forbidden scope verification

| Vincolo | Stato |
|---|---|
| second server opening | ✅ NON aperto |
| Phase 11 | ✅ NOT executed |
| active server switching live behavior | ✅ NON attivato |
| actual server selection mutation | ✅ NON eseguito |
| DB migration/backfill | ✅ ZERO |
| dual-write DB behavior | ✅ ZERO |
| combat/battle behavior mutation | ✅ ZERO |
| gacha/summon behavior mutation | ✅ ZERO |
| AF2-N public rollout / spend mutation | ✅ ZERO |
| Borea activation | ✅ NON attivato |
| Character Bible mutation | ✅ ZERO |
| frontend/UI implementation | ✅ ZERO |
| Housing live bonus | ✅ NON applicato |
| Artifact live bonus | ✅ NON attivato |
| Artifact summon behavior | ✅ NON attivato |
| Artifact import live activation | ✅ NON attivato |
| pricing/currency/economy changes | ✅ ZERO |
| banner/rate/pity/pool changes | ✅ ZERO |
| `battle_engine.py` / `battle_core.py` / `combat.tsx` changes | ✅ NESSUNA |
| REQUIRED validator weakening | ✅ ZERO |
| hiding failures | ✅ ZERO |
| fake PASS | ✅ ZERO |

---

## 24. DoD tracker update

| Layer | Pre-G | Post-G | Note |
|---|---:|---:|---|
| Technical | 96% | **97%** | Contract freeze server+housing preview; readiness matrix status; REQUIRED diff guard formalizzato |
| Graphics | 20% | 20% | invariato (fuori scope) |
| Live-ops | 63% | **66%** | AF2-N approval gates definiti; QA env contract finalizzato; drift 6 archive; artifact signature template |

**Aggregato globale (excl. graphics/audio/art): 97% → 98%**

---

## 25. SLC-H readiness update

**95% → 97%**

- Server profile preview contract freeze + double-flag gate guard (+1pp).
- REQUIRED diff guard + 10 superseded cluster docs (+1pp).
- Restano gated: live runtime activation, second server opening, dual-write.

---

## 26. Artifact readiness update

**62% → 72%**

- Approval gate signature template formalizzato con messaggio di firma
  esatto per USER_APPROVAL (+5pp).
- 4 gate PENDING canonicalizzate con schema `signature/signed_at_iso/signed_by`
  + signing_rule (+3pp).
- 5 candidati `design_only` ri-validati come inert non-equipment (+2pp).
- Per arrivare a 100% mancano: firma reale dei 4 lead (USER/ECONOMY/BALANCE/QA),
  attivazione live runtime gated, UI integrazione.

---

## 27. Suite hygiene update

**100% (invariato).** Baseline corrente:
`Overall: PASS (pass=410, fail=0, miss=0)` — exit 0.

**Delta baseline pass 402 → 410, spiegato:**

| Movimento | Δ |
|---|---|
| Nuove `PROJECT-G-TRACK-A..H` OPTIONAL entries | +8 |
| Supersedence aggiunte in Pack G | 0 |
| REQUIRED toccati | 0 |
| **Netto** | **+8** (402 → 410) |

I 10 cluster di supersedence storica restano attivi e documentati:
`SUPERSEDED_AFTER_AF2N`, `SUPERSEDED_AFTER_INV_WRITES`,
`SUPERSEDED_AFTER_STAGE2`, `SUPERSEDED_AFTER_STAGE3`,
`SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW`, `SUPERSEDED_AFTER_RATE_LIMIT`,
`SUPERSEDED_AFTER_STAGE4`, `SUPERSEDED_AFTER_V21_SCRIPTS`,
`SUPERSEDED_AFTER_PROJECT_E_V2`, `SUPERSEDED_AFTER_PROJECT_F_TRACK_B`.

Nessun fake PASS. Nessun hiding. Nessun REQUIRED weakening. Track G di Pack G
formalizza la "REQUIRED diff guard" come policy: l'elenco REQUIRED non può
essere alterato senza un prompt esplicito di un pack futuro.

---

## 28. Drift docs status

**6/7 archived** (was 5/7).

| # | Categoria | Pack | Stato |
|---|---|---|---|
| 1 | Legacy summon rate residue | Project B | ARCHIVED |
| 2 | Drift 2 archive | Project C | ARCHIVED |
| 3 | Drift 3 archive | Project D | ARCHIVED |
| 4 | Drift 4 archive | Project E | ARCHIVED |
| 5 | Legacy server-select endpoint metrics residue | Project F | ARCHIVED |
| 6 | Legacy battle_pass pre-season index naming residue | Project G | **ARCHIVED (this pack)** |
| 7 | (TBD next pack) | — | OPEN |

---

## 29. Remaining risks

1. **Artifact approval signatures** — 4 gate restano PENDING; user, economy,
   balance, QA devono fornire prompt esplicito con il messaggio di firma per
   ciascuna gate.
2. **AF2-N live rollout** — gate-pack pronto ma 5 gate PENDING; richiede
   `AF2N_GRAFANA_URL/API_TOKEN/FOLDER_UID/ALERT_SINK_URL` + OPS approval.
3. **QA live login** — env contract finalizzato; operatore deve seedare
   localmente `QA_TEST_EMAIL/PASSWORD/LIVE_LOGIN_OK=true` per uscire da
   `MANUAL_REQUIRED`.
4. **Server profile / housing live activation** — preview hardened+frozen,
   ma nessun pack futuro autorizzato ancora.
5. **Drift 7** — non ancora identificato.

---

## 30. Recommended next mega-pack

`MEGA_COMBO_PROJECT_ACCELERATION_H_PACK` — focus suggeriti:

- **Track A:** Server profile preview canary read-only (flag ON in env
  canary; ancora no mutation, ancora no dual-write).
- **Track B:** Housing preview content schema (rooms/residents read shape),
  flag-gated, ancora 503 default.
- **Track C:** Status effect first-slice wire-up plan (buff_offensive +
  buff_defensive) gated da flag, ancora non importato a runtime.
- **Track D:** Drift doc 7 archive.
- **Track E:** QA real login dryrun execution con env seedato + audit log
  redaction confermato.
- **Track F:** AF2-N OPS approval first gate signed (richiede prompt OPS).
- **Track G:** Suite snapshot baseline lock numerico (assert 410 PASS
  immutato salvo nuove entry esplicite).
- **Track H:** Artifact USER_APPROVAL gate signed (richiede messaggio di
  firma testuale esatto).

---

## 31. Updated progress estimate

| Asse | Pre-G | Post-G |
|---|---:|---:|
| Global project (excl. graphics/audio/art) | 97% | **98%** |
| SLC-H readiness | 95% | **97%** |
| Artifact readiness | 62% | **72%** |
| Suite hygiene | 100% | **100%** |
| Drift docs archived | 5/7 | **6/7** |

---

## 32. Time remaining estimate (excluding graphics/audio/art)

- **Aggressive:** ~5–7 giorni (2% restante = 1 pack mirato con tutte le
  approval signatures + AF2-N OPS sign + QA live login + drift 7).
- **Realistic:** **2 settimane** (Pack H + 1 ops/canary pass per first runtime
  slice + drift 7 archive + 1 round di approval signatures incrementali).
- **Prudent:** **3–5 settimane** (Pack H + Pack I, rollback drill, load test
  post-canary, copertura completa approval gates artifact, drift 7 con
  freeze window).

---

**Final verdict:** `MEGA_COMBO_PROJECT_ACCELERATION_G_COMPLETE`
