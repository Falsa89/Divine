#!/usr/bin/env python3
"""
RM1.31-B — Hero Skill Kit Validator Suite Runner
─────────────────────────────────────────────────────────────────────────
Single command to run all Hero Skill Kit / Divine Weapon / Status-resolver
validators sequentially. Read-only orchestrator. NO catalog/DB/runtime
writes.

Exit 0 only if every REQUIRED validator passes; exit 1 if any fails.
Optional validators that are missing are reported and do not fail the
suite unless they are listed as required.

V17 SUITE SUPERSEDENCE CLEANUP METADATA (non-functional, doc only):
  Buckets (see /app/data/design/system_safety/validator_suite_supersedence_cleanup_report_v1.json
  and /app/docs/divine/VALIDATOR_SUITE_SUPERSEDENCE_POST_AF2N.md):
    1) ACTIVE_REQUIRED  — core 5-star/6-star/divine-weapon/balance
    2) ACTIVE_OPTIONAL  — contextual + V13/V14/V15/V16/V17 V16-aware
    3) SUPERSEDED_PRE_AF2N         — auto-marked when AFFINITY_GIFT_RUNTIME_ENABLED == truthy
    4) SUPERSEDED_PRE_INV_WRITES   — auto-marked when AFFINITY_GIFT_INVENTORY_WRITES_ENABLED == truthy
    5) HISTORICAL_MANUAL — apply/seed/rollback scripts; never run by suite
  No ACTIVE_REQUIRED validator removed or weakened. Historical scripts kept on disk.

Usage:
    python3 run_hero_skill_kit_validator_suite.py
    python3 run_hero_skill_kit_validator_suite.py --json-out /tmp/suite.json
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path('/app/backend/scripts')
SAFE_REPORT_DIRS = (Path('/app/backend/reports'), Path('/tmp'))

REQUIRED = [
    ('RM1.28-A', 'validate_5star_passive_advanced_source.py'),
    ('RM1.28-B', 'audit_5star_skill_kits_crosslinks.py'),
    ('RM1.28-C', 'audit_5star_legacy_status_tags.py'),
    ('RM1.28-D', 'validate_5star_legacy_status_tags_normalized.py'),
    ('RM1.28-E', 'validate_5star_manual_review_residuals_resolved.py'),
    ('RM1.29',   'audit_6star_skill_kits_crosslinks.py'),
    ('RM1.30-A', 'validate_6star_catalog_safety_metadata.py'),
    ('RM1.30-B', 'audit_6star_effect_tags_taxonomy.py'),
    ('RM1.30-C', 'audit_hero_skill_kit_catalog_consolidation.py'),
    ('RM1.27-A', 'validate_divine_weapon_catalog.py'),
    ('RM1.27-D', 'audit_divine_weapon_crosslinks.py'),
    ('RM1.32-A', 'validate_5star_balance_foundation.py'),
    ('RM1.32-B', 'validate_6star_balance_foundation.py'),
    ('RM1.32-C2', 'validate_foundation_numeric_trim_rm132c2.py'),
    # PROJECT_K Track C — 5 RC validators PROMOTED to REQUIRED (authorized by Pack K Track C).
    # Promotion is safe: these 5 validators assert structural invariants of
    # status_first_slice_resolver_pure (purity, no tick-loop touch, caps respect,
    # symmetric PvP fairness, rollback runbook). They are independent from any
    # battle wiring and remain stable whether wiring is applied or not.
    # required_diff_guard_status: BREACH_APPROVED_BY_PACK_K_TRACK_C_PROMPT_AUTHORIZED.
    ('PROJECT-J-RC-1-RESOLVER-PURE-DETERMINISTIC', 'validate_project_j_status_first_slice_resolver_pure_deterministic_v1.py'),
    ('PROJECT-J-RC-2-NO-TICK-LOOP-TOUCH', 'validate_project_j_status_first_slice_no_tick_loop_touch_v1.py'),
    ('PROJECT-J-RC-3-CAPS-RESPECT', 'validate_project_j_status_first_slice_caps_respect_v1.py'),
    ('PROJECT-J-RC-4-PVP-FAIRNESS-AUDIT', 'validate_project_j_status_first_slice_pvp_fairness_audit_v1.py'),
    ('PROJECT-J-RC-5-ROLLBACK-RUNBOOK', 'validate_project_j_status_first_slice_rollback_runbook_v1.py'),
]
OPTIONAL = [
    ('RM1.31-C', 'validate_status_resolver_contract.py'),
    ('RM1.32-C', 'audit_balance_foundation_boss_pvp_caps.py'),
    ('RM1.33-A', 'audit_skill_kit_runtime_adapter_safety.py'),
    ('RM1.33-B', 'audit_skill_kit_runtime_adapter_wiretest.py'),
    ('RM1.33-C', 'audit_skill_kit_runtime_debug_endpoint_safety.py'),
    ('RM1.33-D', 'validate_runtime_debug_snapshot_contract.py'),
    ('RM1.33-E', 'audit_skill_kit_runtime_debug_coverage_safety.py'),
    ('RM1.33-F', 'validate_runtime_debug_6star_ultimate_snapshots.py'),
    ('RM1.33-G', 'validate_runtime_debug_5star_snapshot_rejections.py'),
    ('RM1.34', 'validate_boss_family_resistance_table.py'),
    ('RM1.34-B', 'validate_boss_element_faction_matrix.py'),
    ('RM1.34-C', 'validate_boss_enrage_phase_policy_table.py'),
    ('RM1.34-D', 'audit_boss_policy_cross_table_consistency.py'),
    ('RM1.34-E', 'validate_boss_policy_scenario_fixture_seed.py'),
    ('RM1.33-H', 'validate_divine_weapon_preview_catalog_only_fixture.py'),
    ('CS2-A', 'audit_collection_synergies_v2_readiness.py'),
    ('AF2-A', 'audit_affinity_phase2_gift_catalog_readiness.py'),
    ('CS2/AF2-COMBO', 'validate_collection_affinity_readiness_combo.py'),
    ('CS2-B', 'audit_collection_synergy_preview_resolver_safety.py'),
    ('AF2-B', 'validate_affinity_phase2_economy_cap_policy.py'),
    ('AXIS-A', 'audit_canonical_faction_element_axes.py'),
    ('UI-PREVIEW-A', 'audit_collection_affinity_ui_preview_safety.py'),
    ('STACK-A', 'audit_cross_system_progression_stack_safety.py'),
    ('MEGA-COMBO', 'validate_collection_affinity_axis_stack_combo.py'),
    ('CS2-C', 'audit_collection_synergy_ui_preview_contract.py'),
    ('AF2-C', 'validate_affinity_gift_inventory_schema.py'),
    ('STACK-B', 'audit_global_modifier_cap_resolver_safety.py'),
    ('AXIS-B', 'audit_canonical_axis_alias_helper_safety.py'),
    ('MEGA-COMBO-2', 'validate_cs2c_af2c_stackb_axisb_combo.py'),
    ('CS2-D', 'audit_collection_synergy_preview_ui_stub.py'),
    ('AF2-D', 'validate_affinity_phase2_migration_plan_draft.py'),
    ('AF2-E', 'audit_affinity_gifts_readonly_endpoint_safety.py'),
    ('STACK-C', 'validate_global_modifier_cap_resolver_edge_cases.py'),
    ('AXIS-C', 'audit_canonical_axis_dynamic_preview.py'),
    ('MEGA-COMBO-3', 'validate_cs2d_af2d_af2e_stackc_axisc_combo.py'),
    ('CS2-E', 'audit_collection_synergy_preview_navigation.py'),
    ('AF2-F', 'validate_affinity_phase2_rollback_rehearsal.py'),
    ('AF2-G', 'audit_affinity_gift_spend_skeleton_safety.py'),
    ('STACK-D', 'validate_global_modifier_cap_resolver_multiplicative_rejection.py'),
    ('AXIS-D', 'validate_canonical_axis_activation_table.py'),
    ('MEGA-COMBO-4', 'validate_cs2e_af2f_af2g_stackd_axisd_combo.py'),
    # ULTRA-COMBO (AF2-H + STACK-E + STACK-F + AXIS-E + SAFETY-ROLLUP-A
    #              + OPS-A + PATCH-READINESS-A)
    ('AF2-H', 'audit_affinity_gift_spend_auth_ratelimit_safety.py'),
    ('STACK-E', 'validate_global_modifier_cap_resolver_borea_filtering.py'),
    ('STACK-F', 'validate_global_modifier_cap_resolver_debuff_semantics.py'),
    ('AXIS-E', 'audit_canonical_axis_read_through_helper.py'),
    ('SAFETY-ROLLUP-A', 'validate_runtime_activation_readiness_rollup.py'),
    ('OPS-A', 'audit_start_expo_wrapper_resilience.py'),
    ('PATCH-READINESS-A', 'validate_rm134b_patch_readiness_plan.py'),
    ('ULTRA-COMBO', 'validate_ultra_combo_af2h_stackef_axise_safety_ops_patchreadiness.py'),
    # ULTRA-COMBO v6 (AF2-I + RM1.34-B-PATCH-A + RM1.34-B-PATCH-B
    #                 + AXIS-V6 + BASELINE-V6)
    ('AF2-I', 'audit_affinity_gift_spend_auth_ratelimit_contract.py'),
    ('RM1.34-B-PATCH-A', 'validate_rm134b_patch_a_darkness_to_dark.py'),
    ('RM1.34-B-PATCH-B', 'validate_rm134b_patch_b_tides_decision.py'),
    ('AXIS-V6', 'audit_axis_post_patch_alignment_v6.py'),
    ('BASELINE-V6', 'validate_rm134b_axis_patch_baseline_v6.py'),
    ('ULTRA-COMBO-V6', 'validate_af2i_rm134b_axispatch_v6_combo.py'),
    # ULTRA-COMBO V7 (AF2-J + AF2-K-PRE + AXIS-F + OPS-B + SAFETY-ROLLUP-B
    #                 + AF2-L-PRE)
    ('AF2-J', 'audit_affinity_gift_spend_auth_ratelimit_middleware_contract.py'),
    ('AF2-K-PRE', 'validate_affinity_gift_spend_idempotency_ledger_contract.py'),
    ('AXIS-F', 'audit_affinity_gifts_axis_readonly_routes.py'),
    ('OPS-B', 'audit_ops_start_expo_persistence.py'),
    ('SAFETY-ROLLUP-B', 'validate_collection_affinity_runtime_activation_rollup_v2.py'),
    ('AF2-L-PRE', 'validate_affinity_gift_spend_load_test_and_rollback_rehearsal_plan.py'),
    ('ULTRA-COMBO-V7', 'validate_af2j_af2kpre_axisf_opsb_rollupb_combo.py'),
    # ULTRA-COMBO V8 (AF2-K + AF2-L + AF2-M + OPS-C + SAFETY-ROLLUP-C)
    ('AF2-K', 'validate_affinity_gift_transaction_ledger_migration.py'),
    ('AF2-L', 'validate_affinity_gift_spend_load_and_rollback_results.py'),
    ('AF2-M', 'validate_affinity_gift_runtime_operator_signoff.py'),
    ('OPS-C', 'audit_ops_start_expo_autorestore.py'),
    ('SAFETY-ROLLUP-C', 'validate_collection_affinity_runtime_activation_rollup_v3.py'),
    ('ULTRA-COMBO-V8', 'validate_af2k_af2l_af2m_opsc_safetyc_combo.py'),
    # ULTRA-COMBO V9 (AF2-K-COMMIT + AF2-L-FULL + AF2-M-SIGN-PRE
    #                 + AXIS-G + OPS-C-WIRING + SAFETY-ROLLUP-D)
    ('AF2-K-COMMIT', 'validate_affinity_gift_transaction_ledger_commit_result.py'),
    ('AF2-L-FULL', 'run_affinity_gift_spend_full_disabled_load_probe.py'),
    ('AF2-M-SIGN-PRE', 'validate_affinity_gift_runtime_operator_signoff_v2.py'),
    ('AXIS-G', 'audit_affinity_gifts_combined_axis_routes.py'),
    ('OPS-C-WIRING', 'audit_ops_start_expo_boot_wiring.py'),
    ('SAFETY-ROLLUP-D', 'validate_collection_affinity_runtime_activation_rollup_v4.py'),
    ('ULTRA-COMBO-V9', 'validate_af2k_commit_af2l_full_af2m_signpre_axisg_opsc_wiring_safety_rollup_d_combo.py'),
    # ULTRA-COMBO V10 (AF2-M-SIGN-PRODUCT + AF2-L-K6-PREP/FULL-SAFE
    #                  + OPS-C-SUPERVISOR-WIRING + STACK-G-PRE + SAFETY-ROLLUP-E)
    ('V10-PREFLIGHT', 'validate_ultra_combo_v10_preflight.py'),
    ('AF2-M-SIGN-PRODUCT', 'validate_affinity_gift_product_signoff_v3.py'),
    ('AF2-L-K6-PLAN', 'validate_affinity_gift_spend_k6_locust_test_plan.py'),
    ('AF2-L-K6-PREP', 'validate_affinity_gift_spend_k6_prep_probe.py'),
    ('OPS-C-SUP-WIRING', 'audit_ops_supervisor_startup_wiring.py'),
    ('STACK-G-PRE', 'audit_stack_g_battle_cap_resolver_preconnection.py'),
    ('SAFETY-ROLLUP-E', 'validate_collection_affinity_runtime_activation_rollup_v5.py'),
    ('ULTRA-COMBO-V10', 'validate_ultra_combo_v10_productsign_k6_ops_stackg_rollupe.py'),
    # ULTRA-COMBO V11 (AF2-M-SIGN-ENGINEERING+QA+ECONOMY+ROLLBACK_OWNER
    #                  + AF2-L-K6-LIVE-PREP + OPS-C-SUPERVISOR-APPLY
    #                  + AF2-N-GO-NOGO-PACKAGE + SAFETY-ROLLUP-F)
    ('V11-PREFLIGHT', 'validate_ultra_combo_v11_preflight.py'),
    ('AF2-M-V4-ALL-SIGNOFFS', 'validate_affinity_gift_operator_signoff_v4.py'),
    ('AF2-L-K6-LIVE-PREP', 'validate_affinity_gift_spend_k6_live_prep_result_v2.py'),
    ('OPS-C-SUP-APPLY', 'validate_ops_c_supervisor_apply_result.py'),
    ('AF2-N-GO-NOGO-PRE', 'validate_af2n_go_no_go_preflight_package.py'),
    ('SAFETY-ROLLUP-F', 'validate_collection_affinity_runtime_activation_rollup_v6.py'),
    ('ULTRA-COMBO-V11', 'validate_ultra_combo_v11_all_signoffs_pre_af2n.py'),
    # ULTRA-COMBO V12 (AF2-N CONTROLLED CANARY + MONITORING + ROLLBACK READY + SAFETY-ROLLUP-G)
    ('FINAL-USER-APPROVAL',  'validate_final_user_runtime_approval_record.py'),
    ('AF2-N-CANARY-SMOKE',   'validate_af2n_canary_smoke_monitoring.py'),
    ('AF2-N-ACTIVATION',     'validate_af2n_runtime_activation_result.py'),
    ('SAFETY-ROLLUP-G',      'validate_collection_affinity_runtime_activation_rollup_v7.py'),
    ('ULTRA-COMBO-V12',      'validate_ultra_combo_v12_af2n_canary.py'),
    # ULTRA-COMBO V13 (AF2-N-MONITORING-WINDOW + AF2-N-STAGE1-PREP
    #                  + AF2-N-INVENTORY-WIRING-PRE + AF2-L-K6-LIVE-PREP2
    #                  + SAFETY-ROLLUP-H)
    ('AF2-N-MONITORING-WINDOW',     'validate_af2n_monitoring_window_result.py'),
    ('AF2-N-STAGE1-PREP',           'validate_af2n_stage1_1pct_allowlist_plan.py'),
    ('AF2-N-INVENTORY-WIRING-PRE',  'audit_af2n_inventory_wiring_pre.py'),
    ('AF2-L-K6-LIVE-PREP2',         'validate_affinity_gift_spend_k6_live_prep2_result.py'),
    ('SAFETY-ROLLUP-H',             'validate_collection_affinity_runtime_activation_rollup_v8.py'),
    ('ULTRA-COMBO-V13',             'validate_ultra_combo_v13_monitoring_stage1_prep.py'),
    # ULTRA-COMBO V14 (AF2-N-STAGE1-APPLY + STAGE1-MONITORING
    #                  + INVENTORY-WIRING-SHADOW + K6-PREP3
    #                  + STAGE1-ROLLBACK-READINESS + SAFETY-ROLLUP-I)
    ('V14-PREFLIGHT',                 'validate_af2n_v14_preflight.py'),
    ('AF2-N-STAGE1-APPLY',            'validate_af2n_stage1_1pct_apply_result.py'),
    ('AF2-N-STAGE1-MONITORING',       'validate_af2n_stage1_monitoring_window.py'),
    ('AF2-N-INVENTORY-WIRING-SHADOW', 'validate_affinity_gift_inventory_shadow_wiring.py'),
    ('AF2-L-K6-PREP3-PLAN',           'validate_af2n_stage1_k6_live_test_plan.py'),
    ('AF2-L-K6-PREP3-PROBE',          'validate_af2n_stage1_k6_prep_probe.py'),
    ('AF2-N-STAGE1-ROLLBACK-READY',   'validate_af2n_stage1_rollback_readiness.py'),
    ('SAFETY-ROLLUP-I',               'validate_collection_affinity_runtime_activation_rollup_v9.py'),
    ('ULTRA-COMBO-V14',               'validate_ultra_combo_v14_stage1_inventoryshadow.py'),
    # ULTRA-COMBO V15 (STAGE1 EXTENDED MONITORING + INVENTORY-WIRING ACTIVATE
    #                  STAGE1-ONLY [safe block today] + INVENTORY LIVE MONITORING
    #                  + K6 LIVE INSTALL PREP + SAFETY-ROLLUP-J)
    ('V15-PREFLIGHT',                          'validate_af2n_v15_preflight.py'),
    ('AF2-N-STAGE1-EXTENDED-MONITORING-V15',   'validate_af2n_stage1_extended_monitoring_v15.py'),
    ('AF2-N-INVENTORY-WIRING-APPLY',           'validate_affinity_inventory_wiring_stage1_apply_result.py'),
    ('AF2-N-INVENTORY-LIVE-MONITORING',        'validate_affinity_inventory_live_monitoring_stage1.py'),
    ('AF2-L-K6-V15-FALLBACK',                  'validate_af2n_v15_k6_fallback_probe.py'),
    ('V15-ROLLBACK-READINESS',                 'validate_af2n_v15_rollback_readiness.py'),
    ('SAFETY-ROLLUP-J',                        'validate_collection_affinity_runtime_activation_rollup_v10.py'),
    ('ULTRA-COMBO-V15',                        'validate_ultra_combo_v15_inventory_activate_stage1.py'),
    # ULTRA-COMBO V16 (SCHEMA-MIGRATION-USER-INVENTORY + SEED STAGE1 QA
    #                  + INVENTORY-WIRING ACTIVATE RETRY + LIVE MONITORING
    #                  + SAFETY-ROLLUP-K)
    ('V16-PREFLIGHT',                          'validate_af2n_v16_preflight.py'),
    ('AF2-N-INVENTORY-SCHEMA-MIGRATION',       'validate_user_inventory_affinity_state_schema.py'),
    ('AF2-N-STAGE1-QA-SEED',                   'validate_stage1_qa_gift_inventory_seed.py'),
    ('AF2-N-INVENTORY-RETRY-APPLY',            'validate_affinity_inventory_wiring_stage1_retry_apply_result.py'),
    ('AF2-N-INVENTORY-LIVE-MONITORING-V16',    'validate_affinity_inventory_live_monitoring_v16.py'),
    ('SAFETY-ROLLUP-K',                        'validate_collection_affinity_runtime_activation_rollup_v11.py'),
    ('ULTRA-COMBO-V16',                        'validate_ultra_combo_v16_inventory_schema_seed_activate.py'),
    # ULTRA-COMBO V17 (INVENTORY EXTENDED MONITORING + STAGE2 5-10% EXPANSION
    #                  PREP/APPLY-GATED + SUITE SUPERSEDED CLEANUP
    #                  + K6/LOCUST REAL READINESS + SAFETY-ROLLUP-L)
    ('V17-PREFLIGHT',                              'validate_af2n_v17_preflight.py'),
    ('AF2-N-INVENTORY-EXTENDED-MONITORING-V17',    'validate_af2n_inventory_extended_monitoring_v17.py'),
    ('AF2-N-STAGE2-APPLY',                         'validate_af2n_stage2_5_10pct_apply_result.py'),
    ('AF2-N-STAGE2-MONITORING-V17',                'validate_af2n_stage2_monitoring_v17.py'),
    ('SUITE-SUPERSEDENCE-CLEANUP',                 'validate_validator_suite_supersedence_cleanup.py'),
    ('AF2-L-K6-LOCUST-READINESS-V17',              'validate_af2n_v17_k6_locust_readiness.py'),
    ('V17-ROLLBACK-READINESS',                     'validate_af2n_v17_rollback_readiness.py'),
    ('SAFETY-ROLLUP-L',                            'validate_collection_affinity_runtime_activation_rollup_v12.py'),
    ('ULTRA-COMBO-V17',                            'validate_ultra_combo_v17_stage2_monitoring_cleanup_k6.py'),
    # ULTRA-COMBO V18 (STAGE2 EXTENDED MONITORING + STAGE3 QA EXPANSION
    #                  PREP/APPLY-GATED + PUBLIC UI PREVIEW READINESS
    #                  + K6/LOCUST REAL ATTEMPT SAFE + SAFETY-ROLLUP-M)
    ('V18-PREFLIGHT',                              'validate_af2n_v18_preflight.py'),
    ('AF2-N-STAGE2-EXTENDED-MONITORING-V18',       'validate_af2n_stage2_extended_monitoring_v18.py'),
    ('AF2-N-STAGE3-QA-EXPANSION-APPLY',            'validate_af2n_stage3_qa_expansion_apply_result.py'),
    ('AF2-N-STAGE3-MONITORING-V18',                'validate_af2n_stage3_monitoring_v18.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-SAFETY',             'audit_affinity_gifts_public_preview_safety.py'),
    ('AF2-L-K6-LOCUST-V18',                        'validate_af2n_v18_k6_locust_result.py'),
    ('V18-ROLLBACK-READINESS',                     'validate_af2n_v18_rollback_readiness.py'),
    ('SAFETY-ROLLUP-M',                            'validate_collection_affinity_runtime_activation_rollup_v13.py'),
    ('ULTRA-COMBO-V18',                            'validate_ultra_combo_v18_stage2_stage3_publicpreview.py'),
    # ULTRA-COMBO V19 (STAGE3 EXTENDED MONITORING + LOCUST REAL LOW-IMPACT
    #                  + PUBLIC UI PREVIEW READ-ONLY + BROAD-ROLLOUT PLAN
    #                  + SAFETY-ROLLUP-N)
    ('V19-PREFLIGHT',                              'validate_af2n_v19_preflight.py'),
    ('AF2-N-STAGE3-EXTENDED-MONITORING-V19',       'validate_af2n_stage3_extended_monitoring_v19.py'),
    ('AF2-L-LOCUST-LOW-IMPACT-V19',                'validate_af2n_stage3_locust_low_impact_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-IMPLEMENTATION',     'audit_affinity_gifts_public_preview_implementation.py'),
    ('AF2-N-BROAD-ROLLOUT-READINESS-PLAN',         'validate_af2n_broad_rollout_readiness_plan.py'),
    ('V19-ROLLBACK-READINESS',                     'validate_af2n_v19_rollback_readiness.py'),
    ('SAFETY-ROLLUP-N',                            'validate_collection_affinity_runtime_activation_rollup_v14.py'),
    ('ULTRA-COMBO-V19',                            'validate_ultra_combo_v19_stage3_locust_ui_broadprep.py'),
    # ULTRA-COMBO V20 (STAGE4 INTERNAL BETA PREP PLAN-ONLY + ROLLBACK DRILLS
    #                  + SIGNOFFS V5 + LOCUST EXTENDED LOW-IMPACT
    #                  + PUBLIC UI PREVIEW QA/A11Y AUDIT + SAFETY-ROLLUP-O)
    ('V20-PREFLIGHT',                              'validate_af2n_v20_preflight.py'),
    ('AF2-N-STAGE4-INTERNAL-BETA-PLAN',            'validate_af2n_stage4_internal_beta_plan.py'),
    ('AF2-N-V20-ROLLBACK-DRILLS',                  'validate_af2n_v20_rollback_drill_result.py'),
    ('AF2-N-STAGE4-SIGNOFF-PACKAGE-V5',            'validate_af2n_stage4_signoff_package_v5.py'),
    ('AF2-L-LOCUST-EXTENDED-LOW-IMPACT-V20',       'validate_af2n_v20_locust_extended_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-QA-A11Y-V20',        'audit_affinity_gifts_public_preview_qa_a11y.py'),
    ('SAFETY-ROLLUP-O',                            'validate_collection_affinity_runtime_activation_rollup_v15.py'),
    ('ULTRA-COMBO-V20',                            'validate_ultra_combo_v20_stage4_readiness_drills.py'),
    # ULTRA-COMBO V21 (STAGE4 INTERNAL BETA APPLY-GATED + SIGNOFFS V5 APPLY
    #                  + RATE-LIMIT MIDDLEWARE + DB BACKUP DRILL + STAGE4
    #                  MONITORING + LOCUST + SAFETY-ROLLUP-P)
    ('V21-PREFLIGHT',                              'validate_af2n_v21_preflight.py'),
    ('AF2-N-STAGE4-SIGNOFFS-V5-APPLIED',           'validate_af2n_stage4_signoffs_v5_applied.py'),
    ('AF2-N-V21-RATE-LIMIT-AUDIT',                 'audit_affinity_gift_spend_rate_limit_runtime.py'),
    ('AF2-N-V21-RATE-LIMIT-PROBE',                 'validate_affinity_gift_spend_rate_limit_probe.py'),
    ('AF2-N-V21-DB-BACKUP-DRILL',                  'validate_af2n_stage4_db_backup_drill.py'),
    ('AF2-N-STAGE4-INTERNAL-BETA-APPLY',           'validate_af2n_stage4_internal_beta_apply_result.py'),
    ('AF2-N-V21-STAGE4-MONITORING',                'validate_af2n_stage4_monitoring_v21.py'),
    ('AF2-L-LOCUST-STAGE4-V21',                    'validate_af2n_v21_locust_stage4_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-V21-SAFETY',         'audit_affinity_gifts_public_preview_v21_safety.py'),
    ('V21-ROLLBACK-READINESS',                     'validate_af2n_v21_rollback_readiness.py'),
    ('SAFETY-ROLLUP-P',                            'validate_collection_affinity_runtime_activation_rollup_v16.py'),
    ('ULTRA-COMBO-V21',                            'validate_ultra_combo_v21_stage4_apply_gated.py'),
    # ULTRA-COMBO V22 (STAGE4 EXTENDED MONITORING + REDIS RATE-LIMIT MIGRATION PREP
    #                  + INVENTORY/AFFINITY DELTA AUDIT + LOCUST STAGE4 EXTENDED
    #                  + BROAD-ROLLOUT BLOCKER MATRIX + SAFETY-ROLLUP-Q)
    ('V22-PREFLIGHT',                              'validate_af2n_v22_preflight.py'),
    ('AF2-N-V22-STAGE4-EXTENDED-MONITORING',       'validate_af2n_stage4_extended_monitoring_v22.py'),
    ('AF2-N-V22-REDIS-MIGRATION-PLAN-AUDIT',       'audit_affinity_rate_limit_redis_migration_plan.py'),
    ('AF2-N-V22-REDIS-PROBE',                      'validate_affinity_rate_limit_redis_probe.py'),
    ('AF2-N-V22-DELTA-AUDIT',                      'validate_affinity_inventory_delta_consistency_v22.py'),
    ('AF2-L-LOCUST-STAGE4-V22',                    'validate_af2n_v22_locust_stage4_extended_result.py'),
    ('AF2-N-V22-BROAD-ROLLOUT-BLOCKER-MATRIX',     'validate_af2n_broad_rollout_blocker_matrix.py'),
    ('AF2-N-PUBLIC-UI-V22-SAFETY',                 'audit_affinity_gifts_public_preview_v22_safety.py'),
    ('V22-ROLLBACK-READINESS',                     'validate_af2n_v22_rollback_readiness.py'),
    ('SAFETY-ROLLUP-Q',                            'validate_collection_affinity_runtime_activation_rollup_v17.py'),
    ('ULTRA-COMBO-V22',                            'validate_ultra_combo_v22_stage4_monitoring_redisprep.py'),
    # ULTRA-COMBO V23 (REDIS RATE-LIMIT PROVISION/SWITCH-GATED + STAGE4 OBS
    #                  WINDOW + ABUSE MONITORING PREP + DELTA AUDIT V23
    #                  + LOCUST STAGE4 RATE-LIMIT + SAFETY-ROLLUP-R)
    ('V23-PREFLIGHT',                              'validate_af2n_v23_preflight.py'),
    ('AF2-N-V23-REDIS-LIVE-PROBE',                 'validate_af2n_v23_redis_live_probe.py'),
    ('AF2-N-V23-REDIS-SWITCH',                     'validate_af2n_v23_redis_switch.py'),
    ('AF2-N-V23-STAGE4-OBSERVATION-WINDOW',        'validate_af2n_stage4_observation_window_v23.py'),
    ('AF2-N-V23-ABUSE-MONITORING-PREP',            'validate_af2n_v23_abuse_monitoring_prep.py'),
    ('AF2-N-V23-DELTA-AUDIT',                      'validate_affinity_inventory_delta_consistency_v23.py'),
    ('AF2-L-LOCUST-STAGE4-V23',                    'validate_af2n_v23_locust_stage4_ratelimit.py'),
    ('AF2-N-V23-BLOCKER-MATRIX-V2',                'validate_af2n_broad_rollout_blocker_matrix_v2.py'),
    ('AF2-N-PUBLIC-UI-V23-SAFETY',                 'audit_affinity_gifts_public_preview_v23_safety.py'),
    ('V23-ROLLBACK-READINESS',                     'validate_af2n_v23_rollback_readiness.py'),
    ('SAFETY-ROLLUP-R',                            'validate_collection_affinity_runtime_activation_rollup_v18.py'),
    ('ULTRA-COMBO-V23',                            'validate_ultra_combo_v23_redis_switch_observation.py'),
    # ULTRA-COMBO V24 (REAL OBSERVATION WINDOW + ABUSE METRICS INSTRUMENTATION
    #                  + STAGING ROLLBACK DRILL + REDIS HA PLAN + SAFETY-ROLLUP-S)
    ('V24-PREFLIGHT',                              'validate_af2n_v24_preflight.py'),
    ('AF2-N-V24-OBSERVATION-WINDOW-REAL',          'validate_af2n_v24_observation_window_real.py'),
    ('AF2-N-V24-ABUSE-METRICS-INSTRUMENTATION',    'validate_af2n_v24_abuse_metrics_instrumentation.py'),
    ('AF2-N-V24-STAGING-ROLLBACK-DRILL',           'validate_af2n_v24_staging_rollback_drill.py'),
    ('AF2-N-V24-REDIS-HA-DECISION-PLAN',           'validate_af2n_v24_redis_ha_decision_plan.py'),
    ('AF2-N-V24-SUPPORT-ECONOMY-PREP',             'validate_af2n_v24_support_economy_prep.py'),
    ('AF2-N-V24-BLOCKER-MATRIX-V3',                'validate_af2n_broad_rollout_blocker_matrix_v3.py'),
    ('AF2-N-PUBLIC-UI-V24-SAFETY',                 'audit_affinity_gifts_public_preview_v24_safety.py'),
    ('V24-ROLLBACK-READINESS',                     'validate_af2n_v24_rollback_readiness.py'),
    ('SAFETY-ROLLUP-S',                            'validate_collection_affinity_runtime_activation_rollup_v19.py'),
    ('ULTRA-COMBO-V24',                            'validate_ultra_combo_v24_observation_abuse_rollback_redisHA.py'),
    # ULTRA-COMBO V25 (REDIS OPS HARDENING + FAIL-OPEN ALERTING + SUPPORT
    #                  RUNBOOK + ECONOMY STRESS 10X + BLOCKER MATRIX V4
    #                  + SAFETY-ROLLUP-T)
    ('V25-PREFLIGHT',                              'validate_af2n_v25_preflight.py'),
    ('AF2-N-V25-REDIS-OPS-RECOVERY',               'validate_redis_rate_limit_ops_recovery.py'),
    ('AF2-N-V25-REDIS-RESTART-DRILL',              'validate_redis_rate_limit_restart_drill_v25.py'),
    ('AF2-N-V25-FAIL-OPEN-ALERTING-CONTRACT',      'validate_af2n_fail_open_alerting_contract.py'),
    ('AF2-N-V25-ALERTING-READONLY-STATUS',         'audit_af2n_alerting_readonly_status.py'),
    ('AF2-N-V25-SUPPORT-RUNBOOK',                  'validate_af2n_stage4_support_runbook_v25.py'),
    ('AF2-N-V25-ECONOMY-STRESS-10X',               'validate_af2n_economy_stress_10x_simulation_v25.py'),
    ('AF2-N-V25-BLOCKER-MATRIX-V4',                'validate_af2n_broad_rollout_blocker_matrix_v4.py'),
    ('AF2-N-V25-OBSERVATION-WINDOW',               'validate_af2n_stage4_observation_window_v25.py'),
    ('AF2-N-PUBLIC-UI-V25-SAFETY',                 'audit_affinity_gifts_public_preview_v25_safety.py'),
    ('V25-ROLLBACK-READINESS',                     'validate_af2n_v25_rollback_readiness.py'),
    ('SAFETY-ROLLUP-T',                            'validate_collection_affinity_runtime_activation_rollup_v20.py'),
    ('ULTRA-COMBO-V25',                            'validate_ultra_combo_v25_redis_ops_support_economy.py'),
    # ULTRA-COMBO V26 (MANAGED REDIS READINESS + CAP RAISE PLAN + INVENTORY
    #                  SCOPE EXPANSION + BROAD ROLLOUT SIGNOFF V6 PLAN-ONLY
    #                  + ALERTING INTEGRATION PREP + FRONTEND SMOKE + STRESS 2X
    #                  + SAFETY-ROLLUP-U)
    ('V26-PREFLIGHT',                              'validate_af2n_v26_preflight.py'),
    ('AF2-N-V26-MANAGED-REDIS-READINESS',          'validate_affinity_managed_redis_readiness.py'),
    ('AF2-N-V26-CAP-RAISE-PLAN',                   'validate_af2n_cap_raise_plan.py'),
    ('AF2-N-V26-INVENTORY-SCOPE-PLAN',             'validate_af2n_inventory_scope_expansion_plan.py'),
    ('AF2-N-V26-BROAD-ROLLOUT-SIGNOFF-V6',         'validate_af2n_broad_rollout_signoff_package_v6.py'),
    ('AF2-N-V26-ALERTING-INTEGRATION-PREP',        'audit_af2n_alerting_integration_prep.py'),
    ('AF2-N-V26-FRONTEND-SMOKE',                   'audit_affinity_gifts_frontend_smoke_v26.py'),
    ('AF2-N-V26-STRESS-2X',                        'validate_af2n_stress_2x_v26.py'),
    ('AF2-N-V26-BLOCKER-MATRIX-V5',                'validate_af2n_broad_rollout_blocker_matrix_v5.py'),
    ('AF2-N-V26-OBSERVATION-WINDOW',               'validate_af2n_stage4_observation_window_v26.py'),
    ('V26-ROLLBACK-READINESS',                     'validate_af2n_v26_rollback_readiness.py'),
    ('SAFETY-ROLLUP-U',                            'validate_collection_affinity_runtime_activation_rollup_v21.py'),
    ('ULTRA-COMBO-V26',                            'validate_ultra_combo_v26_broad_readiness_plan.py'),
    # ULTRA-COMBO V27 (MANAGED REDIS GATED + ALERTING LIVE/MOCK + CAP RAISE
    #                  S1 5K->25K GATED + OBSERVATION + STRESS 3X
    #                  + SAFETY-ROLLUP-V)
    ('V27-PREFLIGHT',                              'validate_af2n_v27_preflight.py'),
    ('AF2-N-V27-MANAGED-REDIS-SWITCH',             'validate_managed_redis_switch_v27.py'),
    ('AF2-N-V27-ALERTING-SINK',                    'validate_af2n_alerting_sink_v27.py'),
    ('AF2-N-V27-CAP-RAISE-S1',                     'validate_af2n_cap_raise_s1_v27.py'),
    ('AF2-N-V27-STAGE4-OBSERVATION',               'validate_af2n_stage4_observation_v27.py'),
    ('AF2-N-V27-STRESS-3X',                        'validate_af2n_stress_3x_v27.py'),
    ('AF2-N-V27-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v27.py'),
    ('AF2-N-V27-BLOCKER-MATRIX-V6',                'validate_af2n_broad_rollout_blocker_matrix_v6.py'),
    ('AF2-N-V27-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v27_safety.py'),
    ('V27-ROLLBACK-READINESS',                     'validate_af2n_v27_rollback_readiness.py'),
    ('SAFETY-ROLLUP-V',                            'validate_collection_affinity_runtime_activation_rollup_v22.py'),
    ('ULTRA-COMBO-V27',                            'validate_ultra_combo_v27_managed_redis_cap_s1.py'),
    # ULTRA-COMBO V28 (INVENTORY SCOPE S1 EXPANSION 700->2500 + STRESS 5X
    #                  + MANAGED REDIS PROBE (gated) + ALERTING LIVE PROBE
    #                  + BLOCKER MATRIX V7 + SAFETY-ROLLUP-W)
    ('V28-PREFLIGHT',                              'validate_af2n_v28_preflight.py'),
    ('AF2-N-V28-INVENTORY-SCOPE-S1',               'validate_af2n_inventory_scope_s1_v28.py'),
    ('AF2-N-V28-SCOPE-S1-OBSERVATION',             'validate_af2n_scope_s1_observation_v28.py'),
    ('AF2-N-V28-STRESS-5X',                        'validate_af2n_stress_5x_v28.py'),
    ('AF2-N-V28-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v28.py'),
    ('AF2-N-V28-MANAGED-REDIS-PROBE',              'validate_managed_redis_v28_probe.py'),
    ('AF2-N-V28-ALERTING-LIVE-PROBE',              'validate_alerting_live_v28_probe.py'),
    ('AF2-N-V28-BLOCKER-MATRIX-V7',                'validate_af2n_broad_rollout_blocker_matrix_v7.py'),
    ('AF2-N-V28-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v28_safety.py'),
    ('V28-ROLLBACK-READINESS',                     'validate_af2n_v28_rollback_readiness.py'),
    ('SAFETY-ROLLUP-W',                            'validate_collection_affinity_runtime_activation_rollup_v23.py'),
    ('ULTRA-COMBO-V28',                            'validate_ultra_combo_v28_inventory_scope_stress5x.py'),
    # ULTRA-COMBO V29 (ENV-AWARE MANAGED REDIS/ALERTING + V28 SCHEMA-FIX REGRESSION
    #                  + SCOPE S1 EXTENDED MONITORING + STRESS 8X + SIGNOFF V7 + ROLLUP X)
    ('V29-PREFLIGHT',                              'validate_af2n_v29_preflight.py'),
    ('AF2-N-V29-V28-SCHEMA-FIX-REGRESSION',        'validate_af2n_v28_schema_fix_regression_v29.py'),
    ('AF2-N-V29-MANAGED-REDIS-PROBE',              'validate_managed_redis_envaware_v29.py'),
    ('AF2-N-V29-ALERTING-PROBE',                   'validate_alerting_envaware_v29.py'),
    ('AF2-N-V29-SCOPE-S1-EXTENDED-MONITORING',     'validate_af2n_scope_s1_extended_monitoring_v29.py'),
    ('AF2-N-V29-STRESS-8X',                        'validate_af2n_stress_8x_v29.py'),
    ('AF2-N-V29-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v29.py'),
    ('AF2-N-V29-BROAD-ROLLOUT-SIGNOFF-V7',         'validate_af2n_broad_rollout_signoff_package_v7.py'),
    ('AF2-N-V29-BLOCKER-MATRIX-V8',                'validate_af2n_broad_rollout_blocker_matrix_v8.py'),
    ('AF2-N-V29-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v29_safety.py'),
    ('V29-ROLLBACK-READINESS',                     'validate_af2n_v29_rollback_readiness.py'),
    ('SAFETY-ROLLUP-X',                            'validate_collection_affinity_runtime_activation_rollup_v24.py'),
    ('ULTRA-COMBO-V29',                            'validate_ultra_combo_v29_envaware_readiness_postfix.py'),
    # ULTRA-COMBO V30 (CAP S2 GATED + SOAK + STRESS 10X + OBSERVABILITY + ENV-AWARE PROBES + SIGNOFF V8 + ROLLUP Y)
    ('V30-PREFLIGHT',                              'validate_af2n_v30_preflight.py'),
    ('AF2-N-V30-STAGE4-SOAK',                      'validate_af2n_stage4_soak_v30.py'),
    ('AF2-N-V30-CAP-RAISE-S2',                     'validate_af2n_cap_raise_s2_v30.py'),
    ('AF2-N-V30-STRESS-10X',                       'validate_af2n_stress_10x_v30.py'),
    ('AF2-N-V30-MANAGED-REDIS-PROBE',              'validate_managed_redis_envaware_v30.py'),
    ('AF2-N-V30-ALERTING-PROBE',                   'validate_alerting_envaware_v30.py'),
    ('AF2-N-V30-OBSERVABILITY-DASHBOARD-SPEC',     'validate_af2n_observability_dashboard_spec.py'),
    ('AF2-N-V30-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v30.py'),
    ('AF2-N-V30-BROAD-ROLLOUT-SIGNOFF-V8',         'validate_af2n_broad_rollout_signoff_package_v8.py'),
    ('AF2-N-V30-BLOCKER-MATRIX-V9',                'validate_af2n_broad_rollout_blocker_matrix_v9.py'),
    ('AF2-N-V30-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v30_safety.py'),
    ('V30-ROLLBACK-READINESS',                     'validate_af2n_v30_rollback_readiness.py'),
    ('SAFETY-ROLLUP-Y',                            'validate_collection_affinity_runtime_activation_rollup_v25.py'),
    ('ULTRA-COMBO-V30',                            'validate_ultra_combo_v30_capS2_soak_observability.py'),
    # COSMETIC-SKIN-TITLE-SYSTEM-A (DESIGN-ONLY foundation; no runtime/battle attachment)
    ('COSMETIC-SYSTEM-POLICY-A',                   'validate_cosmetic_system_policy_v1.py'),
    ('COSMETIC-SCHEMAS-A',                         'validate_cosmetic_schemas_v1.py'),
    ('COSMETIC-EXAMPLES-A',                        'validate_cosmetic_examples_v1.py'),
    ('COSMETIC-RUNTIME-SAFETY-A',                  'audit_cosmetic_runtime_safety_v1.py'),
    ('COSMETIC-SKIN-TITLE-COMBO-A',                'validate_cosmetic_skin_title_system_a_combo.py'),
    # SERVER-LIFECYCLE-CALENDAR-A (DESIGN-ONLY / AUDIT-ONLY)
    ('SERVER-SHARD-ISOLATION-AUDIT-A',             'audit_server_shard_isolation_v1.py'),
    ('SERVER-LIFECYCLE-POLICIES-A',                'validate_server_lifecycle_policies_v1.py'),
    ('SERVER-AGE-CALENDAR-A',                      'validate_server_age_calendar_schema_v1.py'),
    ('SERVER-MERGE-RECOVERY-A',                    'validate_server_merge_recovery_policy_v1.py'),
    ('SERVER-SHARD-ISOLATION-SAFETY-A',            'audit_server_shard_isolation_safety_v1.py'),
    ('SERVER-LIFECYCLE-COMBO-A',                   'validate_server_lifecycle_calendar_a_combo.py'),
    # SLC-C SINGLE-SHARD → MULTI-SHARD MIGRATION PLAN (DESIGN-ONLY / DRY-RUN)
    ('SLC-C-ACCOUNT-ENTITY',                       'validate_slc_c_account_entity_schema_v1.py'),
    ('SLC-C-ACCOUNT-WIDE-DOC',                     'validate_slc_c_account_wide_document_contract_v1.py'),
    ('SLC-C-SERVER-BOUND-DOC',                     'validate_slc_c_server_bound_document_contract_v1.py'),
    ('SLC-C-COLLECTION-SCOPE-MATRIX',              'validate_slc_c_collection_scope_migration_matrix_v1.py'),
    ('SLC-C-MULTISHARD-INDEX-PLAN',                'validate_slc_c_multishard_index_plan_v1.py'),
    ('SLC-C-PAID-FREE-SPLIT',                      'validate_slc_c_paid_free_currency_split_plan_v1.py'),
    ('SLC-C-ROUTE-PATCH-CONTRACT',                 'validate_slc_c_server_aware_route_patch_contract_v1.py'),
    ('SLC-C-PROFILE-CREATION-CONTRACT',            'validate_slc_c_server_profile_creation_contract_v1.py'),
    ('SLC-C-MIGRATION-PHASE-PLAN',                 'validate_slc_c_single_to_multishard_migration_phase_plan_v1.py'),
    ('SLC-C-ROLLBACK-PLAN',                        'validate_slc_c_multishard_rollback_plan_v1.py'),
    ('SLC-C-REPO-PREFLIGHT',                       'audit_slc_c_repo_multishard_preflight.py'),
    ('SLC-C-CRITICAL-FILES-NO-DIFF',               'audit_slc_c_critical_files_no_diff.py'),
    ('SLC-C-MIGRATION-DRYRUN',                     'simulate_slc_c_migration_dryrun.py'),
    ('SLC-C-API-SMOKE-READONLY',                   'audit_slc_c_api_smoke_readonly.py'),
    ('SLC-C-COMBO',                                'validate_slc_c_combo_v1.py'),
    # SLC-BE SERVER PROFILE CREATION + SELECTION CONTRACT (DESIGN-ONLY / CONTRACT-ONLY)
    ('SLC-BE-PREFLIGHT',                           'validate_slc_be_preflight_v1.py'),
    ('SLC-B-SERVER-PROFILE-CONTRACT',              'validate_server_profile_creation_contract_v1.py'),
    ('SLC-B-SERVER-PROFILE-DEFAULTS',              'validate_server_profile_default_values_v1.py'),
    ('SLC-E-SERVER-SELECTION-CONTRACT',            'validate_server_selection_endpoint_contract_v1.py'),
    ('SLC-E-SERVER-STATUS-POLICY',                 'validate_server_status_transition_policy_v1.py'),
    ('SLC-E-NEW-PLAYER-ROUTING',                   'validate_new_player_server_routing_policy_v1.py'),
    ('SLC-E-ACTIVE-SERVER-RESOLUTION',             'validate_active_server_resolution_contract_v1.py'),
    ('SLC-BE-DRY-RUN-SCENARIOS',                   'validate_server_profile_creation_dry_run_scenarios_v1.py'),
    ('SLC-BE-RUNTIME-SAFETY-AUDIT',                'audit_server_selection_runtime_safety_v1.py'),
    ('SLC-BE-ROLLUP',                              'validate_server_lifecycle_profile_selection_readiness_rollup_v1.py'),
    ('SLC-BE-COMBO',                               'validate_slc_be_server_profile_selection_combo.py'),
    # LIVE-MODES-RECONCILIATION-A + SLC-NEXT-PREP-A (DESIGN-ONLY / AUDIT-ONLY)
    ('LIVE-MODES-RECONCILIATION-A',                'validate_live_mode_benchmark_reconciliation_v1.py'),
    ('LIVE-MODES-CALENDAR-A',                      'validate_live_mode_calendar_v1.py'),
    ('LIVE-MODES-REWARD-FRAMEWORK-A',              'validate_live_mode_reward_framework_v1.py'),
    ('LIVE-MODES-BROADCAST-POLICY-A',              'validate_live_mode_broadcast_policy_v1.py'),
    ('LIVE-MODES-RISK-POLICY-A',                   'validate_live_mode_benchmark_risk_policy_v1.py'),
    ('SANCTUARY-HOUSING-DESIGN-NOTE-A',            'validate_sanctuary_housing_dimora_divina_note_v1.py'),
    ('LIVE-MODES-RUNTIME-SAFETY-AUDIT-A',          'audit_live_mode_reconciliation_runtime_safety_v1.py'),
    ('SLC-NEXT-PREP-A',                            'validate_slc_next_after_be_plan_v1.py'),
    ('LIVE-MODES-SLC-NEXT-COMBO-A',                'validate_live_modes_slc_next_combo_v1.py'),
    # DIVINE BENCHMARK CANONICAL SOURCE PACK (DESIGN-ONLY / SOURCE-OF-TRUTH)
    ('BENCHMARK-CANONICAL-INDEX-A',                'validate_benchmark_canonical_index_v1.py'),
    ('BENCHMARK-LIVE-SPECIAL-MODES-CANONICAL-A',   'validate_live_special_modes_canonical_v1.py'),
    ('BENCHMARK-SYSTEM-LIBRARY-A',                 'validate_benchmark_system_library_v1.py'),
    ('BENCHMARK-RISK-POLICY-EXPANDED-A',           'validate_benchmark_risk_policy_expanded_v1.py'),
    ('BENCHMARK-SANCTUARY-HOUSING-CANONICAL-A',    'validate_sanctuary_housing_dimora_divina_canonical_v1.py'),
    ('BENCHMARK-SUMMON-PITY-FRAGMENT-CANONICAL-A', 'validate_summon_pity_fragment_canonical_v1.py'),
    ('BENCHMARK-SERVER-LIFECYCLE-CAL-MERGE-A',     'validate_server_lifecycle_calendar_merge_canonical_v1.py'),
    ('BENCHMARK-EVENT-HUB-DAILY-GUIDE-A',          'validate_event_hub_daily_guide_canonical_v1.py'),
    ('BENCHMARK-GUILD-SOCIAL-COOP-A',              'validate_guild_social_coop_canonical_v1.py'),
    ('BENCHMARK-EQUIPMENT-FORGE-RELIC-A',          'validate_equipment_forge_relic_canonical_v1.py'),
    ('BENCHMARK-BATTLE-STATS-REPORTING-A',         'validate_battle_stats_reporting_canonical_v1.py'),
    ('BENCHMARK-SLC-F-NEXT-CHECKPOINT-A',          'validate_slc_f_next_checkpoint_canonical_v1.py'),
    ('BENCHMARK-CANONICAL-RUNTIME-SAFETY-AUDIT-A', 'audit_benchmark_canonical_runtime_safety_v1.py'),
    ('BENCHMARK-CANONICAL-COMBO-A',                'validate_benchmark_canonical_combo_v1.py'),
    # SLC-F ROUTE PATCH DRY-RUN (DESIGN-ONLY / DRY-RUN)
    ('SLC-F-PREFLIGHT',                            'validate_slc_f_preflight_v1.py'),
    ('SLC-F-ROUTE-SCOPE-INVENTORY',                'audit_slc_f_route_scope_inventory_v1.py'),
    ('SLC-F-COLLECTION-SCOPE-MATRIX',              'validate_slc_f_collection_scope_matrix_v1.py'),
    ('SLC-F-ENDPOINT-PATCH-CONTRACT',              'validate_slc_f_endpoint_patch_contract_v1.py'),
    ('SLC-F-LEGACY-S1-COMPATIBILITY-PLAN',         'validate_slc_f_legacy_s1_compatibility_plan_v1.py'),
    ('SLC-F-DRY-RUN-SIMULATION',                   'simulate_slc_f_route_patch_dryrun_v1.py'),
    ('SLC-F-ROUTE-PATCH-RISK-MATRIX',              'validate_slc_f_route_patch_risk_matrix_v1.py'),
    ('SLC-F-RUNTIME-SAFETY-AUDIT',                 'audit_slc_f_runtime_safety_v1.py'),
    ('SLC-F-READINESS-ROLLUP',                     'validate_slc_f_readiness_rollup_v1.py'),
    ('SLC-F-COMBO',                                'validate_slc_f_route_patch_dryrun_combo_v1.py'),
    # SLC-D MERGE TOOLING OFFLINE SIMULATION (DESIGN-ONLY / DRY-RUN)
    ('SLC-D-PREFLIGHT',                            'validate_slc_d_preflight_v1.py'),
    ('SLC-D-TOOLING-OFFLINE-PLAN',                 'validate_server_merge_tooling_offline_plan_v1.py'),
    ('SLC-D-ELIGIBILITY-POLICY',                   'validate_server_merge_eligibility_policy_v1.py'),
    ('SLC-D-GROUP-PLANNING-CONTRACT',              'validate_server_merge_group_planning_contract_v1.py'),
    ('SLC-D-CONFLICT-RESOLUTION-CONTRACT',         'validate_server_merge_conflict_resolution_contract_v1.py'),
    ('SLC-D-RECOVERY-SEASON-CONTRACT',             'validate_server_merge_recovery_season_contract_v1.py'),
    ('SLC-D-RECOVERY-POLICY',                      'validate_server_merge_recovery_policy_v1.py'),
    ('SLC-D-CALENDAR-HARMONIZATION-POLICY',        'validate_server_merge_calendar_harmonization_policy_v1.py'),
    ('SLC-D-DRYRUN-SCENARIOS',                     'validate_server_merge_dryrun_scenarios_v1.py'),
    ('SLC-D-OFFLINE-SIMULATION',                   'simulate_slc_d_merge_tooling_offline_v1.py'),
    ('SLC-D-RISK-MATRIX',                          'validate_server_merge_risk_matrix_v1.py'),
    ('SLC-D-ABORT-ROLLBACK-POLICY',                'validate_server_merge_abort_rollback_policy_v1.py'),
    ('SLC-D-RUNTIME-SAFETY-AUDIT',                 'audit_slc_d_runtime_safety_v1.py'),
    ('SLC-D-READINESS-ROLLUP',                     'validate_slc_d_merge_tooling_offline_readiness_rollup_v1.py'),
    ('SLC-D-COMBO',                                'validate_slc_d_merge_tooling_combo_v1.py'),
    # SLC-G DEFAULT S1 MIGRATION COMMIT GATED PREP (PRE_COMMIT_GATED_DRY_RUN_FIRST)
    ('SLC-G-PREFLIGHT',                            'validate_slc_g_preflight_v1.py'),
    ('SLC-G-BACKFILL-DRYRUN',                      'simulate_slc_g_default_s1_backfill_dryrun.py'),
    ('SLC-G-WRITE-GATE-CONTRACT',                  'validate_slc_g_write_gate_contract_v1.py'),
    ('SLC-G-ROLLBACK-PLAN',                        'validate_slc_g_rollback_plan_v1.py'),
    ('SLC-G-IDEMPOTENCY-CONTRACT',                 'validate_slc_g_idempotency_contract_v1.py'),
    ('SLC-G-COMBO',                                'validate_slc_g_combo_v1.py'),
    # SLC-G-GUILDS-UNSAFE-CLEANUP-A (READ-ONLY FIRST / GATED CLEANUP PLAN)
    ('SLC-G-GUILDS-UNSAFE-AUDIT',                  'audit_slc_g_guilds_unsafe_readonly_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-PLAN',                  'validate_slc_g_guilds_cleanup_plan_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-GATE-CONTRACT',         'validate_slc_g_guilds_cleanup_gate_contract_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-ROLLBACK-PLAN',         'validate_slc_g_guilds_cleanup_rollback_plan_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-COMBO',                 'validate_slc_g_guilds_cleanup_combo_v1.py'),
    ('SLC-G-GUILDS-CLEANUP-B-POST-APPLY',          'validate_slc_g_guilds_cleanup_b_post_apply_v1.py'),
    ('SLC-G-COMMIT-A-POST-APPLY',                  'validate_slc_g_commit_a_post_apply_v1.py'),
    # SLC-H SERVER SELECTION ENDPOINT DESIGN-ONLY (CONTRACT-ONLY / READ-ONLY)
    ('SLC-H-ENDPOINT-CONTRACT',                    'validate_slc_h_endpoint_contract_v1.py'),
    ('SLC-H-REJECTION-MODES',                      'validate_slc_h_rejection_modes_v1.py'),
    ('SLC-H-SERVER-STATUS-CONTRACT',               'validate_slc_h_server_status_contract_v1.py'),
    ('SLC-H-READINESS-GATES',                      'validate_slc_h_readiness_gates_v1.py'),
    ('SLC-H-COMBO',                                'validate_slc_h_combo_v1.py'),
    # SLC-F APPLY PREP + HOUSING ADDENDUM (DESIGN-ONLY / NO RUNTIME APPLY)
    ('SLC-F-APPLY-PREP-STAGED-PLAN',               'validate_slc_f_apply_prep_staged_plan_v1.py'),
    ('SLC-F-APPLY-READINESS-GATES',                'validate_slc_f_apply_readiness_gates_v1.py'),
    ('HOUSING-DIMORA-DIVINA-V2',                   'validate_sanctuary_housing_dimora_divina_v2.py'),
    ('DIMORA-DIVINA-RUNTIME-SAFETY-AUDIT',         'audit_dimora_divina_runtime_safety_v1.py'),
    ('SLC-F-APPLY-PREP-HOUSING-ADDENDUM-COMBO',    'validate_slc_f_apply_prep_housing_addendum_combo_v1.py'),
    ('SLC-F-BATCH-0-1-POST-APPLY',                 'validate_slc_f_batch_0_1_post_apply_v1.py'),
    # SLC-F APPLY BATCH-1B POST-APPLY (READ-ONLY VERIFICATION)
    ('SLC-F-BATCH-1B-POST-APPLY',                  'validate_slc_f_batch_1b_post_apply_v1.py'),
    # SLC-F APPLY BATCH-2 POST-APPLY (READ-ONLY VERIFICATION; SAFE NO-OP APPLY)
    ('SLC-F-BATCH-2-POST-APPLY',                   'validate_slc_f_batch_2_post_apply_v1.py'),
    # SLC-F EQUIPMENT SERVER_SCOPE EXTENSION POST-APPLY (READ-ONLY; SAFE NO-OP APPLY)
    ('SLC-F-EQUIPMENT-SCOPE-POST-APPLY',           'validate_slc_f_equipment_scope_post_apply_v1.py'),
    # SLC-F RAIDS EQUIPMENT SERVER_SCOPE EXTENSION POST-APPLY (PATCH APPLIED)
    ('SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY',     'validate_slc_f_raids_equipment_scope_post_apply_v1.py'),
    # SLC-F GVG WAR INSERT SERVER_SCOPE EXTENSION POST-APPLY (PATCH APPLIED)
    ('SLC-F-GVG-WAR-SCOPE-POST-APPLY',             'validate_slc_f_gvg_war_scope_post_apply_v1.py'),
    # SLC-F UNIQUE-ITEMS SERVER_SCOPE EXTENSION POST-APPLY (PATCH APPLIED)
    ('SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY',        'validate_slc_f_unique_items_scope_post_apply_v1.py'),
    # SLC-F POST-MICROBATCH CONSOLIDATION AUDIT (READ-ONLY)
    ('SLC-F-POST-MICROBATCH-CONSOLIDATION-AUDIT-V1', 'audit_slc_f_post_microbatch_consolidation_v1.py'),
    # SLC-F COSMETICS SCHEMA SPLIT REFACTOR (READY_NOT_APPLIED - design-only, no runtime patch)
    ('SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1',   'validate_slc_f_cosmetics_refactor_v1.py'),
    # SLC-F MINOR WRITE SURFACES AUDIT (READ-ONLY; NO RUNTIME PATCH)
    ('SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1',        'audit_slc_f_minor_write_surfaces_v1.py'),
    # MEGA-COMBO V1 BLOCK_A ECONOMY PAID/FREE SPLIT PREP (AUDIT/PREP ONLY; NO RUNTIME PATCH)
    ('MEGA-COMBO-V1-BLOCK-A-ECONOMY-PREP',         'audit_economy_paid_free_split_prep_v1.py'),
    # MEGA-COMBO V1 BLOCK_B GACHA/SUMMON DRIFT DOCS HOUSEKEEPING (DOC/AUDIT ONLY; NO DB WRITE)
    ('MEGA-COMBO-V1-BLOCK-B-DRIFT-HOUSEKEEPING',   'audit_drift_docs_gacha_summon_count_v1.py'),
    # MEGA-COMBO V2 BLOCK_A ECONOMY DAILY_CLAIMS SCOPE APPLY (PATCH APPLIED)
    ('V2-BLOCK-A-ECONOMY-DAILY-CLAIMS-POST-APPLY', 'validate_v2_economy_daily_claims_scope.py'),
    # MEGA-COMBO V2 BLOCK_B GVG USER_MAIL SCOPE APPLY (PATCH APPLIED)
    ('V2-BLOCK-B-GVG-USER-MAIL-POST-APPLY',        'validate_v2_gvg_user_mail_scope.py'),
    # MEGA-COMBO V2 ROLLUP (5 blocks consistency)
    ('V2-ROLLUP',                                  'validate_mega_combo_slc_acceleration_v2_rollup.py'),
    # MEGA-COMBO V3 BLOCK_E ROSTER VISIBILITY INVARIANTS (HTTP smoke; READ-ONLY)
    ('V3-ROSTER-VISIBILITY-INVARIANTS',            'validate_roster_visibility_invariants_v1.py'),
    # MEGA-COMBO V4 BLOCK_A BATTLE PASS TECHNICAL HARDENING (READY_NOT_APPLIED audit)
    ('V4-BLOCK-A-BATTLE-PASS-HARDENING-AUDIT',     'validate_v4_battle_pass_technical_hardening.py'),
    # MEGA-COMBO V4 BLOCK_D SLC-F OBSERVABILITY ROLLUP (READ-ONLY)
    ('V4-BLOCK-D-SLC-F-OBSERVABILITY-ROLLUP',      'validate_slc_f_observability_rollup_v1.py'),
    # MEGA-COMBO V4 BLOCK_E REDIS RATE-LIMIT OPS AUDIT (READ-ONLY)
    ('V4-BLOCK-E-REDIS-RATE-LIMIT-OPS-AUDIT',      'audit_redis_rate_limit_ops_v1.py'),
    # MEGA-COMBO V5 BLOCK_B AF2-N OBSERVABILITY METRICS PIPELINE (READ-ONLY DOC AUDIT)
    ('V5-BLOCK-B-AF2N-OBSERVABILITY-PIPELINE',     'validate_af2n_observability_pipeline_v1.py'),
    # MEGA-COMBO V5 BLOCK_C ROSTER VISIBILITY INVARIANTS V2 (HTTP smoke; superset of v1)
    ('V5-BLOCK-C-ROSTER-VISIBILITY-INVARIANTS-V2', 'validate_roster_visibility_invariants_v2.py'),
    # MEGA-COMBO V6 BLOCK_B AF2-N METRICS SNAPSHOT EXPORT (READ-ONLY validator; does NOT run export)
    ('V6-BLOCK-B-AF2N-METRICS-SNAPSHOT-EXPORT',    'validate_af2n_metrics_snapshot_export_v1.py'),
    # MEGA-COMBO V6 BLOCK_E SUITE RUNTIME HEALTH (non-blocking on H3/H4; HTTP smoke + supervisorctl)
    ('V6-BLOCK-E-SUITE-RUNTIME-HEALTH',            'validate_suite_runtime_health_v1.py'),
    # MEGA-COMBO V7 BLOCK_A ECONOMY /server/select DEPRECATION NOTICE (apply low-risk; read-only validator)
    ('V7-BLOCK-A-ECONOMY-SERVER-SELECT-DEPRECATION', 'validate_v7_economy_server_select_deprecation.py'),
    # MEGA-COMBO V7 BLOCK_B BATTLE PASS TECHNICAL HARDENING POST SIGNOFF ($setOnInsert; read-only validator)
    ('V7-BLOCK-B-BATTLE-PASS-HARDENING-POST-SIGNOFF', 'validate_v7_battle_pass_technical_hardening.py'),
    # MEGA-COMBO V7 BLOCK_C SERVER PROFILES CANONICAL INDEXES DEFINITION (design-only; no DB write)
    ('V7-BLOCK-C-SERVER-PROFILES-INDEXES-DEFINITION', 'validate_server_profiles_schema_indexes_definition_v1.py'),
    # MEGA-COMBO V7 BLOCK_E BOREA INERT BASELINE INVARIANT HARDENING (HTTP smoke; 9 dedicated invariants)
    ('V7-BLOCK-E-BOREA-INERT-BASELINE',             'validate_borea_inert_baseline_v1.py'),
    # MEGA-COMBO V8 BLOCK_A SERVER PROFILES COLLECTION CREATION PLAN (design/script-only; dry-run gated, no DB write)
    ('V8-BLOCK-A-SERVER-PROFILES-COLLECTION-PLAN',  'validate_server_profiles_collection_creation_plan_v1.py'),
    # MEGA-COMBO V8 BLOCK_B BATTLE PASS USER_SEASON INDEX DEFINITION (design/dry-run-only; no live create_index)
    ('V8-BLOCK-B-BATTLE-PASS-INDEX-USER-SEASON',    'validate_battle_pass_user_season_index_definition_v1.py'),
    # MEGA-COMBO V8 BLOCK_C AF2N DASHBOARD RENDER JSON (design/export-only; no runtime, no daemon)
    ('V8-BLOCK-C-AF2N-DASHBOARD-RENDER-JSON',       'validate_af2n_dashboard_render_json_v1.py'),
    # MEGA-COMBO V8 BLOCK_E SUITE OPTIMIZATION PARALLEL AUDIT (audit-only; no runner change, no validator weakening)
    ('V8-BLOCK-E-SUITE-OPTIMIZATION-PARALLEL-AUDIT', 'audit_suite_optimization_parallel_v1.py'),
    # PROJECT_A Track A SERVER PROFILES OPS (live ops apply inert: collection + 3 canonical indexes; no runtime)
    ('PROJECT-A-TRACK-A-SERVER-PROFILES-OPS',       'validate_project_a_server_profiles_ops_v1.py'),
    # PROJECT_A Track B BATTLE PASS USER_SEASON UNIQUE INDEX (live ops apply; V4 R4 closed)
    ('PROJECT-A-TRACK-B-BATTLE-PASS-INDEX-OPS',     'validate_project_a_battle_pass_index_ops_v1.py'),
    # PROJECT_A Track C AF2-N RUNTIME ROUTING PREFLIGHT (no runtime mutation)
    ('PROJECT-A-TRACK-C-AF2N-RUNTIME-ROUTING-PREFLIGHT', 'validate_project_a_af2n_runtime_routing_preflight_v1.py'),
    # PROJECT_A Track F GACHA/SUMMON DRIFT CLEANUP PLAN (audit/plan only; 7 drift docs classified)
    ('PROJECT-A-TRACK-F-GACHA-SUMMON-DRIFT-CLEANUP-PLAN', 'validate_project_a_gacha_summon_drift_cleanup_plan_v1.py'),
    # PROJECT_A Track G QA/RELEASE DOD TRACKER (project management; 7 DoD rows)
    ('PROJECT-A-TRACK-G-QA-RELEASE-DOD-TRACKER',    'validate_project_completion_dod_tracker_v1.py'),
    # PROJECT_B Track A SERVER PROFILES DUAL-ROUTE INERT SKELETON (flag-gated, runtime OFF)
    ('PROJECT-B-TRACK-A-SERVER-PROFILES-DUAL-ROUTE', 'validate_project_b_server_profiles_dual_route.py'),
    # PROJECT_B Track B HOUSING RESOLVER PURE STUB (inert, NOT imported by runtime)
    ('PROJECT-B-TRACK-B-HOUSING-RESOLVER-STUB-INERT', 'validate_project_b_housing_resolver_stub_inert.py'),
    # PROJECT_B Track C HERO SKILL KIT CATALOG FREEZE (sha256 invariant; 6 baselines)
    ('PROJECT-B-TRACK-C-HERO-SKILL-KIT-CATALOG-FREEZE', 'validate_project_b_hero_skill_kit_catalog_freeze_v1.py'),
    # PROJECT_B Track E SUITE PARALLEL RUNNER (optional --parallel; default sequential unchanged)
    ('PROJECT-B-TRACK-E-SUITE-PARALLEL-RUNNER',     'validate_project_b_suite_parallel_runner_v1.py'),
    # PROJECT_B Track G QA RELEASE MOBILE SMOKE FLOW (static matrix validator)
    ('PROJECT-B-TRACK-G-QA-RELEASE-MOBILE-SMOKE-FLOW', 'validate_project_b_qa_release_mobile_smoke_flow_v1.py'),
    # PROJECT_B Track H ARTIFACT BIBLE V1 SCHEMA + LAUNCH CANDIDATES (hard invariants enforcement)
    ('PROJECT-B-TRACK-H-ARTIFACT-BIBLE-SCHEMA',     'validate_project_b_artifact_bible_schema_v1.py'),
    # PROJECT_C Track A SERVER PROFILES DUAL-ROUTE BEHAVIOR LAYER (flag-gated, default 503)
    ('PROJECT-C-TRACK-A-SERVER-PROFILES-BEHAVIOR',  'validate_project_c_server_profiles_behavior_v1.py'),
    # PROJECT_C Track B HOUSING RESOLVER INTEGRATION DESIGN (5 phases; stub NOT imported by runtime)
    ('PROJECT-C-TRACK-B-HOUSING-RESOLVER-INTEGRATION-DESIGN', 'validate_project_c_housing_resolver_integration_design_v1.py'),
    # PROJECT_C Track C STATUS EFFECT CATALOG BASELINE (10 categories + 10 effects, anti-power-creep caps)
    ('PROJECT-C-TRACK-C-STATUS-EFFECT-CATALOG-BASELINE', 'validate_project_c_status_effect_catalog_baseline_v1.py'),
    # PROJECT_C Track D DRIFT_DOC_2 deprecated_banner_legacy_pool ARCHIVE (audit only; 2/7 archived)
    ('PROJECT-C-TRACK-D-DRIFT-DOC-2-ARCHIVE',       'validate_project_c_drift_doc_2_archive_v1.py'),
    # PROJECT_C Track E QA MOBILE SMOKE RUNNER CLI (GET-only, non-mutating; --help smoke)
    ('PROJECT-C-TRACK-E-QA-MOBILE-SMOKE-RUNNER',    'validate_project_c_qa_mobile_smoke_runner_v1.py'),
    # PROJECT_C Track F AF2-N DASHBOARD PROVISION OPS TEMPLATES (3 Grafana templates, no secret baked)
    ('PROJECT-C-TRACK-F-AF2N-DASHBOARD-PROVISION-OPS', 'validate_project_c_af2n_dashboard_provision_ops_v1.py'),
    # PROJECT_C Track G LEGACY /server/select DEPRECATION METRICS (design only, 3 metrics, 4-phase kill-switch)
    ('PROJECT-C-TRACK-G-LEGACY-SERVER-SELECT-DEPRECATION-METRICS', 'validate_project_c_legacy_server_select_deprecation_metrics_v1.py'),
    # PROJECT_C Track H ARTIFACT BIBLE V1 USER APPROVAL + BONUS RESOLVER STUB DESIGN (pure stub, NOT imported by runtime)
    ('PROJECT-C-TRACK-H-ARTIFACT-BIBLE-USER-APPROVAL-AND-BONUS-RESOLVER-STUB', 'validate_project_c_artifact_bible_user_approval_v1.py'),
    # PROJECT_D Track A SERVER PROFILES FLAGGED PREVIEW BEHAVIOR (double-flag-gated; default 503 unchanged)
    ('PROJECT-D-TRACK-A-SERVER-PROFILES-FLAGGED-PREVIEW', 'validate_project_d_server_profiles_flagged_preview.py'),
    # PROJECT_D Track B HOUSING RESOLVER PHASE 2 UNIT TESTS (8 UT pass; stub NOT imported)
    ('PROJECT-D-TRACK-B-HOUSING-RESOLVER-PHASE2-TESTS', 'validate_project_d_housing_resolver_stub_caps_v1.py'),
    # PROJECT_D Track C STATUS EFFECT RUNTIME ADAPTER SKELETON (pure module, NOT imported by battle/runtime)
    ('PROJECT-D-TRACK-C-STATUS-EFFECT-ADAPTER-SKELETON', 'validate_project_d_status_effect_adapter_stub_inert.py'),
    # PROJECT_D Track D DRIFT_DOC_3 obsolete_pity_counter_format FREEZE_READ_ONLY (3/7 archived)
    ('PROJECT-D-TRACK-D-DRIFT-DOC-3-ARCHIVE',         'validate_project_d_drift_doc_3_archive_v1.py'),
    # PROJECT_D Track E QA RUNNER LOGIN STEP GATED (wrapper only allows POST /api/login; live MANUAL_REQUIRED)
    ('PROJECT-D-TRACK-E-QA-RUNNER-LOGIN-SAFETY',      'validate_project_d_qa_runner_login_safety.py'),
    # PROJECT_D Track F BASELINE FAIL ISOLATION (3 DEPRECATED_VALIDATOR classified; not hidden; rebaseline plan)
    ('PROJECT-D-TRACK-F-BASELINE-FAIL-ISOLATION',     'audit_project_d_baseline_fail_isolation_v1.py'),
    # PROJECT_D Track G AF2-N DASHBOARD LOCAL VALIDATION (3 Grafana templates shape; 5 alert UIDs; no external calls)
    ('PROJECT-D-TRACK-G-AF2N-DASHBOARD-LOCAL-VALIDATION', 'validate_project_d_af2n_dashboard_local_templates_v1.py'),
    # PROJECT_D Track H ARTIFACT BIBLE V1 APPROVAL FREEZE (design-only; 7 freeze invariants; 5 draft candidates)
    ('PROJECT-D-TRACK-H-ARTIFACT-BIBLE-V1-APPROVAL-FREEZE', 'validate_project_d_artifact_bible_v1_approval_freeze.py'),
    # PROJECT_E Track A — SLC v2 successors (replace v1 deprecated cluster; default green when v1 SUPERSEDED)
    ('SLC-C-REPO-PREFLIGHT-V2',                    'validate_slc_c_repo_multishard_post_g_invariant_v2.py'),
    ('SLC-C-COMBO-V2',                             'validate_slc_c_combo_v2.py'),
    ('SLC-D-PREFLIGHT-V2',                         'validate_slc_d_preflight_v2.py'),
    ('SLC-D-COMBO-V2',                             'validate_slc_d_merge_tooling_combo_v2.py'),
    ('SLC-BE-PREFLIGHT-V2',                        'validate_slc_be_preflight_v2.py'),
    ('SLC-BE-COMBO-V2',                            'validate_slc_be_server_profile_selection_combo_v2.py'),
    ('SLC-F-PREFLIGHT-V2',                         'validate_slc_f_preflight_v2.py'),
    ('SLC-F-COMBO-V2',                             'validate_slc_f_route_patch_dryrun_combo_v2.py'),
    # PROJECT_E Track A marker validator (zero-fail recovery summary)
    ('PROJECT-E-TRACK-A-SLC-V2-ZERO-FAIL-RECOVERY','validate_project_e_slc_v2_zero_fail_recovery_v1.py'),
    # PROJECT_E Track B HOUSING PHASE 3 INTEGRATION DESIGN (no runtime)
    ('PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN', 'validate_project_e_housing_phase3_stub_tests_v1.py'),
    # PROJECT_E Track C STATUS EFFECT NON-RUNTIME UNIT TESTS
    ('PROJECT-E-TRACK-C-STATUS-EFFECT-NON-RUNTIME-UT', 'validate_project_e_status_effect_non_runtime_ut_v1.py'),
    # PROJECT_E Track D DRIFT_DOC_4 archive (4/7 archived)
    ('PROJECT-E-TRACK-D-DRIFT-DOC-4-ARCHIVE',      'validate_project_e_drift_doc_4_archive_v1.py'),
    # PROJECT_E Track E QA RUNNER TEST CREDS LOGIN DRY-RUN (manual_required live; no secrets logged)
    ('PROJECT-E-TRACK-E-QA-LOGIN-DRYRUN-SAFETY',   'validate_project_e_qa_login_dryrun_safety_v1.py'),
    # PROJECT_E Track F AF2-N DASHBOARD PROVISIONING DRILL (offline; no external calls)
    ('PROJECT-E-TRACK-F-AF2N-DASHBOARD-PROVISIONING-DRILL', 'validate_project_e_af2n_dashboard_provisioning_drill_v1.py'),
    # PROJECT_E Track G ARTIFACT BONUS RESOLVER NON-RUNTIME UNIT TESTS
    ('PROJECT-E-TRACK-G-ARTIFACT-BONUS-RESOLVER-NON-RUNTIME-UT', 'validate_project_e_artifact_bonus_resolver_non_runtime_ut_v1.py'),
    # PROJECT_E Track H PROJECT COMPLETION DoD RECALIBRATION (doc-only)
    ('PROJECT-E-TRACK-H-PROJECT-COMPLETION-DOD-RECALIBRATION', 'validate_project_e_project_completion_dod_recalibration_v1.py'),
    # PROJECT_F Track A SERVER PROFILES READ-ONLY PREVIEW HARDENING (default 503; double-flag gate; no DB writes)
    ('PROJECT-F-TRACK-A-SERVER-PROFILES-READ-ONLY-PREVIEW-HARDENING', 'validate_project_f_server_profiles_read_only_preview.py'),
    # PROJECT_F Track B HOUSING READ-ONLY PREVIEW CONTRACT (disabled-by-default 503 skeleton)
    ('PROJECT-F-TRACK-B-HOUSING-READ-ONLY-PREVIEW-CONTRACT', 'validate_project_f_housing_read_only_preview.py'),
    # PROJECT_F Track C STATUS EFFECT ADAPTER PHASE 2 NON-RUNTIME CONTRACT TESTS
    ('PROJECT-F-TRACK-C-STATUS-EFFECT-ADAPTER-PHASE2-TESTS', 'validate_project_f_status_effect_adapter_phase2_tests.py'),
    # PROJECT_F Track D DRIFT DOC 5 ARCHIVE (audit/doc only; 5/7 archived)
    ('PROJECT-F-TRACK-D-DRIFT-DOC-5-ARCHIVE', 'validate_project_f_drift_doc_5_archive_v1.py'),
    # PROJECT_F Track E QA TEST CREDENTIALS SAFE DRY-RUN (manual_required default; no secret logging)
    ('PROJECT-F-TRACK-E-QA-CREDENTIALS-SAFE-DRYRUN', 'validate_project_f_qa_credentials_safety.py'),
    # PROJECT_F Track F AF2-N DASHBOARD PROVISIONING PHASE 3 DRY-RUN (offline; no external calls)
    ('PROJECT-F-TRACK-F-AF2N-DASHBOARD-PROVISIONING-PHASE3-DRYRUN', 'validate_project_f_af2n_dashboard_phase3_dryrun_v1.py'),
    # PROJECT_F Track G SUITE HYGIENE LOCK & REGRESSION GUARD
    ('PROJECT-F-TRACK-G-SUITE-HYGIENE-LOCK', 'validate_project_f_suite_hygiene_lock_v1.py'),
    # PROJECT_F Track H ARTIFACT BIBLE IMPORT PLAN & APPROVAL GATE (design-only; 4 PENDING gates)
    ('PROJECT-F-TRACK-H-ARTIFACT-BIBLE-IMPORT-PLAN-APPROVAL-GATE', 'validate_project_f_artifact_import_plan_v1.py'),
    # PROJECT_G Track A SERVER PROFILES PREVIEW CONTRACT FREEZE (default 503; double-flag gate)
    ('PROJECT-G-TRACK-A-SERVER-PROFILES-PREVIEW-CONTRACT-FREEZE', 'validate_project_g_server_profiles_preview_contract_v1.py'),
    # PROJECT_G Track B HOUSING PREVIEW CONTRACT FREEZE + 7-substructure CAP SNAPSHOT
    ('PROJECT-G-TRACK-B-HOUSING-PREVIEW-CONTRACT-FREEZE', 'validate_project_g_housing_preview_contract_v1.py'),
    # PROJECT_G Track C STATUS EFFECT RUNTIME READINESS MATRIX (10 categories; non-runtime)
    ('PROJECT-G-TRACK-C-STATUS-EFFECT-RUNTIME-READINESS-MATRIX', 'validate_project_g_status_effect_runtime_readiness_matrix_v1.py'),
    # PROJECT_G Track D DRIFT DOC 6 ARCHIVE (audit/doc only; 6/7 archived)
    ('PROJECT-G-TRACK-D-DRIFT-DOC-6-ARCHIVE', 'validate_project_g_drift_doc_6_archive_v1.py'),
    # PROJECT_G Track E QA SAFE LOGIN ENV CONTRACT (MANUAL_REQUIRED default; no secret logging)
    ('PROJECT-G-TRACK-E-QA-SAFE-LOGIN-ENV-CONTRACT', 'validate_project_g_qa_safe_login_env_contract_v1.py'),
    # PROJECT_G Track F AF2-N DASHBOARD PROVISIONING APPROVAL GATE (5 PENDING gates; 0 external calls)
    ('PROJECT-G-TRACK-F-AF2N-DASHBOARD-PROVISIONING-APPROVAL-GATE', 'validate_project_g_af2n_dashboard_provisioning_approval_gate_v1.py'),
    # PROJECT_G Track G SUITE HEALTH FINALIZATION & REQUIRED DIFF GUARD
    ('PROJECT-G-TRACK-G-SUITE-HEALTH-FINALIZATION', 'validate_project_g_suite_health_finalization_v1.py'),
    # PROJECT_G Track H ARTIFACT APPROVAL GATE SIGNATURE PACK (4 PENDING gates; signature template)
    ('PROJECT-G-TRACK-H-ARTIFACT-APPROVAL-GATE-SIGNATURE', 'validate_project_g_artifact_approval_gate_signature_v1.py'),
    # PROJECT_H Track A FINAL SLC-H RELEASE CANDIDATE GATE
    ('PROJECT-H-TRACK-A-FINAL-SLC-H-RC-GATE', 'validate_project_h_final_slc_h_rc_gate_v1.py'),
    # PROJECT_H Track B FINAL HOUSING MVP RELEASE CANDIDATE GATE
    ('PROJECT-H-TRACK-B-FINAL-HOUSING-MVP-RC-GATE', 'validate_project_h_final_housing_mvp_rc_gate_v1.py'),
    # PROJECT_H Track C FINAL STATUS RUNTIME GATE & FIRST SLICE PLAN
    ('PROJECT-H-TRACK-C-FINAL-STATUS-RUNTIME-GATE-FIRST-SLICE', 'validate_project_h_final_status_runtime_gate_v1.py'),
    # PROJECT_H Track D DRIFT DOC 7 FINAL ARCHIVE (7/7)
    ('PROJECT-H-TRACK-D-DRIFT-DOC-7-FINAL-ARCHIVE', 'validate_project_h_drift_doc_7_final_archive_v1.py'),
    # PROJECT_H Track E QA RELEASE CANDIDATE SMOKE GATE (9 safe checks)
    ('PROJECT-H-TRACK-E-QA-RELEASE-CANDIDATE-SMOKE-GATE', 'validate_project_h_qa_release_candidate_smoke_gate_v1.py'),
    # PROJECT_H Track F AF2-N FINAL DASHBOARD LIVE READINESS GATE
    ('PROJECT-H-TRACK-F-AF2N-FINAL-DASHBOARD-LIVE-READINESS-GATE', 'validate_project_h_af2n_final_dashboard_live_readiness_gate_v1.py'),
    # PROJECT_H Track G ARTIFACT FINAL APPROVAL GATE & IMPORT READINESS
    ('PROJECT-H-TRACK-G-ARTIFACT-FINAL-APPROVAL-GATE', 'validate_project_h_artifact_final_approval_gate_v1.py'),
    # PROJECT_H Track H PROJECT RELEASE CANDIDATE DoD FINALIZATION (9 layers; next-stage plan)
    ('PROJECT-H-TRACK-H-PROJECT-RC-DOD-FINALIZATION', 'validate_project_h_release_candidate_dod_finalization_v1.py'),
    # PROJECT_I Track A SERVER PROFILES PREVIEW CANARY FLAG FLIP (authorized; code-path verified in-process; local backend untouched)
    ('PROJECT-I-TRACK-A-SERVER-PROFILES-PREVIEW-CANARY-FLIP', 'validate_project_i_server_profiles_preview_canary_flip_v1.py'),
    # PROJECT_I Track B HOUSING PREVIEW CANARY FLAG FLIP (authorized; zero-bonus envelope; local backend untouched)
    ('PROJECT-I-TRACK-B-HOUSING-PREVIEW-CANARY-FLIP', 'validate_project_i_housing_preview_canary_flip_v1.py'),
    # PROJECT_I Track C STATUS RUNTIME REQUIRED VALIDATOR AUGMENTATION PREP (zero added; activation pack will add)
    ('PROJECT-I-TRACK-C-STATUS-RUNTIME-REQUIRED-VALIDATOR-AUGMENTATION', 'validate_project_i_status_runtime_required_validator_augmentation_v1.py'),
    # PROJECT_I Track D QA LIVE LOGIN CANARY (MANUAL_REQUIRED if env unset; no secret logging)
    ('PROJECT-I-TRACK-D-QA-LIVE-LOGIN-CANARY', 'validate_project_i_qa_live_login_canary_v1.py'),
    # PROJECT_I Track E AF2-N APPROVAL SIGNATURES & CANARY PLAN (5 PENDING; 0 external calls)
    ('PROJECT-I-TRACK-E-AF2N-APPROVAL-SIGNATURES', 'validate_project_i_af2n_approval_signatures_v1.py'),
    # PROJECT_I Track F ARTIFACT APPROVAL SIGNATURES & IMPORT CANARY PLAN (4 PENDING; no live bonus/summon/import)
    ('PROJECT-I-TRACK-F-ARTIFACT-APPROVAL-SIGNATURES', 'validate_project_i_artifact_approval_signatures_v1.py'),
    # PROJECT_I Track G DRIFT DB CLEANUP FREEZE-WINDOW PLAN (no cleanup executed)
    ('PROJECT-I-TRACK-G-DRIFT-DB-CLEANUP-FREEZE-WINDOW-PLAN', 'validate_project_i_drift_db_cleanup_freeze_window_plan_v1.py'),
    # PROJECT_I Track H PROJECT 99->100 FINAL LIVE-GATE ROADMAP
    ('PROJECT-I-TRACK-H-PROJECT-99-TO-100-FINAL-LIVE-GATE-ROADMAP', 'validate_project_i_project_99_to_100_final_live_gate_roadmap_v1.py'),
    # PROJECT_J Track A STATUS FIRST SLICE SCOPE LOCK & FLAG CONTRACT (flag default OFF)
    ('PROJECT-J-TRACK-A-STATUS-FIRST-SLICE-SCOPE-LOCK', 'validate_project_j_status_first_slice_scope_lock_v1.py'),
    # PROJECT_J Track B STATUS RESOLVER PURE MODULE (inert; not imported by battle/runtime)
    ('PROJECT-J-TRACK-B-STATUS-RESOLVER-PURE-MODULE', 'validate_project_j_status_resolver_pure_module_v1.py'),
    # PROJECT_J Track C STATUS FIRST SLICE REQUIRED-CANDIDATE VALIDATORS SET (5 OPTIONAL)
    ('PROJECT-J-TRACK-C-STATUS-FIRST-SLICE-REQUIRED-VALIDATORS-SET', 'validate_project_j_status_first_slice_required_validators_set_v1.py'),
    # PROJECT_J Track D STATUS FIXTURE MATRIX + 10 GOLDEN TESTS
    ('PROJECT-J-TRACK-D-STATUS-FIXTURE-MATRIX-AND-GOLDEN-TESTS', 'validate_project_j_status_fixture_matrix_and_golden_tests_v1.py'),
    # PROJECT_J Track E BATTLE PAYLOAD STATUS PREVIEW CONTRACT (design only)
    ('PROJECT-J-TRACK-E-BATTLE-PAYLOAD-STATUS-PREVIEW-CONTRACT', 'validate_project_j_battle_payload_status_preview_contract_v1.py'),
    # PROJECT_J Track F STATUS ROLLBACK + KILL-SWITCH PLAN
    ('PROJECT-J-TRACK-F-STATUS-ROLLBACK-KILL-SWITCH-PLAN', 'validate_project_j_status_rollback_kill_switch_plan_v1.py'),
    # PROJECT_J Track G STATUS QA SAFE SMOKE EXTENSION (SS1-SS5)
    ('PROJECT-J-TRACK-G-STATUS-QA-SAFE-SMOKE-EXTENSION', 'validate_project_j_status_qa_safe_smoke_extension_v1.py'),
    # PROJECT_J Track H PROJECT J COMPLETION + NEXT PACK ROADMAP
    ('PROJECT-J-TRACK-H-PROJECT-J-COMPLETION-AND-NEXT-PACK-ROADMAP', 'validate_project_j_completion_and_next_pack_roadmap_v1.py'),
    # PROJECT_K Track A STATUS PREFIGHT INSERTION POINT AUDIT (honest blocker; battle runtime layer absent)
    ('PROJECT-K-TRACK-A-STATUS-PREFIGHT-INSERTION-POINT-AUDIT', 'validate_project_k_status_prefight_insertion_point_audit_v1.py'),
    # PROJECT_K Track B STATUS PREFIGHT FLAGGED WIRING (NOT APPLIED — awaiting battle runtime layer)
    ('PROJECT-K-TRACK-B-STATUS-PREFIGHT-FLAGGED-WIRING', 'validate_project_k_status_prefight_flagged_wiring_v1.py'),
    # PROJECT_K Track C STATUS REQUIRED VALIDATORS PROMOTION (5 RC promoted to REQUIRED — see REQUIRED block above)
    ('PROJECT-K-TRACK-C-STATUS-REQUIRED-VALIDATORS-PROMOTION', 'validate_project_k_status_required_validators_promotion_v1.py'),
    # PROJECT_K Track D STATUS CANARY FIXTURE EXECUTION (10/10 golden tests against pure resolver)
    ('PROJECT-K-TRACK-D-STATUS-CANARY-FIXTURE-EXECUTION', 'validate_project_k_status_canary_fixture_execution_v1.py'),
    # PROJECT_K Track E STATUS PAYLOAD PREVIEW CANARY CONTRACT (0 leaks across 5 audited endpoints)
    ('PROJECT-K-TRACK-E-STATUS-PAYLOAD-PREVIEW-CANARY-CONTRACT', 'validate_project_k_status_payload_preview_canary_contract_v1.py'),
    # PROJECT_K Track F STATUS RUNTIME CANARY ROLLBACK DRILL (in-process drill executed; flag transitions honest)
    ('PROJECT-K-TRACK-F-STATUS-RUNTIME-CANARY-ROLLBACK-DRILL', 'validate_project_k_status_runtime_canary_rollback_drill_v1.py'),
    # PROJECT_K Track G STATUS FIRST SLICE QA RC GATE (13 safe checks)
    ('PROJECT-K-TRACK-G-STATUS-FIRST-SLICE-QA-RC-GATE', 'validate_project_k_status_first_slice_qa_rc_gate_v1.py'),
    # PROJECT_K Track H PROJECT K COMPLETION + LIVE GATE STATUS (next pack: PROJECT_L)
    ('PROJECT-K-TRACK-H-PROJECT-K-COMPLETION-AND-LIVE-GATE-STATUS', 'validate_project_k_completion_and_live_gate_status_v1.py'),
    # PROJECT_L Track A BATTLE RUNTIME SEAM AUDIT (SEAM_SAFE_NOW_INERT)
    ('PROJECT-L-TRACK-A-BATTLE-RUNTIME-SEAM-AUDIT', 'validate_project_l_battle_runtime_seam_audit_v1.py'),
    # PROJECT_L Track B MINIMAL BATTLE RUNTIME SEAM (CREATED INERT; isolated module; not imported live)
    ('PROJECT-L-TRACK-B-MINIMAL-BATTLE-RUNTIME-SEAM-INERT', 'validate_project_l_minimal_battle_runtime_seam_v1.py'),
    # PROJECT_L Track C STATUS PREFIGHT DRY-RUN CANARY (DR1-DR5; live activation blocked)
    ('PROJECT-L-TRACK-C-STATUS-PREFIGHT-DRY-RUN-CANARY', 'validate_project_l_status_prefight_dry_run_canary_v1.py'),
    # PROJECT_L Track D STATUS REQUIRED VALIDATORS POST-SEAM GUARD (19 REQUIRED intact)
    ('PROJECT-L-TRACK-D-STATUS-REQUIRED-VALIDATORS-POST-SEAM-GUARD', 'validate_project_l_status_required_validators_post_seam_guard_v1.py'),
    # PROJECT_L Track E STATUS PAYLOAD NO-LEAK REGRESSION (0 leaks across 5 endpoints)
    ('PROJECT-L-TRACK-E-STATUS-PAYLOAD-NO-LEAK-REGRESSION', 'validate_project_l_status_payload_no_leak_regression_v1.py'),
    # PROJECT_L Track F STATUS CANARY ROLLBACK SCRIPT + DRILL (dry-run executed; non-destructive)
    ('PROJECT-L-TRACK-F-STATUS-CANARY-ROLLBACK-SCRIPT-AND-DRILL', 'validate_project_l_status_canary_rollback_script_and_drill_v1.py'),
    # PROJECT_L Track G STATUS FIRST SLICE RC GATE (13 safe checks)
    ('PROJECT-L-TRACK-G-STATUS-FIRST-SLICE-RC-GATE', 'validate_project_l_status_first_slice_rc_gate_v1.py'),
    # PROJECT_L Track H PROJECT L COMPLETION + NEXT STEP (next pack: PROJECT_M)
    ('PROJECT-L-TRACK-H-PROJECT-L-COMPLETION-AND-NEXT-STEP', 'validate_project_l_completion_and_next_step_v1.py'),
    # PROJECT_M Track A BATTLE ENGINE SINGLE POINT WIRING AUDIT (SINGLE_POINT_SAFE_NOW_FLAGGED)
    ('PROJECT-M-TRACK-A-BATTLE-ENGINE-SINGLE-POINT-AUDIT', 'validate_project_m_battle_engine_single_point_audit_v1.py'),
    # PROJECT_M Track B BATTLE ENGINE STATUS SEAM SINGLE POINT WIRING (flag-OFF byte-identical proven)
    ('PROJECT-M-TRACK-B-BATTLE-ENGINE-STATUS-SEAM-WIRING', 'validate_project_m_battle_engine_status_seam_wiring_v1.py'),
    # PROJECT_M Track C FLAG OFF BYTE-IDENTICAL REGRESSION GUARD (deterministic 3v3 fixture; sha256 match)
    ('PROJECT-M-TRACK-C-FLAG-OFF-BYTE-IDENTICAL-REGRESSION-GUARD', 'validate_project_m_flag_off_byte_identical_regression_v1.py'),
    # PROJECT_M Track D FLAG ON IN-PROCESS CANARY FIXTURE (C1-C6 buffs + cap clamp + out-of-slice)
    ('PROJECT-M-TRACK-D-FLAG-ON-IN-PROCESS-CANARY-FIXTURE', 'validate_project_m_flag_on_in_process_canary_fixture_v1.py'),
    # PROJECT_M Track E STATUS PAYLOAD + BATTLE LOG NO-LEAK GUARD (endpoints + source-level scan)
    ('PROJECT-M-TRACK-E-STATUS-PAYLOAD-BATTLE-LOG-NO-LEAK-GUARD', 'validate_project_m_status_payload_battle_log_no_leak_v1.py'),
    # PROJECT_M Track F BATTLE ENGINE STATUS SEAM ROLLBACK DRILL (dry-run + temp-copy restore byte-identical to backup)
    ('PROJECT-M-TRACK-F-BATTLE-ENGINE-STATUS-SEAM-ROLLBACK-DRILL', 'validate_project_m_battle_engine_status_seam_rollback_drill_v1.py'),
    # PROJECT_M Track G STATUS FIRST SLICE CANARY ENV RC GATE (13 safe checks)
    ('PROJECT-M-TRACK-G-STATUS-FIRST-SLICE-CANARY-ENV-RC-GATE', 'validate_project_m_status_first_slice_canary_env_rc_gate_v1.py'),
    # PROJECT_M Track H PROJECT M COMPLETION + NEXT STEP (next pack: PROJECT_N)
    ('PROJECT-M-TRACK-H-PROJECT-M-COMPLETION-AND-NEXT-STEP', 'validate_project_m_completion_and_next_step_v1.py'),
    # PROJECT_N Track A CANARY ENV PRECHECK (NON_PROD_LOCAL_ONLY confirmed)
    ('PROJECT-N-TRACK-A-CANARY-ENV-PRECHECK', 'validate_project_n_canary_env_precheck_v1.py'),
    # PROJECT_N Track B STATUS FIRST SLICE CANARY FLAG FLIP (executed then rolled back; final state FLAG_OFF)
    ('PROJECT-N-TRACK-B-STATUS-FIRST-SLICE-CANARY-FLAG-FLIP', 'validate_project_n_status_first_slice_canary_flag_v1.py'),
    # PROJECT_N Track C CANARY FLAG ON BEHAVIOR SMOKE (B1-B7 PASS; battle byte-identical with flag ON)
    ('PROJECT-N-TRACK-C-CANARY-FLAG-ON-BEHAVIOR-SMOKE', 'validate_project_n_canary_flag_on_behavior_smoke_v1.py'),
    # PROJECT_N Track D CANARY LIGHT LOAD + STABILITY (150 req 100% 2xx; p99 ~ 68ms)
    ('PROJECT-N-TRACK-D-CANARY-LIGHT-LOAD-STABILITY', 'validate_project_n_canary_light_load_stability_v1.py'),
    # PROJECT_N Track E CANARY PAYLOAD/LOG/METRICS NO-LEAK GUARD
    ('PROJECT-N-TRACK-E-CANARY-PAYLOAD-LOG-METRICS-NO-LEAK', 'validate_project_n_canary_payload_log_metrics_no_leak_v1.py'),
    # PROJECT_N Track F CANARY ROLLBACK + KILL-SWITCH DRILL (6-step drill)
    ('PROJECT-N-TRACK-F-CANARY-ROLLBACK-KILL-SWITCH-DRILL', 'validate_project_n_canary_rollback_kill_switch_drill_v1.py'),
    # PROJECT_N Track G STATUS FIRST SLICE DEV-LIVE READINESS GATE (7 green-checks listed)
    ('PROJECT-N-TRACK-G-STATUS-FIRST-SLICE-DEV-LIVE-READINESS-GATE', 'validate_project_n_status_first_slice_dev_live_readiness_gate_v1.py'),
    # PROJECT_N Track H PROJECT N COMPLETION + NEXT STEP (next pack: PROJECT_O)
    ('PROJECT-N-TRACK-H-PROJECT-N-COMPLETION-AND-NEXT-STEP', 'validate_project_n_completion_and_next_step_v1.py'),
    # PROJECT_O Track A DEV-LIVE PRECHECK (NON_PROD_LOCAL_ONLY confirmed)
    ('PROJECT-O-TRACK-A-DEV-LIVE-PRECHECK', 'validate_project_o_dev_live_precheck_v1.py'),
    # PROJECT_O Track B STATUS FIRST SLICE DEV-LIVE FLAG FLIP (executed + rolled back; FLAG_OFF)
    ('PROJECT-O-TRACK-B-STATUS-FIRST-SLICE-DEV-LIVE-FLAG-FLIP', 'validate_project_o_status_first_slice_dev_live_flag_v1.py'),
    # PROJECT_O Track C DEV-LIVE GAMEPLAY REGRESSION + SHA GUARD (flag OFF == flag ON == baseline)
    ('PROJECT-O-TRACK-C-DEV-LIVE-GAMEPLAY-REGRESSION-SHA-GUARD', 'validate_project_o_dev_live_gameplay_regression_v1.py'),
    # PROJECT_O Track D DEV-LIVE LIGHT LOAD + OBSERVABILITY (300/300 2xx, p99~74ms)
    ('PROJECT-O-TRACK-D-DEV-LIVE-LIGHT-LOAD-OBSERVABILITY', 'validate_project_o_dev_live_light_load_observability_v1.py'),
    # PROJECT_O Track E DEV-LIVE PAYLOAD/LOG/METRICS NO-LEAK
    ('PROJECT-O-TRACK-E-DEV-LIVE-PAYLOAD-LOG-METRICS-NO-LEAK', 'validate_project_o_dev_live_payload_log_metrics_no_leak_v1.py'),
    # PROJECT_O Track F DEV-LIVE ROLLBACK + KILL-SWITCH DRILL (6-step)
    ('PROJECT-O-TRACK-F-DEV-LIVE-ROLLBACK-KILL-SWITCH-DRILL', 'validate_project_o_dev_live_rollback_kill_switch_drill_v1.py'),
    # PROJECT_O Track G PROD READINESS GATE PREP (9 green-checks; no rollout)
    ('PROJECT-O-TRACK-G-PROD-READINESS-GATE-PREP', 'validate_project_o_prod_readiness_gate_prep_v1.py'),
    # PROJECT_O Track H PROJECT O COMPLETION + NEXT STEP (next pack: PROJECT_P)
    ('PROJECT-O-TRACK-H-PROJECT-O-COMPLETION-AND-NEXT-STEP', 'validate_project_o_completion_and_next_step_v1.py'),
    # PROJECT_P Track A PROD ROLLOUT PRECHECK + SIGNATURE GATE (BLOCKING_MISSING_ALL_PROD_SIGNATURES; 0/6 signatures)
    ('PROJECT-P-TRACK-A-PROD-ROLLOUT-PRECHECK-AND-SIGNATURE-GATE', 'validate_project_p_prod_rollout_precheck_and_signature_gate_v1.py'),
    # PROJECT_P Track B PROD ROLLOUT STAGE 1% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-B-PROD-ROLLOUT-STAGE-1-PERCENT', 'validate_project_p_prod_rollout_stage_1_percent_v1.py'),
    # PROJECT_P Track C PROD ROLLOUT STAGE 5% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-C-PROD-ROLLOUT-STAGE-5-PERCENT', 'validate_project_p_prod_rollout_stage_5_percent_v1.py'),
    # PROJECT_P Track D PROD ROLLOUT STAGE 25% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-D-PROD-ROLLOUT-STAGE-25-PERCENT', 'validate_project_p_prod_rollout_stage_25_percent_v1.py'),
    # PROJECT_P Track E PROD ROLLOUT STAGE 100% (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-E-PROD-ROLLOUT-STAGE-100-PERCENT', 'validate_project_p_prod_rollout_stage_100_percent_v1.py'),
    # PROJECT_P Track F PROD ROLLOUT NO-LEAK + LOAD + ROLLBACK FINAL (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-F-PROD-ROLLOUT-NO-LEAK-LOAD-AND-ROLLBACK-FINAL', 'validate_project_p_prod_rollout_no_leak_load_and_rollback_final_v1.py'),
    # PROJECT_P Track G POST-PROD STATUS FIRST-SLICE DOD (READY_NOT_APPLIED_PENDING_APPROVAL)
    ('PROJECT-P-TRACK-G-POST-PROD-STATUS-FIRST-SLICE-DOD', 'validate_project_p_post_prod_status_first_slice_dod_v1.py'),
    # PROJECT_P Track H PROJECT P COMPLETION + NEXT SYSTEM
    ('PROJECT-P-TRACK-H-PROJECT-P-COMPLETION-AND-NEXT-SYSTEM', 'validate_project_p_completion_and_next_system_v1.py'),
    # PROJECT_Q ARTIFACT BIBLE APPROVAL + IMPORT DRY-RUN PACK (8 tracks, READY_PENDING_APPROVAL: 0/5 ARTIFACT_* signatures present, NO DB writes, NO live import)
    ('PROJECT-Q-TRACK-A-ARTIFACT-DIRECTION-CANONICAL-LOCK', 'validate_project_q_artifact_direction_canonical_lock_v1.py'),
    ('PROJECT-Q-TRACK-B-ARTIFACT-BIBLE-SCHEMA-VALIDATION', 'validate_project_q_artifact_bible_schema_validation_v1.py'),
    ('PROJECT-Q-TRACK-C-ARTIFACT-CANDIDATE-EXPANSION', 'validate_project_q_artifact_candidate_expansion_v1.py'),
    ('PROJECT-Q-TRACK-D-ARTIFACT-BONUS-CAP-ECONOMY-DRY-RUN', 'validate_project_q_artifact_bonus_cap_economy_dry_run_v1.py'),
    ('PROJECT-Q-TRACK-E-ARTIFACT-IMPORT-DRY-RUN-SCRIPT', 'validate_project_q_artifact_import_dry_run_script_v1.py'),
    ('PROJECT-Q-TRACK-F-ARTIFACT-IMPORT-APPROVAL-GATE-ROLLBACK', 'validate_project_q_artifact_import_approval_gate_rollback_v1.py'),
    ('PROJECT-Q-TRACK-G-ARTIFACT-RUNTIME-NO-LEAK', 'validate_project_q_artifact_runtime_no_leak_v1.py'),
    ('PROJECT-Q-TRACK-H-PROJECT-Q-COMPLETION-AND-NEXT-SYSTEM', 'validate_project_q_completion_and_next_system_v1.py'),
    # PROJECT_R STATUS SECOND SLICE DESIGN PACK (8 tracks, design-only: no runtime, no DB, no battle_engine mutation, no live env flag)
    ('PROJECT-R-TRACK-A-STATUS-SECOND-SLICE-SCOPE-AND-BOUNDARY', 'validate_project_r_status_second_slice_scope_v1.py'),
    ('PROJECT-R-TRACK-B-STATUS-SECOND-SLICE-BALANCE-AND-CAPS', 'validate_project_r_status_second_slice_balance_caps_v1.py'),
    ('PROJECT-R-TRACK-C-STATUS-SECOND-SLICE-SCHEMA-AND-FIXTURE-PLAN', 'validate_project_r_status_second_slice_schema_fixture_plan_v1.py'),
    ('PROJECT-R-TRACK-D-STATUS-SECOND-SLICE-RESOLVER-EXTENSION-DESIGN', 'validate_project_r_status_second_slice_resolver_extension_design_v1.py'),
    ('PROJECT-R-TRACK-E-STATUS-SECOND-SLICE-PAYLOAD-AND-NO-LEAK-PLAN', 'validate_project_r_status_second_slice_payload_no_leak_plan_v1.py'),
    ('PROJECT-R-TRACK-F-STATUS-SECOND-SLICE-ROLLBACK-AND-KILL-SWITCH-DESIGN', 'validate_project_r_status_second_slice_rollback_killswitch_v1.py'),
    ('PROJECT-R-TRACK-G-STATUS-SECOND-SLICE-QA-AND-RELEASE-GATE', 'validate_project_r_status_second_slice_qa_release_gate_v1.py'),
    ('PROJECT-R-TRACK-H-PROJECT-R-COMPLETION-AND-NEXT-PACK', 'validate_project_r_completion_and_next_pack_v1.py'),
    # PROJECT_S STATUS SECOND SLICE PURE RESOLVER PACK (8 tracks: pure resolver module created INERT, no runtime import, no battle_engine mutation, no DB)
    ('PROJECT-S-TRACK-A-SECOND-SLICE-PURE-RESOLVER-SPEC-LOCK', 'validate_project_s_second_slice_resolver_spec_lock_v1.py'),
    ('PROJECT-S-TRACK-B-STATUS-SECOND-SLICE-PURE-RESOLVER-MODULE', 'validate_project_s_second_slice_resolver_module_v1.py'),
    ('PROJECT-S-TRACK-C-SECOND-SLICE-GOLDEN-FIXTURE-MATRIX', 'validate_project_s_second_slice_golden_fixture_matrix_v1.py'),
    ('PROJECT-S-TRACK-D-SECOND-SLICE-CAPS-AND-STACKING-VALIDATOR', 'validate_project_s_second_slice_caps_stacking_v1.py'),
    ('PROJECT-S-TRACK-E-SECOND-SLICE-RUNTIME-NO-IMPORT-GUARD', 'validate_project_s_second_slice_runtime_no_import_guard_v1.py'),
    ('PROJECT-S-TRACK-F-SECOND-SLICE-ROLLBACK-AND-DELETION-PLAN', 'validate_project_s_second_slice_rollback_deletion_plan_v1.py'),
    ('PROJECT-S-TRACK-G-SECOND-SLICE-IMPLEMENTATION-RC-GATE', 'validate_project_s_second_slice_implementation_rc_gate_v1.py'),
    ('PROJECT-S-TRACK-H-PROJECT-S-COMPLETION-AND-NEXT-PACK', 'validate_project_s_completion_and_next_pack_v1.py'),
    # PROJECT_T STATUS SECOND SLICE SINGLE-POINT WIRING CANARY PACK (8 tracks; wiring applied flag-off-safe; flag OFF -> strict identity)
    ('PROJECT-T-TRACK-A-SECOND-SLICE-SINGLE-POINT-AUDIT', 'validate_project_t_second_slice_single_point_audit_v1.py'),
    ('PROJECT-T-TRACK-B-SECOND-SLICE-BATTLE-ENGINE-WIRING', 'validate_project_t_second_slice_battle_engine_wiring_v1.py'),
    ('PROJECT-T-TRACK-C-SECOND-SLICE-FLAG-OFF-BYTE-IDENTICAL-GUARD', 'validate_project_t_second_slice_flag_off_regression_v1.py'),
    ('PROJECT-T-TRACK-D-SECOND-SLICE-FLAG-ON-IN-PROCESS-CANARY', 'validate_project_t_second_slice_flag_on_canary_v1.py'),
    ('PROJECT-T-TRACK-E-SECOND-SLICE-PAYLOAD-AND-LOG-NO-LEAK-GUARD', 'validate_project_t_second_slice_payload_log_no_leak_v1.py'),
    ('PROJECT-T-TRACK-F-SECOND-SLICE-ROLLBACK-DRILL', 'validate_project_t_second_slice_rollback_drill_v1.py'),
    ('PROJECT-T-TRACK-G-SECOND-SLICE-DEV-CANARY-RC-GATE', 'validate_project_t_second_slice_dev_canary_rc_gate_v1.py'),
    ('PROJECT-T-TRACK-H-PROJECT-T-COMPLETION-AND-NEXT-PACK', 'validate_project_t_completion_and_next_pack_v1.py'),
    # PROJECT_U STATUS SECOND SLICE CANARY ENV FLAG FLIP PACK (8 tracks; flag flipped in-canary then rolled back OFF; .env post-rollback byte-identical to pre-flip backup)
    ('PROJECT-U-TRACK-A-SECOND-SLICE-CANARY-ENV-PRECHECK', 'validate_project_u_second_slice_canary_env_precheck_v1.py'),
    ('PROJECT-U-TRACK-B-SECOND-SLICE-CANARY-FLAG-FLIP', 'validate_project_u_second_slice_canary_flag_flip_v1.py'),
    ('PROJECT-U-TRACK-C-SECOND-SLICE-FLAG-ON-BEHAVIOR-SMOKE', 'validate_project_u_second_slice_flag_on_behavior_smoke_v1.py'),
    ('PROJECT-U-TRACK-D-SECOND-SLICE-CANARY-LIGHT-LOAD', 'validate_project_u_second_slice_canary_light_load_v1.py'),
    ('PROJECT-U-TRACK-E-SECOND-SLICE-PAYLOAD-LOG-NO-LEAK', 'validate_project_u_second_slice_payload_log_no_leak_v1.py'),
    ('PROJECT-U-TRACK-F-SECOND-SLICE-ROLLBACK-KILL-SWITCH-DRILL', 'validate_project_u_second_slice_rollback_kill_switch_v1.py'),
    ('PROJECT-U-TRACK-G-SECOND-SLICE-DEV-LIVE-READINESS-GATE', 'validate_project_u_second_slice_dev_live_readiness_gate_v1.py'),
    ('PROJECT-U-TRACK-H-PROJECT-U-COMPLETION-AND-NEXT-PACK', 'validate_project_u_completion_and_next_pack_v1.py'),
    # PROJECT_V STATUS SECOND SLICE DEV-LIVE ROLLOUT PACK (8 tracks; flag flipped in dev-live then rolled back OFF; .env post-rollback byte-identical to pre-flip backup; no DB writes; no battle_engine.py mutations)
    ('PROJECT-V-TRACK-A-SECOND-SLICE-DEV-LIVE-PRECHECK', 'validate_project_v_second_slice_dev_live_precheck_v1.py'),
    ('PROJECT-V-TRACK-B-SECOND-SLICE-DEV-LIVE-FLAG-ROLLOUT', 'validate_project_v_second_slice_dev_live_flag_rollout_v1.py'),
    ('PROJECT-V-TRACK-C-SECOND-SLICE-DEV-LIVE-BEHAVIOR-REGRESSION', 'validate_project_v_second_slice_dev_live_behavior_regression_v1.py'),
    ('PROJECT-V-TRACK-D-SECOND-SLICE-DEV-LIVE-EXTENDED-LOAD', 'validate_project_v_second_slice_dev_live_extended_load_v1.py'),
    ('PROJECT-V-TRACK-E-SECOND-SLICE-DEV-LIVE-PAYLOAD-LOG-METRICS-NO-LEAK', 'validate_project_v_second_slice_dev_live_payload_log_metrics_no_leak_v1.py'),
    ('PROJECT-V-TRACK-F-SECOND-SLICE-DEV-LIVE-ROLLBACK-KILL-SWITCH', 'validate_project_v_second_slice_dev_live_rollback_kill_switch_v1.py'),
    ('PROJECT-V-TRACK-G-SECOND-SLICE-PROD-READINESS-GATE-PREP', 'validate_project_v_second_slice_prod_readiness_gate_prep_v1.py'),
    ('PROJECT-V-TRACK-H-PROJECT-V-COMPLETION-AND-NEXT-PACK', 'validate_project_v_completion_and_next_pack_v1.py'),
    # PROJECT_W STATUS SECOND SLICE PROD ROLLOUT PACK (8 tracks; READY_NOT_APPLIED_PENDING_APPROVAL — no prod signatures present; no flag flip; no DB writes; no prod env touch; rollback paths documented per stage)
    ('PROJECT-W-TRACK-A-SECOND-SLICE-PROD-PRECHECK-SIGNATURE-GATE', 'validate_project_w_second_slice_prod_precheck_v1.py'),
    ('PROJECT-W-TRACK-B-SECOND-SLICE-PROD-STAGE-1', 'validate_project_w_second_slice_prod_stage_1_v1.py'),
    ('PROJECT-W-TRACK-C-SECOND-SLICE-PROD-STAGE-5', 'validate_project_w_second_slice_prod_stage_5_v1.py'),
    ('PROJECT-W-TRACK-D-SECOND-SLICE-PROD-STAGE-25', 'validate_project_w_second_slice_prod_stage_25_v1.py'),
    ('PROJECT-W-TRACK-E-SECOND-SLICE-PROD-STAGE-100', 'validate_project_w_second_slice_prod_stage_100_v1.py'),
    ('PROJECT-W-TRACK-F-SECOND-SLICE-PROD-FINAL-NO-LEAK-LOAD-ROLLBACK', 'validate_project_w_second_slice_prod_final_validation_v1.py'),
    ('PROJECT-W-TRACK-G-SECOND-SLICE-POST-PROD-DOD', 'validate_project_w_second_slice_post_prod_dod_v1.py'),
    ('PROJECT-W-TRACK-H-PROJECT-W-COMPLETION-AND-NEXT-SYSTEM', 'validate_project_w_completion_and_next_system_v1.py'),
    # PROJECT_X FRONTEND A NAVIGATION & FEATURE VISIBILITY AUDIT PACK (8 tracks; audit-only / roadmap-only; no frontend UI implementation; no backend mutation; no DB writes; no feature flag flips)
    ('PROJECT-X-TRACK-A-FRONTEND-ROUTE-AND-NAVIGATION-INVENTORY', 'validate_project_x_frontend_route_inventory_v1.py'),
    ('PROJECT-X-TRACK-B-BACKEND-FEATURE-ENDPOINT-VISIBILITY-MATRIX', 'validate_project_x_backend_feature_visibility_matrix_v1.py'),
    ('PROJECT-X-TRACK-C-PLAYER-SAFE-MENU-PLACEMENT-PLAN', 'validate_project_x_player_safe_menu_placement_plan_v1.py'),
    ('PROJECT-X-TRACK-D-FEATURE-ACCESS-POLICY-AND-LOCK-COPY', 'validate_project_x_feature_access_policy_lock_copy_v1.py'),
    ('PROJECT-X-TRACK-E-FRONTEND-SAFE-PREVIEW-IMPLEMENTATION-BACKLOG', 'validate_project_x_frontend_safe_preview_backlog_v1.py'),
    ('PROJECT-X-TRACK-F-LIVE-GATE-APPROVAL-MATRIX-UI-DEPENDENCIES', 'validate_project_x_live_gate_approval_matrix_ui_dependencies_v1.py'),
    ('PROJECT-X-TRACK-G-FRONTEND-QA-SMOKE-NAVIGATION-PLAN', 'validate_project_x_frontend_qa_smoke_navigation_plan_v1.py'),
    ('PROJECT-X-TRACK-H-PROJECT-X-COMPLETION-AND-NEXT-PACK', 'validate_project_x_completion_and_next_pack_v1.py'),
    # PROJECT_Y FRONTEND SAFE PREVIEW UI IMPLEMENTATION PACK (8 tracks; SafeFeatureCard + 3 nuove route preview locked/read-only; no menu mutation; no backend route mutation; no DB writes; no flag flips; 503 graceful)
    ('PROJECT-Y-TRACK-A-FRONTEND-SAFE-PREVIEW-TARGET-SELECTION', 'validate_project_y_safe_preview_target_selection_v1.py'),
    ('PROJECT-Y-TRACK-B-FRONTEND-LOCKED-CARD-COMPONENT', 'validate_project_y_locked_card_component_v1.py'),
    ('PROJECT-Y-TRACK-C-ARTIFACT-COLLECTION-PREVIEW-UI', 'validate_project_y_artifact_collection_preview_ui_v1.py'),
    ('PROJECT-Y-TRACK-D-HOUSING-PREVIEW-UI', 'validate_project_y_housing_preview_ui_v1.py'),
    ('PROJECT-Y-TRACK-E-STATUS-CODEX-PREVIEW-UI', 'validate_project_y_status_codex_preview_ui_v1.py'),
    ('PROJECT-Y-TRACK-F-SAFE-MENU-ENTRY-OR-DEV-PANEL', 'validate_project_y_safe_menu_entry_dev_panel_v1.py'),
    ('PROJECT-Y-TRACK-G-FRONTEND-QA-SMOKE-SAFE-PREVIEW', 'validate_project_y_frontend_qa_smoke_safe_preview_v1.py'),
    ('PROJECT-Y-TRACK-H-PROJECT-Y-COMPLETION-AND-NEXT-PACK', 'validate_project_y_completion_and_next_pack_v1.py'),
    # PROJECT_Z FRONTEND SAFE PREVIEW POLISH & MOBILE QA PACK (8 tracks; hub /safe-previews + 1 voce menu Altro + mobile polish 3 route + accessibility guard; no broad refactor; no new bottom tab; no live actions; expo-go mobile screenshot manual pending)
    ('PROJECT-Z-TRACK-A-SAFE-MENU-WIRING-TARGET-AUDIT', 'validate_project_z_safe_menu_wiring_target_audit_v1.py'),
    ('PROJECT-Z-TRACK-B-SAFE-MENU-OR-PREVIEW-HUB-WIRING', 'validate_project_z_safe_menu_or_preview_hub_wiring_v1.py'),
    ('PROJECT-Z-TRACK-C-ARTIFACT-PREVIEW-MOBILE-POLISH', 'validate_project_z_artifact_preview_mobile_polish_v1.py'),
    ('PROJECT-Z-TRACK-D-HOUSING-PREVIEW-MOBILE-POLISH', 'validate_project_z_housing_preview_mobile_polish_v1.py'),
    ('PROJECT-Z-TRACK-E-STATUS-CODEX-MOBILE-POLISH', 'validate_project_z_status_codex_mobile_polish_v1.py'),
    ('PROJECT-Z-TRACK-F-ACCESSIBILITY-AND-LOCKED-ACTION-GUARD', 'validate_project_z_accessibility_locked_action_guard_v1.py'),
    ('PROJECT-Z-TRACK-G-EXPO-GO-MOBILE-QA-SMOKE', 'validate_project_z_expo_go_mobile_qa_smoke_v1.py'),
    ('PROJECT-Z-TRACK-H-PROJECT-Z-COMPLETION-AND-NEXT-PACK', 'validate_project_z_completion_and_next_pack_v1.py'),
    # PROJECT_FRONTEND_B CORE USER FLOW AUDIT PACK (8 tracks; audit-only / roadmap-only; no UI/route/menu/backend/DB/flag mutation; mappa flussi core e produce QA backlog 12-item P1-P3)
    ('PROJECT-FRONTEND-B-TRACK-A-HEROES-FLOW-AUDIT', 'validate_project_frontend_b_heroes_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-B-COMBAT-FLOW-AUDIT', 'validate_project_frontend_b_combat_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-C-GACHA-FLOW-AUDIT', 'validate_project_frontend_b_gacha_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-D-ECONOMY-FLOW-AUDIT', 'validate_project_frontend_b_economy_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-E-SAFE-PREVIEW-FLOW-AUDIT', 'validate_project_frontend_b_safe_preview_flow_audit_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-F-NAVIGATION-RISK-MATRIX', 'validate_project_frontend_b_navigation_risk_matrix_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-G-QA-BACKLOG', 'validate_project_frontend_b_qa_backlog_v1.py'),
    ('PROJECT-FRONTEND-B-TRACK-H-PROJECT-FB-COMPLETION-AND-NEXT-PACK', 'validate_project_frontend_b_completion_and_next_pack_v1.py'),
    # PROJECT_J REQUIRED-CANDIDATE entries previously here have been PROMOTED to REQUIRED (see REQUIRED block above).
    # The 5 RC validators (resolver-pure-deterministic, no-tick-loop-touch, caps-respect, pvp-fairness-audit, rollback-runbook)
    # are now executed as part of the REQUIRED tier — authorized by PROJECT_K Track C.
]
BASELINE_DIFF = ('RM1.32-PRE', 'validate_hero_skill_kit_catalog_baseline_diff.py')


def run_one(script: Path, extra_args: list[str] | None = None) -> dict:
    if not script.exists():
        return {'present': False, 'exit_code': None, 'duration_s': 0.0, 'tail': '<missing>'}
    t0 = datetime.now(timezone.utc)
    try:
        env = dict(os.environ)
        env['SUITE_RUNNER_ACTIVE'] = '1'
        proc = subprocess.run(
            ['python3', str(script)] + (extra_args or []),
            capture_output=True, text=True, timeout=60, env=env,
        )
        tail = (proc.stdout or proc.stderr or '').strip().splitlines()
        tail = tail[-3:] if tail else ['<no output>']
        return {
            'present': True,
            'exit_code': proc.returncode,
            'duration_s': (datetime.now(timezone.utc) - t0).total_seconds(),
            'tail': '\n        '.join(tail),
        }
    except subprocess.TimeoutExpired:
        return {'present': True, 'exit_code': 124, 'duration_s': 60.0, 'tail': '<TIMEOUT>'}
    except Exception as e:
        return {'present': True, 'exit_code': -1, 'duration_s': 0.0, 'tail': f'<ERROR: {e}>'}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='run_hero_skill_kit_validator_suite')
    ap.add_argument('--json-out', help='Path under /app/backend/reports or /tmp to write the full report JSON')
    ap.add_argument('--include-baseline-diff', action='store_true',
                    help='Also run RM1.32-PRE baseline diff validator (off by default — baselines intentionally change in approved tasks)')
    ap.add_argument('--allow-changed', action='append', default=[],
                    help='Forwarded to baseline diff validator (only used with --include-baseline-diff). Repeatable.')
    ap.add_argument('--parallel', action='store_true',
                    help='PROJECT_B Track E — Run OPTIONAL validators concurrently via ThreadPoolExecutor. '
                         'REQUIRED validators always remain sequential. Output order is preserved; failures, '
                         'misses, exit codes, and SUPERSEDED markers are reported identically. Default: sequential (unchanged).')
    ap.add_argument('--parallel-workers', type=int, default=8,
                    help='Max worker threads for --parallel (default 8; clamped to 1..16).')
    args = ap.parse_args(argv)

    # AF2-N supersedence: when the runtime canary is active, V10/V11
    # validators that explicitly assert the pre-AF2-N "runtime OFF" state
    # are SUPERSEDED by their V12 counterparts. Mark them as SUPERSEDED
    # so the suite remains green post-canary.
    # V17: env vars may not be propagated to the suite's shell; fall back
    # to a live canary-status probe so detection is robust.
    af2n_active = os.environ.get('AFFINITY_GIFT_RUNTIME_ENABLED', '') == 'true_explicit_affinity_gift_runtime_on'
    inv_writes_active = os.environ.get('AFFINITY_GIFT_INVENTORY_WRITES_ENABLED', '') == 'true_explicit_affinity_inventory_on'
    stage2_applied = False
    stage3_applied = False
    if not (af2n_active and inv_writes_active) or True:  # always probe to also detect stage2/stage3
        try:
            import urllib.request as _u, urllib.error as _e
            with _u.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
                st = json.loads(r.read().decode())
            af2n_active = af2n_active or (st.get('feature_flag_currently_enabled') is True)
            inv_writes_active = inv_writes_active or (st.get('inventory_mutation_enabled') is True)
            stage2_applied = (st.get('canary_allowlist_size', 0) > 50) or (st.get('canary_ledger_cap', 0) > 500)
            stage3_applied = (st.get('canary_allowlist_size', 0) > 100) or (st.get('canary_ledger_cap', 0) > 1000)
        except Exception:
            pass
    SUPERSEDED_AFTER_AF2N = frozenset({
        # V6-V11 validators that explicitly assert pre-AF2-N "runtime OFF" state
        'AF2-G', 'AF2-H', 'AF2-I', 'AF2-J', 'AF2-K',
        'MEGA-COMBO-4', 'ULTRA-COMBO',
        'ULTRA-COMBO-V6', 'ULTRA-COMBO-V7', 'ULTRA-COMBO-V8', 'ULTRA-COMBO-V9',
        'V10-PREFLIGHT', 'AF2-M-SIGN-PRODUCT', 'ULTRA-COMBO-V10',
        'V11-PREFLIGHT', 'AF2-M-V4-ALL-SIGNOFFS', 'ULTRA-COMBO-V11',
        'AF2-N-GO-NOGO-PRE',  # this is by definition the pre-flip package
    }) if af2n_active else frozenset()
    SUPERSEDED_AFTER_INV_WRITES = frozenset({
        # Validators that assert ledger has 0 inventory_mutated / 0 affinity_points_mutated rows
        # or that canary-status has inventory_mutation_enabled=False
        'AF2-N-CANARY-SMOKE', 'AF2-N-ACTIVATION', 'SAFETY-ROLLUP-G', 'ULTRA-COMBO-V12',
        'AF2-N-MONITORING-WINDOW', 'AF2-N-STAGE1-PREP', 'AF2-N-INVENTORY-WIRING-PRE',
        'AF2-L-K6-LIVE-PREP2', 'SAFETY-ROLLUP-H', 'ULTRA-COMBO-V13',
        'V14-PREFLIGHT', 'AF2-N-STAGE1-APPLY', 'AF2-N-STAGE1-MONITORING',
        'AF2-N-INVENTORY-WIRING-SHADOW',
        'AF2-L-K6-PREP3-PROBE', 'AF2-N-STAGE1-ROLLBACK-READY',
        'SAFETY-ROLLUP-I', 'ULTRA-COMBO-V14',
        'V15-PREFLIGHT', 'AF2-N-INVENTORY-WIRING-APPLY',
        'AF2-N-INVENTORY-LIVE-MONITORING',
        'AF2-L-K6-V15-FALLBACK',
        'V15-ROLLBACK-READINESS', 'SAFETY-ROLLUP-J', 'ULTRA-COMBO-V15',
        # NOTE: AF2-N-STAGE1-EXTENDED-MONITORING-V15 is V16-aware (fixed) and remains active.
    }) if inv_writes_active else frozenset()
    # V17: Stage2 expansion (allowlist>50 or cap>500) supersedes V16 preflight
    # composite which assert exact stage1 sizes (allowlist==50, cap==500).
    SUPERSEDED_AFTER_STAGE2 = frozenset({
        'V16-PREFLIGHT', 'ULTRA-COMBO-V16',
    }) if stage2_applied else frozenset()
    # V18: Stage3 expansion (allowlist>100 or cap>1000) supersedes V17 preflight
    # and V17 composite which assert stage2 sizes (allowlist==100, cap==1000).
    SUPERSEDED_AFTER_STAGE3 = frozenset({
        'V17-PREFLIGHT', 'ULTRA-COMBO-V17',
        'AF2-N-INVENTORY-EXTENDED-MONITORING-V17', 'AF2-N-STAGE2-MONITORING-V17',
        'AF2-L-K6-LOCUST-READINESS-V17', 'V17-ROLLBACK-READINESS', 'SAFETY-ROLLUP-L',
    }) if stage3_applied else frozenset()
    # V19: Public UI preview implementation (file presence) supersedes V18 audit
    # and V18 composite which assert the entire frontend/ tree is unchanged.
    SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW = frozenset({
        'AF2-N-PUBLIC-UI-PREVIEW-SAFETY', 'ULTRA-COMBO-V18',
    }) if Path('/app/frontend/app/affinity-gifts-preview.tsx').exists() else frozenset()
    # V21: Rate-limit active supersedes pre-AF2N load probes / rollups that
    # blast the gift-spend endpoint expecting 423 — they now get 429 once
    # burst threshold is hit. The behavior is still safe (no DB write), but
    # these validators predate the rate-limit guard.
    rate_limit_active = os.environ.get('AFFINITY_GIFT_RATE_LIMIT_ENABLED', '') == 'true_explicit_affinity_rate_limit_on'
    if not rate_limit_active:
        try:
            import urllib.request as _u2
            with _u2.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
                _st2 = json.loads(r.read().decode())
            rate_limit_active = bool(_st2.get('rate_limit_enabled'))
        except Exception:
            pass
    SUPERSEDED_AFTER_RATE_LIMIT = frozenset({
        # Old pre-V12 load probes hit gift-spend many times and now meet 429.
        'AF2-L-FULL',
        'SAFETY-ROLLUP-D', 'SAFETY-ROLLUP-E', 'SAFETY-ROLLUP-F',
        'AF2-L-K6-PREP',
    }) if rate_limit_active else frozenset()
    # V21: Stage4 applied (allowlist>200 OR cap>2500) supersedes V20 hard-coded
    # assertions of allowlist==200, cap==2500, signoff PENDING, plan stage4_applied=false,
    # apply/rollback scripts NOT present.
    try:
        from pathlib import Path as _P
        _stage4_applied_marker = _P('/app/data/design/affinity/af2n_stage4_internal_beta_apply_result_v1.json')
        stage4_applied = False
        if _stage4_applied_marker.exists():
            _d = json.loads(_stage4_applied_marker.read_text())
            stage4_applied = bool(_d.get('stage4_applied'))
    except Exception:
        stage4_applied = False
    SUPERSEDED_AFTER_STAGE4 = frozenset({
        'V20-PREFLIGHT',
        'AF2-N-STAGE4-INTERNAL-BETA-PLAN',
        'AF2-N-STAGE4-SIGNOFF-PACKAGE-V5',
        'ULTRA-COMBO-V20',
        'ULTRA-COMBO-V19',  # asserts allowlist<=500, broken post-Stage4 (700)
    }) if stage4_applied else frozenset()
    # V21: Stage4 apply/rollback script presence supersedes V20 composite which
    # asserts these scripts do NOT exist. Mark V20 composite SUPERSEDED once we
    # ship the V21 apply/rollback scripts.
    v21_apply_script_present = Path('/app/backend/scripts/apply_af2n_stage4_internal_beta.py').exists()
    v21_rollback_script_present = Path('/app/backend/scripts/rollback_af2n_stage4_internal_beta.py').exists()
    SUPERSEDED_AFTER_V21_SCRIPTS = frozenset({
        'ULTRA-COMBO-V20',
    }) if (v21_apply_script_present and v21_rollback_script_present) else frozenset()
    # PROJECT_E Track A — SLC v1 cluster supersedence (post SLC-G commit-A multishard baseline).
    # The 8 v1 OPTIONAL validators of the SLC-C/D/BE/F cluster enforce the obsolete
    # invariant `multishard==design-only` which no longer holds post SLC-G commit-A.
    # PROJECT_E ships 8 v2 successors that validate the current post-SLC-G safety
    # invariants without weakening coverage. The v1 cluster is SUPERSEDED unless
    # the operator explicitly opts-in to historical execution via env var
    # SUITE_KEEP_DEPRECATED_AUDITS=true (default OFF). When OFF, the suite reports
    # them as [SUPERSEDED] (--), preserving honest evidence in the JSON report.
    project_e_v2_successors_present = all(
        Path(f'/app/backend/scripts/{s}').exists() for s in (
            'validate_slc_c_repo_multishard_post_g_invariant_v2.py',
            'validate_slc_c_combo_v2.py',
            'validate_slc_d_preflight_v2.py',
            'validate_slc_d_merge_tooling_combo_v2.py',
            'validate_slc_be_preflight_v2.py',
            'validate_slc_be_server_profile_selection_combo_v2.py',
            'validate_slc_f_preflight_v2.py',
            'validate_slc_f_route_patch_dryrun_combo_v2.py',
        )
    )
    keep_deprecated = os.environ.get('SUITE_KEEP_DEPRECATED_AUDITS', '').strip().lower() == 'true'
    SUPERSEDED_AFTER_PROJECT_E_V2 = frozenset({
        'SLC-C-REPO-PREFLIGHT', 'SLC-C-COMBO',
        'SLC-D-PREFLIGHT', 'SLC-D-COMBO',
        'SLC-BE-PREFLIGHT', 'SLC-BE-COMBO',
        'SLC-F-PREFLIGHT', 'SLC-F-COMBO',
    }) if (project_e_v2_successors_present and not keep_deprecated) else frozenset()
    # PROJECT_F Track B — authorized creation of disabled-by-default /api/housing/preview
    # skeleton. The 12 historical OPTIONAL validators below asserted "no /api/housing route
    # exists" or "housing_preview not implemented". Those negative-existence invariants are
    # legitimately superseded by the new Pack-F authorized invariant enforced by
    # validate_project_f_housing_read_only_preview.py (route exists, 503 by default, no DB
    # writes, no live bonus, no resolver import). The historical v1 validators remain
    # physically on disk (no delete) and are reported as [SUPERSEDED] (--) to preserve
    # honest evidence in the JSON report. The successor validator is OPTIONAL and PASS by
    # default. No REQUIRED validator is touched; no fake PASS; no hiding of fresh failures.
    project_f_track_b_skeleton_present = (
        Path('/app/backend/routes/housing_preview.py').exists() and
        Path('/app/backend/scripts/validate_project_f_housing_read_only_preview.py').exists() and
        Path('/app/data/design/housing/project_f_housing_read_only_preview_contract_v1.json').exists()
    )
    SUPERSEDED_AFTER_PROJECT_F_TRACK_B = frozenset({
        'SLC-F-BATCH-0-1-POST-APPLY',
        'SLC-F-BATCH-1B-POST-APPLY',
        'SLC-F-BATCH-2-POST-APPLY',
        'SLC-F-EQUIPMENT-SCOPE-POST-APPLY',
        'SLC-F-RAIDS-EQUIPMENT-SCOPE-POST-APPLY',
        'SLC-F-GVG-WAR-SCOPE-POST-APPLY',
        'SLC-F-UNIQUE-ITEMS-SCOPE-POST-APPLY',
        'SLC-F-COSMETICS-SCHEMA-SPLIT-REFACTOR-V1',
        'PROJECT-B-TRACK-B-HOUSING-RESOLVER-STUB-INERT',
        'PROJECT-C-TRACK-B-HOUSING-RESOLVER-INTEGRATION-DESIGN',
        'PROJECT-D-TRACK-B-HOUSING-RESOLVER-PHASE2-TESTS',
        'PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN',
    }) if (project_f_track_b_skeleton_present and not keep_deprecated) else frozenset()
    SUPERSEDED = (SUPERSEDED_AFTER_AF2N | SUPERSEDED_AFTER_INV_WRITES
                  | SUPERSEDED_AFTER_STAGE2 | SUPERSEDED_AFTER_STAGE3
                  | SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW
                  | SUPERSEDED_AFTER_RATE_LIMIT
                  | SUPERSEDED_AFTER_STAGE4
                  | SUPERSEDED_AFTER_V21_SCRIPTS
                  | SUPERSEDED_AFTER_PROJECT_E_V2
                  | SUPERSEDED_AFTER_PROJECT_F_TRACK_B)

    results: list[dict] = []
    any_required_fail = False

    print('RM1.31-B — Hero Skill Kit Validator Suite Runner')
    if af2n_active:
        print('  (AF2-N canary ACTIVE — pre-AF2-N validators marked SUPERSEDED)')
    if inv_writes_active:
        print('  (AF2-N inventory writes ACTIVE — V12-V15 pre-inventory-on validators marked SUPERSEDED)')
    if stage2_applied:
        print('  (Stage2 expansion DETECTED — V16 preflight + V16 composite marked SUPERSEDED)')
    if stage3_applied:
        print('  (Stage3 expansion DETECTED — V17 preflight + V17 composite + V17 sub-validators marked SUPERSEDED)')
    print('=' * 70)
    print(f'{"TASK":10s} {"SCRIPT":54s} {"EXIT":>5s}')
    print('-' * 70)
    for task, name in REQUIRED:
        if task in SUPERSEDED:
            print(f'{task:10s} {name:54s} {"--":>5s}  [SUPERSEDED]')
            results.append({'task': task, 'script': name, 'required': True, 'status': 'SUPERSEDED'})
            continue
        r = run_one(SCRIPTS_DIR / name)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        if status != 'PASS':
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': True, 'status': status, **r})

    print('-- optional --')
    if args.parallel:
        # PROJECT_B Track E — concurrent OPTIONAL execution; output order preserved.
        from concurrent.futures import ThreadPoolExecutor
        max_workers = max(1, min(16, int(args.parallel_workers or 8)))
        tasks_to_run: list[tuple[int, str, str]] = []
        cached_results: dict[int, dict] = {}
        for idx, (task, name) in enumerate(OPTIONAL):
            if task in SUPERSEDED:
                cached_results[idx] = {'task': task, 'script': name, 'required': False, 'status': 'SUPERSEDED'}
            else:
                tasks_to_run.append((idx, task, name))
        if tasks_to_run:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_map = {executor.submit(run_one, SCRIPTS_DIR / name): (idx, task, name)
                              for idx, task, name in tasks_to_run}
                for future in future_map:
                    idx, task, name = future_map[future]
                    try:
                        r = future.result()
                    except Exception as exc:  # noqa: BLE001
                        r = {'present': False, 'exit_code': 1, 'stdout': '', 'stderr': f'parallel exec error: {exc}'}
                    status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
                    cached_results[idx] = {'task': task, 'script': name, 'required': False, 'status': status, **r}
        # Print in original order to preserve identical output ordering.
        for idx, (task, name) in enumerate(OPTIONAL):
            entry = cached_results[idx]
            if entry.get('status') == 'SUPERSEDED':
                print(f'{task:10s} {name:54s} {"--":>5s}  [SUPERSEDED]')
                results.append(entry)
                continue
            if entry.get('present') and entry.get('exit_code') not in (0, None):
                any_required_fail = True
            print(f'{task:10s} {name:54s} {entry["exit_code"]!s:>5s}  [{entry["status"]}]')
            results.append(entry)
    else:
        for task, name in OPTIONAL:
            if task in SUPERSEDED:
                print(f'{task:10s} {name:54s} {"--":>5s}  [SUPERSEDED]')
                results.append({'task': task, 'script': name, 'required': False, 'status': 'SUPERSEDED'})
                continue
            r = run_one(SCRIPTS_DIR / name)
            status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
            # Optional: don't fail suite if MISS, but fail if explicit FAIL
            if r['present'] and r['exit_code'] not in (0, None):
                any_required_fail = True
            print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
            results.append({'task': task, 'script': name, 'required': False, 'status': status, **r})
    if args.include_baseline_diff:
        print('-- baseline diff (RM1.32-PRE) --')
        task, name = BASELINE_DIFF
        extra: list[str] = []
        for p in (args.allow_changed or []):
            extra.extend(['--allow-changed', p])
        r = run_one(SCRIPTS_DIR / name, extra_args=extra)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        if r['present'] and r['exit_code'] not in (0, None):
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': True, 'status': status, **r})
    print('=' * 70)

    overall = 'PASS' if not any_required_fail else 'FAIL'
    n_pass = sum(1 for r in results if r['status'] == 'PASS')
    n_fail = sum(1 for r in results if r['status'] == 'FAIL')
    n_miss = sum(1 for r in results if r['status'] == 'MISS')
    print(f'Overall: {overall}  (pass={n_pass}, fail={n_fail}, miss={n_miss})')

    if args.json_out:
        out = Path(args.json_out).resolve()
        if not any(str(out).startswith(str(s.resolve())) for s in SAFE_REPORT_DIRS):
            print(f'REJECTED --json-out: "{out}" outside allowed dirs {[str(s) for s in SAFE_REPORT_DIRS]}')
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            'suite': 'RM1.31-B',
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'overall': overall,
            'counts': {'pass': n_pass, 'fail': n_fail, 'miss': n_miss},
            'results': results,
        }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'JSON report written: {out}')

    return 0 if overall == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
