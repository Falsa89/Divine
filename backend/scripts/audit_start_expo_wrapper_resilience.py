#!/usr/bin/env python3
"""
OPS-A — start-expo.sh wrapper resilience audit.

Reads `/app/data/design/ops/start_expo_wrapper_resilience_plan_v1.json` and
asserts that all required audit checks defined therein pass on the live
system. Read-only.
"""
from __future__ import annotations
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path('/app')
PLAN = ROOT / 'data' / 'design' / 'ops' / 'start_expo_wrapper_resilience_plan_v1.json'
SCRIPT = Path('/usr/local/bin/start-expo.sh')
RECOVERY_DOC = ROOT / 'docs' / 'ops' / 'EXPO_WRAPPER_RECOVERY.md'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# Plan present
record('plan_present', PLAN.exists(), str(PLAN))
plan = json.loads(PLAN.read_text(encoding='utf-8'))
record('plan_id',
       plan.get('doc_id') == 'start_expo_wrapper_resilience_plan_v1', '')
record('plan_task_origin', plan.get('task_origin') == 'OPS-A', '')

# Recovery doc present
record('recovery_doc_present', RECOVERY_DOC.exists(), str(RECOVERY_DOC))

# Script present + executable + content
record('script_exists', SCRIPT.exists(), str(SCRIPT))
if SCRIPT.exists():
    st = SCRIPT.stat()
    record('script_executable',
           bool(st.st_mode & stat.S_IXUSR), 'chmod +x required')
    txt = SCRIPT.read_text(encoding='utf-8')
    record('script_has_fuser_cleanup',
           'fuser -k 3000/tcp' in txt, '')
    record('script_has_pkill_cleanup',
           'pkill' in txt and 'metro' in txt, '')
    record('script_uses_exec',
           re.search(r'^\s*exec\s+npx\s+expo\s+start', txt, re.MULTILINE) is not None,
           'must use exec npx expo start')
    record('script_port_3000',
           '--port 3000' in txt, '')
    record('script_no_CI_var',
           'CI=1' not in txt, 'CI=1 disables HMR; should not be set')

# Supervisor config references the wrapper
sv_conf = None
for candidate in [
    Path('/etc/supervisor/conf.d/supervisord.conf'),
    Path('/etc/supervisor/conf.d/expo.conf'),
]:
    if candidate.exists():
        sv_conf = candidate
        break
if sv_conf is None:
    # try glob
    for c in Path('/etc/supervisor/conf.d').glob('*.conf'):
        t = c.read_text(encoding='utf-8', errors='ignore')
        if 'program:expo' in t:
            sv_conf = c
            break
if sv_conf is not None:
    txt = sv_conf.read_text(encoding='utf-8', errors='ignore')
    record('supervisor_block_references_wrapper',
           '/usr/local/bin/start-expo.sh' in txt, str(sv_conf))
else:
    record('supervisor_block_references_wrapper', False,
           'no supervisor config with program:expo found')

# expo RUNNING (best-effort)
try:
    r = subprocess.run(['sudo', 'supervisorctl', 'status', 'expo'],
                       capture_output=True, text=True, timeout=15)
    out = (r.stdout or '') + (r.stderr or '')
    record('expo_running', 'RUNNING' in out, f'output: {out.strip()[:200]}')
except Exception as e:
    record('expo_running', False, f'{e!r}')

print('=' * 70)
print('OPS-A — start-expo.sh Wrapper Resilience Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
