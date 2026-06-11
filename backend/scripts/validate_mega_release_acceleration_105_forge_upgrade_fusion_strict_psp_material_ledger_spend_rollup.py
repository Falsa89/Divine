#!/usr/bin/env python3
"""Pack 105 — Rollup validator (runs all 10 Pack 105 sub-validators)."""
import os, sys, subprocess
R = os.path.dirname(os.path.abspath(__file__))
VALIDATORS = [
    'validate_v110_pack_105_sot.py',
    'validate_v110_pack_105_reward_source.py',
    'validate_v110_pack_105_forge_endpoints.py',
    'validate_v110_pack_105_forge_catalog.py',
    'validate_v110_pack_105_static_anti_leak.py',
    'validate_v110_pack_105_runtime_smoke_e2e.py',
    'validate_v110_pack_105_data_invariants.py',
    'validate_v110_pack_105_live_readiness_update.py',
    'validate_v110_pack_105_gate_invariant_preservation.py',
    'validate_v110_pack_105_cleanup_rollback.py',
]
failed = []
for v in VALIDATORS:
    p = subprocess.run([sys.executable, os.path.join(R, v)], capture_output=True, text=True)
    if p.returncode != 0:
        print(f'[FAIL] {v}'); print(p.stdout); print(p.stderr); failed.append(v)
    else:
        print(f'[PASS] {v}')
if failed:
    print(f'[v110 MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_ROLLUP] BLOCKED failed={failed}')
    sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_ROLLUP] OK all_10_validators_passed')
print('PUBLIC_SYNC_TAG_v110_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SUPERPACK')
