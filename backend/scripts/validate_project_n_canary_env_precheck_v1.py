#!/usr/bin/env python3
"""PROJECT_N Track A validator — canary env precheck."""
import json, os, socket, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_n_canary_env_precheck_v1.json')
ENV = Path('/app/backend/.env')
FENV = Path('/app/frontend/.env')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_CANARY_ENV_PRECHECK_READY': fail('verdict mismatch')
    if m.get('env_classification') not in ('CANARY_ENV_CONFIRMED', 'NON_PROD_LOCAL_ONLY'): fail(f'classification {m.get("env_classification")} not safe')
    # Independent verification of non-prod signals.
    host = socket.gethostname()
    if not (host.startswith('agent-env') or host.startswith('canary') or host.startswith('dev')):
        fail(f'hostname {host!r} does not look like a non-prod env')
    if not ENV.exists(): fail('backend/.env missing')
    env_txt = ENV.read_text()
    if 'mongodb://localhost' not in env_txt: fail('MONGO_URL not localhost — cannot prove non-prod')
    if 'PROD' in env_txt.upper() and 'PRODUCTION' in env_txt.upper(): fail('PROD/PRODUCTION marker in backend/.env')
    if FENV.exists():
        fe = FENV.read_text()
        if 'preview.emergentagent' not in fe and 'localhost' not in fe and 'canary' not in fe:
            fail('frontend/.env does not indicate non-prod URL')
    # Forbidden prod env vars must not be true.
    for k in ('PRODUCTION', 'LIVE_ENV', 'PROD_MODE', 'IS_PROD'):
        if os.environ.get(k, '').strip().lower() == 'true':
            fail(f'prod env var {k} is true')
    print('[PASS] PROJECT_N Track A canary precheck READY: NON_PROD_LOCAL_ONLY confirmed')
    sys.exit(0)


if __name__ == '__main__': main()
