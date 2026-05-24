#!/usr/bin/env python3
"""PROJECT_U Track A validator — canary env precheck."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_u_second_slice_canary_env_precheck_v1.json')
ALLOWED_CLASSIFICATIONS = ('DEV_CANARY_CONFIRMED', 'NON_PROD_LOCAL_ONLY')
FORBIDDEN_CLASSIFICATIONS = ('PROD_LIKE_BLOCKED',)
ENV = Path('/app/backend/.env')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') not in ('TRACK_A_SECOND_SLICE_CANARY_ENV_PRECHECK_READY', 'TRACK_A_SECOND_SLICE_CANARY_ENV_PRECHECK_BLOCKED_ENV_NOT_PROVEN'): fail('verdict invalid')
    cls = m.get('classification')
    if cls in FORBIDDEN_CLASSIFICATIONS: fail(f'classification forbidden: {cls}')
    if cls not in ALLOWED_CLASSIFICATIONS and cls != 'ENV_NOT_PROVEN': fail(f'classification invalid: {cls}')
    # Verify env audit: MONGO_URL must be local for NON_PROD_LOCAL_ONLY
    if cls == 'NON_PROD_LOCAL_ONLY':
        env_audit = m.get('env_audit', {})
        if env_audit.get('mongo_is_local') is not True: fail('mongo_is_local must be True for NON_PROD_LOCAL_ONLY')
        if env_audit.get('production_traffic') is not False: fail('production_traffic must be False')
        if ENV.exists():
            env_txt = ENV.read_text()
            for line in env_txt.splitlines():
                if line.strip().startswith('MONGO_URL='):
                    if 'localhost' not in line and '127.0.0.1' not in line:
                        fail(f'env MONGO_URL not local but classification is NON_PROD_LOCAL_ONLY: {line!r}')
    prereq = m.get('prerequisites_satisfied', {})
    for k in ('project_t_complete', 'seam_module_present', 'battle_engine_wired_single_point', 'identity_fallback_present', 'suite_baseline_519_pass'):
        if prereq.get(k) is not True: fail(f'prerequisite {k} must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print(f'[PASS] PROJECT_U Track A canary env precheck READY — classification={cls}; eligibility={m.get("flip_eligibility")}')
    sys.exit(0)


if __name__ == '__main__': main()
