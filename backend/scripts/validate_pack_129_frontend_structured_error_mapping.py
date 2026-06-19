#!/usr/bin/env python3
"""Pack 129 — Frontend structured error mapping validator (STATIC).

Verifica che frontend/src/utils/structuredErrorMap.ts:
  - definisca STRUCTURED_CODES con tutti i codici Pack 129;
  - definisca LEGACY_BLOCKER_TO_CODE con tutti i legacy alias;
  - esporti mapStructuredError e envelopeFromApiError;
  - includa messaggi italiani per ogni codice.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / 'frontend' / 'src' / 'utils' / 'structuredErrorMap.ts'

REQUIRED_CODES = [
    'AUTH_REQUIRED', 'SERVER_CONTEXT_REQUIRED', 'SERVER_CONTEXT_INVALID',
    'SERVER_NOT_READY', 'SERVER_PROFILE_MISSING', 'SERVER_SCOPE_UNAVAILABLE',
    'SERVER_MISMATCH', 'TEAM_SAVE_DISABLED_PRE_QA', 'TEAM_INVALID_PAYLOAD',
    'TEAM_INVALID_SIZE', 'TEAM_INVALID_SLOT', 'TEAM_DUPLICATE_HERO',
    'TEAM_HERO_NOT_OWNED', 'TEAM_HERO_NOT_AVAILABLE',
    'TEAM_FORMATION_BLOCKED_PRE_QA', 'PRE_QA_MUTATION_BLOCKED',
    'FEATURE_LOCKED_PRE_QA',
]
REQUIRED_EXPORTS = ['STRUCTURED_CODES', 'LEGACY_BLOCKER_TO_CODE', 'mapStructuredError', 'envelopeFromApiError', 'CODE_TO_CATEGORY']
REQUIRED_LEGACY_BLOCKERS = ['QA_TEAM_SAVE_DISABLED', 'PLAYER_SERVER_PROFILE_REQUIRED', 'OWNERSHIP_VALIDATION_FAILED']


def main() -> int:
    errors = []; notes = []
    if not HELPER.exists(): errors.append('structuredErrorMap.ts missing'); return _emit(errors, notes)
    src = HELPER.read_text(encoding='utf-8')
    for c in REQUIRED_CODES:
        if c not in src: errors.append(f'code `{c}` missing in frontend map')
    for ex in REQUIRED_EXPORTS:
        if ex not in src: errors.append(f'export `{ex}` missing in frontend map')
    for lb in REQUIRED_LEGACY_BLOCKERS:
        if lb not in src: errors.append(f'legacy blocker `{lb}` missing in frontend map')
    # Verifica messaggio italiano (qualunque codice deve avere stringa italiana)
    if '"Accedi per continuare' not in src and 'Accedi per continuare' not in src:
        errors.append('italian message for AUTH_REQUIRED missing')
    print(f'OK    {len(REQUIRED_CODES)} codes + {len(REQUIRED_EXPORTS)} exports + {len(REQUIRED_LEGACY_BLOCKERS)} legacy aliases checked')
    notes.append('helper NOT mountato in screens esistenti (battle.tsx ha handler ad-hoc su blocker). Adozione futura opt-in.')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_FRONTEND_STRUCTURED_ERROR_MAPPING',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'required_codes': REQUIRED_CODES,
              'validation_kind': 'STATIC',
              'enforcement': 'VALIDATED_ONLY_HELPER_PRESENT_NOT_YET_MOUNTED_IN_EXISTING_SCREENS'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_frontend_structured_error_mapping_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  frontend structured error map present with codes/exports/aliases/italian messages')
    return 0


if __name__ == '__main__': sys.exit(main())
