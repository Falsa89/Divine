#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
H = REPO_ROOT/'backend/helpers/combat_preview_adapter.py'
def main():
  errs=[]
  if not H.exists(): errs.append('adapter missing'); return _emit(errs)
  src=H.read_text(encoding='utf-8')
  for req in ['build_combat_preview_input','build_post_battle_preview','PACK_130_REAL_PLAYER_SNAPSHOT','BATTLE_ENGINE_EXECUTION_DEFERRED']:
    if req not in src: errs.append(f'symbol missing: {req}')
  for forbidden in ['update_one(','insert_one(','db.users.','grant_reward','add_exp','battle_engine.simulate(']:
    if forbidden in src: errs.append(f'forbidden in adapter: {forbidden}')
  return _emit(errs)
def _emit(errs):
  report={'pack':'PACK_131_SNAPSHOT_TO_COMBAT_ADAPTER','status':'PASS' if not errs else 'FAIL','errors':errs,'validation_kind':'STATIC','enforcement':'ENFORCED_ADAPTER_PURE_NO_WRITE_NO_ENGINE_CALL'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_snapshot_to_combat_adapter_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  print('PASS  adapter pure, no DB write, no engine call')
  return 0
if __name__=='__main__': sys.exit(main())
