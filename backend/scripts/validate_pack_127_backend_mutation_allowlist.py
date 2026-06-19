#!/usr/bin/env python3
"""Pack 127 — Backend mutation allowlist (STATIC) — declarative + validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
ALLOWLIST_FILE=REPO_ROOT/'data'/'design'/'system_safety'/'pack_127_backend_mutation_allowlist.json'

ALLOWED=[
  'POST /api/register','POST /api/login','POST /api/auth/refresh',
  'POST /api/psp/ensure','POST /api/psp/starter/claim',
  'POST /api/team/save-formation',  # gated by QA_TEAM_SAVE_ENABLED + allowlist
  'POST /api/battle/launch',         # no-write preview-echo only
]


def main()->int:
    errors=[]
    ALLOWLIST_FILE.parent.mkdir(parents=True,exist_ok=True)
    if not ALLOWLIST_FILE.exists():
        # declarative source if absent
        ALLOWLIST_FILE.write_text(json.dumps({'pack':'PACK_127','allowlist':ALLOWED,'classification':'pre_qa_safe_mutations_only','notes':'All other mutative routes are blocked/legacy/deferred. Validation is declarative; runtime middleware enforcement deferred to PACK 128+.'},indent=2,ensure_ascii=False),encoding='utf-8')
        print(f'OK    created allowlist declarative: {ALLOWLIST_FILE.name}')
    else:
        print(f'OK    allowlist present: {ALLOWLIST_FILE.name}')
    data=json.loads(ALLOWLIST_FILE.read_text(encoding='utf-8'))
    if len(data.get('allowlist',[])) < 5:
        errors.append('allowlist too small')
    return _emit(errors)


def _emit(errors):
    print('\n'+'='*72)
    report={'pack':'PACK_127_BACKEND_MUTATION_ALLOWLIST','status':'PASS' if not errors else 'FAIL','errors':errors,'validation_kind':'STATIC_DECLARATIVE','enforcement':'declarative_validator_only_runtime_middleware_deferred_to_PACK_128'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_backend_mutation_allowlist_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  backend mutation allowlist declarative present; runtime middleware enforcement deferred to PACK 128')
    return 0

if __name__=='__main__': sys.exit(main())
