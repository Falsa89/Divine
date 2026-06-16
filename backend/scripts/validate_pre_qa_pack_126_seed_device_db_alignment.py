#!/usr/bin/env python3
"""
Pack 126 — Validator: device DB seed alignment.
Verifica che il test account abbia >=10 hero_id canonical su un server_id specifico.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ['greek_hoplite','norse_berserker','celtic_archer','arcane_lightning_enchantress','greek_sanctuary_muse','angelic_priestess','creature_coral_guardian','norse_thunder_spear','celtic_moor_druidess','egyptian_nile_healer']
UID = '651253e2-da8d-466b-98f3-82f008d158ed'
SID = 's1'


def main() -> int:
    errors: list[str] = []
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
    except ImportError:
        errors.append('pymongo/dotenv missing')
        return _emit(errors, {})
    load_dotenv(REPO_ROOT / 'backend' / '.env')
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        errors.append('MONGO_URL missing')
        return _emit(errors, {})
    client = MongoClient(mongo_url)
    names = client.list_database_names()
    db_name = next((n for n in names if n not in ('admin','local','config')), None)
    db = client[db_name]
    docs = list(db.user_heroes.find({'user_id': UID, 'server_id': SID, 'hero_id': {'$in': CANONICAL}}, {'hero_id':1, '_qa_seed':1}))
    have = {d['hero_id'] for d in docs}
    missing = [h for h in CANONICAL if h not in have]
    detail = {'uid': UID, 'server_id': SID, 'db': db_name, 'have_count': len(have), 'missing': missing}
    if missing:
        errors.append(f'missing canonical on server {SID}: {missing}')
    else:
        print(f'OK    {UID}@{SID}: 10/10 canonical heroes')
    return _emit(errors, detail)


def _emit(errors, detail):
    print('\n' + '='*72)
    print('Pack 126 — seed device DB alignment')
    print('='*72)
    report = {'pack': 'PRE_QA_PACK_126_SEED_DEVICE_DB_ALIGNMENT', 'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'detail': detail}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_seed_device_db_alignment_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  device DB has 10 canonical heroes for test account')
    return 0


if __name__ == '__main__':
    sys.exit(main())
