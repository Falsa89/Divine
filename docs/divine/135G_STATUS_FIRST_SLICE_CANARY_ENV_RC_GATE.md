# 135G — STATUS FIRST SLICE CANARY ENV RC GATE

**Pack**: `PROJECT_M` — Track G
**Verdict**: `TRACK_G_STATUS_FIRST_SLICE_CANARY_ENV_RC_GATE_READY`
**Marker JSON**: `/app/data/design/project_management/project_m_status_first_slice_canary_env_rc_gate_v1.json`
**Validator**: `/app/backend/scripts/validate_project_m_status_first_slice_canary_env_rc_gate_v1.py`

## 13 automation check (PASS)

| ID | Check | Esito |
|----|-------|-------|
| S1 | `GET /api/heroes` → 200, count 100 | ✅ |
| S2 | `GET /api/heroes/primordial_gaia` → 404 | ✅ |
| S3–S4 | `GET /api/heroes/borea` & `greek_borea` → 200 | ✅ |
| S5 | `GET/POST /api/server-profiles/select` → 503 | ✅ |
| S6 | `GET /api/housing/preview` → 503 | ✅ |
| S7–S8 | `STATUS_RUNTIME_BUFF_SLICE_ENABLED` e `STATUS_FIRST_SLICE_BATTLE_ENGINE_CANARY_OK` unset | ✅ |
| S9 | Patch marker `_project_m_status_seam` presente in `battle_engine.py` | ✅ |
| S10 | `battle_core.py` / `server.py` / `routes/combat.py` md5 invariati | ✅ |
| S11 | 0 leak su endpoint live | ✅ |
| S12 | 19 REQUIRED suite validator passano | ✅ |
| S13 | Rollback dry-run OK | ✅ |

## Canary progression

| Stage | Stato |
|-------|-------|
| 1 in-process dry-run (Pack L) | READY |
| 2 in-process canary fixture (Pack M Track D) | READY |
| 3 canary env flag flip | **BLOCKED** until PROJECT_N |
| 4 dev live | BLOCKED until PROJECT_N+ |
| 5 prod | BLOCKED until separate prod approval |

## Conformità ai guardrail

- ✅ Nessun live rollout eseguito.
