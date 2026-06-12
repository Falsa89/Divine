#!/usr/bin/env python3
"""Pack 109 — Pack 91-108 preservation rollup matrix.

Verifica che TUTTI i rollup precedenti esistano e siano registrati nella
master suite.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = open(os.path.join(R, 'backend/scripts/run_hero_skill_kit_validator_suite.py')).read()
ROLLUPS = (
    'validate_mega_release_acceleration_104_shop_soul_equipment_forge_strict_writes_rollup.py',
    'validate_mega_release_acceleration_105_forge_upgrade_fusion_strict_psp_material_ledger_spend_rollup.py',
    'validate_mega_release_acceleration_106_mail_achievements_daily_weekly_controlled_rewards_rollup.py',
    'validate_mega_release_acceleration_107_arena_pvp_guild_events_server_scope_guards_rollup.py',
    'validate_mega_release_acceleration_108_guild_server_scope_retrofit_frontend_playable_loop_polish_rollup.py',
)
for rp in ROLLUPS:
    assert os.path.exists(os.path.join(R, 'backend/scripts', rp)), f'missing rollup file: {rp}'
    assert rp in SUITE, f'rollup not registered in suite: {rp}'
print('[v110 PACK_109_PACK_91_108_PRESERVATION] OK five_previous_rollups_present_and_registered')
