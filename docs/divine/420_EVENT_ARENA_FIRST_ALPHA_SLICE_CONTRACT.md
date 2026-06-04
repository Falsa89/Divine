# 420 — Event/Arena First Alpha Slice Contract

**Pack:** `MEGA_RELEASE_ACCELERATION_19_v70`

## Scopo
Far evolvere Event/Arena dalla fase di gate-only a una prima alpha slice giocabile preview, non autoritativa.

## File
- `data/design/modes/event_arena_first_alpha_slice_contract_v1.json`
- `data/design/modes/event_first_alpha_slice_contract_v1.json`
- `data/design/modes/arena_first_alpha_slice_contract_v1.json`
- `data/design/modes/event_arena_first_alpha_forbidden_scope_v1.json`

## Event first alpha
- `single_test_event_preview = true`, `event_id = event_alpha_test_001`.
- 7 step timeline deterministica.
- Result preview `event_clear_preview` senza reward / event currency / permanent progress.

## Arena first alpha
- `bot_non_ranked_preview = true`, `arena_match_id = arena_alpha_bot_001`, opponent `bot_preview`, bracket `unranked_alpha`.
- 6 step timeline deterministica.
- Result preview senza reward / ranking / MMR / leaderboard.

## Guardrail
`db_writes=0`, `reward_grant_enabled=false`, `event_currency_enabled=false`, `arena_ranking_enabled=false`, `leaderboard_writes=false`, `matchmaking_live=false`, `public_pvp_enabled=false`, `manual_approval_required=true`.
