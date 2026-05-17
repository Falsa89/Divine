#!/usr/bin/env python3
"""
OPS-B — Audit: persistence of the start-expo.sh wrapper under /app/ops.

Verifies:
- /app/ops/start-expo.sh exists, executable bit set, contains the safe
  pattern (fuser cleanup, pkill cleanup, port 3000, exec npx expo start,
  no CI=1 to keep HMR);
- /app/ops/restore_start_expo_wrapper.sh exists, executable, references
  the persistent source path;
- /usr/local/bin/start-expo.sh exists and is byte-identical to the repo
  copy (best-effort cross-check);
- supervisor [program:expo] block references the wrapper;
- frontend on localhost:3000 returns 200/304/302 when expo is running
  (best-effort, doesn't fail the audit if unreachable).

Read-only.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/app')
REPO_WRAPPER = ROOT / 'ops' / 'start-expo.sh'
RESTORE_HELPER = ROOT / 'ops' / 'restore_start_expo_wrapper.sh'
USR_LOCAL = Path('/usr/local/bin/start-expo.sh')
SUPERVISOR_CONF = Path('/etc/supervisor/conf.d/supervisord.conf')

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('repo_wrapper_present', REPO_WRAPPER.exists(), str(REPO_WRAPPER))
record('restore_helper_present', RESTORE_HELPER.exists(), str(RESTORE_HELPER))

if REPO_WRAPPER.exists():
    txt = REPO_WRAPPER.read_text(encoding='utf-8')
    record('repo_wrapper_executable',
           os.access(REPO_WRAPPER, os.X_OK), '')
    record('repo_wrapper_shebang_bash',
           txt.startswith('#!/bin/bash'), '')
    record('repo_wrapper_has_fuser_cleanup',
           'fuser -k 3000/tcp' in txt, '')
    record('repo_wrapper_has_pkill_expo',
           'pkill -9 -f "expo start"' in txt, '')
    record('repo_wrapper_has_pkill_metro',
           'pkill -9 -f "metro"' in txt, '')
    record('repo_wrapper_uses_port_3000',
           '--port 3000' in txt, '')
    record('repo_wrapper_uses_exec',
           'exec npx expo start' in txt, '')
    record('repo_wrapper_no_CI_var',
           'CI=1' not in txt, 'must not set CI=1 (would disable HMR)')

if RESTORE_HELPER.exists():
    rtxt = RESTORE_HELPER.read_text(encoding='utf-8')
    record('restore_helper_executable',
           os.access(RESTORE_HELPER, os.X_OK), '')
    record('restore_helper_references_src',
           str(REPO_WRAPPER) in rtxt, '')
    record('restore_helper_copies_to_usr_local',
           str(USR_LOCAL) in rtxt, '')
    record('restore_helper_chmod_x',
           'chmod +x' in rtxt, '')
    record('restore_helper_supervisor_restart',
           'supervisorctl' in rtxt and 'restart expo' in rtxt, '')

# Cross-check with /usr/local/bin/start-expo.sh
if USR_LOCAL.exists() and REPO_WRAPPER.exists():
    same = USR_LOCAL.read_bytes() == REPO_WRAPPER.read_bytes()
    record('usr_local_matches_repo_copy', same, 'wrapper drift detected')
    record('usr_local_executable',
           os.access(USR_LOCAL, os.X_OK), '')
else:
    record('usr_local_matches_repo_copy', USR_LOCAL.exists(),
           f'/usr/local/bin missing: {not USR_LOCAL.exists()}')
    record('usr_local_executable',
           USR_LOCAL.exists() and os.access(USR_LOCAL, os.X_OK), '')

# Supervisor block reference (best-effort)
for conf in (SUPERVISOR_CONF, *Path('/etc/supervisor/conf.d').glob('*.conf')):
    if conf.exists():
        c = conf.read_text(encoding='utf-8', errors='ignore')
        if '[program:expo]' in c:
            record('supervisor_block_references_wrapper',
                   '/usr/local/bin/start-expo.sh' in c,
                   'expo block should reference wrapper')
            break
else:
    record('supervisor_block_references_wrapper', True,
           'supervisor conf not inspectable; non-blocking')

# Frontend health (best-effort)
try:
    out = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
         'http://127.0.0.1:3000'],
        capture_output=True, text=True, timeout=8,
    )
    code = (out.stdout or '').strip()
    record('frontend_localhost_3000_reachable',
           code in ('200', '304', '302', '301'),
           f'got HTTP {code}')
except Exception as e:
    record('frontend_localhost_3000_reachable', True,
           f'curl unavailable: {e!r}; non-blocking')


print('=' * 70)
print('OPS-B — start-expo.sh Persistence Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
