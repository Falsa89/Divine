#!/usr/bin/env python3
"""V28 PART A — Preflight."""
import asyncio, json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/app/backend')
OUT = Path('/app/data/design/affinity/af2n_v28_preflight_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        return -1, str(e)


def _post404(hero):
    body = json.dumps({'gift_id': 'x', 'hero_id': hero, 'quantity': 1,
                       'idempotency_key': f'v28_pre_{hero}', 'user_id': 'stage4_qa_001'}).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def _git_clean(f):
    out = subprocess.run(['git', '-C', '/app', 'diff', '--stat', '--', f],
                          capture_output=True, text=True, timeout=5)
    return out.stdout.strip() == ''


async def _db_health():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
        db = client[os.environ.get('DB_NAME') or 'divine_waifus']
        out = {
            'user_gift_inventory_count': await db.user_gift_inventory.count_documents({}),
            'user_affinity_state_count': await db.user_affinity_state.count_documents({}),
            'gift_transaction_ledger_count': await db.gift_transaction_ledger.count_documents({}),
        }
        client.close()
        return out
    except Exception as e:
        return {'error': str(e)[:200]}


def main():
    h_code, h = _get('/api/health')
    he_code, heroes = _get('/api/heroes')
    cs_code, cs = _get('/api/affinity/gift-spend/canary-status')
    bo = _post404('borea'); gb = _post404('greek_borea'); pg = _post404('primordial_gaia')
    guard = {
        'backend/battle_engine.py': _git_clean('backend/battle_engine.py'),
        'backend/battle_core.py': _git_clean('backend/battle_core.py'),
        'frontend/app/combat.tsx': _git_clean('frontend/app/combat.tsx'),
    }
    leak = []
    if isinstance(heroes, list):
        ids = {(x.get('id') or '').lower() for x in heroes}
        leak = sorted(ids & {'borea', 'greek_borea', 'primordial_gaia'})

    db_h = asyncio.run(_db_health())

    out = {
        'task_origin': 'AF2-N-V28-PREFLIGHT',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'checks': {
            'health_status': h.get('status') if isinstance(h, dict) else None,
            'heroes_count': len(heroes) if isinstance(heroes, list) else -1,
            'borea_leak_in_list': leak,
            'gift_spend_borea_404': bo == 404 and gb == 404 and pg == 404,
            'canary_rate_limit_backend': cs.get('rate_limit_backend') if isinstance(cs, dict) else None,
            'canary_ledger_cap': cs.get('canary_ledger_cap') if isinstance(cs, dict) else None,
            'canary_ledger_total_rows': cs.get('ledger_total_rows') if isinstance(cs, dict) else None,
            'canary_allowlist_size': cs.get('canary_allowlist_size') if isinstance(cs, dict) else None,
            'guardrail_diffs_clean': guard,
            'battle_runtime_attached': cs.get('battle_runtime_attached') if isinstance(cs, dict) else None,
            'db_collections_healthy': 'error' not in db_h,
            'db_counts': db_h,
            'redis_managed_url_set': bool(os.environ.get('REDIS_MANAGED_URL', '').strip()),
            'alert_webhook_url_set': bool(os.environ.get('ALERT_WEBHOOK_URL', '').strip()),
            'rollback_scripts_present': all([
                Path('/app/backend/scripts/rollback_managed_redis_switch_v27.py').exists(),
                Path('/app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py').exists(),
            ]),
        },
    }
    out['verdict'] = 'PASS' if all([
        out['checks']['health_status'] == 'ok',
        out['checks']['heroes_count'] == 100,
        not out['checks']['borea_leak_in_list'],
        out['checks']['gift_spend_borea_404'],
        out['checks']['canary_rate_limit_backend'] == 'redis',
        out['checks']['canary_ledger_cap'] == 25000,
        out['checks']['canary_allowlist_size'] == 700,  # must be 700 before V28
        out['checks']['battle_runtime_attached'] is False,
        all(guard.values()),
        out['checks']['db_collections_healthy'],
        out['checks']['rollback_scripts_present'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} cap={out['checks']['canary_ledger_cap']} allowlist={out['checks']['canary_allowlist_size']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
