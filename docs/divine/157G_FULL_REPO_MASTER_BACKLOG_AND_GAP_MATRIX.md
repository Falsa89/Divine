# 157G — Master Fix Backlog & Feature Completeness Gap Matrix (Track G)

Verdetto: `TRACK_G_MASTER_FIX_BACKLOG_AND_BATCHING_PLAN_READY`
File backlog: `data/design/audit/full_repo/master_fix_backlog_and_batching_plan_v1.json`
File gap matrix: `data/design/audit/full_repo/feature_completeness_gap_matrix_v1.json`

## Master backlog
- 34 pack pianificati
- P0: 3 (gacha lock, artifact lock, soul-forge audit)
- P1: 6 (shop IAP, BP modernization, heroes legacy, menu hardening, server profiles inert, IAP design, ...)
- P2: 13
- P3: 13

## Sequenza raccomandata (TOP 12)
1. PROJECT_GACHA_RATE_SANITY_FIX_OR_LOCK_PACK
2. PROJECT_ARTIFACT_CONSTELLATION_SURFACE_LOCK_PACK
3. PROJECT_SOUL_FORGE_PERMANENT_DESTRUCTION_AUDIT_PACK
4. PROJECT_MENU_DEV_ROUTE_HARDENING_PACK
5. PROJECT_HERO_LIST_LEGACY_OWNED_VISIBILITY_FIX_PACK
6. PROJECT_IAP_DESIGN_PACK
7. PROJECT_SHOP_IAP_DESIGN_AND_SAFE_SHOP_LOCK_PACK
8. PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION_PACK
9. PROJECT_VIP_DESIGN_PACK
10. PROJECT_EXCLUSIVE_ITEMS_ROLE_CLASSIFICATION_PACK
11. PROJECT_SERVER_PROFILES_PREVIEW_ENDPOINT_INERT_IMPLEMENTATION_PACK
12. PROJECT_FRONTEND_D_COMBAT_UI_DECOMPOSITION_AUDIT_PACK

## Batching proposal
- BATCH_1_LOCK_DANGEROUS: gacha + artifact + soul-forge + menu hardening
- BATCH_2_MONETIZATION_DESIGN: IAP + shop + BP + VIP
- BATCH_3_DATA_CLEANUP: heroes legacy + exclusive items role
- BATCH_4_PREVIEW_ROLLOUT: server profiles + status + housing
- BATCH_5_REFACTOR: combat UI + equipment schema

## Feature Completeness Gap Matrix
50 feature catalogate con stato/route/endpoint/risk/missing_parts/decision_needed/priority.
Stati: PRESENT_LIVE(18), PRESENT_LOCKED_PREVIEW(3), PRESENT_BACKEND_ONLY(1), PRESENT_FRONTEND_ONLY(1), PRESENT_LEGACY(5), PRESENT_DEV_ONLY(1), PARTIAL(8), MISSING(8), DEFERRED_BY_DESIGN(2), NEEDS_DECISION(2).
