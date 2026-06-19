#!/usr/bin/env python3
"""Pack 129 — Mutation guard / Team allowlist interaction (STATIC).

Verifica che POST /api/team/save-formation sia nell'allowlist Pack 128.
Se il middleware Pack 128 fosse attivo, la route deve PASSARE (allowlisted)
ma essere comunque gated dal QA_TEAM_SAVE_ENABLED env del Pack 125.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AL_FILE = REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_128_backend_mutation_allowlist.json'


def main() -> int:
    errors = []; notes = []
    if not AL_FILE.exists(): errors.append('pack_128_backend_mutation_allowlist.json missing'); return _emit(errors, notes)
    data = json.loads(AL_FILE.read_text(encoding='utf-8'))
    al = data.get('allowlist', [])
    needle = 'POST /api/team/save-formation'
    matched = any((needle == e or (isinstance(e, dict) and e.get('method') == 'POST' and e.get('path') == '/api/team/save-formation')) for e in al)
    if not matched:
        errors.append(f'`{needle}` NOT in Pack 128 allowlist (route bloccata se middleware attivo)')
    else:
        print(f'OK    `{needle}` is in Pack 128 allowlist')
    notes.append('Pack 128 middleware is DORMANT by default (PRE_QA_MUTATION_GUARD_ENABLED unset). When active, this route would pass; QA_TEAM_SAVE_ENABLED gate Pack 125 still applies.')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_MUTATION_GUARD_TEAM_ALLOWLIST_INTERACTION',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_ALLOWLIST_COHERENT_WITH_PACK_128'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_mutation_guard_team_allowlist_interaction_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes: print(f'  NOTE  {n}')
    print('PASS  team save route is in Pack 128 allowlist; double-gated by QA_TEAM_SAVE_ENABLED Pack 125')
    return 0


if __name__ == '__main__': sys.exit(main())
