# 124B — PROJECT_B Track B — HOUSING_MVP_RESOLVER_STUB

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_B`  
**Track**: B  
**Mode**: `pure_module_not_imported_by_runtime`  
**Verdict**: 🟢 `TRACK_B_HOUSING_MVP_RESOLVER_STUB_CREATED_INERT`

---

## 1. Scopo

Creare il primo **stub puro** del `HousingBonusResolver` come modulo Python in `/app/backend/game_logic/` (nuovo package non-runtime). Lo stub e' **inert**: tutti i bonus emessi sono **0**, l'output shape e' canonical, le caps canonical sono dichiarate ma **non enforced live**.

## 2. Architettura

```
/app/backend/game_logic/
  __init__.py                            # package marker ("non-runtime")
  housing_bonus_resolver_stub.py         # NEW pure module
      └ resolve_housing_bonus(user_state) → {hp/atk/def/healing}=0
      └ validate_caps_definition(caps) → list[str]
      └ CANONICAL_CAPS dict
      └ INERT_MARKER = "HOUSING_BONUS_RESOLVER_STUB_INERT_PROJECT_B_TRACK_B_V1"
```

## 3. Public API

### `resolve_housing_bonus(user_state)`
- **Input**: `{user_id, housing_rooms[], objects[], residents[]}`
- **Output**: `{hp_bonus: 0, atk_bonus: 0, def_bonus: 0, healing_bonus: 0}` (sempre)
- **Side effects**: nessuno (pure function)
- **Type-checked**: input deve essere dict, le liste devono essere liste

### `validate_caps_definition(caps)`
- **Output**: lista di stringhe errore (vuota = valid)
- **Verifica**: presenza delle 6 chiavi canonical + valori positivi int

## 4. Canonical caps (read-only)

| Cap | Valore |
|---|---|
| `per_room` | 6 |
| `category` | 4 |
| `item` | 12 |
| `bonus` | 8 |
| `mode` | 2 |
| `master_cap` | 30 |

## 5. Non-runtime guarantee

Lo stub **non** e' importato da:
- `/app/backend/server.py`
- `/app/backend/game_systems.py`
- `/app/backend/battle_engine.py`
- `/app/backend/battle_core.py`
- `/app/backend/routes/*.py`
- `/app/frontend/app/**/*.tsx`

Il validator verifica tutti questi paths via `grep` su `housing_bonus_resolver_stub`.

## 6. Validator

- **Path**: `/app/backend/scripts/validate_project_b_housing_resolver_stub_inert.py`
- **Suite task_id**: `PROJECT-B-TRACK-B-HOUSING-RESOLVER-STUB-INERT` (OPTIONAL)
- **Type**: import dinamico + invocazione API + grep non-runtime
- **Verifiche**: marker, output zero, caps validation negativa, no runtime import

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| `/api/housing` live | ❌ No |
| Live resolver imported by runtime | ❌ No |
| Battle/account stat application | ❌ No |
| DB writes | ❌ No |
| Frontend/UI | ❌ No |
