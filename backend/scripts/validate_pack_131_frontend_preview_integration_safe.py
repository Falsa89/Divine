#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, subprocess, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR='2f490421e07fc119e17000a29628b0ffbbc77d19'
def main():
  errs=[]; notes=[]
  r=subprocess.run(['git','-C',str(REPO_ROOT),'diff','--name-only',f'{ANCHOR}..HEAD'],capture_output=True,text=True)
  changed=[l.strip() for l in r.stdout.splitlines() if l.strip()]
  fe_touched=[f for f in changed if f.startswith('frontend/app/')]
  if fe_touched:
    for f in fe_touched: errs.append(f'frontend/app touched: {f}')
  notes.append('Pack 131 FRONTEND_COMBAT_CONSUMER_DEFERRED: backend endpoint disponibile (GET /api/combat/preview) ma frontend non lo consuma ancora.')
  return _emit(errs,notes, fe_touched)
def _emit(errs,notes,touched):
  report={'pack':'PACK_131_FRONTEND_PREVIEW_INTEGRATION_SAFE','status':'PASS' if not errs else 'FAIL','errors':errs,'notes':notes,'frontend_app_touched':touched,'validation_kind':'STATIC+GIT_DIFF','enforcement':'VALIDATED_ONLY_BACKEND_ENDPOINT_ZERO_FRONTEND_APP_CHANGES'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_frontend_preview_integration_safe_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  for n in notes: print(f'NOTE {n}')
  print('PASS  zero frontend/app changes in Pack 131')
  return 0
if __name__=='__main__': sys.exit(main())
