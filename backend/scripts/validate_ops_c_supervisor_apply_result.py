#!/usr/bin/env python3
"""OPS-C-SUPERVISOR-APPLY — Validator for the apply-attempt result."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

R = Path('/app/data/design/ops/ops_c_supervisor_apply_result_v1.json')
DST = Path('/etc/supervisor/conf.d/startup_check.conf')
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('result_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'ops_c_supervisor_apply_result_v1', '')
rec('task', r.get('task_origin') == 'OPS-C-SUPERVISOR-APPLY-PREP/FULL-SAFE', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('runtime_off', r.get('runtime_attached') is False, '')
rec('db_write_off', r.get('db_write') is False, '')

applied = r.get('applied')
rnna = r.get('ready_not_applied')
rec('result_mode_acceptable', (applied is True and rnna in (None, False)) or (applied is False and rnna is True),
    f'applied={applied} ready_not_applied={rnna}')
if applied is False:
    rec('reason_present', bool(r.get('reason')), '')
    rec('detail_present', bool(r.get('detail')), '')

steps = r.get('steps_executed') or []
rec('steps_min_4', len(steps) >= 4, f'got {len(steps)}')
rec('backup_step_present', any(s.get('step') == 'backup_conf_d' for s in steps), '')
rec('reread_step_present', any(s.get('step') == 'supervisorctl_reread' for s in steps), '')
rec('update_step_present', any(s.get('step') == 'supervisorctl_update' for s in steps), '')

post = r.get('post_state') or {}
rec('post_backend_running', post.get('backend_running') is True, '')
rec('post_expo_running', post.get('expo_running') is True, '')
rec('post_mongodb_running', post.get('mongodb_running') is True, '')
rec('post_fastapi_hook', post.get('fastapi_startup_hook_active') is True, '')

sf = r.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('AF2N_allowed_today') is False, '')
rec('sf_wiring_state_known', sf.get('supervisor_wiring_state') in ('READY_NOT_APPLIED','APPLIED'), '')

# Live: verify services are still running
try:
    out = subprocess.run(['supervisorctl','status'], capture_output=True, text=True, timeout=10)
    s = out.stdout or ''
    rec('live_backend_running', 'backend' in s and 'RUNNING' in s, '')
    rec('live_expo_running', 'expo' in s and 'RUNNING' in s, '')
    rec('live_mongodb_running', 'mongodb' in s and 'RUNNING' in s, '')
except Exception as e:
    rec('live_backend_running', False, f'{e!r}')

rec('dst_state_matches_applied_flag',
    (applied is True and DST.exists()) or (applied is False and not DST.exists()),
    f'applied={applied} dst_exists={DST.exists()}')

print('='*70); print('OPS-C-SUPERVISOR-APPLY — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
