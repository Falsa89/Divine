# 141F — PROJECT_S Track F: Second-Slice Rollback & Deletion Plan

## Verdict
`TRACK_F_SECOND_SLICE_ROLLBACK_AND_DELETION_PLAN_READY`

## Marker JSON
`/app/data/design/status_effects/project_s_second_slice_rollback_deletion_plan_v1.json`

## Validator
`/app/backend/scripts/validate_project_s_second_slice_rollback_deletion_plan_v1.py` → **[PASS]**

## Rollback script
`/app/backend/scripts/rollback_project_s_status_second_slice_pure_resolver.py`

### Modalità
- **Default**: dry-run; nessuna cancellazione.
- **`--execute`**: GATED su `PROJECT_S_ROLLBACK_PURE_RESOLVER_OK=true`. Senza il marker, abort con exit code 3.

### Test eseguiti dal validator
1. Dry-run → exit 0, output contiene `[DRY-RUN]`, nessun file cancellato.
2. `--execute` senza env gate → abort, exit code != 0, output `[ABORT]`.
3. Forbidden files (first-slice, battle_engine, battle_core) verificati esistenti e intatti dopo dry-run.

## Deletion targets (9 file Project S)
Resolver `.py` + 8 marker JSON Track A-H.

## Forbidden to delete (hard guard)
- `/app/backend/game_logic/status_first_slice_resolver_pure.py`
- `/app/backend/game_logic/status_prefight_runtime_seam.py`
- `/app/backend/battle_engine.py`
- `/app/backend/battle_core.py`

Il validator verifica overlap a 0 fra `forbidden_to_delete` e `deletion_targets`.

## Side effects
Nessuno. `rollback_executed_in_pack_s=false`, `db_writes=false`.
