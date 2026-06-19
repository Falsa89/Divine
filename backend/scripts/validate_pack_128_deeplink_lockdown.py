#!/usr/bin/env python3
"""Pack 128 — Deeplink lockdown helper validator (STATIC).

Verifica presenza statica di `frontend/src/utils/preQaDeeplinkGuard.ts` e
che esporti `interceptDeeplink` + `extractPath`. Lo stato di enforcement
runtime intercept (mount in _layout.tsx) viene riportato come VALIDATED_ONLY
finché non viene fatto mount esplicito in Pack 128.x / Pack 129.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER = REPO_ROOT / 'frontend' / 'src' / 'utils' / 'preQaDeeplinkGuard.ts'
LAYOUT = REPO_ROOT / 'frontend' / 'app' / '_layout.tsx'


def main() -> int:
    errors = []
    notes = []
    if not HELPER.exists():
        errors.append('preQaDeeplinkGuard.ts missing'); return _emit(errors, notes)
    src = HELPER.read_text(encoding='utf-8')
    for fn in ['interceptDeeplink', 'extractPath', 'DeeplinkInterceptResult', 'StructuredErrorCode']:
        if fn not in src:
            errors.append(f'export `{fn}` missing in preQaDeeplinkGuard.ts')
    # Verifica che il helper NON sia ancora montato (per dichiarare VALIDATED_ONLY)
    layout_src = LAYOUT.read_text(encoding='utf-8') if LAYOUT.exists() else ''
    mounted = 'preQaDeeplinkGuard' in layout_src or 'interceptDeeplink' in layout_src
    if mounted:
        notes.append('deeplink guard appears mounted in _layout.tsx — promotable a ENFORCED in Pack 129 dopo smoke test')
    else:
        notes.append('deeplink guard NOT mounted in _layout.tsx — enforcement runtime = VALIDATED_ONLY (helper presente, mount deferred per minimizzare touch UI)')
    print('OK    preQaDeeplinkGuard.ts present with required exports')
    return _emit(errors, notes, mounted)


def _emit(errors, notes, mounted=False):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_DEEPLINK_LOCKDOWN',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'validation_kind': 'STATIC',
        'enforcement': 'ENFORCED_HELPER_MOUNTED' if mounted else 'VALIDATED_ONLY_HELPER_NOT_MOUNTED',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_deeplink_lockdown_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  deeplink lockdown helper present (mount deferred)')
    return 0


if __name__ == '__main__': sys.exit(main())
