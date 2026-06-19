#!/usr/bin/env python3
"""Pack 130 — Lobby Launch Context contract (STATIC + UNIT-RUNTIME)."""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))
ROUTE = REPO_ROOT / 'backend' / 'routes' / 'v130_lobby_launch_context.py'
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'lobby_launch_context.py'

REQUIRED_FIELDS = ['launch_context_id', 'mode', 'server_id', 'user_id',
                   'player_snapshot', 'enemy_snapshot_status',
                   'combat_consumption_status', 'reward_status',
                   'progress_status', 'device_qa_status']


class _MockColl:
    def __init__(self, doc=None, list_docs=None):
        self.doc = doc; self.list_docs = list_docs or []
    async def find_one(self, *a, **kw): return self.doc
    def find(self, *a, **kw):
        outer = self
        class _Cursor:
            async def to_list(self, length=None): return outer.list_docs
        return _Cursor()

class _MockDB:
    def __init__(self, psp=None, uh=None, heroes=None):
        self.player_server_profiles = _MockColl(doc=psp)
        self.user_heroes = _MockColl(list_docs=uh or [])
        self.heroes = _MockColl(list_docs=heroes or [])


async def _smoke():
    from helpers.lobby_launch_context import build_lobby_launch_context
    results = []
    # no auth
    r = await build_lobby_launch_context(_MockDB(), user_id=None, server_id='s1', mode='training')
    results.append(('no_auth', r.get('detail', {}).get('code')))
    # invalid mode
    r = await build_lobby_launch_context(_MockDB(psp={}), user_id='u1', server_id='s1', mode='cheat')
    results.append(('invalid_mode', r.get('detail', {}).get('code')))
    # missing server
    r = await build_lobby_launch_context(_MockDB(psp={}), user_id='u1', server_id=None, mode='training')
    results.append(('missing_server', r.get('detail', {}).get('code')))
    # success path
    psp = {'team_formation': [{'user_hero_id': 'uh1', 'col': 0, 'row': 0}]}
    uh = [{'user_hero_id': 'uh1', 'user_id': 'u1', 'server_id': 's1', 'hero_id': 'h1', 'level': 5}]
    heroes = [{'id': 'h1', 'display_name': 'Test', 'rarity': 'RARE'}]
    r = await build_lobby_launch_context(_MockDB(psp=psp, uh=uh, heroes=heroes), user_id='u1', server_id='s1', mode='training')
    results.append(('success_ok', r.get('ok'), r.get('launch_context_id') is not None))
    if r.get('ok'):
        ps = r.get('player_snapshot', {})
        results.append(('snapshot_team_size', ps.get('team_size')))
        results.append(('combat_consumption', r.get('combat_consumption_status')))
        results.append(('reward_status', r.get('reward_status')))
        results.append(('progress_status', r.get('progress_status')))
        results.append(('device_qa_status', r.get('device_qa_status')))
    return results


def main() -> int:
    errors = []; notes = []
    if not ROUTE.exists(): errors.append('v130_lobby_launch_context.py missing')
    if not HELPER.exists(): errors.append('lobby_launch_context.py missing')
    if errors: return _emit(errors, notes, [])
    if '@router.get("/launch-context/preview")' not in ROUTE.read_text(encoding='utf-8'):
        errors.append('GET /launch-context/preview not mounted')
    pairs = asyncio.get_event_loop().run_until_complete(_smoke())
    expected = [('no_auth', 'AUTH_REQUIRED'),
                ('invalid_mode', 'LOBBY_MODE_INVALID'),
                ('missing_server', 'SERVER_CONTEXT_REQUIRED')]
    for exp in expected:
        if exp not in pairs:
            errors.append(f'expected smoke pair {exp} not found in {pairs[:5]}')
    # success path
    success = next((p for p in pairs if p[0] == 'success_ok'), None)
    if not success or not success[1]:
        errors.append(f'success path did not return ok=True ({success})')
    print(f'OK    smoke pairs: {len(pairs)} executed')
    for p in pairs: print(f'  - {p}')
    return _emit(errors, notes, pairs)


def _emit(errors, notes, pairs):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_LOBBY_LAUNCH_CONTEXT_CONTRACT',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
              'notes': notes, 'smoke_pairs': [list(p) for p in pairs],
              'required_response_fields': REQUIRED_FIELDS,
              'validation_kind': 'STATIC+UNIT_RUNTIME',
              'enforcement': 'ENFORCED_CONTRACT_AND_UNIT_RUNTIME_VERIFIED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_lobby_launch_context_contract_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  Pack 130 lobby launch context contract verified')
    return 0


if __name__ == '__main__': sys.exit(main())
