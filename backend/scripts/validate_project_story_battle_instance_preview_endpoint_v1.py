"""validate_project_story_battle_instance_preview_endpoint_v1.py

MEGA_BATCH_ACCELERATION_1 TRACK A validator. Preview-only/gated endpoint.
No DB writes. No reward/EXP/story progress. No story.tsx/combat.tsx changes.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / 'backend' / 'routes' / 'story_battle_instance_preview.py'
SERVER = ROOT / 'backend' / 'server.py'
DESIGN = ROOT / 'data' / 'design' / 'story_visual_battle' / 'story_battle_instance_preview_endpoint_v1.json'
MARKER = ROOT / 'data' / 'design' / 'story_visual_battle' / 'story_battle_instance_preview_endpoint_proof_marker_v1.json'
STORY = ROOT / 'frontend' / 'app' / 'story.tsx'
COMBAT = ROOT / 'frontend' / 'app' / 'combat.tsx'

FAILS: list[str] = []


def _read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def _fail(m: str) -> None:
    FAILS.append(m)


def main() -> int:
    if not ROUTE.exists():
        _fail(f'missing route file: {ROUTE}')
    else:
        text = _read(ROUTE)
        if 'STORY_BATTLE_INSTANCE_PREVIEW_ENABLED' not in text:
            _fail('route missing STORY_BATTLE_INSTANCE_PREVIEW_ENABLED flag')
        for ep in ('/config', '/create-preview', '/validate-payload', '/sample'):
            if f'"{ep}"' not in text and f"'{ep}'" not in text:
                _fail(f'route missing endpoint: {ep}')
        if 'APIRouter(prefix="/api/story/battle-instance-preview"' not in text:
            _fail('route prefix /api/story/battle-instance-preview missing')
        # No DB write tokens
        for tok in ('insert_one', 'update_one', 'update_many', 'delete_one', 'delete_many', 'find_one_and_update'):
            if tok in text:
                _fail(f"forbidden DB write token '{tok}' in route")
        # No reward/EXP/progress grant tokens
        for tok in ('grant_reward', 'grantReward', 'add_exp', 'addExp', 'advance_story_progress'):
            if tok in text:
                _fail(f"forbidden grant token '{tok}' in route")
        # 503 logic
        if '503' not in text:
            _fail('route missing 503 inert behavior')

    if SERVER.exists():
        st = _read(SERVER)
        if 'story_battle_instance_preview' not in st:
            _fail('server.py does not register story_battle_instance_preview router')
    else:
        _fail('server.py missing')

    if not DESIGN.exists():
        _fail(f'missing design JSON: {DESIGN}')
    if not MARKER.exists():
        _fail(f'missing proof marker: {MARKER}')
    else:
        d = json.loads(_read(MARKER))
        for k, v in {
            'default_flag_off_returns_503': True,
            'db_writes': 0,
            'reward_grant_enabled': False,
            'exp_grant_enabled': False,
            'story_progress_enabled': False,
            'visual_runtime_enabled': False,
            'story_runtime_conversion': False,
            'battle_engine_changed': False,
            'story_battle_endpoint_changed': False,
            'battle_simulate_endpoint_changed': False,
            'story_tsx_changed': False,
            'combat_tsx_changed': False,
        }.items():
            if d.get(k) != v:
                _fail(f'proof_marker.{k} expected {v!r}, got {d.get(k)!r}')

    # story.tsx must still reference /api/story/battle (unchanged)
    if STORY.exists() and '/api/story/battle' not in _read(STORY):
        _fail('story.tsx no longer references /api/story/battle')
    # combat.tsx must still reference /api/battle/simulate (unchanged)
    if COMBAT.exists() and '/api/battle/simulate' not in _read(COMBAT):
        _fail('combat.tsx no longer references /api/battle/simulate')

    if FAILS:
        print('[FAIL] PROJECT_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT validator')
        for f in FAILS:
            print(f'  - {f}')
        return 1
    print('[PASS] PROJECT_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
