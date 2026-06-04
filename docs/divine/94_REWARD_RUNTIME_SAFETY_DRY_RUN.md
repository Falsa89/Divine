# 94 — Reward Runtime Safety / Dry-Run (v94)

## Pack
`MEGA_RELEASE_ACCELERATION_43_v94`

## Decision
`dry_run_only=true`, `canary_design_no_apply=true`, `live_grant=false`. Nessun reward live in v94.

## Reward types coperti (7)
- story_reward
- tower_reward
- arena_reward + MMR
- raid_boss_reward (boss fragment grant: false)
- guild_reward + guild_score (guild_score_mutation: 0)
- event_currency (event_currency_live: false)
- live_announcement_triggered (no_reward_policy: true)

## Global guards
- idempotency_key_required: `{user_alias}::{reward_type}::{source_id}::{epoch_day}`
- replay_window_seconds: 86400
- negative_inventory_guard: true
- no_duplicate_grant: true
- canary_allowlist_only: true (canary list: [`qa_alias_canary_001`])
- dry_run_only: true

## Rollback
- Strategy: two_phase_reservation (phase 1 reserve + validate; phase 2 apply NOT_APPLIED_IN_v94)
- Trigger: `if_any_live_grant_detected_in_validator_or_simulator`
- Action: revert contract + report blocker

## Dry-run simulator
File: `backend/scripts/simulate_v94_reward_score_runtime_dry_run.py`

Test cases:
- story_victory_reward (PASS dry-run)
- tower_floor_reward (PASS)
- arena_win_loss_mmr (PASS, no_mmr_apply)
- raid_boss_contribution (PASS, no_fragment_grant)
- guild_war_score (PASS, no_score_mutation)
- event_currency (PASS, no_currency_grant)
- duplicate_claim_replay (REJECT, idempotent receipt returned)
- malformed_claim (REJECT, error MALFORMED_REWARD_CLAIM)
- over_cap_claim (REJECT, error REWARD_CAP_EXCEEDED)
- unauthorized_claim (REJECT, error REWARD_UNAUTHORIZED)

Output: `data/design/reward_runtime/v94_reward_score_dry_run_result_v1.json`

## Safety
- db_writes=0
- reward_live=false
- ranking_live=false
- guild_score_mutation=0
- event_currency_live=false
