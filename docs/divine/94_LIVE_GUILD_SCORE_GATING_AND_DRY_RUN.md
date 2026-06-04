# 94 — Live/Guild Score Gating and Dry-Run (v94)

## Pack
`MEGA_RELEASE_ACCELERATION_43_v94`

## Gating
`score_live=false`, `ranking_live=false`, `guild_score_mutation=0`, `event_currency_live=false`, `dry_run_only=true`.

## Gated systems (8)
- guild_war_score
- guild_raid_contribution
- server_boss_contribution
- faction_boss_contribution
- territory_front_score
- live_event_kill_score
- live_event_kill_streak_score
- global_ranking_update

Ogni sistema: `dry_run_only=true`, `canary_required=true`, `canary_enabled=false`, `db_writes=0`.

## Ranking update policy
`blocked_unless_canary_flag_explicitly_enabled`. Canary flag state in v94: **DISABLED**.

## Safety
- db_writes=0
- reward_live=false
- ranking_live=false
- guild_score_mutation=0
- event_currency_live=false
- score_live=false
