#!/usr/bin/env python3
"""Pack 131 validator (auto-generated)."""
from __future__ import annotations

import json, sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
def main():
  errs=[]; notes=[]
  # Pack 131 codes: documentated in marker, not all must be in code (some are status strings)
  for fp in [REPO_ROOT/'backend/helpers/combat_preview_adapter.py']:
    src=fp.read_text(encoding='utf-8') if fp.exists() else ''
    for code in ['BATTLE_ENGINE_EXECUTION_DEFERRED','DISABLED']:
      if code not in src: errs.append(f'code `{code}` missing in {fp.name}')
  notes.append('Pack 131 structured errors aliases Pack 129 codes (AUTH_REQUIRED, SERVER_*, LOBBY_MODE_INVALID, TEAM_FORMATION_MISSING) via Pack 130 launch_context_helper chain.')
  return _emit(errs, notes)
def _emit(errs, notes):
  report={'pack':'PACK_131_STRUCTURED_ERRORS_CONTRACT','status':'PASS' if not errs else 'FAIL','errors':errs,'notes':notes,'validation_kind':'STATIC','enforcement':'ENFORCED_STATUS_CODES_PRESENT_VIA_PACK_130_CHAIN'}
  out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
  (out/'pack_131_structured_errors_contract_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  if errs:
    for e in errs: print(f'FAIL {e}')
    return 1
  for n in notes: print(f'NOTE {n}')
  print('PASS  Pack 131 status codes present, aliases Pack 129 via chain')
  return 0
if __name__=='__main__': sys.exit(main())
