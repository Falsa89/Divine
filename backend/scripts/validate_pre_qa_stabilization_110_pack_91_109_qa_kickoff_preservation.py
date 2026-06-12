#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Pack 91-109 + QA Kickoff preservation."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = open(os.path.join(R, 'backend/scripts/run_hero_skill_kit_validator_suite.py')).read()
for reg in (
    'mega_release_acceleration_104_shop_soul_equipment_forge_strict_writes_rollup',
    'mega_release_acceleration_105_forge_upgrade_fusion_strict_psp_material_ledger_spend_rollup',
    'mega_release_acceleration_106_mail_achievements_daily_weekly_controlled_rewards_rollup',
    'mega_release_acceleration_107_arena_pvp_guild_events_server_scope_guards_rollup',
    'mega_release_acceleration_108_guild_server_scope_retrofit_frontend_playable_loop_polish_rollup',
    'mega_release_acceleration_109_closed_alpha_rc_sweep_and_release_gate_rollup',
):
    assert reg in SUITE, f'rollup not registered: {reg}'
# QA kickoff artifacts still present.
for p in ('docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_TESTER_RUNBOOK.md',
          'docs/divine/111_CLOSED_ALPHA_INTERNAL_QA_KICKOFF_AND_FEEDBACK_REPORT.md',
          'docs/divine/templates/qa_tester_feedback_form.md',
          'docs/divine/templates/qa_bug_triage_matrix.md',
          'backend/scripts/qa_safety_invariants_probe.py'):
    assert os.path.exists(os.path.join(R, p)), f'QA kickoff artifact missing: {p}'
print('[v110 PRE_QA_110_PACK_91_109_QA_KICKOFF_PRESERVATION] OK six_rollups_registered qa_kickoff_artifacts_intact')
