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
    SUPERSEDED = (SUPERSEDED_AFTER_AF2N | SUPERSEDED_AFTER_INV_WRITES
                  | SUPERSEDED_AFTER_STAGE2 | SUPERSEDED_AFTER_STAGE3
                  | SUPERSEDED_AFTER_PUBLIC_UI_PREVIEW
                  | SUPERSEDED_AFTER_RATE_LIMIT
                  | SUPERSEDED_AFTER_STAGE4
                  | SUPERSEDED_AFTER_V21_SCRIPTS)

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
