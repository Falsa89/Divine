#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_ui_route_implementation_v1.json')
ROUTE = Path('/app/frontend/app/daily-hub.tsx')
FORBIDDEN_TOKENS = [r'\bClaim all\b', r'\bRiscatta tutto\b', r'\bReclama\b', r'\bRiscatta ora\b']
FORBIDDEN_API = [r'/api/mail/claim', r'/api/events/claim', r'/api/achievements/claim', r'/api/battlepass/claim', r'/api/shop/daily/claim', r'/api/gacha/pull', r'/api/server-profiles/select', r'/api/housing/preview']
MUTATING_HTTP = [r"method:\s*['\"]POST", r"method:\s*['\"]PUT", r"method:\s*['\"]DELETE", r"method:\s*['\"]PATCH"]

def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_B_DAILY_HUB_UI_ROUTE_IMPLEMENTATION_READY'
    assert ROUTE.exists(), 'daily-hub.tsx missing'
    text = ROUTE.read_text()
    for pat in FORBIDDEN_TOKENS:
        assert not re.search(pat, text, flags=re.IGNORECASE), f'forbidden token {pat}'
    for pat in FORBIDDEN_API:
        assert not re.search(pat, text), f'forbidden api call {pat}'
    for pat in MUTATING_HTTP:
        assert not re.search(pat, text), f'forbidden http method {pat}'
    # no fetch call at all
    assert 'fetch(' not in text, 'daily-hub should NOT call any fetch endpoint'
    assert m['mutating_api_calls_count'] == 0
    assert m['claim_buttons_count'] == 0
    assert m['new_bottom_tab'] is False
    assert m['broad_navigation_refactor'] is False
    print(f'[PASS] FC Track B route impl READY — entries={m["entries_count"]}, claim_buttons=0, mutating_calls=0, fetch_calls=0')
    return 0
if __name__ == '__main__': sys.exit(main())
