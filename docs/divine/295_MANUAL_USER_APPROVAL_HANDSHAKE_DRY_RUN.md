# 295 — Manual User Approval Handshake (DRY-RUN)

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_14_EPHEMERAL_SIMULATION_INVARIANT_REPORT_AND_STAGING_DB_BLUEPRINT_PACK_v50`
**Track**: D
**Public Sync Tag**: `PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14`
**Contract version**: `manual_user_approval_handshake_dry_run_v1`

## Scopo
Definire l'**handshake manuale** richiesto al titolare/QA/game director per ogni
futura transizione di promozione live. Strettamente **dry-run**, **no endpoint**,
**no runtime execution**, **no automatic approval**.

## File design
- `data/design/economy_safety/manual_user_approval_handshake_dry_run_v1.json`
- `data/design/economy_safety/manual_user_approval_handshake_dry_run_marker_v1.json`

## Frase di approvazione (template)
```
I APPROVE <operation_family> <transition> WITH CHECKSUM <checksum_sha256> ON <date>
```
Placeholder obbligatori: `<operation_family>`, `<transition>`, `<checksum_sha256>`, `<date>`.

## Transition enum
- `dry_run_to_staging_dry_run`
- `staging_dry_run_to_canary_dry_run`
- `canary_dry_run_to_canary_live_BLOCKED`
- `canary_live_to_live_BLOCKED`

Le transizioni `*_BLOCKED` indicano che la transizione richiede esplicita
approvazione manuale dell'utente prima di qualsiasi attuazione.

## Stato corrente per ogni famiglia
Tutte e 8 le famiglie hanno:
`current_approval_state = pending`, `approval_phrase_recorded = null`,
`checksum_sha256_recorded = null`, `date_recorded = null`,
`transition_recorded = null`, `db_writes = 0`, `live_apply_allowed = false`.

## Forbidden
no_endpoint · no_runtime_execution · no_automatic_approval ·
no_real_db_connection · no_mongo_url · no_pymongo · no_motor · no_env_read ·
no_filesystem_writes · no_db_writes · no_live_apply · no_production_mutation ·
no_endpoint_path_change · no_feature_flag_change · no_default_503_change ·
no_server_py_change · no_frontend_change · no_battle_engine_change
