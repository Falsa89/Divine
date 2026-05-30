#!/usr/bin/env python3
"""
PROJECT_HOME_MENU_REWIRING validator (statico, OPTIONAL).

Asserisce:
  - 5 JSON design tracks (A..E) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_HOME_MENU_REWIRING
  - MD5 invarianti baseline su 5 file protetti
  - frontend/app/_layout.tsx UNTOUCHED (no diff su file; verifica via grep coerenza)
  - frontend/app/(tabs)/home.tsx contiene router.push('/guide') e router.push('/tower-of-the-hells')
  - frontend/app/(tabs)/home.tsx NON contiene piu' router.push('/tower') al di fuori di commenti
  - frontend/app/(tabs)/menu.tsx contiene route '/guide' e route '/tower-of-the-hells'
  - frontend/app/(tabs)/menu.tsx NON contiene piu' route '/tower' al di fuori di commenti
  - frontend/app/guide.tsx esiste
  - frontend/app/tower-of-the-hells.tsx esiste
  - locks attivi su shop / item-shop / battlepass / vip
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/home_menu_rewiring'

REQUIRED_JSON = {
    'navigation_surface_audit_v1.json':              'TRACK_A_NAVIGATION_SURFACE_AUDIT_READY',
    'safe_menu_rewiring_implementation_v1.json':     'TRACK_B_SAFE_MENU_REWIRING_IMPLEMENTATION_READY',
    'mode_discoverability_registry_update_v1.json':  'TRACK_C_MODE_DISCOVERABILITY_REGISTRY_UPDATE_READY',
    'guide_and_tower_smoke_checks_v1.json':          'TRACK_D_GUIDE_AND_TOWER_SMOKE_CHECKS_READY',
    'mobile_qa_and_ui_policy_v1.json':               'TRACK_E_MOBILE_QA_AND_UI_POLICY_READY',
}
PROOF_MARKER = DIR / 'home_menu_rewiring_suite_registration_proof_marker_v1.json'

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}

HOME = ROOT / 'frontend/app/(tabs)/home.tsx'
MENU = ROOT / 'frontend/app/(tabs)/menu.tsx'
GUIDE = ROOT / 'frontend/app/guide.tsx'
TOWER = ROOT / 'frontend/app/tower-of-the-hells.tsx'

# Strip JS comments (line // and block /* */) for executable-code checks
JS_LINE_COMMENT = re.compile(r'//[^\n]*')
JS_BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)


def strip_js_comments(text: str) -> str:
    s = JS_BLOCK_COMMENT.sub('', text)
    s = JS_LINE_COMMENT.sub('', s)
    return s


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    # 1) MD5 invariants
    for rel, exp in MD5_INVARIANTS.items():
        p = ROOT / rel
        if not p.exists():
            fail(f'missing MD5-protected file: {rel}')
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if h != exp:
            fail(f'MD5 mismatch on {rel}: expected={exp} actual={h}')

    # 2) Design JSON tracks
    for fname, expected_verdict in REQUIRED_JSON.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing JSON track: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if data.get('task_id') != 'PROJECT_HOME_MENU_REWIRING':
            fail(f'wrong task_id in {p}')
        if data.get('verdict') != expected_verdict:
            fail(f'expected verdict {expected_verdict} in {p}, got {data.get("verdict")!r}')

    # 3) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    if marker.get('verdict') != 'PROJECT_HOME_MENU_REWIRING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING':
        fail(f'proof marker verdict mismatch: {marker.get("verdict")!r}')

    # 4) Route runtime files exist
    if not GUIDE.exists():
        fail('missing frontend/app/guide.tsx')
    if not TOWER.exists():
        fail('missing frontend/app/tower-of-the-hells.tsx')

    # 5) Home contains correct links (executable code only)
    home_src = HOME.read_text()
    home_code = strip_js_comments(home_src)
    if "router.push('/guide'" not in home_code:
        fail("home.tsx missing executable router.push('/guide')")
    if "router.push('/tower-of-the-hells'" not in home_code:
        fail("home.tsx missing executable router.push('/tower-of-the-hells')")
    # No legacy /tower push outside comments
    legacy_tower_pushes = re.findall(r"router\.push\(\s*['\"]/tower['\"]", home_code)
    if legacy_tower_pushes:
        fail(f'home.tsx still contains executable legacy router.push("/tower"): {legacy_tower_pushes}')

    # 6) Menu contains correct routes (executable code only)
    menu_src = MENU.read_text()
    menu_code = strip_js_comments(menu_src)
    if "route: '/guide'" not in menu_code:
        fail("menu.tsx missing executable route: '/guide'")
    if "route: '/tower-of-the-hells'" not in menu_code:
        fail("menu.tsx missing executable route: '/tower-of-the-hells'")
    legacy_tower_routes = re.findall(r"route:\s*['\"]/tower['\"]", menu_code)
    if legacy_tower_routes:
        fail(f'menu.tsx still contains executable legacy route "/tower": {legacy_tower_routes}')

    # 7) _layout.tsx untouched: stable check on Stack.Screen name="tower-of-the-hells" present at count = 1
    layout_src = (ROOT / 'frontend/app/_layout.tsx').read_text()
    layout_code = re.sub(r'\{/\*.*?\*/\}', '', layout_src, flags=re.DOTALL)
    if layout_code.count('name="tower-of-the-hells"') != 1:
        fail('layout.tsx route count for tower-of-the-hells != 1')

    # 8) Locks preserved
    bp_src = (ROOT / 'frontend/app/battlepass.tsx').read_text()
    if 'const BP_LOCKED_V2 = true' not in bp_src:
        fail('BP_LOCKED_V2 not preserved as true')
    if 'const BP_PREMIUM_BUY_LOCKED_V2 = true' not in bp_src:
        fail('BP_PREMIUM_BUY_LOCKED_V2 not preserved as true')
    vip_src = (ROOT / 'frontend/app/vip.tsx').read_text()
    if 'const VIP_LOCKED_V2 = true' not in vip_src:
        fail('VIP_LOCKED_V2 not preserved as true')
    shop_src = (ROOT / 'frontend/app/shop.tsx').read_text()
    if 'const SHOP_LOCKED_V2 = true' not in shop_src:
        fail('SHOP_LOCKED_V2 not preserved as true')
    item_shop_src = (ROOT / 'frontend/app/item-shop.tsx').read_text()
    if 'const ITEM_SHOP_LOCKED_V2 = true' not in item_shop_src:
        fail('ITEM_SHOP_LOCKED_V2 not preserved as true')

    # 9) Constraints honored
    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_layout_tsx_edit', 'no_tower_gameplay_progress_asyncstorage',
        'no_guide_content_schema_rewrites', 'no_tutorial_first_unlock_wiring',
        'no_backend_routes_endpoints', 'no_db_writes_migrations',
        'no_combat_or_battle_engine', 'no_required_validator_weakening',
        'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    print('[PASS] PROJECT_HOME_MENU_REWIRING master validator')


if __name__ == '__main__':
    main()
