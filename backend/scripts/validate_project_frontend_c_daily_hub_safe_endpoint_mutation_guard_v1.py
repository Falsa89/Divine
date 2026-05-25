#!/usr/bin/env python3
import json, sys, re, hashlib
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_safe_endpoint_mutation_guard_v1.json')
ROUTE = Path('/app/frontend/app/daily-hub.tsx')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
MUTATING_API = [r'/api/mail/claim', r'/api/events/claim', r'/api/achievements/claim', r'/api/battlepass/claim', r'/api/shop/daily/claim', r'/api/gacha/pull', r'/api/artifacts/pull', r'/api/server-profiles/select', r'/api/housing/preview']

def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_E_DAILY_HUB_SAFE_ENDPOINT_AND_MUTATION_GUARD_READY'
    assert m['mutating_api_calls'] == 0
    assert m['GET_endpoint_calls'] == 0
    assert m['POST_PUT_DELETE_PATCH_calls'] == 0
    assert m['claim_buttons'] == 0
    assert m['router_push_only'] is True
    assert m['backend_route_added'] is False
    text = ROUTE.read_text()
    assert 'fetch(' not in text
    for pat in MUTATING_API:
        assert not re.search(pat, text), f'forbidden api ref: {pat}'
    # backend integrity
    assert hashlib.md5(BE.read_bytes()).hexdigest() == '151ca35ad3bc35f0a6209cb3744ed440'
    assert hashlib.md5(ENV.read_bytes()).hexdigest() == 'ff60bbb79efa329b71aa8ed351ea89b3'
    print('[PASS] FC Track E endpoint/mutation guard READY — mutating=0, GET=0, fetch=0, battle_engine_intact=True, env_intact=True')
    return 0
if __name__ == '__main__': sys.exit(main())
