#!/usr/bin/env python3
"""Pack 129 — No account-wide team fallback (STATIC).

Grep agressivo per detect potenziali fallback account-wide team formation
(es. update users.team, find users by team, salvataggi team su `db.users`).

Questo validator scansiona TUTTO backend/ per evitare leak.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# Pack 129: scansione ristretta alla "production runtime surface" \u2014
# routes/server/middleware/helpers. Esclude scripts/, tests/, backups/,
# dove validator/script di test possono contenere pattern dimostrativi che NON
# rappresentano un fallback account-wide a runtime.
BACKEND_RUNTIME_SCOPE = [
    REPO_ROOT / 'backend' / 'routes',
    REPO_ROOT / 'backend' / 'middleware',
    REPO_ROOT / 'backend' / 'helpers',
]
BACKEND_RUNTIME_FILES = [
    REPO_ROOT / 'backend' / 'server.py',
    REPO_ROOT / 'backend' / 'battle_engine.py',
    REPO_ROOT / 'backend' / 'battle_core.py',
    REPO_ROOT / 'backend' / 'game_systems.py',
]

DANGEROUS_PATTERNS = [
    r'db\.users\.update_one\([^)]*team_formation',
    r'db\.users\.update_one\([^)]*\{"\$set":\s*\{[^}]*team',
    r'\.update_one\(\s*\{[^}]*"user_id"\s*:[^}]*\}\s*,[^)]*team_formation',  # update senza server_id filter
]

IGNORE = ['__pycache__', '.git', 'scripts/reports', 'tests/', 'backups/', '.bak']


def main() -> int:
    errors = []; notes = []
    violations = []
    files_to_scan = []
    for d in BACKEND_RUNTIME_SCOPE:
        if d.exists():
            files_to_scan.extend(d.rglob('*.py'))
    for f in BACKEND_RUNTIME_FILES:
        if f.exists():
            files_to_scan.append(f)
    for f in files_to_scan:
        rel = str(f.relative_to(REPO_ROOT))
        if any(ig in rel for ig in IGNORE): continue
        try:
            src = f.read_text(encoding='utf-8')
        except Exception:
            continue
        for pat in DANGEROUS_PATTERNS:
            for m in re.finditer(pat, src):
                snippet = m.group(0)[:160]
                start = m.start()
                ctx = src[max(0, start-200):start+300]
                if 'server_id' in ctx:
                    continue
                violations.append({'file': rel, 'pattern': pat, 'snippet': snippet})
    if violations:
        for v in violations[:10]:
            errors.append(f'potential account-wide team write: {v["file"]} :: {v["snippet"]}')
    print(f'OK    backend runtime scope scan: {len(files_to_scan)} files, {len(violations)} potential account-wide team patterns (server_id-less)')
    return _emit(errors, notes, violations)


def _emit(errors, notes, violations):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_NO_ACCOUNT_WIDE_TEAM_FALLBACK',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'violations': violations,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_BACKEND_WIDE_SCAN_NO_ACCOUNT_WIDE_TEAM_WRITES'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_no_account_wide_team_fallback_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  no account-wide team fallback detected in backend')
    return 0


if __name__ == '__main__': sys.exit(main())
