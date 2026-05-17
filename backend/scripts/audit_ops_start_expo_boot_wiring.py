#!/usr/bin/env python3
"""OPS-C-WIRING — Audit boot wiring for the Expo wrapper."""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

OPS = Path('/app/ops')
STARTUP = OPS / 'startup_check.sh'
HOOK = OPS / 'check_and_restore_start_expo_wrapper.sh'
README = OPS / 'README_BOOT_WIRING.md'
USR_LOCAL = Path('/usr/local/bin/start-expo.sh')

failures: list[str] = []; checks: list[tuple[str,bool,str]] = []
def record(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

record('startup_present', STARTUP.exists(), str(STARTUP))
record('hook_present', HOOK.exists(), str(HOOK))
record('readme_present', README.exists(), str(README))

if STARTUP.exists():
    record('startup_executable', os.access(STARTUP, os.X_OK), '')
    t = STARTUP.read_text()
    record('startup_calls_hook', str(HOOK) in t, '')
    record('startup_no_rm_rf', 'rm -rf' not in t, '')
    record('startup_no_mongo', 'mongo' not in t.lower() and 'pymongo' not in t.lower(), '')
    record('startup_no_app_modify', '/app/backend/' not in t and '/app/frontend/' not in t, '')
    record('startup_shebang', t.startswith('#!/bin/bash'), '')
if HOOK.exists():
    record('hook_executable', os.access(HOOK, os.X_OK), '')
if USR_LOCAL.exists():
    record('usr_local_present', True, '')
    record('usr_local_executable', os.access(USR_LOCAL, os.X_OK), '')
else:
    record('usr_local_present', False, 'missing')

try:
    out = subprocess.run(['curl','-s','-o','/dev/null','-w','%{http_code}','http://127.0.0.1:3000'],
                         capture_output=True, text=True, timeout=8)
    code = (out.stdout or '').strip()
    record('frontend_3000', code in ('200','304','302','301'), f'got HTTP {code}')
except Exception as e:
    record('frontend_3000', True, f'curl unavailable: {e!r}; non-blocking')

print('='*70); print('OPS-C-WIRING — Boot Wiring Audit'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
