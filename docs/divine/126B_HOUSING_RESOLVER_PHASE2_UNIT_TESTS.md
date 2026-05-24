# 126B — PROJECT_D Track B — HOUSING RESOLVER PHASE 2 UNIT TESTS

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_B_HOUSING_RESOLVER_PHASE2_TESTS_READY`  
**Rollback**: N/A (validator only)

## Scopo

Fornire **unit-test style validation** del puro stub `housing_bonus_resolver_stub.py` senza alcun runtime import. Copre 8 casi UT_HOUSING_1..8.

## Casi UT

| ID | Caso | Esito atteso |
|---|---|---|
| UT_HOUSING_1 | minimal dict `{user_id}` → zero-envelope con 4 chiavi canoniche (`hp_bonus`, `atk_bonus`, `def_bonus`, `healing_bonus`) | OK |
| UT_HOUSING_2 | non-dict (None, list) → solleva `TypeError` | OK |
| UT_HOUSING_3 | envelope stabile su input dict varianti | OK |
| UT_HOUSING_4 | `validate_caps_definition(CANONICAL_CAPS)` ritorna `[]` (no errors) | OK |
| UT_HOUSING_5 | caps key set = `{per_room, category, item, bonus, mode, master_cap}` | OK |
| UT_HOUSING_6 | ogni cap value è int positivo | OK |
| UT_HOUSING_7 | `INERT_MARKER` + `INERT_BONUS_OUTPUT` canonici e a zero | OK |
| UT_HOUSING_8 | stub NON importato da `server.py`, `game_systems.py`, `routes/*.py` | OK |

## Forbidden scope rispettato

Live housing runtime ❌, battle/account stat application ❌, DB writes ❌, frontend ❌, runtime import of stub ❌.
