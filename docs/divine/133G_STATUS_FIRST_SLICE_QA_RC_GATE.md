# 133G — STATUS FIRST SLICE QA RC GATE

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_K` — Track G
**Verdict**: `TRACK_G_STATUS_FIRST_SLICE_QA_RC_GATE_READY`
**Marker JSON**: `/app/data/design/status_effects/project_k_status_first_slice_qa_rc_gate_v1.json`
**Validator**: `/app/backend/scripts/validate_project_k_status_first_slice_qa_rc_gate_v1.py`

---

## Obiettivo

Definire e validare il **QA Release Candidate Gate** per lo status first slice, raccogliendo controlli automatici (smoke + invarianti) e manuali (QA mobile) in un singolo cancello di rilascio.

## Check eseguiti (13)

### Smoke (6)

| ID | Endpoint | Atteso | Osservato |
|----|----------|--------|-----------|
| S1 | `GET /api/heroes` | `200` & count `100` | ✅ |
| S2 | `GET /api/heroes/primordial_gaia` | `404` | ✅ |
| S3 | `GET /api/heroes/borea` | `200` | ✅ |
| S4 | `GET /api/heroes/greek_borea` | `200` | ✅ |
| S5 | `GET/POST /api/server-profiles/select` | `503` | ✅ |
| S6 | `GET /api/housing/preview` | `503` | ✅ |

### Forbidden env unset (S9)

Verificato che le seguenti env **non siano** valorizzate a `true`:

- `HOUSING_LIVE_BONUS_ENABLED`
- `ARTIFACT_LIVE_BONUS_ENABLED`
- `ARTIFACT_IMPORT_LIVE_ENABLED`
- `SECOND_SERVER_OPENING_ENABLED`
- `PHASE_11_ENABLED`
- `STATUS_RUNTIME_BUFF_SLICE_ENABLED`

### Resolver & payload (K1–K3)

- K1: `status_first_slice_resolver_pure.is_runtime_active() = False` ✅
- K2: resolver non importato da alcun battle runtime (battle layer assente) ✅
- K3: `status_envelope_preview` non leak su `/api/heroes`, `/api/heroes/borea`, `/api/server-profiles/select`, `/api/housing/preview` ✅

## Verdict

13/13 check `PASS`. Il QA RC Gate è **READY**.

## Conformità ai guardrail

- ✅ Nessuna mutazione battle.
- ✅ Nessuna implementazione frontend (i requisiti di QA mobile restano definiti come *manual checks* nel marker JSON, non come codice).
