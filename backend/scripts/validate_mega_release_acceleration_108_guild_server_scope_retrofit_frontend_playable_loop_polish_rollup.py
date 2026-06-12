#!/usr/bin/env python3
"""MEGA RELEASE ACCELERATION 108 — Guild Server-Scope Retrofit + Frontend
Playable Loop Polish ROLLUP.

Verifica che TUTTI i validatori Pack 108 siano stati creati e che il
final report Pack 108 esista. Non lancia gli altri validator: la master
suite li eseguirà individualmente.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_v110_pack_108_sot.py',
    'validate_v110_pack_108_guild_strict_endpoints.py',
    'validate_v110_pack_108_guild_legacy_quarantine.py',
    'validate_v110_pack_108_guild_reward_lock.py',
    'validate_v110_pack_108_arena_pvp_event_preservation.py',
    'validate_v110_pack_108_frontend_playable_loop_map.py',
    'validate_v110_pack_108_frontend_ui_flags_default_off.py',
    'validate_v110_pack_108_server_switch_refresh_guard.py',
    'validate_v110_pack_108_locked_deferred_ui_copy_audit.py',
    'validate_v110_pack_108_runtime_smoke_e2e.py',
    'validate_v110_pack_108_static_anti_leak_guard.py',
    'validate_v110_pack_108_data_invariants.py',
    'validate_v110_pack_108_gate_invariant_preservation.py',
    'validate_v110_pack_108_cleanup_rollback.py',
    'validate_v110_pack_108_live_readiness_update.py',
    'smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), s

final_report = os.path.join(R, 'docs/divine/110_GUILD_SERVER_SCOPE_RETROFIT_FRONTEND_PLAYABLE_LOOP_POLISH_FINAL_REPORT.md')
assert os.path.exists(final_report), final_report
rep = open(final_report).read().lower()
for token in ('pack 108', 'verdict', 'reward_live_general', 'release_readiness_claimed',
              'guild_legacy_quarantined', 'pack_108_test_artifact'):
    assert token in rep, f'final report token missing: {token}'

print('[MEGA_RELEASE_ACCELERATION_108_ROLLUP] OK fifteen_validators_present smoke_script_present final_report_present')
