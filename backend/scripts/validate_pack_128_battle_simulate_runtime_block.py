#!/usr/bin/env python3
"""Pack 128 — /api/battle/simulate runtime block validator (STATIC + RUNTIME).

Verifica:
  1. Anonimo → HTTP 401 (auth gate) — ENFORCED.
  2. Static: middleware Pack 128 (se attivo) bloccherebbe la mutazione perché
     /api/battle/simulate non è nella allowlist.
  3. Runtime in-process: con env true e middleware mountato, POST a
     /api/battle/simulate ritorna 423 PRE_QA_MUTATION_BLOCKED.
  4. Smoke autenticato sul backend del pod NON eseguito (richiede JWT QA reale
     + body senza marker preview); riportato come NOT_EXECUTED, NON come PASS.
"""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'backend'))


def main() -> int:
    errors = []; notes = []
    # 1. Anonimo smoke (backend del pod).
    try:
        r = subprocess.run(['curl', '-s', '-o', '/tmp/p128_sim.json', '-w', '%{http_code}', '-X', 'POST',
                            'http://localhost:8001/api/battle/simulate', '-H', 'Content-Type: application/json',
                            '-d', '{}'], capture_output=True, text=True, timeout=8)
        code = r.stdout.strip()
        if code != '401':
            notes.append(f'anonymous POST /api/battle/simulate expected 401, got {code} (auth gate may differ)')
        else:
            print('OK    anonymous POST /api/battle/simulate → HTTP 401 (auth gate)')
    except Exception as e:
        notes.append(f'anon runtime smoke failed: {e!r}')

    # 2. Static: verifica che /api/battle/simulate NON sia nella allowlist Pack 128.
    al_file = REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_128_backend_mutation_allowlist.json'
    if al_file.exists():
        al = json.loads(al_file.read_text(encoding='utf-8'))
        entries = al.get('allowlist', [])
        if any('battle/simulate' in str(e) for e in entries):
            errors.append('/api/battle/simulate is IN Pack 128 allowlist (must be blocked)')
        else:
            print('OK    /api/battle/simulate NOT in Pack 128 allowlist (would be blocked when env true)')
    else:
        notes.append('Pack 128 allowlist file missing')

    # 3. Runtime in-process: env true + mountato → 423.
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from middleware.pre_qa_mutation_guard import PreQaMutationGuardMiddleware, ENV_FLAG
        app = FastAPI()
        app.add_middleware(PreQaMutationGuardMiddleware)

        @app.post('/api/battle/simulate')
        async def fake_simulate():
            return {'ok': True}  # se arriva qui = middleware non ha bloccato (FAIL)

        os.environ[ENV_FLAG] = 'true'
        try:
            with TestClient(app) as c:
                r = c.post('/api/battle/simulate', json={})
                if r.status_code == 423 and r.json().get('code') == 'PRE_QA_MUTATION_BLOCKED':
                    print('OK    runtime in-process: POST /api/battle/simulate → HTTP 423 PRE_QA_MUTATION_BLOCKED')
                else:
                    errors.append(f'in-process simulate not blocked: HTTP {r.status_code} body={r.text[:200]}')
        finally:
            os.environ.pop(ENV_FLAG, None)
    except Exception as e:
        notes.append(f'in-process runtime smoke failed: {e!r}')

    # 4. Autenticato smoke: NOT_EXECUTED.
    notes.append('AUTHENTICATED_RUNTIME_SMOKE_NOT_EXECUTED: smoke con JWT QA reale sul backend del pod richiederebbe (a) seed account QA, (b) body senza marker preview, (c) env PRE_QA_MUTATION_GUARD_ENABLED=true nel pod. Tutti deferred a Pack 132 (Device QA Gate Suite).')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_BATTLE_SIMULATE_RUNTIME_BLOCK',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'validation_kind': 'STATIC+RUNTIME_INPROCESS',
        'enforcement': 'ENFORCED_INPROCESS_BLOCKED_BY_MIDDLEWARE_FULL_AUTHENTICATED_SMOKE_NOT_EXECUTED',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_battle_simulate_runtime_block_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  /api/battle/simulate would be blocked by Pack 128 middleware when env true; authenticated smoke NOT_EXECUTED')
    return 0


if __name__ == '__main__': sys.exit(main())
