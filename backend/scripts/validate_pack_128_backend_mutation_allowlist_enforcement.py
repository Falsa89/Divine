#!/usr/bin/env python3
"""Pack 128 — Backend mutation allowlist enforcement (RUNTIME smoke with env on).

Questo validator esegue uno smoke RUNTIME completo:
  1. Avvia un'app FastAPI minimal in-process con il middleware Pack 128 montato.
  2. Imposta env `PRE_QA_MUTATION_GUARD_ENABLED=true` per la durata del test.
  3. Verifica che POST allowlisted ritorni la response del downstream e che
     POST non-allowlisted ritorni HTTP 423 PRE_QA_MUTATION_BLOCKED.
  4. Verifica che GET passi inalterato (Track C separato).

Non tocca il backend in esecuzione nel pod. Tutto in-process e isolato.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))


def main() -> int:
    errors = []; notes = []
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from middleware.pre_qa_mutation_guard import PreQaMutationGuardMiddleware, ENV_FLAG
    except Exception as e:
        errors.append(f'cannot import test deps: {e!r}'); return _emit(errors, notes)

    # Setup app in-process minimal.
    app = FastAPI()
    app.add_middleware(PreQaMutationGuardMiddleware)

    @app.post('/api/login')
    async def login_ok():
        return {'ok': True}

    @app.post('/api/gacha/pull')
    async def gacha_pull():
        return {'pulled': True}

    @app.get('/api/heroes')
    async def heroes_ok():
        return {'heroes': []}

    # Smoke 1: env unset → middleware DORMANT, gacha/pull passa.
    os.environ.pop(ENV_FLAG, None)
    with TestClient(app) as c:
        r = c.post('/api/gacha/pull', json={})
        if r.status_code != 200:
            errors.append(f'DORMANT mode: /api/gacha/pull expected 200, got {r.status_code}')
        else:
            print('OK    DORMANT mode: non-allowlisted route passes (HTTP 200)')

    # Smoke 2: env true → enforcement attivo.
    os.environ[ENV_FLAG] = 'true'
    try:
        with TestClient(app) as c:
            r_login = c.post('/api/login', json={})
            if r_login.status_code != 200:
                errors.append(f'ACTIVE mode: /api/login (allowlisted) expected 200, got {r_login.status_code}')
            else:
                print('OK    ACTIVE mode: allowlisted POST /api/login passes (HTTP 200)')

            r_gacha = c.post('/api/gacha/pull', json={})
            if r_gacha.status_code != 423:
                errors.append(f'ACTIVE mode: /api/gacha/pull (NOT allowlisted) expected 423, got {r_gacha.status_code}')
            else:
                body = r_gacha.json()
                if body.get('code') != 'PRE_QA_MUTATION_BLOCKED':
                    errors.append(f'ACTIVE mode: block code expected PRE_QA_MUTATION_BLOCKED, got {body.get("code")}')
                else:
                    print('OK    ACTIVE mode: non-allowlisted POST blocked HTTP 423 PRE_QA_MUTATION_BLOCKED')

            r_get = c.get('/api/heroes')
            if r_get.status_code != 200:
                errors.append(f'ACTIVE mode: GET /api/heroes expected 200 (not subject to mutation block), got {r_get.status_code}')
            else:
                print('OK    ACTIVE mode: GET request passes (Track C separate)')
    finally:
        os.environ.pop(ENV_FLAG, None)

    notes.append('Smoke runtime in-process eseguito con TestClient FastAPI; backend del pod NON modificato/toccato.')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_BACKEND_MUTATION_ALLOWLIST_ENFORCEMENT',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'validation_kind': 'STATIC+RUNTIME_INPROCESS',
        'enforcement': 'ENFORCED_RUNTIME_INPROCESS_FULL_HTTP_SMOKE_REQUIRES_ENV_TRUE_IN_QA_SUPERVISOR',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_backend_mutation_allowlist_enforcement_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  mutation allowlist enforcement verified runtime in-process (HTTP 423 block + allowlist passthrough)')
    return 0


if __name__ == '__main__': sys.exit(main())
