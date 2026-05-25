#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_frontend_qa_smoke_v1.json')
ROUTE = Path('/app/frontend/app/daily-hub.tsx')
FORBIDDEN = [r'Riscatta tutto', r'Claim all', r'Reclama', r'Riscatta ora', r'Apri tutto']
ROUTER_TARGETS = ['/mail', '/events', '/achievements', '/battlepass', '/shop']

def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_G_DAILY_HUB_FRONTEND_QA_SMOKE_READY'
    assert m['fake_screenshot_verification'] is False
    static = m['static_smoke']
    assert static['route_compile'] == 'PASS'
    assert static['only_navigation_actions'] is True
    text = ROUTE.read_text()
    for pat in FORBIDDEN:
        assert not re.search(pat, text, flags=re.IGNORECASE), f'forbidden label {pat}'
    for t in ROUTER_TARGETS:
        assert f"'{t}'" in text, f'router target {t} missing'
    # Verify each target file exists
    targets_exist = 0
    for t in ROUTER_TARGETS:
        name = t.lstrip('/')
        if Path(f'/app/frontend/app/{name}.tsx').exists():
            targets_exist += 1
    assert targets_exist == len(ROUTER_TARGETS), f'only {targets_exist}/{len(ROUTER_TARGETS)} target files exist'
    print(f'[PASS] FC Track G QA smoke READY — route_compile=PASS, router_targets={targets_exist}/{len(ROUTER_TARGETS)} exist, forbidden_labels=0, manual_checks={len(m["manual_qa_checklist"])}')
    return 0
if __name__ == '__main__': sys.exit(main())
