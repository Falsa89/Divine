# 125D — PROJECT_C Track D — DRIFT_DOC_2 DEPRECATED BANNER ARCHIVE

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_C`  
**Track**: D  
**Mode**: `audit_archive_doc_only_no_db_cleanup`  
**Verdict**: 🟢 `TRACK_D_DRIFT_DOC_2_ARCHIVE_READY`  
**Rollback**: N/A (audit only)

---

## 1. Scopo

Continuare il cleanup gated dei 7 drift doc archiviando il **secondo** drift doc (`DRIFT_DOC_2`, classe `deprecated_banner_legacy_pool`) come `KNOWN_NONBLOCKING_ARCHIVED_V2`. **Nessun** DB cleanup, **nessun** file fisico spostato in questo pack. Continua la catena iniziata in V_B (DRIFT_DOC_1).

## 2. Target drift doc

| Campo | Valore |
|---|---|
| ID | DRIFT_DOC_2 |
| Classe | `deprecated_banner_legacy_pool` |
| Descrizione | Riferimenti residui a banner pool legacy v0 in `gacha.py` e snapshot pool obtainable pre-V1 BLOCK_B |
| Data mutation required | ❌ No |
| Behavior mutation required | ❌ No |
| User-facing impact | none |

## 3. Archive action

| Aspetto | Valore |
|---|---|
| Type | `DOC_AUDIT_FREEZE` |
| Status post-pack | `KNOWN_NONBLOCKING_ARCHIVED_V2` |
| Physical move | Differito a `DRIFT_DOC_2_PHYSICAL_ARCHIVE_OPS_PACK` (futuro opzionale) |

## 4. Progressione catena

| Step | Drift docs totali | Archived | Pending |
|---|---|---|---|
| Post V_A Track F | 7 | 0 | 7 |
| Post V_B Track D | 7 | 1 | 6 |
| **Post V_C Track D** | **7** | **2** | **5** |

## 5. Forbidden scope rispettato

- DB cleanup ❌
- Gacha/summon behavior change ❌
- Roster mutation ❌
- Borea activation ❌

## 6. Validator

`/app/backend/scripts/validate_project_c_drift_doc_2_archive_v1.py` — read-only, controlla marker JSON, classe drift doc, conta archiviati `=2` e coerenza upstream.
