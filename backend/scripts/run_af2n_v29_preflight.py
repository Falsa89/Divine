#!/usr/bin/env python3
"""V29 PART A — Preflight checks (read-only)."""
import asyncio, json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
OUT = Path('/app/data/design/affinity/af2n_v29_preflight_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _get(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {'error': str(e)[:120]}


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request('http://127.0.0.1:8001/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=4) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return -1


def _git_clean(f):
    out = subprocess.run(['git', '-C', '/app', 'diff', '--stat', '--', f],
                          capture_output=True, text=True, timeout=5)
    return out.stdout.strip() == ''


async def _async_main():
    from motor.motor_asyncio import AsyncIOMotorClient
    started = datetime.now(timezone.utc).isoformat()
    sup = subprocess.run(['supervisorctl', 'status'], capture_output=True, text=True, timeout=8).stdout
    services = {}
    for line in sup.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            services[parts[0]] = parts[1]

    cs = _get('/api/affinity/gift-spend/canary-status') or {}
    heroes = _get('/api/heroes') or []
    leak = sorted({(h.get('id') or '').lower() for h in heroes if isinstance(h, dict)} & {'borea','greek_borea','primordial_gaia'})
    borea_codes = []
    for a in ('borea', 'greek_borea', 'primordial_gaia'):
        borea_codes.append({'alias': a, 'code': _post({'gift_id':'x','hero_id':a,'quantity':1,'idempotency_key':f'v29_pre_b_{a}_aabbccdd','user_id':'stage4_qa_001'})})

    # Schema fix report exists
    fix_report = Path('/app/data/design/affinity/af2n_v28_scope_s1_schema_fix_result.json')
    fix_pass = False
    if fix_report.exists():
        try: fix_pass = json.loads(fix_report.read_text()).get('verdict') == 'PASS'
        except Exception: pass

    # DB inventory schema count
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']
    marker_total = await db.user_gift_inventory.count_documents({'meta.v28_scope_s1': True})
    marker_flat = await db.user_gift_inventory.count_documents({'meta.v28_scope_s1': True, 'gift_id': {'$exists': True}, 'quantity': {'$exists': True}})
    marker_nested = await db.user_gift_inventory.count_documents({'meta.v28_scope_s1': True, 'balances': {'$exists': True}})
    client.close()

    out = {
        'task_origin': 'AF2-N-V29-PREFLIGHT',
        'timestamp_utc': started,
        'services': services,
        'canary_status': {
            'rate_limit_backend': cs.get('rate_limit_backend'),
            'canary_ledger_cap': cs.get('canary_ledger_cap'),
            'canary_allowlist_size': cs.get('canary_allowlist_size'),
            'ledger_total_rows': cs.get('ledger_total_rows'),
        },
        'heroes_count': len(heroes),
        'borea_aliases_blocked': borea_codes,
        'borea_in_public_heroes': leak,
        'v28_schema_fix_report_pass': fix_pass,
        'inventory_schema_v28': {
            'marker_total': marker_total, 'marker_flat': marker_flat, 'marker_nested': marker_nested,
        },
        'guardrails_clean': {
            'backend/battle_engine.py': _git_clean('backend/battle_engine.py'),
            'backend/battle_core.py': _git_clean('backend/battle_core.py'),
            'frontend/app/combat.tsx': _git_clean('frontend/app/combat.tsx'),
        },
    }
    out['verdict'] = 'PASS' if all([
        services.get('backend') == 'RUNNING',
        services.get('redis') == 'RUNNING',
        cs.get('rate_limit_backend') == 'redis',
        cs.get('canary_ledger_cap') == 25000,
        cs.get('canary_allowlist_size') == 2500,
        len(heroes) == 100,
        not leak,
        all(c['code'] == 404 for c in borea_codes),
        fix_pass,
        marker_total == 1800,
        marker_flat == 1800,
        marker_nested == 0,
        all(out['guardrails_clean'].values()),
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} heroes={len(heroes)} cap={cs.get('canary_ledger_cap')} allowlist={cs.get('canary_allowlist_size')} marker_flat={marker_flat} nested={marker_nested}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(asyncio.run(_async_main()))
