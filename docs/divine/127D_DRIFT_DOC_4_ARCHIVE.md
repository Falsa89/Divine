# 127D — PROJECT_E Track D — DRIFT_DOC_4 DUPLICATE_SUMMON_LOG_FORMAT DEDUPE DESIGN FREEZE

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_E`  
**Verdict**: 🟢 `TRACK_D_DRIFT_DOC_4_ARCHIVE_READY`  
**Rollback**: N/A (audit only)

## Scopo

Quarto step della cleanup chain V_A Track F: **DRIFT_DOC_4** (`duplicate_summon_log_format`) marcato `KNOWN_NONBLOCKING_DEDUPE_DESIGN_FROZEN_V1`. Action V_A: `dedupe_design_required` (richiede data mutation futura, ma **non eseguita in V_E**).

## Catena drift

| Step | Processed |
|---|---|
| Post V_A | 0/7 |
| Post V_B | 1/7 (DRIFT_DOC_1 archived) |
| Post V_C | 2/7 (DRIFT_DOC_2 archived) |
| Post V_D | 3/7 (DRIFT_DOC_3 frozen) |
| **Post V_E** | **4/7 (DRIFT_DOC_4 dedupe design frozen)** |

## Dedupe design steps (NON eseguiti in V_E)

1. Snapshot `summon_history` pre-dedupe
2. Identify duplicate criterion: `(user_id, summon_timestamp, banner_id)`
3. Emit candidates list (JSON design only)
4. Safety smoke: gacha/pull route response shape invariata
5. Rollback strategy: per-doc restore da `$set` log
6. Future apply: dedicated `DRIFT_DOC_4_DEDUPE_OPS_PACK` con tutti i signoff

## Forbidden scope rispettato

DB cleanup ❌, gacha/summon behavior change ❌, roster mutation ❌, Borea activation ❌, banner/rate/pity/pool change ❌, dedupe execution ❌.
