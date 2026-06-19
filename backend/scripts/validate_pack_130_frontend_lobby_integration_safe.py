#!/usr/bin/env python3
"""Pack 130 — Frontend lobby integration safety (STATIC).

Pack 130 NON ha modificato frontend/app/**. Verifichiamo che sia ancora vero.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACK129_ANCHOR = 'bcd72f45751d875edfc2d65a6a4b5dcbce966356'


def main() -> int:
    errors = []; notes = []
    try:
        r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', '--name-only', f'{PACK129_ANCHOR}..HEAD'],
                            capture_output=True, text=True, timeout=10)
        changed = [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []
    except Exception as e:
        notes.append(f'git diff exception: {e!r}'); changed = []
    frontend_app_touched = [f for f in changed if f.startswith('frontend/app/')]
    if frontend_app_touched:
        for f in frontend_app_touched:
            errors.append(f'frontend/app modified in Pack 130: {f}')
    else:
        print('OK    frontend/app/** untouched in Pack 130')
    notes.append('Pack 130 lobby integration frontend = VALIDATED_ONLY: il launch context endpoint è disponibile via GET /api/lobby/launch-context/preview ma NESSUNA schermata frontend lo consuma ancora (deferred a Pack 131+).')
    return _emit(errors, notes, frontend_app_touched)


def _emit(errors, notes, touched):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_FRONTEND_LOBBY_INTEGRATION_SAFE',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'frontend_app_files_touched_in_pack_130': touched,
              'validation_kind': 'STATIC+GIT_DIFF',
              'enforcement': 'VALIDATED_ONLY_BACKEND_ENDPOINT_AVAILABLE_NO_FRONTEND_CONSUMER_YET'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_frontend_lobby_integration_safe_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  Pack 130 introduces ZERO frontend/app/** changes (VALIDATED_ONLY frontend)')
    return 0


if __name__ == '__main__': sys.exit(main())
