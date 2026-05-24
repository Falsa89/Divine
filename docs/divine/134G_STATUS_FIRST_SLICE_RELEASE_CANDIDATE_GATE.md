# 134G — STATUS FIRST SLICE RELEASE CANDIDATE GATE

**Pack**: `PROJECT_L_STATUS_FIRST_SLICE_FLAGGED_CANARY_ENV` — Track G
**Verdict**: `TRACK_G_STATUS_FIRST_SLICE_RC_GATE_READY`
**Marker JSON**: `/app/data/design/project_management/project_l_status_first_slice_rc_gate_v1.json`
**Validator**: `/app/backend/scripts/validate_project_l_status_first_slice_rc_gate_v1.py`

---

## Obiettivo

Definire e validare il **Release Candidate Gate** del status first slice dopo la creazione del seam: stato runtime, stato suite, stato payload.

## Automation checks (13)

| ID | Check | Esito |
|----|-------|-------|
| S1 | `GET /api/heroes` → 200, count 100 | ✅ |
| S2 | `GET /api/heroes/primordial_gaia` → 404 | ✅ |
| S3 | `GET /api/heroes/borea` → 200 | ✅ |
| S4 | `GET /api/heroes/greek_borea` → 200 | ✅ |
| S5 | `GET/POST /api/server-profiles/select` → 503 | ✅ |
| S6 | `GET /api/housing/preview` → 503 | ✅ |
| S7 | `STATUS_RUNTIME_BUFF_SLICE_ENABLED` + `STATUS_RUNTIME_SEAM_CANARY_OK` non = `true` | ✅ |
| S8 | `seam.is_seam_active()` False con flag unset | ✅ |
| S9 | seam non importato da battle_engine / battle_core / server / routes | ✅ |
| S10 | nessun leak `status_envelope_preview` / `__seam_version` | ✅ |
| S11 | resolver puro: empty input → zero envelope | ✅ |
| S12 | 19 REQUIRED validator passing (via suite parallel) | ✅ |
| S13 | rollback dry-run OK (Track F) | ✅ |

## Manual checks (definiti, da eseguire in canary env)

- M1: mobile QA su browse eroi (no leak status preview visibile in UI).
- M2: mobile QA su combat screen (no behavior change con flag OFF).
- M3: smoke su canary env BEFORE flag flip.

## Canary progression

| Stage | Nome | Status |
|-------|------|--------|
| 1 | dry-run (in-process) | READY (questo pack) |
| 2 | canary env | BLOCKED until PROJECT_M approval |
| 3 | dev live | BLOCKED until PROJECT_M+ approval |
| 4 | prod | BLOCKED until separate prod approval |

## Conformità ai guardrail

- ✅ Nessun live rollout eseguito.
