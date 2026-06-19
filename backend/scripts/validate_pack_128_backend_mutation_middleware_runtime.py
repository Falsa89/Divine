#!/usr/bin/env python3
"""Pack 128 — Backend mutation middleware runtime validator (STATIC + UNIT-RUNTIME).

UNIT-RUNTIME: importa direttamente PreQaMutationGuardMiddleware e testa la
logica di matching via la funzione pura `is_allowed`. Questo prova che la
logica di enforcement funziona, indipendentemente dallo stato dell'env nel pod
(env-gating è testato dal validator `_backend_mutation_allowlist_enforcement`).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))

MIDDLEWARE_FILE = REPO_ROOT / 'backend' / 'middleware' / 'pre_qa_mutation_guard.py'
SERVER_FILE = REPO_ROOT / 'backend' / 'server.py'


def main() -> int:
    errors = []; notes = []
    if not MIDDLEWARE_FILE.exists():
        errors.append('middleware file missing'); return _emit(errors, notes)
    if not SERVER_FILE.exists():
        errors.append('server.py missing'); return _emit(errors, notes)
    server_src = SERVER_FILE.read_text(encoding='utf-8')
    if 'PreQaMutationGuardMiddleware' not in server_src:
        errors.append('PreQaMutationGuardMiddleware NOT mounted in server.py')
    else:
        print('OK    middleware mounted in server.py')
    if 'app.add_middleware(PreQaMutationGuardMiddleware' not in server_src:
        errors.append('add_middleware(PreQaMutationGuardMiddleware) line missing')

    # Unit-runtime: import e test funzionale.
    try:
        from middleware.pre_qa_mutation_guard import is_allowed, load_allowlist, ENV_FLAG, _MUTATING_METHODS
    except Exception as e:
        errors.append(f'cannot import middleware: {e!r}')
        return _emit(errors, notes)
    al = load_allowlist()
    if len(al) < 5:
        errors.append(f'loaded allowlist too small ({len(al)} entries)')
    print(f'OK    allowlist loaded: {len(al)} entries')
    # Test matching: route allowlisted passa.
    if not is_allowed('POST', '/api/login', al):
        errors.append('is_allowed(POST,/api/login) returned False (regression)')
    # Test matching: route non-allowlisted bloccata.
    if is_allowed('POST', '/api/gacha/pull', al):
        errors.append('is_allowed(POST,/api/gacha/pull) returned True (would leak gacha mutation)')
    if is_allowed('DELETE', '/api/user/everything', al):
        errors.append('is_allowed(DELETE,/api/user/everything) returned True (would leak destructive op)')
    # Test case insensitivity.
    if not is_allowed('post', '/api/login', al):
        errors.append('is_allowed case-insensitive on method failed')
    print('OK    is_allowed matching logic verified (unit-runtime)')
    notes.append(f'ENV_FLAG name = `{ENV_FLAG}`')
    notes.append(f'mutating methods enforced = {sorted(_MUTATING_METHODS)}')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_BACKEND_MUTATION_MIDDLEWARE_RUNTIME',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'validation_kind': 'STATIC+UNIT_RUNTIME',
        'enforcement': 'ENFORCED_CODE_AND_UNIT_RUNTIME_FULL_HTTP_SMOKE_REQUIRES_ENV_TRUE',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_backend_mutation_middleware_runtime_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  middleware mounted + matching logic verified (unit-runtime); full HTTP smoke requires env true')
    return 0


if __name__ == '__main__': sys.exit(main())
