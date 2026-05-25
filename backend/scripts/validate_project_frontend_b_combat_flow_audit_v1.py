#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_b_combat_flow_audit_v1.json')
BE = Path('/app/backend/battle_engine.py')
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_B_COMBAT_AND_POST_BATTLE_FLOW_AUDIT_READY'
    assert m['audit_only'] is True
    # battle_engine.py must remain integro
    assert hashlib.md5(BE.read_bytes()).hexdigest() == '151ca35ad3bc35f0a6209cb3744ed440'
    assert any('battle_engine' in s for s in m['do_not_touch'])
    assert any('combat.tsx' in s for s in m['do_not_touch'])
    assert len(m['flow_steps']) >= 6
    print(f'[PASS] FB Track B combat flow audit READY — routes={len(m["routes_audited"])}, gaps={len(m["gaps_identified"])}, battle_engine_intact=True')
    return 0
if __name__ == '__main__': sys.exit(main())
