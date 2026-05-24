# 135B — BATTLE ENGINE STATUS SEAM SINGLE-POINT WIRING

**Pack**: `PROJECT_M` — Track B
**Verdict**: `TRACK_B_BATTLE_ENGINE_STATUS_SEAM_WIRED_FLAG_OFF_SAFE`
**Marker JSON**: `/app/data/design/status_effects/project_m_battle_engine_status_seam_wiring_result_v1.json`
**Validator**: `/app/backend/scripts/validate_project_m_battle_engine_status_seam_wiring_v1.py`

## Patch eseguita

Due sezioni minime in `/app/backend/battle_engine.py`:

1. **Import block** (top del modulo, dopo gli import di stdlib/fastapi/pydantic): `try/except` bind del seam su `_project_m_status_seam`; fallback identity se il seam non è importabile.
2. **Call site** (dentro `simulate_battle`, prima di `battle_log = []`): 2 chiamate `team_a = _project_m_status_seam(team_a); team_b = _project_m_status_seam(team_b)`.

## Hashes

| File | MD5 |
|------|-----|
| `battle_engine.py` (pre-patch, backup) | `e631d9af4caa79d63e5e3d44145bce43` |
| `battle_engine.py` (post-patch, live) | `d04feb03e1388db8557d17bd42d5b4d1` |
| `battle_core.py` | `80d94afba9eb2930e63b06cfed645b77` (invariato) |
| `server.py` | `9b3affcbdb3d4c50efc7ce8b9bc603cb` (invariato) |
| `routes/combat.py` | `1f531d75792b34e5ff37293e4ed61725` (invariato) |

## Backup file

`/app/backend/battle_engine.py.project_m_pre_patch.bak` salvato prima della patch e usato dal rollback drill (Track F).

## Rollback script

`/app/backend/scripts/rollback_project_m_battle_engine_status_seam.py` con dry-run di default e `--apply` esplicito.

## Flag OFF byte-identical

Fixture deterministica 3v3 (random.seed=42, max_turns=5):
- pre-patch SHA256 stable payload: `d951767a72b54b339eb660f6308d72c943a9a9e318539f639ce9fc7f416d3725`
- post-patch SHA256 stable payload: **identica**

## Conformità ai guardrail

- ✅ No DoT / tick loop.
- ✅ No damage / heal formula change.
- ✅ No round loop change.
- ✅ No broad refactor.
- ✅ No battle_core mutation.
- ✅ No combat.tsx / frontend.
- ✅ No DB write.
