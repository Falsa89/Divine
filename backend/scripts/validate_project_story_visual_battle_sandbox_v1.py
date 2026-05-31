"""validate_project_story_visual_battle_sandbox_v1.py

PROJECT_STORY_VISUAL_BATTLE_SANDBOX_PACK (v32 PHASE_3) validator.
Sandbox dev/QA only. No reward, no progress, no replay reward, no DB writes,
no AsyncStorage writes, no live runtime conversion.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / 'backend' / 'routes' / 'story_battle_instance_preview.py'
SANDBOX_TSX = ROOT / 'frontend' / 'app' / 'story-visual-battle-sandbox.tsx'
CONTRACT = ROOT / 'data' / 'design' / 'story_visual_battle' / 'story_visual_battle_sandbox_contract_v1.json'
MARKER = ROOT / 'data' / 'design' / 'story_visual_battle' / 'story_visual_battle_sandbox_proof_marker_v1.json'
STORY_TSX = ROOT / 'frontend' / 'app' / 'story.tsx'
COMBAT_TSX = ROOT / 'frontend' / 'app' / 'combat.tsx'
MANIFEST = ROOT / 'frontend' / 'constants' / 'homeAssetsManifest.ts'
BATTLE_ENGINE = ROOT / 'backend' / 'battle_engine.py'

FAILS: list[str] = []


def _read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def _fail(m: str) -> None:
    FAILS.append(m)


def main() -> int:
    # Backend route check
    if not ROUTE.exists():
        _fail(f'missing route file: {ROUTE}')
    else:
        t = _read(ROUTE)
        if 'sandbox-playback' not in t:
            _fail('route missing /sandbox-playback endpoint')
        if 'SANDBOX_CONTRACT_VERSION' not in t:
            _fail('route missing SANDBOX_CONTRACT_VERSION constant')
        if '_synthetic_timeline' not in t:
            _fail('route missing _synthetic_timeline helper')
        # Sandbox endpoint must use same flag and 503 default
        if 'STORY_BATTLE_INSTANCE_PREVIEW_ENABLED' not in t:
            _fail('route missing feature flag STORY_BATTLE_INSTANCE_PREVIEW_ENABLED')
        # No DB write tokens
        for tok in ('insert_one', 'update_one', 'update_many', 'delete_one', 'find_one_and_update'):
            if tok in t:
                _fail(f"forbidden DB write token '{tok}' in route")
        # No reward/EXP/story progress grant tokens
        for tok in ('grant_reward', 'grantReward', 'add_exp', 'advance_story_progress'):
            if tok in t:
                _fail(f"forbidden grant token '{tok}' in route")

    # Frontend sandbox route check
    if not SANDBOX_TSX.exists():
        _fail(f'missing frontend sandbox file: {SANDBOX_TSX}')
    else:
        ft = _read(SANDBOX_TSX)
        if '/api/story/battle-instance-preview/sandbox-playback' not in ft:
            _fail('sandbox tsx must call /api/story/battle-instance-preview/sandbox-playback')
        if '/api/story/battle-instance-preview/create-preview' not in ft:
            _fail('sandbox tsx must call /api/story/battle-instance-preview/create-preview')
        # FORBIDDEN: must NOT call legacy/visual battle endpoints (check active fetch only, not comments)
        if re.search(r"fetch\([^)]*['\"][^'\"]*/api/battle/simulate[^'\"]*['\"]", ft):
            _fail('sandbox tsx must NOT actively call /api/battle/simulate')
        # The /api/story/battle endpoint should not be invoked. Check for active fetch.
        if re.search(r"fetch\([^)]*['\"][^'\"]*/api/story/battle(?!-)[^'\"]*['\"]", ft):
            _fail('sandbox tsx must NOT call /api/story/battle')
        # AsyncStorage writes forbidden
        if 'AsyncStorage' in ft and ('setItem' in ft or 'mergeItem' in ft):
            _fail('sandbox tsx must NOT use AsyncStorage.setItem/mergeItem')
        # SANDBOX banner required
        if 'SANDBOX' not in ft:
            _fail('sandbox tsx must include SANDBOX banner text')

    # Contract + marker checks
    if not CONTRACT.exists():
        _fail(f'missing contract: {CONTRACT}')
    else:
        c = json.loads(_read(CONTRACT))
        if c.get('runtime_activation_for_normal_users_allowed_in_this_pack') is not False:
            _fail('contract.runtime_activation_for_normal_users_allowed_in_this_pack must be false')
        if c.get('frontend_route', {}).get('linked_from_home') is not False:
            _fail('contract.frontend_route.linked_from_home must be false')
        if c.get('frontend_route', {}).get('linked_from_menu') is not False:
            _fail('contract.frontend_route.linked_from_menu must be false')

    if not MARKER.exists():
        _fail(f'missing marker: {MARKER}')
    else:
        m = json.loads(_read(MARKER))
        expected = {
            'db_writes': 0,
            'async_storage_writes': 0,
            'reward_grant_enabled': False,
            'exp_grant_enabled': False,
            'story_progress_enabled': False,
            'replay_reward_enabled': False,
            'battle_engine_changed': False,
            'story_battle_endpoint_changed': False,
            'battle_simulate_endpoint_changed': False,
            'story_tsx_changed': False,
            'combat_tsx_changed': False,
            'home_routes_changed': False,
            'home_assets_manifest_changed': False,
            'frontend_linked_from_home': False,
            'frontend_linked_from_menu': False,
            'frontend_linked_from_tabs': False,
            'runtime_activation_for_normal_users': False,
        }
        for k, v in expected.items():
            if m.get(k) != v:
                _fail(f'marker.{k} expected {v!r}, got {m.get(k)!r}')

    # Forbidden files unchanged
    if STORY_TSX.exists() and '/api/story/battle' not in _read(STORY_TSX):
        _fail('story.tsx no longer references /api/story/battle')
    if COMBAT_TSX.exists() and '/api/battle/simulate' not in _read(COMBAT_TSX):
        _fail('combat.tsx no longer references /api/battle/simulate')
    if MANIFEST.exists():
        mt = _read(MANIFEST)
        if not re.search(r"play\s*:\s*'\/story'", mt):
            _fail("homeAssetsManifest.ts no longer has play:'/story'")
        # Sandbox route must NOT be referenced by home manifest
        if 'story-visual-battle-sandbox' in mt:
            _fail('homeAssetsManifest.ts must NOT link to sandbox route')
    if not BATTLE_ENGINE.exists():
        _fail('battle_engine.py missing')

    if FAILS:
        print('[FAIL] PROJECT_STORY_VISUAL_BATTLE_SANDBOX validator')
        for f in FAILS:
            print('  -', f)
        return 1
    print('[PASS] PROJECT_STORY_VISUAL_BATTLE_SANDBOX validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
