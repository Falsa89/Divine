# 110 — Pack 107 SOT (Source Of Truth)
## ARENA / PVP / GUILD / EVENTS — SERVER-SCOPE GUARDS

> Documento canonico Pack 107: audit + honest blocker per superfici competitive/social/live.

## Strict keys

| Surface | Server-scoped key richiesta |
|---|---|
| Arena MMR/rank/season | `user_id + server_id + season` |
| Arena match history | `user_id + server_id + match_id` |
| Guild membership | `user_id + server_id + guild_id` |
| Guild chat/events/war | `guild_id + server_id` |
| Event progress/ranking | `user_id + server_id + event_id` |
| Leaderboard | `server_id + event_id|season` |

## Endpoints Pack 107

* `GET  /api/competitive-guards/health`
* `POST /api/competitive-guards/arena/preflight?server_id=<sid>`
* `POST /api/competitive-guards/pvp/preflight?server_id=<sid>`
* `POST /api/competitive-guards/guild/preflight?server_id=<sid>`
* `POST /api/competitive-guards/event/preflight?server_id=<sid>`

## Status per Surface

| Surface | Status | Active Blockers |
|---|---|---|
| Arena | `READY_GATED_REWARDS_DEFERRED` | `ARENA_SERVER_SCOPE_REQUIRED`, `ARENA_REWARD_LIVE_DISABLED` |
| PvP | `READY_GATED_REWARDS_DEFERRED` | `PVP_RANKING_SERVER_SCOPE_DEFERRED` |
| Guild | `AUDIT_LEGACY_NOT_SERVER_SCOPED` | `GUILD_SERVER_SCOPE_REQUIRED`, `GUILD_REWARD_LIVE_DISABLED` |
| Event | `READY_GATED_REWARDS_DEFERRED` | `EVENT_SERVER_SCOPE_REQUIRED`, `EVENT_REWARD_LIVE_DISABLED` |

## Audit Legacy Routes

| File | Esiste | Server-scope | Quarantine Pack 107 |
|---|---|---|---|
| `routes/arena.py` | NO | N/A | safe by absence |
| `routes/pvp.py` | NO | N/A | safe by absence |
| `routes/guild.py` | SI | NO (0 server_id) | **audit honest blocker** (no quarantine forzata, scope futuro Pack) |
| `routes/event.py` | NO | N/A | safe by absence |

## Kill switches (default OFF)

| Env | Scope |
|---|---|
| `ARENA_REWARD_LIVE_ENABLED` | arena reward live |
| `PVP_REWARD_LIVE_ENABLED` | pvp reward live |
| `GUILD_REWARD_LIVE_ENABLED` | guild reward live |
| `EVENT_REWARD_LIVE_ENABLED` | event reward live |

## Leaderboard

`LEADERBOARD_SERVER_SCOPE_REQUIRED` enforced via blocker canonico nel `/health` di Pack 107.
Nessun endpoint leaderboard live introdotto.

NESSUN reward live attivato. Pack 107 è audit-only.

## Frontend guards

* `EXPO_PUBLIC_COMPETITIVE_GUARDS_UI_ENABLED` default `'false'`
* Nessuna UI Arena/Guild/Event abilitata ai consumatori in Pack 107.

## Forbidden in Pack 107 paths

* Arena/PvP/Guild/Event reward live
* Battlepass / AFK reward live
* `users.gold/gems/experience` mutation
* premium / hard / gems grant
* IAP / gacha / payment
* account-wide ranking/guild/event writes
* hardcoded `server_id="s1"`
* cross-server arena/guild/event leak
* false `filter_applied=true`
* `reward_live_general=true`
* `release_readiness_claimed=true`

## Deferred Blockers

* **Guild server-scope retrofit**: `routes/guild.py` legacy NON è server-scoped. Un futuro Pack (`AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_PACK_NEXT`) dovrà applicare il filtro `server_id` a tutte le find/update di guild membership/search.
* **Arena/PvP/Event implementation**: nessuna route live presente. Future Pack potranno implementare arena/pvp/event runtime in modalità strict server-scoped + ledger-gated.

## Safety summary

- reward_live_general=false
- release_readiness_claimed=false
- premium_grants=false
- no_arena_pvp_guild_event_reward_live=true
- no_cross_server_ranking_leak=true
- no_battlepass_afk_reward_live=true
- no users.gold/users.gems/users.experience mutation
- Pack 91-106 preservati
