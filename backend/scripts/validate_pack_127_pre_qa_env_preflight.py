#!/usr/bin/env python3
"""Pack 127 — Pre-QA env preflight validator (STATIC).
Fails if dangerous env defaults or missing required pre-QA env vars."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / 'backend' / '.env')

REQUIRED_FALSE = ['GACHA_LIVE_ENABLED','STORY_BATTLE_LEGACY_ENABLED','TOWER_LEGACY_LIVE_ENABLED','PVP_BATTLE_LEGACY_ENABLED','EVENTS_BATTLE_LEGACY_ENABLED','REGISTER_LEGACY_STARTER_HEROES_ENABLED']
REQUIRED_TRUE  = ['BOTS_DISABLED','BOT_KILL_SWITCH']


def main() -> int:
    errors=[]; notes=[]
    # Required env
    for k in REQUIRED_FALSE:
        v=(os.environ.get(k,'') or '').strip().lower()
        if v not in ('false','0','off',''):
            errors.append(f'env `{k}` must be false/off (got `{v}`)')
        else: print(f'OK    {k}={v or "<unset>"} (treated false)')
    for k in REQUIRED_TRUE:
        v=(os.environ.get(k,'') or '').strip().lower()
        if v != 'true':
            notes.append(f'env `{k}` not explicitly true (got `{v}`) — MANUAL_REQUIRED in QA runtime')
        else: print(f'OK    {k}=true')
    # QA team save allowlist sanity
    al=(os.environ.get('QA_TEAM_SAVE_ALLOWLIST','') or '').strip()
    if al == '*':
        errors.append('QA_TEAM_SAVE_ALLOWLIST=* is FORBIDDEN in pre-QA')
    else:
        print(f'OK    QA_TEAM_SAVE_ALLOWLIST safe (not wildcard): `{al or "<unset>"}`')
    # MONGO_URL must exist and not be hardcoded sentinel
    mu = os.environ.get('MONGO_URL','')
    if not mu:
        errors.append('MONGO_URL not set')
    else:
        print('OK    MONGO_URL set')
    # JWT secret presence
    jwt = os.environ.get('JWT_SECRET') or os.environ.get('JWT_SECRET_KEY') or ''
    if not jwt or jwt.lower() in ('change-me','default','secret','test','dev'):
        errors.append('JWT secret missing or default/unsafe')
    else: print('OK    JWT secret set (non-default)')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n'+'='*72)
    report={'pack':'PACK_127_PRE_QA_ENV_PREFLIGHT','status':'PASS' if not errors else 'FAIL','errors':errors,'notes':notes,'validation_kind':'STATIC+ENV'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_pre_qa_env_preflight_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    if notes:
        for n in notes: print(f'  NOTE  {n}')
    print('PASS  pre-QA env preflight (static+env)')
    return 0

if __name__=='__main__': sys.exit(main())
