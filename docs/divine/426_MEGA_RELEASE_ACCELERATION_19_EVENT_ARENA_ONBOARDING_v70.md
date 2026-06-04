# 426 — MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_ONBOARDING_v70

**Pack:** `MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING_SUPER_PACK_v70`
**Tag:** `PUBLIC_SYNC_TAG_v70_MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING`

## Riepilogo
v70 accorpa due lane (stesso pattern preview/deeplink-only, stessi guardrail):
1. **Event/Arena First Alpha Slice preview** — nuovo screen deeplink-only con switch Event/Arena, timeline 6-7 step, result preview disabled.
2. **First Session Onboarding preview** — nuovo screen deeplink-only con 6 step (welcome -> training -> story -> event/arena -> asset explainer -> next steps).

**Esclusione:** `hero_asset_staging_import_and_resolver_super_pack` resta deferred/gated finché l'utente non fornisce il pack asset reale.

## Track A-G
- **A**: 4 JSON contract Event/Arena first alpha.
- **B**: nuovo screen `event-arena-first-alpha-slice-preview.tsx`.
- **C**: 3 JSON contract First Session Onboarding.
- **D**: nuovo screen `first-session-onboarding-preview.tsx`.
- **E**: 3 JSON shared navigation boundary + deferred asset gate.
- **F**: QA matrix v1 (23 casi) + progress report v14.
- **G**: 7 docs (420-426), 7 markers, 7 validator Python, 7 tuple OPTIONAL nel master suite, public_sync_tag.

## Invarianti
MD5 invariants ufficiali e extra unchanged guardrails intatti.

## Verdict atteso
`MEGA_RELEASE_ACCELERATION_19_EVENT_ARENA_FIRST_ALPHA_AND_FIRST_SESSION_ONBOARDING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Next recommended v71
- `first_session_onboarding_hardening_or_menu_preview_gate`
- `hero_asset_staging_import_and_resolver_super_pack` (solo dopo asset pack reale)
- `alpha_internal_qa_execution_super_pack`
