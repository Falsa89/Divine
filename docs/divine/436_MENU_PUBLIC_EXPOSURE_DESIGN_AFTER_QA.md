# 436 — Menu Public Exposure Design after QA

**Pack:** `MEGA_RELEASE_ACCELERATION_21_v72`

## File
- `data/design/navigation/menu_public_exposure_design_after_qa_v1.json`
- `data/design/navigation/menu_public_exposure_gate_matrix_v1.json`
- `data/design/navigation/menu_public_exposure_forbidden_scope_v1.json`

## Pattern
- `design_only=true`, `public_menu_exposure_enabled=false`, `home_menu_routing_enabled=false`, `production_navigation_changed=false`.
- `manual_approval_required=true`, `qa_pass_required=true`, `zero_p0_required=true`, `zero_p1_required=true`.
- Asset pack non richiesto per preview exposure ma richiesto per production exposure.

## Gate matrix
8 gates: qa_pass (PASS), zero_p0_open (PASS), zero_p1_open (PASS), guardrail_assertions_pass (PASS), md5_invariants_intact (PASS), manual_approval (NOT SATISFIED), closed_alpha_testing_complete (NOT SATISFIED), asset_pack_for_production_exposure (NOT SATISFIED).
- `overall_ready_for_public_exposure=false`.

## Candidate menu sections (future, non attivi)
Training preview, Story alpha preview, Event/Arena alpha preview, Alpha Preview Hub.

## Forbidden before approval
public_tabs_route, home_cta_route, mandatory_onboarding_route, account_completion_flag, reward_progress_persistence, production_release_exposure.
