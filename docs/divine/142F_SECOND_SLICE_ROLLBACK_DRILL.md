# 142F — PROJECT_T Track F: Rollback Drill

## Verdict
`TRACK_F_SECOND_SLICE_ROLLBACK_DRILL_READY`

## Marker JSON
`/app/data/design/status_effects/project_t_second_slice_rollback_drill_v1.json`

## Validator
`/app/backend/scripts/validate_project_t_second_slice_rollback_drill_v1.py` → **[PASS]**

## Rollback script
`/app/backend/scripts/rollback_project_t_status_second_slice_battle_engine_wiring.py`

### Modalità
- **Default**: dry-run. Report dei file che sarebbero ripristinati/cancellati. Nessuna modifica.
- **`--execute`**: GATED su `PROJECT_T_ROLLBACK_SECOND_SLICE_WIRING_OK=true`. Senza il marker, abort con exit code 3.

### Operazioni in caso di rollback live
1. Restore `/app/backend/battle_engine.py` dal backup `/app/backend/battle_engine.py.project_t_pre_wire_backup` (md5 `d04feb03...`).
2. Cancellazione di `/app/backend/game_logic/status_second_slice_runtime_seam.py`.

## Forbidden to delete (hard guard)
- `/app/backend/game_logic/status_first_slice_resolver_pure.py`
- `/app/backend/game_logic/status_prefight_runtime_seam.py`
- `/app/backend/game_logic/status_second_slice_resolver_pure.py` (resolver Project S, NON cancellabile)
- `/app/backend/battle_core.py`

## Test eseguiti dal validator
1. **Dry-run**: exit 0, output `[DRY-RUN]`, md5 di `battle_engine.py` invariato. ✅
2. **`--execute` senza env gate**: exit != 0, output `[ABORT]`. ✅
3. **Temp-copy drill**: in tempdir simulata l'operazione di restore; md5 post-restore = md5 backup dichiarato. ✅
4. **Forbidden files intact**: tutti i file forbidden esistono post-drill. ✅

## Side effects
Nessuno. DB writes: 0. Real battle_engine.py invariato dopo dry-run.
