# v106 — Existing Data Model Audit

**Pack**: `MEGA_RELEASE_ACCELERATION_55_v106`
**Source JSON**: `data/design/server_scope/v106_existing_data_model_audit_v1.json`

## Sintesi

17 collection auditate. Nessuna ha `server_id` come field today. **0/17 enforce isolation server-bound**.

| Outcome | Count |
|---|---|
| should move to player_server_profiles | 8 |
| remain account-global | 3 (users, vip, [hard wallet design]) |
| split mixed | 5 (currencies, gacha_history, reward_claims, battle_pass, shop_purchases) |
| separate collection (chat) | 1 |
| critical risk migration | 3 (arena_profile, guild_membership, chat_messages) |
| high risk migration | 6 (user_heroes, inventory, currencies, live_event_state, server_actors_bots, reward_claims) |

## Highlight P0

- `users` resta **account-global** (identità globale). 
- `user_heroes`, `teams`, `inventory`, `story_progress`, `tower_progress`, `arena_profile`, `guild_membership`, `live_event_state`, `server_actors_bots` → **migrare a `player_server_profiles`** con backfill su `server_id='s1'` default.
- `currencies` → **split** soft (server-bound: gold, server_tokens) vs hard (account-global: gems).
- `chat_messages` → **collection separata** server-scoped via channel_key prefix `{server_id}:` (v109).
- `battle_pass`, `gacha_history`, `shop_purchases` → **design decision** pending.
