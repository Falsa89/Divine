#!/usr/bin/env python3
# INLINE_CONFIRM Track E — API contract kept + no formula change.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_e_api_contract_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
B = Path('/app/backend/routes/soul_forge.py')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_E_API_CONTRACT_KEPT_NO_FORMULA_CHANGE_READY'
    assert d['normalize_helper_present'] is True
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert d['reward_formula_change'] is False
    # invariants
    assert md5(BE) == d['battle_engine_md5']
    assert md5(ENV) == d['backend_env_md5']
    # frontend still uses /api/soul/forge
    t = F.read_text()
    assert "apiCall('/api/soul/forge'" in t, 'frontend must still call /api/soul/forge'
    assert 'normalizeForgeResponse' in t
    # backend still has the endpoint and formula constants
    bt = B.read_text()
    assert '@router.post("/soul/forge")' in bt
    assert 'SOUL_ESSENCE_VALUES' in bt and 'LEVEL_BONUS_RATE' in bt
    print('[PASS] INLINE_CONFIRM Track E API contract kept, no formula change')
    return 0
if __name__ == '__main__': sys.exit(main())
