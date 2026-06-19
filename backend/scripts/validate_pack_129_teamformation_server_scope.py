#!/usr/bin/env python3
"""Pack 129 — TeamFormation server-scope audit (STATIC).

Audit del Pack 125 endpoint backend/routes/v96_team_formation.py per
confermare proprietà server-scoped:
  - PSP find_one con (user_id, server_id) — fail-closed se assente
  - ownership user_heroes filter by server_id (o _qa_seed marker)
  - update_one filter (user_id, server_id) — mai user-only
  - no fallback account-wide
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE = REPO_ROOT / 'backend' / 'routes' / 'v96_team_formation.py'

REQUIRED_SIGNALS = [
    'find_one(\n            {"user_id": uid_uuid, "server_id": server_id}',
    'update_one(\n            {"user_id": uid_uuid, "server_id": server_id}',
    '@router.post("/save-formation")',
    'Depends(get_current_user)',
    'PLAYER_SERVER_PROFILE_REQUIRED',
    '_qa_seed',
    'team_formation',
]
FORBIDDEN_SIGNALS = [
    # account-wide fallback (mai accettabile):
    'find_one({"user_id": uid_uuid})',  # senza server_id
    'update_one({"user_id": uid_uuid})',  # senza server_id
    'await db.users.update_one(',  # save su users → account-wide
]


def main() -> int:
    errors = []; notes = []
    if not ROUTE.exists(): errors.append('v96_team_formation.py missing'); return _emit(errors, notes)
    src = ROUTE.read_text(encoding='utf-8')
    for sig in REQUIRED_SIGNALS:
        if sig not in src: errors.append(f'required signal missing: `{sig[:60]}...`')
    for fp in FORBIDDEN_SIGNALS:
        if fp in src: errors.append(f'forbidden account-wide pattern detected: `{fp}`')
    print(f'OK    route file scanned: {len(REQUIRED_SIGNALS)} required signals + {len(FORBIDDEN_SIGNALS)} forbidden patterns')
    if 'team_formation_payload' in src and 'await db.player_server_profiles.update_one' in src:
        print('OK    write target = player_server_profiles (NOT users)')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_TEAMFORMATION_SERVER_SCOPE',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_PACK_125_ENDPOINT_AUDITED_NO_ACCOUNT_WIDE_FALLBACK'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_teamformation_server_scope_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  TeamFormation V1 endpoint is server-scoped, no account-wide fallback detected')
    return 0


if __name__ == '__main__': sys.exit(main())
