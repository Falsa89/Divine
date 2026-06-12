#!/usr/bin/env python3
"""Pack 107 — Rollup validator."""
import os, sys, subprocess
R = os.path.dirname(os.path.abspath(__file__))
VALIDATORS = [
    'validate_v110_pack_107_sot.py',
    'validate_v110_pack_107_competitive_guards_endpoints.py',
    'validate_v110_pack_107_arena_audit.py',
    'validate_v110_pack_107_pvp_audit.py',
    'validate_v110_pack_107_guild_audit.py',
    'validate_v110_pack_107_event_audit.py',
    'validate_v110_pack_107_runtime_smoke_e2e.py',
    'validate_v110_pack_107_data_invariants.py',
    'validate_v110_pack_107_gate_invariant_preservation.py',
    'validate_v110_pack_107_cleanup_rollback.py',
]
failed = []
for v in VALIDATORS:
    p = subprocess.run([sys.executable, os.path.join(R, v)], capture_output=True, text=True)
    if p.returncode != 0:
        print(f'[FAIL] {v}'); print(p.stdout); print(p.stderr); failed.append(v)
    else: print(f'[PASS] {v}')
if failed:
    print(f'[v110 MEGA_RELEASE_ACCELERATION_107_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_ROLLUP] BLOCKED failed={failed}'); sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_107_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_ROLLUP] OK all_10_validators_passed')
print('PUBLIC_SYNC_TAG_v110_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_SUPERPACK')
