#!/usr/bin/env python3
"""OPS-C-SUPERVISOR-WIRING — Audit (ready_not_applied path).

Verifies:
  - all four supporting assets exist (snippet, apply, rollback, doc)
  - snippet has correct [program:startup_check] block
  - apply script contains backup + reread/update + verify + rollback
  - rollback script removes the conf and reloads supervisor
  - snippet is NOT currently installed at /etc/supervisor/conf.d/startup_check.conf
    (ready_not_applied) OR is installed AND backend+expo are RUNNING
  - V10 acceptance: either path is allowed
"""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

SNIPPET = Path('/app/ops/supervisor_startup_check_snippet.conf')
APPLY = Path('/app/ops/apply_supervisor_startup_check_wiring.sh')
ROLLBACK = Path('/app/ops/rollback_supervisor_startup_check_wiring.sh')
DOC = Path('/app/docs/divine/68_OPS_SUPERVISOR_STARTUP_WIRING.md')
DST = Path('/etc/supervisor/conf.d/startup_check.conf')

failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('snippet_present', SNIPPET.exists(), str(SNIPPET))
rec('apply_present', APPLY.exists(), str(APPLY))
rec('rollback_present', ROLLBACK.exists(), str(ROLLBACK))
rec('doc_present', DOC.exists(), str(DOC))

if SNIPPET.exists():
    t = SNIPPET.read_text()
    rec('snippet_program_block', '[program:startup_check]' in t, '')
    rec('snippet_command_correct', 'bash /app/ops/startup_check.sh' in t, '')
    rec('snippet_autorestart_false', 'autorestart=false' in t, '')
    rec('snippet_priority_10', 'priority=10' in t, '')
    rec('snippet_no_rm_rf', 'rm -rf' not in t, '')
    rec('snippet_no_mongo', 'mongo' not in t.lower() and 'pymongo' not in t.lower(), '')

if APPLY.exists():
    rec('apply_executable', os.access(APPLY, os.X_OK), '')
    t = APPLY.read_text()
    rec('apply_has_backup', '/app/backups/supervisor' in t and 'cp -rp /etc/supervisor/conf.d' in t, '')
    rec('apply_uses_reread_update', 'supervisorctl reread' in t and 'supervisorctl update' in t, '')
    rec('apply_verifies_status', 'supervisorctl status' in t, '')
    rec('apply_auto_rollback', 'rollback_supervisor_startup_check_wiring.sh' in t, '')
    rec('apply_set_euo', 'set -euo pipefail' in t, '')
    rec('apply_no_rm_rf', 'rm -rf' not in t, '')

if ROLLBACK.exists():
    rec('rollback_executable', os.access(ROLLBACK, os.X_OK), '')
    t = ROLLBACK.read_text()
    rec('rollback_removes_conf', 'rm -f' in t and 'startup_check.conf' in t, '')
    rec('rollback_reloads_supervisor', 'supervisorctl reread' in t and 'supervisorctl update' in t, '')
    rec('rollback_no_rm_rf', 'rm -rf' not in t, '')

# Wiring state
if DST.exists():
    rec('wiring_state', True, 'APPLIED')
    try:
        out = subprocess.run(['supervisorctl', 'status'], capture_output=True, text=True, timeout=10)
        s = out.stdout or ''
        rec('backend_running', 'backend' in s and 'RUNNING' in s.split('backend')[1][:40], '')
        rec('expo_running', 'expo' in s and 'RUNNING' in s.split('expo')[1][:40], '')
    except Exception as e:
        rec('backend_running', False, f'supervisorctl unreachable: {e!r}')
        rec('expo_running', False, f'supervisorctl unreachable: {e!r}')
else:
    rec('wiring_state', True, 'READY_NOT_APPLIED')
    # When not applied, backend+expo must still be alive
    try:
        out = subprocess.run(['supervisorctl', 'status'], capture_output=True, text=True, timeout=10)
        s = out.stdout or ''
        rec('backend_running_unaffected', 'backend' in s and 'RUNNING' in s, '')
        rec('expo_running_unaffected', 'expo' in s and 'RUNNING' in s, '')
    except Exception as e:
        rec('backend_running_unaffected', False, f'{e!r}')
        rec('expo_running_unaffected', False, f'{e!r}')

print('='*70); print('OPS-C-SUPERVISOR-WIRING — Audit'); print('='*70)
for n, ok, note in checks:
    marker = 'OK' if ok else 'X'
    print(f'  [{marker}] {n} {("- " + note) if note else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
