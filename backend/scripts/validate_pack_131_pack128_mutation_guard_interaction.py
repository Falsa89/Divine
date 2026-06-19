#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
R = REPO_ROOT/'backend/routes/v131_combat_preview.py'
def main():
  errs=[]; notes=[]
  if not R.exists(): errs.append('route missing'); return _emit(errs,notes)
  src=R.read_text(encoding='utf-8')
  if '@router.post(' in src: errs.append('Pack 131 route uses POST — should be GET (no Pack 128 allowlist mod)')
  if '@router.get("/preview")' not in src: errs.append('GET /preview not found')
  notes.append('Pack 128 middleware DORMANT in pod; Pack 131 route is GET → bypassa naturalmente.')
  return _emit(errs,notes)
def _emit(errs,notes):
  report={'pack':'PACK_131_PACK128_MUTATION_GUARD_INTERACTION','status':'PASS' if not errs else 'FAIL','errors':errs,'notes':notes,'validation_kind':'STATIC','enforcement':'ENFORCED_GET_ONLY_NO_ALLOWLIST_MOD'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_pack128_mutation_guard_interaction_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  for n in notes: print(f'NOTE {n}')
  print('PASS  Pack 131 GET-only, no Pack 128 allowlist modification needed')
  return 0
if __name__=='__main__': sys.exit(main())
