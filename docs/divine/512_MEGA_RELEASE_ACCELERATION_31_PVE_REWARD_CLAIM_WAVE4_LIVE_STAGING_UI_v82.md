# 512 — MEGA_RELEASE_ACCELERATION_31 PvE Reward Claim Wave-4 + Live-Staging Design + UI Hardening (v82)

## Verdetto
`MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_DESIGN_AND_UI_HARDENING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Stato
- `wave4_local_apply = applied_local_staging` (8/8 utenti)
- `wave4_observation = pass` (8/8 criteria)
- `wave4_rollback_drill = pass` (2 sample tx, policy `sample_two_canary_tx`)
- `wave4_negative_tests = pass` (7/7 incluso event_arena_ranking_reward_reject)
- `live_db_readiness_design_gate = design_only_no_apply`
- `reward_claim_ui_summary_hardened = ready_v82`
- `applied_to_live = false`, `db_writes = 0`, `local_file_writes = 6`
- `live_reward_grant = false`, `production_ui_exposure = false`
- Tag: `PUBLIC_SYNC_TAG_v82_MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_UI`

## Track summary
- **A** — Wave4 scope lock + plan + live-staging boundary + forbidden scope (4 JSON + marker)
- **B** — 3 staging file wave4 (8 alias, 8 route fixtures, 8 plan) + manifest + marker
- **C** — Runner v1 esteso con 4 nuovi CLI wave4 + FORBIDDEN_REWARD_KEYS_WAVE4 + VALID_WAVE4_ROUTES
- **D** — Wave4 apply 8/8 + 7 negative tests + ledger snapshot + replay tests
- **E** — Observation pass + rollback drill (2 tx) + live-DB readiness design gate (design-only)
- **F** — TSX hardening (status chips, snapshot section, labels DB_WRITES_0/LOCAL_FILE_ONLY, emphasis styles) + alpha-menu refresh + static data + result JSON
- **G** — QA matrix 24 PASS + progress v26 + readiness v82→v83 + docs 506–512 + markers + 7 validators + suite

## Approval checksum
`468cac7a8894ae81867f6e4c1f81ec3e9b458c9c4a4221668a68f486ea9b4d58`

## Next recommended v83
`pve_reward_claim_live_db_design_contract_v83`

Alternative: `pve_reward_claim_canary_wave5_or_live_staging_db_contract_v83`, `pve_reward_claim_canary_wave4_fix_v83` (se regressione).
