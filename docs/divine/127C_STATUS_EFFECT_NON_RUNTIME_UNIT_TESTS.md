# 127C — PROJECT_E Track C — STATUS EFFECT NON-RUNTIME UNIT TESTS

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_E`  
**Verdict**: 🟢 `TRACK_C_STATUS_EFFECT_NON_RUNTIME_UT_READY`  
**Rollback**: N/A (validator only)

## Casi UT

| ID | Caso |
|---|---|
| UT_STATUS_1 | every catalog effect → canonical category (`buff_offensive`..`meta`) |
| UT_STATUS_2 | stacking rules parse: `1<=duration_turns<=10`, `1<=stack_max<=5` |
| UT_STATUS_3 | hard control (`stun`, `freeze`) presenti nella categoria `control` |
| UT_STATUS_4 | `dispellable`, `cleansable` sono bool |
| UT_STATUS_5 | no Borea-only status leak |
| UT_STATUS_6 | adapter NON importato da `battle_engine.py`, `battle_core.py`, `routes/*.py`, `server.py` |

## Forbidden scope rispettato

battle_engine.py ❌, battle_core.py ❌, combat.tsx ❌, status live activation ❌.
