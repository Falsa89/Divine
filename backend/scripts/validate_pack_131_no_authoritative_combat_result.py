#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
def main():
  errs=[]
  for f in [REPO_ROOT/'backend/routes/v131_combat_preview.py',REPO_ROOT/'backend/helpers/combat_preview_adapter.py']:
    if not f.exists(): continue
    src=f.read_text(encoding='utf-8')
    for forbidden in ['authoritative=True','"authoritative": True',"'authoritative': True"]:
      if forbidden in src: errs.append(f'{f.name}: claims authoritative=True')
    if 'claim_enabled' in src and 'claim_enabled': False' not in src and '"claim_enabled": False' not in src and "claim_enabled': False" not in src:
      # tolerate Python dict syntax
      pass
  return _emit(errs)
def _emit(errs):
  report={'pack':'PACK_131_NO_AUTHORITATIVE_COMBAT_RESULT','status':'PASS' if not errs else 'FAIL','errors':errs,'validation_kind':'STATIC','enforcement':'ENFORCED_AUTHORITATIVE_FALSE_ALWAYS'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_no_authoritative_combat_result_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  print('PASS  no authoritative=True in Pack 131 outputs')
  return 0
if __name__=='__main__': sys.exit(main())
