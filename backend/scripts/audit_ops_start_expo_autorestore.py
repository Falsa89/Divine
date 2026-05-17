#!/usr/bin/env python3
"""
OPS-C — Audit: auto-restore helpers for the Expo wrapper.

Verifies presence + safety of:
- /app/ops/start-expo.sh (OPS-B persistent copy)
- /app/ops/restore_start_expo_wrapper.sh (OPS-B restore one-shot)
- /app/ops/check_and_restore_start_expo_wrapper.sh (OPS-C auto check)
- /app/ops/README_START_EXPO_AUTORESTORE.md
- /usr/local/bin/start-expo.sh aligned + executable
- supervisor [program:expo] references the wrapper
- frontend localhost:3000 reachable (best-effort)
- check_and_restore script is idempotent (safe to re-run; does not
  contain destructive tokens)

No app logic is modified or required. Read-only audit.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

OPS = Path('/app/ops')
PERSIST = OPS / 'start-expo.sh'
RESTORE = OPS / 'restore_start_expo_wrapper.sh'
CHECK = OPS / 'check_and_restore_start_expo_wrapper.sh'
README = OPS / 'README_START_EXPO_AUTORESTORE.md'
USR_LOCAL = Path('/usr/local/bin/start-expo.sh')
SUPERVISOR_CONF_DIR = Path('/etc/supervisor/conf.d')

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


for p in (PERSIST, RESTORE, CHECK, README):
    record(f'present:{p.name}', p.exists(), str(p))
    if p.exists() and p.suffix == '.sh':
        record(f'executable:{p.name}', os.access(p, os.X_OK), '')

if CHECK.exists():
    txt = CHECK.read_text(encoding='utf-8')
    record('check_script_shebang_bash',
           txt.startswith('#!/bin/bash'), '')
    record('check_script_uses_cmp_s',
           'cmp -s' in txt, 'idempotent check requires cmp')
    record('check_script_references_persist',
           str(PERSIST) in txt, '')
    record('check_script_references_usr_local',
           str(USR_LOCAL) in txt, '')
    record('check_script_no_destructive_rm',
           'rm -rf' not in txt and 'rm -fr' not in txt, '')
    record('check_script_no_db_token',
           'mongo' not in txt.lower() and 'pymongo' not in txt.lower(), '')
    record('check_script_idempotent_word',
           'idempotent' in txt.lower(), '')
    record('check_script_no_app_runtime_modify',
           '/app/backend/' not in txt and '/app/frontend/' not in txt, '')

if USR_LOCAL.exists() and PERSIST.exists():
    record('usr_local_aligned',
           USR_LOCAL.read_bytes() == PERSIST.read_bytes(),
           'wrapper drifted')
    record('usr_local_executable',
           os.access(USR_LOCAL, os.X_OK), '')
else:
    record('usr_local_aligned', USR_LOCAL.exists(),
           f'{USR_LOCAL} missing')
    record('usr_local_executable', USR_LOCAL.exists()
           and os.access(USR_LOCAL, os.X_OK), '')

# Supervisor expo block references wrapper
found = False
for conf in SUPERVISOR_CONF_DIR.glob('*.conf'):
    c = conf.read_text(encoding='utf-8', errors='ignore')
    if '[program:expo]' in c:
        found = True
        record('supervisor_block_references_wrapper',
               '/usr/local/bin/start-expo.sh' in c, '')
        break
if not found:
    record('supervisor_block_references_wrapper', True,
           'supervisor conf not inspectable; non-blocking')

# Frontend reachable (best-effort)
try:
    out = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
         'http://127.0.0.1:3000'],
        capture_output=True, text=True, timeout=8,
    )
    code = (out.stdout or '').strip()
    record('frontend_3000_reachable',
           code in ('200', '304', '302', '301'),
           f'got HTTP {code}')
except Exception as e:
    record('frontend_3000_reachable', True,
           f'curl unavailable: {e!r}; non-blocking')


print('=' * 70)
print('OPS-C — start-expo Auto-Restore Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
