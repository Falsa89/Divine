#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
FILES=[REPO_ROOT/'backend/routes/v131_combat_preview.py',REPO_ROOT/'backend/helpers/combat_preview_adapter.py']
FORBIDDEN=['update_one(','update_many(','insert_one(','insert_many(','delete_one(','delete_many(','replace_one(','find_one_and_update(','find_one_and_delete(','find_one_and_replace(','bulk_write(','create_index(']
def main():
  errs=[]
  for f in FILES:
    if not f.exists(): continue
    src=f.read_text(encoding='utf-8')
    for fp in FORBIDDEN:
      if fp in src: errs.append(f'{f.name}: {fp}')
  return _emit(errs)
def _emit(errs):
  report={'pack':'PACK_131_NO_DB_WRITES','status':'PASS' if not errs else 'FAIL','errors':errs,'validation_kind':'STATIC','enforcement':'ENFORCED_NO_DB_WRITE_PACK_131'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_no_db_writes_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  print('PASS  zero DB writes in Pack 131')
  return 0
if __name__=='__main__': sys.exit(main())
