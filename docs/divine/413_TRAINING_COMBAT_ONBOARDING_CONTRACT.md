# 413 — Training + Combat Onboarding Contract

**Pack:** `MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS_SUPER_PACK_v69`

## Scopo
Definisce il contratto di onboarding per Training + Combat Basics in modalita' preview locale, deeplink-only, non autoritativa.

## File
- `data/design/onboarding/training_combat_onboarding_contract_v1.json`
- `data/design/onboarding/combat_basics_tutorial_flow_v1.json`
- `data/design/onboarding/training_preview_forbidden_scope_v1.json`

## Pattern
- `onboarding_preview = true`, `authoritative_runtime = false`
- `backend_used = false`, `battle_engine_runtime_used = false`
- `db_writes = 0`, `reward_grant_enabled = false`, `permanent_progress_enabled = false`
- `result_authoritative = false`, `local_preview_adapter = true`

## Insegna
team positioning, attack order, skill preview, result preview, reward preview disabled, progress preview disabled, preview vs real battle.
