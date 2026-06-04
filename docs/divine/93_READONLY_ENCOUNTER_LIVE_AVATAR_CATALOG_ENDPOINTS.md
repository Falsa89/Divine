# 93 — Read-Only Encounter/Live/Avatar Catalog Endpoints (v93)

## Pack
`MEGA_RELEASE_ACCELERATION_42_PLAYABILITY_COMPLETION_SUPERPACK_v93`

## Design contract endpoints (BLOCKED implementation)

| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| GET | `/api/encounter-source/catalog` | catalog encounter (story/tower/arena/training/raid/event/guild_live) | BLOCKED_MD5_LOCKED_SERVER |
| GET | `/api/encounter-source/get?mode=X&source_id=Y` | specific encounter | BLOCKED_MD5_LOCKED_SERVER |
| GET | `/api/live-mode/catalog` | live/guild/special mode encounter catalog | BLOCKED_MD5_LOCKED_SERVER |
| GET | `/api/avatar-placeholder/catalog` | avatar placeholder dev registry | BLOCKED_MD5_LOCKED_SERVER |

## Blocker
`backend/server.py` e' MD5-lockato (`055df030...f148`). La registrazione di un nuovo router richiede modifica a server.py, vietata da v93.

## Fallback (v93)
Mantenere inline mirror dei JSON catalog dentro le schermate (pre-battle-lobby, live-guild-qa-hub, live-mode-pre-entry-lobby, nuove schermate v93). Etichettare apertamente come 'inline mirror (v93 endpoint blocked)'.

## Decisione
- Contract status: `DESIGN_READY_IMPLEMENTATION_BLOCKED`
- Inline mirror removal: `skipped_due_to_md5_lock_blocker`
- Read-only, idempotent, no DB writes, no reward

## Safety
- db_writes=0
- reward_live=false
- endpoint_live_mutation=false
- md5_lock_mutation=false
