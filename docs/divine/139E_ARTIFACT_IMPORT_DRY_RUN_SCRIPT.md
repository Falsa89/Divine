# 139E — PROJECT_Q Track E: Artifact Import Dry-Run Script

## Verdict
`TRACK_E_ARTIFACT_IMPORT_DRY_RUN_SCRIPT_READY`

## Marker JSON
`/app/data/design/artifacts/project_q_artifact_import_dry_run_script_v1.json`

## Script
`/app/backend/scripts/import_project_q_artifact_bible_dry_run_v1.py`

## Validator
`/app/backend/scripts/validate_project_q_artifact_import_dry_run_script_v1.py` → **[PASS]**

## Modalità
- **Default**: `dry-run`. Esegue solo schema + invariants validation, **0 DB writes**.
- **`--apply`**: GATED su tutte e 5 le firme `ARTIFACT_*` (USER, ECONOMY, BALANCE, QA, IMPORT_LIVE_OK). In assenza, abort con exit code 3.
- **`--rollback`**: rimozione safe del batch (8 `artifact_id`) — non eseguito in questo pack.

## Risultato esecuzione dry-run
```
[INFO] loaded 8 candidates
[INFO] schema+invariants: 8 PASS / 0 FAIL
[DRY-RUN] no DB writes performed; pass --apply (with signatures) or --rollback for live ops
```

- `candidates_loaded: 8`
- `schema_validation_pass_count: 8`
- `schema_validation_fail_count: 0`
- `hard_invariants_pass_count: 8`
- `hard_invariants_fail_count: 0`
- `db_writes_attempted: 0`
- `db_writes_executed: 0`
- `would_write_collection: artifacts (mongodb local divine_waifus)`
- `would_write_count_if_applied: 8`

## Side effects
Nessuno: `db_touch == false`. Il DB non è stato toccato.
