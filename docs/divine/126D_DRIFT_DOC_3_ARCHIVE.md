# 126D — PROJECT_D Track D — DRIFT_DOC_3 OBSOLETE_PITY_COUNTER_FORMAT FREEZE

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_D_DRIFT_DOC_3_ARCHIVE_READY`  
**Rollback**: N/A (audit only)

## Scopo

Terzo step della cleanup chain V_A Track F: **DRIFT_DOC_3** (`obsolete_pity_counter_format`) viene marcato `KNOWN_NONBLOCKING_FROZEN_READ_ONLY_V1`. **Nessun** banner/rate/pity/pool change, **nessun** DB cleanup.

L'action `freeze_read_only` (vs `archive_into_attic` di DRIFT_DOC_1/2) deriva dal V_A plan: il formato pity counter v0 è ancora leggibile dal codice attuale e non richiede migrazione fisica.

## Target

| Campo | Valore |
|---|---|
| ID | DRIFT_DOC_3 |
| Class | `obsolete_pity_counter_format` |
| Action V_A | `freeze_read_only` |
| Status post-V_D | `KNOWN_NONBLOCKING_FROZEN_READ_ONLY_V1` |

## Catena drift

| Step | Archived |
|---|---|
| Post V_A Track F | 0/7 |
| Post V_B Track D | 1/7 (DRIFT_DOC_1) |
| Post V_C Track D | 2/7 (DRIFT_DOC_2) |
| **Post V_D Track D** | **3/7 (DRIFT_DOC_3 frozen)** |

## Forbidden scope rispettato

DB cleanup ❌, gacha/summon behavior change ❌, roster mutation ❌, Borea activation ❌, banner/rate/pity/pool change ❌.
