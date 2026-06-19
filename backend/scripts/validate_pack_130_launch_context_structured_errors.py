#!/usr/bin/env python3
"""Pack 130 — Launch context structured errors usage (STATIC)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'lobby_launch_context.py'

REQUIRED_CODES = [
    'AUTH_REQUIRED', 'LOBBY_MODE_INVALID', 'TEAM_FORMATION_MISSING',
    'TEAM_FORMATION_EMPTY', 'SNAPSHOT_BUILD_FAILED',
    'COMBAT_CONSUMPTION_DEFERRED_TO_PACK_131',
]


def main() -> int:
    errors = []; notes = []
    if not HELPER.exists(): errors.append('lobby_launch_context.py missing'); return _emit(errors, notes)
    src = HELPER.read_text(encoding='utf-8')
    if 'build_structured_detail' not in src:
        errors.append('build_structured_detail not used in lobby_launch_context')
    if 'state_to_structured_code' not in src:
        errors.append('state_to_structured_code not used (Pack 129 server_ready_guard adoption missing)')
    for c in REQUIRED_CODES:
        if c not in src:
            errors.append(f'required code `{c}` missing in helper')
    print(f'OK    helper uses Pack 129 structured_errors + server_ready_guard; {len(REQUIRED_CODES)} codes verified')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_LAUNCH_CONTEXT_STRUCTURED_ERRORS',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'required_codes': REQUIRED_CODES,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_STRUCTURED_ERRORS_USED_ALONG_WITH_SERVER_READY_GUARD'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_launch_context_structured_errors_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  Pack 130 helper uses structured_errors + server_ready_guard from Pack 129')
    return 0


if __name__ == '__main__': sys.exit(main())
