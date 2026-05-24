# 135A — BATTLE ENGINE SINGLE POINT WIRING AUDIT

**Pack**: `PROJECT_M_STATUS_FIRST_SLICE_CANARY_ENV_EXECUTION` — Track A
**Verdict**: `TRACK_A_BATTLE_ENGINE_SINGLE_POINT_WIRING_AUDIT_READY`
**Classificazione**: `SINGLE_POINT_SAFE_NOW_FLAGGED`
**Marker JSON**: `/app/data/design/status_effects/project_m_battle_engine_single_point_audit_v1.json`
**Validator**: `/app/backend/scripts/validate_project_m_battle_engine_single_point_audit_v1.py`

## Audit

`battle_engine.simulate_battle` localizzato a `/app/backend/battle_engine.py:379`. L'insertion point sicuro è immediatamente dopo la docstring, **prima** dell'inizializzazione di `battle_log = []` e dello state combat: `team_a`/`team_b` sono ancora input grezzi, nessun draw random, nessuna entry log esiste.

## Pattern di chiamata

```python
team_a = _project_m_status_seam(team_a)
team_b = _project_m_status_seam(team_b)
```

Il seam, con flag OFF, ritorna `team_payload` invariato (stessa `id()`). Il rebinding è quindi semantica identity → nessun side effect.

## Pre-patch MD5

| File | MD5 |
|------|-----|
| `battle_engine.py` | `e631d9af4caa79d63e5e3d44145bce43` |
| `battle_core.py` | `80d94afba9eb2930e63b06cfed645b77` |
| `server.py` | `9b3affcbdb3d4c50efc7ce8b9bc603cb` |
| `routes/combat.py` | `1f531d75792b34e5ff37293e4ed61725` |

## Conformità ai guardrail

- ✅ Audit read-only.
- ✅ Nessuna mutazione runtime in Track A.
- ✅ Nessun broad refactor.
