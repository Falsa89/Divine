# 98 — Server Actors Runtime Persistence

## Pack

`MEGA_RELEASE_ACCELERATION_47_v98`

## Stato

`GATED_DEFAULT_OFF_DESIGN_READY_NO_RUNTIME_DB_WRITES_YET`

## Collection: `server_actors`

Schema: `actor_id`, `is_bot=true`, `synthetic_server_actor=true`, `bot_archetype`, `account_level` (start 1), `server_id/shard_id`, `roster_snapshot`, `resource_profile`, `progression_state`, `event_unlock_state`, `guild_state`, `faction_state`, `chat_persona`, `created_by_system=true`, `runtime_enabled`, `created_at`, `updated_at`, `current_server_age_at_birth_days`, `current_player_average_level_at_birth`.

## Gating

- Env: `V98_SERVER_ACTORS_RUNTIME_ENABLED` (default `false`).
- Effect quando disabilitato: nessun DB write, nessuna creazione, nessuna mutazione live.

## Seed policy

- Mass creation protection ON.
- Max seed per run: 5.
- Seed solo con esplicito admin trigger.
- No irreversible mass creation.

## Rules enforced

- start_level_1
- respect server_age cap + player_avg cap + p95
- no top-3 domination
- no premium reward theft
- no real IAP
- no day-one high-level
- event access requires unlock

## Admin endpoint

`GET /api/admin/server-actors/status` — read-only, runtime verified.

## Verdict

`SERVER_ACTOR_RUNTIME_PERSISTENCE_GATED_DESIGN_READY_NO_DB_WRITES`
