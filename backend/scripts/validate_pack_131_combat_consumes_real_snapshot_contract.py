#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT/'backend'))
def main():
  errs=[]
  for f in ['backend/routes/v131_combat_preview.py','backend/helpers/combat_preview_adapter.py']:
    p=REPO_ROOT/f
    if not p.exists(): errs.append(f'missing: {f}')
  try:
    from helpers.combat_preview_adapter import build_combat_preview_input, build_post_battle_preview
    snap={'heroes':[{'snapshot_status':'OK','user_hero_id':'uh1','hero_id':'h1','level':5,'stars':3,'rarity':'RARE','element':'FIRE','slot':{'col':0,'row':0}}],'player_snapshot_hash':'abc'}
    out=build_combat_preview_input(snap, mode='training', server_id='s1')
    if out['combat_preview_input']['source']!='PACK_130_REAL_PLAYER_SNAPSHOT': errs.append('wrong source')
    if out['combat_preview_input']['authoritative']!=False: errs.append('authoritative must be False')
    if out['battle_engine_execution_status']!='BATTLE_ENGINE_EXECUTION_DEFERRED': errs.append('engine not deferred')
    if out['reward_status']!='DISABLED' or out['exp_status']!='DISABLED' or out['progress_status']!='DISABLED': errs.append('reward/exp/progress not DISABLED')
    if len(out['combat_preview_input']['team_a'])!=1: errs.append('team_a wrong size')
  except Exception as e: errs.append(f'import/exec failed: {e!r}')
  return _emit(errs)
def _emit(errs):
  report={'pack':'PACK_131_COMBAT_CONSUMES_REAL_SNAPSHOT_CONTRACT','status':'PASS' if not errs else 'FAIL','errors':errs,'validation_kind':'STATIC+UNIT_RUNTIME','enforcement':'ENFORCED_HELPER_BUILDS_PREVIEW_INPUT_FROM_PACK_130_SNAPSHOT'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_combat_consumes_real_snapshot_contract_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  print('PASS  Pack 131 adapter consumes Pack 130 snapshot, preview-only, no engine execution')
  return 0
if __name__=='__main__': sys.exit(main())
