# 432 — MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_ALPHA_QA_v71

**Pack:** `MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_AND_ALPHA_INTERNAL_QA_SUPER_PACK_v71`
**Tag:** `PUBLIC_SYNC_TAG_v71_MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_ALPHA_QA`

## Riepilogo
v71 accorpa due lane (stesso pattern preview/design/read-only):
1. **First Session Onboarding Hardening + Menu Preview Gate** — patch hardening sullo screen onboarding esistente (banner, hardening panel, state machine labels, complete-onboarding disabled indicator) + design del menu preview gate e safe hub route map + nuovo screen deeplink-only `alpha-preview-hub.tsx`.
2. **Alpha Internal QA Execution** — plan, device matrix, severity matrix, evidence template + runner read-only `alpha_internal_qa_readiness_runner_v1.py`.

**Esclusione:** `hero_asset_staging_import_and_resolver_super_pack` resta deferred/gated finché l'utente non fornisce il pack asset reale.

## Track A-G
- **A**: 3 JSON onboarding hardening (contract + state machine + forbidden scope).
- **B**: patch hardening su `first-session-onboarding-preview.tsx`.
- **C**: 3 JSON navigation (menu gate contract + safe route map + forbidden scope).
- **D**: nuovo screen `alpha-preview-hub.tsx` deeplink-only.
- **E**: 4 JSON QA design + runner read-only.
- **F**: QA matrix v1 (24 casi) + progress report v15.
- **G**: 6 docs (427-432), 6 markers, 6 validator Python, 6 tuple OPTIONAL nel master suite, public_sync_tag.

## Invarianti
MD5 invariants ufficiali e extra unchanged guardrails intatti.

## Verdict atteso
`MEGA_RELEASE_ACCELERATION_20_ONBOARDING_MENU_GATE_AND_ALPHA_INTERNAL_QA_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

## Next recommended v72
- `alpha_internal_qa_run_and_bugfix_batch`
- `hero_asset_staging_import_and_resolver_super_pack` (solo dopo asset pack reale)
- `menu_public_exposure_design_after_QA`
