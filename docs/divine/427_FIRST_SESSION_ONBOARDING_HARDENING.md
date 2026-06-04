# 427 — First Session Onboarding Hardening

**Pack:** `MEGA_RELEASE_ACCELERATION_20_v71`

## File
- `data/design/onboarding/first_session_onboarding_hardening_contract_v1.json`
- `data/design/onboarding/first_session_onboarding_state_machine_preview_v1.json`
- `data/design/onboarding/first_session_onboarding_hardening_forbidden_scope_v1.json`
- Screen patchato: `frontend/app/first-session-onboarding-preview.tsx`.

## Hardening
- Aggiunto banner aggiornato `DEEPLINK-ONLY - HARDENED v71`.
- Aggiunto **Hardening Panel** con: `account_mutation=false`, `async_storage_persistence=false`, `permanent_onboarding_complete=false`, `db_writes=0`, `reward_grant_enabled=false`, `state_machine=preview_only_local`.
- Aggiunta state machine label per ogni step (intro, training_preview, story_alpha_preview, event_arena_preview, asset_status_explainer, qa_ready_summary).
- Indicatore disabilitato "Completa onboarding (DISABILITATO - preview, nessuna scrittura)".
- Nessuna API/auth/DB toccata.
