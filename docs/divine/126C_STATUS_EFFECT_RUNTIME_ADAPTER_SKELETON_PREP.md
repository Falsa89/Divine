# 126C — PROJECT_D Track C — STATUS EFFECT RUNTIME ADAPTER SKELETON PREP

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_D`  
**Verdict**: 🟢 `TRACK_C_STATUS_EFFECT_RUNTIME_ADAPTER_SKELETON_CREATED_INERT`  
**Rollback**: rm `/app/backend/game_logic/status_effect_runtime_adapter_stub.py` (zero impatto runtime)

## Scopo

Creare un **adapter skeleton puro** per status effects, in preparazione del futuro wiring battle. **NON** importato da `battle_engine.py`, `battle_core.py`, `combat.tsx`, `server.py`, né `routes/*.py`.

## Mapping contracts

| Campo | Tipo | Set canonico |
|---|---|---|
| `status_id` | str | non vuoto |
| `category` | str | 10 categorie (`buff_offensive`, ..., `meta`) |
| `polarity` | str | positive / negative / neutral |
| `stacking` | str | none / refresh / stack_capped |
| `boss_behavior` | str | normal / reduced / immune |
| `source_lock` | bool | — |
| `display_hint` | str | 7 icone canoniche |

## API

```python
build_status_mapping(status_id, category, polarity, stacking, boss_behavior, source_lock, display_hint) -> dict
validate_canonical_sets() -> bool
```

`build_status_mapping` lancia `ValueError` su campi fuori set canonico. Sempre `runtime_active=False`.

## Forbidden scope rispettato

battle_engine.py ❌, battle_core.py ❌, combat.tsx ❌, status live activation ❌, HP bar/status UI ❌, VFX runtime ❌, Borea activation ❌.
