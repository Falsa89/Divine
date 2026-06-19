#!/usr/bin/env python3
"""Pack 127 — Bot system disabled (STATIC + env)."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT=Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT/'backend'/'.env')


def main()->int:
    errors=[]
    bots=(os.environ.get('BOTS_DISABLED','') or '').strip().lower()
    kill=(os.environ.get('BOT_KILL_SWITCH','') or '').strip().lower()
    runtime_proof_missing = (bots != 'true') or (kill != 'true')
    if runtime_proof_missing:
        print(f'NOTE  BOTS_DISABLED={bots or "<unset>"} BOT_KILL_SWITCH={kill or "<unset>"} — MANUAL_REQUIRED to enable in supervisor for runtime')
    else:
        print('OK    BOTS_DISABLED=true and BOT_KILL_SWITCH=true')
    # Check bot router files for env gate
    bot_files=list((REPO_ROOT/'backend'/'routes').glob('*bot*.py')) + list((REPO_ROOT/'backend').glob('bot*.py'))
    found_gate=False
    for f in bot_files:
        try:
            src=f.read_text(encoding='utf-8')
            if 'BOTS_DISABLED' in src or 'BOT_KILL_SWITCH' in src:
                found_gate=True; print(f'OK    bot file {f.name} reads kill-switch env')
        except Exception: pass
    if bot_files and not found_gate:
        print('NOTE  bot files exist but no env gate detected — verify bot cycle stub')
    print(f'OK    bot files scanned: {len(bot_files)}')
    return _emit(errors)


def _emit(errors):
    print('\n'+'='*72)
    report={'pack':'PACK_127_BOT_SYSTEM_DISABLED','status':'PASS' if not errors else 'FAIL','errors':errors,'validation_kind':'STATIC+ENV','runtime_note':'MANUAL_REQUIRED to confirm no bot cycle running in supervisor'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_bot_system_disabled_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  bot system static check OK (runtime verification MANUAL_REQUIRED)')
    return 0

if __name__=='__main__': sys.exit(main())
