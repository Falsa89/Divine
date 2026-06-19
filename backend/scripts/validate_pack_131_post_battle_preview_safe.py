#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT/'backend'))
def main():
  errs=[]
  try:
    from helpers.combat_preview_adapter import build_post_battle_preview
    p=build_post_battle_preview()['post_battle_preview']
    for k,exp in [('preview_only',True),('authoritative',False),('claim_enabled',False),('inventory_mutation',False),('economy_mutation',False),('hero_progression_mutation',False),('not_granted',True),('claim_disabled',True)]:
      if p.get(k)!=exp: errs.append(f'{k}: expected {exp}, got {p.get(k)}')
    for k in ['reward_status','exp_status','progress_status']:
      if p.get(k)!='DISABLED': errs.append(f'{k} not DISABLED')
    if p.get('next_gate')!='PACK_132_OR_LATER': errs.append('next_gate wrong')
  except Exception as e: errs.append(f'import: {e!r}')
  return _emit(errs)
def _emit(errs):
  report={'pack':'PACK_131_POST_BATTLE_PREVIEW_SAFE','status':'PASS' if not errs else 'FAIL','errors':errs,'validation_kind':'UNIT_RUNTIME','enforcement':'ENFORCED_NO_CLAIM_NO_GRANT_NO_MUTATION'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_post_battle_preview_safe_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  print('PASS  post-battle preview safe: no claim, no grant, no mutation')
  return 0
if __name__=='__main__': sys.exit(main())
