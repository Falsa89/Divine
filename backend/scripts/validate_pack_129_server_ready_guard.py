#!/usr/bin/env python3
"""Pack 129 — Server Ready Guard validator (STATIC + UNIT-RUNTIME).

Verifica:
  1. backend/helpers/server_ready_guard.py esiste e definisce gli stati richiesti.
  2. check_server_ready è importabile.
  3. Comportamento unit-runtime con DB mock (motor-like async stub).
"""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'server_ready_guard.py'

REQUIRED_STATES = ['SERVER_READY', 'SERVER_CONTEXT_MISSING', 'SERVER_CONTEXT_INVALID',
                    'SERVER_PROFILE_MISSING', 'SERVER_SCOPE_UNAVAILABLE', 'SERVER_MISMATCH']


class _MockColl:
    def __init__(self, present): self.present = present
    async def find_one(self, *_a, **_kw):
        return {'user_id': 'u1', 'server_id': 's1'} if self.present else None

class _MockDB:
    def __init__(self, present): self.player_server_profiles = _MockColl(present)


async def _smoke(check, db_ok, db_miss):
    results = []
    # 1. missing server_id
    s, _ = await check(db_ok, 'u1', None); results.append(('SERVER_CONTEXT_MISSING', s))
    # 2. invalid format
    s, _ = await check(db_ok, 'u1', 'has space'); results.append(('SERVER_CONTEXT_INVALID', s))
    # 3. PSP missing
    s, _ = await check(db_miss, 'u1', 's1'); results.append(('SERVER_PROFILE_MISSING', s))
    # 4. SERVER_READY
    s, _ = await check(db_ok, 'u1', 's1'); results.append(('SERVER_READY', s))
    # 5. SERVER_MISMATCH
    s, _ = await check(db_ok, 'u1', 's1', auth_context_server_id='s2'); results.append(('SERVER_MISMATCH', s))
    # 6. missing user_id
    s, _ = await check(db_ok, '', 's1'); results.append(('SERVER_SCOPE_UNAVAILABLE', s))
    return results


def main() -> int:
    errors = []; notes = []
    if not HELPER.exists(): errors.append('server_ready_guard.py missing'); return _emit(errors, notes, [])
    src = HELPER.read_text(encoding='utf-8')
    for st in REQUIRED_STATES:
        if st not in src: errors.append(f'state `{st}` missing in helper')
    try:
        from helpers.server_ready_guard import check_server_ready, STATE_TO_CODE, state_to_structured_code, STATE_READY
    except Exception as e:
        errors.append(f'cannot import helper: {e!r}'); return _emit(errors, notes, [])
    print('OK    helper imports + state constants present')
    db_ok = _MockDB(present=True); db_miss = _MockDB(present=False)
    pairs = asyncio.get_event_loop().run_until_complete(_smoke(check_server_ready, db_ok, db_miss))
    for expected, actual in pairs:
        if actual != expected:
            errors.append(f'expected {expected}, got {actual}')
        else:
            print(f'OK    {expected} smoke passes')
    # state_to_structured_code
    if state_to_structured_code(STATE_READY) != '':
        errors.append('state_to_structured_code(SERVER_READY) should be empty')
    return _emit(errors, notes, pairs)


def _emit(errors, notes, pairs):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_SERVER_READY_GUARD',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'unit_runtime_smoke_pairs': [{'expected': e, 'actual': a} for e, a in pairs],
              'validation_kind': 'STATIC+UNIT_RUNTIME',
              'enforcement': 'ENFORCED_HELPER_PRESENT_LOGIC_VERIFIED'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_server_ready_guard_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  server_ready_guard helper present, all 6 states verified via unit-runtime smoke')
    return 0


if __name__ == '__main__': sys.exit(main())
