# 98 — GDPR Data Export & Hard Delete

## Pack

`MEGA_RELEASE_ACCELERATION_47_v98`

## GDPR Data Export

**Endpoint**: `GET /api/auth/data-export` (auth required).

Format: JSON. Campi inclusi: account_id, alias, username, provider, level, experience, gold, gems, stamina, team_formation, created_at, last_login, pending_deletion.

**Esclusi per sicurezza**: provider_user_id_hash, password_hash, refresh_token_hash, internal_db_id.

**Runtime**: ATTIVO.

## Hard Delete

**Endpoint**: `POST /api/auth/hard-delete-confirm`.

**Runtime**: `GATED_DEFAULT_OFF` (env `V98_HARD_DELETE_RUNTIME_ENABLED=false`).

Quando disabilitato risponde `DISABLED_PENDING_COMMERCIAL_REVIEW`.

Quando abilitato (post-commercial-review): elimina `refresh_tokens` + documento user (irreversibile, audit trail richiesto).

## Cron script

`backend/scripts/cron_v98_hard_delete_dry_run.py`

Scan giornaliero degli account con `pending_deletion=true AND scheduled_deletion_at < now`.

Default: dry-run, log candidati, no DB mutation.
Quando V98_HARD_DELETE_RUNTIME_ENABLED=true: hard delete con audit.

## Verdict

`GDPR_DATA_EXPORT_RUNTIME_ACTIVE + HARD_DELETE_CRON_DRY_RUN_READY_RUNTIME_GATED_COMMERCIAL_REVIEW`
