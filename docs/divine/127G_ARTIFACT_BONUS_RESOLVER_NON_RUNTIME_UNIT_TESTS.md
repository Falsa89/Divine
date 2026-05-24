# 127G — PROJECT_E Track G — ARTIFACT BONUS RESOLVER NON-RUNTIME UNIT TESTS

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_E`  
**Verdict**: 🟢 `TRACK_G_ARTIFACT_BONUS_RESOLVER_UT_READY`

## Casi UT

| ID | Caso |
|---|---|
| UT_ARTIFACT_1 | resolve ritorna zero envelope con 5 chiavi canoniche |
| UT_ARTIFACT_2 | caps `hp_pct/atk_pct/def_pct/crit_pct` con `min<max` |
| UT_ARTIFACT_3 | candidates NON equipment (no slot weapon/armor/helmet/boots/gloves/accessory) |
| UT_ARTIFACT_4 | candidates remain `draft` (design-only) |
| UT_ARTIFACT_5 | stub NON importato da `server.py`, `routes/*.py` |
| UT_ARTIFACT_6 | `validate_caps_definition()` ritorna True |

## Forbidden scope rispettato

Artifact live bonus ❌, artifact summon ❌, gacha/rate/pity change ❌, frontend ❌, DB writes ❌, equipment semantics ❌.
