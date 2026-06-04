# 415 — Event + Arena Alpha Gate Design

**Pack:** `MEGA_RELEASE_ACCELERATION_18_v69`

## File
- `data/design/modes/event_arena_alpha_gate_contract_v1.json`
- `data/design/modes/event_alpha_gate_design_v1.json`
- `data/design/modes/arena_alpha_gate_design_v1.json`
- `data/design/modes/event_arena_forbidden_scope_v1.json`

## Gate Event
event_design_contract_signed, event_currency_design_locked, event_reward_table_design_locked, event_idempotency_design_locked, event_rollback_design_locked, event_observation_plan_signed, event_anti_abuse_design_locked, manual_approval_pre_live.

## Gate Arena
arena_design_contract_signed, arena_ranking_design_locked, arena_mmr_design_locked, arena_match_idempotency_design_locked, arena_rollback_design_locked, arena_observation_plan_signed, arena_anti_abuse_design_locked, manual_approval_pre_live.

## Vincoli
`db_writes=0`, `reward_grant_enabled=false`, `event_currency_enabled=false`, `arena_ranking_enabled=false`, `leaderboard_writes=false`, `matchmaking_live=false`, `public_pvp_enabled=false`, manual approval obbligatoria pre-live.
