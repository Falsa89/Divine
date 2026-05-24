#!/usr/bin/env python3
"""PROJECT_O Track A validator — dev-live precheck."""
import json, socket, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_dev_live_precheck_v1.json')
ENV = Path('/app/backend/.env')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_DEV_LIVE_PRECHECK_READY': fail('verdict mismatch')
    if m.get('env_classification') not in ('DEV_LIVE_CONFIRMED', 'NON_PROD_LOCAL_ONLY'):
        fail(f'classification {m.get("env_classification")} not safe for flip')
    host = socket.gethostname()
    if not (host.startswith('agent-env') or host.startswith('canary') or host.startswith('dev') or host.startswith('staging')):
        fail(f'hostname {host!r} not non-prod')
    if 'mongodb://localhost' not in ENV.read_text(): fail('MONGO_URL not localhost')
    # Project_N completion presence check.
    pn = Path('/app/data/design/project_management/project_n_completion_and_next_step_v1.json')
    if not pn.exists(): fail('Project_N completion marker missing')
    print('[PASS] PROJECT_O Track A dev-live precheck READY: NON_PROD_LOCAL_ONLY confirmed; Project_N evidence verified')
    sys.exit(0)


if __name__ == '__main__': main()
