#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, subprocess, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHOR='2f490421e07fc119e17000a29628b0ffbbc77d19'
def main():
  errs=[]
  r=subprocess.run(['git','-C',str(REPO_ROOT),'diff','--name-only',f'{ANCHOR}..HEAD'],capture_output=True,text=True)
  changed=[l.strip() for l in r.stdout.splitlines() if l.strip()]
  for f in changed:
    if f in ('backend/battle_engine.py','backend/battle_core.py','backend/game_systems.py'):
      errs.append(f'forbidden engine file modified: {f}')
  # static: route does not import battle_engine
  route=REPO_ROOT/'backend/routes/v131_combat_preview.py'
  if route.exists():
    src=route.read_text(encoding='utf-8')
    for fp in ['from battle_engine','from backend.battle_engine','import battle_engine','battle_engine.simulate(']:
      if fp in src: errs.append(f'route imports/calls battle_engine: {fp}')
  return _emit(errs, changed)
def _emit(errs, changed):
  report={'pack':'PACK_131_NO_BATTLE_ENGINE_MUTATION','status':'PASS' if not errs else 'FAIL','errors':errs,'files_changed_since_pack130':changed,'validation_kind':'STATIC+GIT_DIFF','enforcement':'ENFORCED_BATTLE_ENGINE_NOT_TOUCHED_NOT_CALLED'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_no_battle_engine_mutation_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  print('PASS  battle_engine untouched, not imported, not called')
  return 0
if __name__=='__main__': sys.exit(main())
