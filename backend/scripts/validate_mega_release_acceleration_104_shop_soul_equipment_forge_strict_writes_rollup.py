#!/usr/bin/env python3
"""Pack 104 — Rollup validator (runs all 10 Pack 104 sub-validators)."""
import os, sys, subprocess
R = os.path.dirname(os.path.abspath(__file__))
VALIDATORS = [
    'validate_v110_pack_104_sot.py',
    'validate_v110_pack_104_reward_source.py',
    'validate_v110_pack_104_economy_endpoints.py',
    'validate_v110_pack_104_shop_catalog.py',
    'validate_v110_pack_104_static_anti_leak.py',
    'validate_v110_pack_104_runtime_smoke_e2e.py',
    'validate_v110_pack_104_data_invariants.py',
    'validate_v110_pack_104_live_readiness_update.py',
    'validate_v110_pack_104_gate_invariant_preservation.py',
    'validate_v110_pack_104_cleanup_rollback.py',
]
failed = []
for v in VALIDATORS:
    p = subprocess.run([sys.executable, os.path.join(R, v)], capture_output=True, text=True)
    if p.returncode != 0:
        print(f'[FAIL] {v}'); print(p.stdout); print(p.stderr); failed.append(v)
    else:
        print(f'[PASS] {v}')
if failed:
    print(f'[v110 MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_ROLLUP] BLOCKED failed={failed}')
    sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_ROLLUP] OK all_10_validators_passed')
print('PUBLIC_SYNC_TAG_v110_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_SUPERPACK')
