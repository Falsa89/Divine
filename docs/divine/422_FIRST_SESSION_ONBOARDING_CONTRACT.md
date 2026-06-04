# 422 — First Session Onboarding Contract

**Pack:** `MEGA_RELEASE_ACCELERATION_19_v70`

## File
- `data/design/onboarding/first_session_onboarding_contract_v1.json`
- `data/design/onboarding/first_session_preview_flow_v1.json`
- `data/design/onboarding/first_session_onboarding_forbidden_scope_v1.json`

## Pattern
- `first_session_preview_only = true`, `permanent_onboarding_complete = false`.
- `account_flag_writes = false`, `tutorial_completion_persistence = false`, `async_storage_persistence = false`.
- `forced_public_routing = false`, `manual_approval_required = true`.

## Step
1. welcome
2. training_combat_onboarding_preview
3. story_alpha_slice_preview
4. event_arena_gate_or_alpha_preview
5. hero_asset_status_explainer
6. next_steps_summary

Tutti i passi sono preview-only. I link sono deeplink-only verso schermate preview esistenti.
