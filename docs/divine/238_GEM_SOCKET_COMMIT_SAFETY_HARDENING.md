# 238 - PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK (v37 Track A)

**Mode**: ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT  
**Flag**: `GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED` (default off -> 503)

## Endpoints
- `GET /api/gem-socket-commit-safety-preview/config`
- `POST /api/gem-socket-commit-safety-preview/validate-request`
- `POST /api/gem-socket-commit-safety-preview/guard-plan-preview`
- `POST /api/gem-socket-commit-safety-preview/idempotency-preview`

## 15 guard checks (preview)
`ownership_verified`, `gear_locked_or_favorite_check`, `active_team_loadout_check`, `active_pvp_loadout_check`, `active_guild_war_loadout_check`, `socket_index_eligible`, `gem_valid_and_not_consumed`, `expected_gear_version_match`, `expected_gem_version_match`, `expected_gear_socket_state_version_match`, `expected_gem_inventory_version_match`, `idempotency_key_required`, `atomic_commit_required_future`, `rollback_strategy_required_future`, `audit_log_required_future`.

## Safety
`commit_enabled=false`, `gear_mutation_enabled=false`, `gem_inventory_mutation_enabled=false`, `premium_users_gems_used=false`, `db_writes=0`. Esistente `backend/routes/gem_socket_preview.py` invariato.
