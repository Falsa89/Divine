# 97 — Server Actors / Bot Lifecycle

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Core rules

- `is_bot = true` (internal)
- `synthetic_server_actor = true`
- `created_by_system = true`
- Alias prefix `sa_` (distinguibile per admin)
- No real IAP, no real PII
- **Public facing indistinguishable**: i player non vedono che sono bot (immersione).
- **Admin distinguishable**: l'admin panel mostra il flag.

## Start state

- `account_level = 1`
- `gold = 0`, `gems = 0`, `stamina = 100`
- `team_formation = []`
- **No day-one high-level bots forbidden**.

## Progression rules

### Server age based
- Daily level gain baseline: 1
- Daily level gain active: 2
- Max level cap formula: `min(player_avg_level + 5, server_age_days * 1.5, hard_cap=60 [internal alpha])`

### Player average adaptation
- Enabled
- Sample window: 7 giorni
- Min sample size: 10 player reali
- Fallback se under-sampled: server_age_only

### Caps
- By server age
- By player percentile (p95 max)
- **Never dominates top 10**

## Archetypes (5)

| ID | Label | Daily Login | Activity (min) | Pull/wk | Premium Pull/wk | Event | Chat | Power Band Max |
|----|-------|-------------|----------------|---------|------------------|-------|------|----------------|
| f2p_base | F2P Base | 50% | 15 | 5 | 0 | low | 5% | p40 |
| f2p_active | F2P Active | 95% | 60 | 20 | 2 | medium | 15% | p70 |
| advanced_pull_bot | Advanced Pull | 85% | 90 | 35 | 8 | high | 20% | p80 |
| spender_like_controlled | Spender-like | 90% | 75 | 50 | 25 | high | 18% | p90 |
| whale_like_limited | Whale-like | 95% | 120 | 80 | 50 | very_high | 12% | p95 |

### Whale-like caps
- Max 3 bot per server
- `cap_top_3_forbidden = true`
- `no_real_iap = true`

### Global caps
- `never_dominate_top_3 = true`
- `never_steal_premium_rewards = true`
- Max total bots: 30% of player count
- Max bots per guild: 4
- Max bots in top 10 leaderboard: 20%

## Event access

- Respect level unlock
- Respect event unlock
- Respect guild membership/requirements
- **No bypass**

## Forbidden

- day_one_level_100_bots
- random_runtime_generation
- ranking_domination
- premium_reward_theft
- economy_exploit
- real_iap
- real_pii
- event_access_bypass

## Persistence runtime

**DESIGN_CONTRACT_ONLY_V97**.

DB writes per bot accounts persistenti: **DEFERRED_TO_V98** (controlled rollout gated).

## Verdict

`SERVER_ACTOR_LIFECYCLE_POLICY_READY_RUNTIME_DEFERRED_TO_V98`
