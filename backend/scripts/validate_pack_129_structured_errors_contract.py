#!/usr/bin/env python3
"""Pack 129 — Structured Errors contract (STATIC + UNIT-RUNTIME).

Verifica che backend/helpers/structured_errors.py:
  - esporti tutti i codici richiesti dal prompt Pack 129;
  - build_structured_detail produca la shape attesa;
  - legacy_blocker_to_code mappi i blocker Pack 125 noti.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))
HELPER = REPO_ROOT / 'backend' / 'helpers' / 'structured_errors.py'

REQUIRED_CODES = [
    'AUTH_REQUIRED',
    'SERVER_CONTEXT_REQUIRED', 'SERVER_CONTEXT_INVALID', 'SERVER_NOT_READY',
    'SERVER_PROFILE_MISSING', 'SERVER_SCOPE_UNAVAILABLE', 'SERVER_MISMATCH',
    'TEAM_SAVE_DISABLED_PRE_QA', 'TEAM_INVALID_PAYLOAD', 'TEAM_INVALID_SIZE',
    'TEAM_INVALID_SLOT', 'TEAM_DUPLICATE_HERO', 'TEAM_HERO_NOT_OWNED',
    'TEAM_HERO_NOT_AVAILABLE', 'TEAM_FORMATION_BLOCKED_PRE_QA',
    'PRE_QA_MUTATION_BLOCKED', 'FEATURE_LOCKED_PRE_QA',
]
REQUIRED_LEGACY = [
    'AUTHENTICATION_REQUIRED',
    'AUTHENTICATION_INVALID',
    'QA_TEAM_SAVE_DISABLED',
    'QA_TEAM_SAVE_ALLOWLIST_EMPTY',
    'QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED',
    'PLAYER_SERVER_PROFILE_REQUIRED',
    'TEAM_TOO_LARGE',
    'DUPLICATE_POSITIONS',
    'DUPLICATE_HEROES',
    'OWNERSHIP_VALIDATION_FAILED',
]


def main() -> int:
    errors = []; notes = []
    if not HELPER.exists(): errors.append('structured_errors.py missing'); return _emit(errors, notes, {})
    try:
        from helpers.structured_errors import (build_structured_detail, legacy_blocker_to_code, ALL_CODES)
    except Exception as e:
        errors.append(f'cannot import structured_errors: {e!r}'); return _emit(errors, notes, {})

    for c in REQUIRED_CODES:
        if c not in ALL_CODES:
            errors.append(f'required code `{c}` missing in ALL_CODES')
    print(f'OK    {len(REQUIRED_CODES)} codes required, {len(ALL_CODES)} present')

    # legacy aliasing smoke
    for legacy in REQUIRED_LEGACY:
        mapped = legacy_blocker_to_code(legacy)
        if not mapped:
            errors.append(f'legacy alias `{legacy}` not mapped')
    print(f'OK    {len(REQUIRED_LEGACY)} legacy aliases verified')

    # build_structured_detail shape
    payload = build_structured_detail(
        detail='test', code='TEAM_INVALID_SIZE',
        route='/api/x', method='POST', recoverable=True,
    )
    for k in ['detail', 'code', 'category', 'route', 'method', 'next_gate', 'recoverable']:
        if k not in payload:
            errors.append(f'build_structured_detail missing field `{k}`')
    if payload.get('category') != 'validation':
        errors.append(f'TEAM_INVALID_SIZE category expected validation, got {payload.get("category")}')
    print('OK    build_structured_detail shape verified (7 fields, correct default category)')

    return _emit(errors, notes, payload)


def _emit(errors, notes, sample):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_STRUCTURED_ERRORS_CONTRACT',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'sample_payload': sample,
              'required_codes_count': len(REQUIRED_CODES),
              'required_legacy_aliases_count': len(REQUIRED_LEGACY),
              'validation_kind': 'STATIC+UNIT_RUNTIME',
              'enforcement': 'ENFORCED_HELPER_LIBRARY_AVAILABLE_OPT_IN_ADOPTION_IN_ROUTES'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_structured_errors_contract_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  structured errors contract: codes + aliases + builder verified')
    return 0


if __name__ == '__main__': sys.exit(main())
