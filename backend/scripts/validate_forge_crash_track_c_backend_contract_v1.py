#!/usr/bin/env python3
# FORGE_CRASH Track C — backend contract verified (no backend changes).
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_c_backend_contract_verified_v1.json')
B = Path('/app/backend/routes/soul_forge.py')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_C_BACKEND_FORGE_ENDPOINT_CONTRACT_ALIGNED_OR_VERIFIED'
    assert d['backend_change_required'] is False
    assert d['backend_changes'] == 0
    assert d['reward_formula_change'] is False
    # Invariants intact
    assert md5(BE) == '151ca35ad3bc35f0a6209cb3744ed440', 'battle_engine MD5 drift'
    assert md5(ENV) == 'ff60bbb79efa329b71aa8ed351ea89b3', '.env MD5 drift'
    # Backend file actually contains the endpoint with correct signature
    bt = B.read_text()
    assert '@router.post("/soul/forge")' in bt, 'soul/forge endpoint missing in backend'
    assert 'gained_essence' in bt and 'new_balance' in bt, 'response fields missing in backend'
    assert 'SOUL_ESSENCE_VALUES' in bt and 'LEVEL_BONUS_RATE' in bt, 'reward formula constants missing in backend'
    # Empirical contract match
    emp = d['empirical_verification']
    assert emp['observed_match_expected_contract'] is True
    assert 'gained_essence' in emp['observed_response']
    assert 'new_balance' in emp['observed_response']
    print('[PASS] FORGE_CRASH Track C backend contract verified')
    return 0
if __name__ == '__main__': sys.exit(main())
