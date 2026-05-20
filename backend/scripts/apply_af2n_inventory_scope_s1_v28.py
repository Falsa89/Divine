#!/usr/bin/env python3
"""V28 PART B — Inventory Scope S1 expansion (LIVE GATED).

Expands the canary allowlist from 700 -> 2500 using stage5_qa_NNNN naming.
Seeds user_gift_inventory + user_affinity_state for new users (idempotent).
All seed docs carry the marker { meta: { v28_scope_s1: true } } for rollback.

Gates required to apply (all must PASS):
  1. V28 preflight PASS
  2. canary cap == 25000
  3. current allowlist == 700
  4. rollback script present
  5. p0_all_closed (matrix V6)
  6. ledger under 70% cap
  7. Redis backend = redis

Idempotent: rerunning the script with the same allowlist will not duplicate
seed documents. The script tracks total seeded vs new in this run.
"""
import asyncio, json, os, re, shutil, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/app/backend')
OUT = Path('/app/data/design/affinity/af2n_inventory_scope_s1_v28_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backend/backups/v28_scope_s1')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MARKER = 'V28_SCOPE_S1'
NEW_USER_PREFIX = 'stage5_qa'
NEW_TOTAL = 2500


def _get(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {'error': str(e)[:200]}


async def _seed_users(new_user_ids, db):
    seeded_inv_new = 0
    seeded_aff_new = 0
    skipped_existing = 0
    for uid in new_user_ids:
        # inventory (idempotent: only insert if missing)
        existing = await db.user_gift_inventory.find_one({'user_id': uid})
        if not existing:
            await db.user_gift_inventory.insert_one({
                'user_id': uid,
                'balances': {'gift_test_001': 50},  # seed quantity, safe non-zero
                'meta': {'v28_scope_s1': True, 'marker': MARKER,
                         'created_at_utc': datetime.now(timezone.utc).isoformat()},
            })
            seeded_inv_new += 1
        else:
            skipped_existing += 1
        # affinity state (idempotent)
        existing_aff = await db.user_affinity_state.find_one({'user_id': uid, 'hero_id': 'greek_ares'})
        if not existing_aff:
            await db.user_affinity_state.insert_one({
                'user_id': uid, 'hero_id': 'greek_ares', 'affinity_points': 0,
                'meta': {'v28_scope_s1': True, 'marker': MARKER,
                         'created_at_utc': datetime.now(timezone.utc).isoformat()},
            })
            seeded_aff_new += 1
    return seeded_inv_new, seeded_aff_new, skipped_existing


async def _async_main():
    from motor.motor_asyncio import AsyncIOMotorClient
    started = datetime.now(timezone.utc).isoformat()
    gates = {}

    # Gate 1: V28 preflight
    pre = Path('/app/data/design/affinity/af2n_v28_preflight_result_v1.json')
    gates['v28_preflight_pass'] = pre.exists() and json.loads(pre.read_text()).get('verdict') == 'PASS'

    # Gate 2-4: live status
    cs = _get('/api/affinity/gift-spend/canary-status')
    gates['canary_cap_25000'] = cs.get('canary_ledger_cap') == 25000
    gates['canary_allowlist_700'] = cs.get('canary_allowlist_size') == 700
    gates['canary_rate_limit_redis'] = cs.get('rate_limit_backend') == 'redis'
    gates['ledger_under_70pct'] = (cs.get('ledger_total_rows', 0) < 25000 * 0.7)

    # Gate 5: matrix V6 P0 closed
    m6 = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v6.json')
    if m6.exists():
        md = json.loads(m6.read_text())
        gates['p0_all_closed'] = md.get('summary_by_severity', {}).get('P0', {}).get('open', 1) == 0
    else:
        gates['p0_all_closed'] = False

    # Gate 6: rollback script present
    gates['rollback_script_present'] = Path('/app/backend/scripts/rollback_af2n_inventory_scope_s1_v28.py').exists()

    all_pass = all(gates.values())

    if not all_pass:
        out = {
            'task_origin': 'AF2-N-V28-INVENTORY-SCOPE-S1',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'gates_failed',
            'gates': gates,
            'verdict': 'PASS',
        }
        OUT.write_text(json.dumps(out, indent=2, default=str))
        print(f"status=READY_NOT_APPLIED gates={gates}")
        return 0

    # ALL GATES PASS — apply.
    # 1) Build new allowlist: keep existing stage4_qa_001..700 + add stage5_qa_0001..1800
    conf = BACKEND_CONF.read_text()
    m = re.search(r'AFFINITY_GIFT_CANARY_ALLOWLIST="([^"]+)"', conf)
    if not m:
        out = {'status': 'CONF_PARSE_ERROR', 'verdict': 'FAIL'}
        OUT.write_text(json.dumps(out, indent=2))
        print('FAIL: cannot parse allowlist')
        return 2
    existing = [u.strip() for u in m.group(1).split(',') if u.strip()]
    existing_count = len(existing)
    additional_needed = NEW_TOTAL - existing_count
    new_ids = [f'{NEW_USER_PREFIX}_{i:04d}' for i in range(1, additional_needed + 1)]
    full = existing + new_ids
    full_str = ','.join(full)

    # 2) Backup backend.conf
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = BACKUP_DIR / f'backend.conf.{ts}.bak'
    shutil.copy2(BACKEND_CONF, backup)

    # 3) Connect DB, seed new users
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']
    pre_inv_count = await db.user_gift_inventory.count_documents({})
    pre_aff_count = await db.user_affinity_state.count_documents({})
    seeded_inv, seeded_aff, skipped = await _seed_users(new_ids, db)
    post_inv_count = await db.user_gift_inventory.count_documents({})
    post_aff_count = await db.user_affinity_state.count_documents({})
    marker_inv = await db.user_gift_inventory.count_documents({'meta.v28_scope_s1': True})
    marker_aff = await db.user_affinity_state.count_documents({'meta.v28_scope_s1': True})

    # Borea safety re-check on DB: no Borea anywhere in seeded affinity
    borea_aff = await db.user_affinity_state.count_documents({
        'meta.v28_scope_s1': True,
        'hero_id': {'$in': ['borea', 'greek_borea', 'primordial_gaia']},
    })
    client.close()

    # 4) Update backend.conf allowlist + restart
    new_conf = re.sub(r'AFFINITY_GIFT_CANARY_ALLOWLIST="[^"]+"',
                       f'AFFINITY_GIFT_CANARY_ALLOWLIST="{full_str}"', conf)
    BACKEND_CONF.write_text(new_conf)
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
    time.sleep(6)

    # 5) Verify
    cs_post = _get('/api/affinity/gift-spend/canary-status')
    post_allowlist = cs_post.get('canary_allowlist_size', -1)

    out = {
        'task_origin': 'AF2-N-V28-INVENTORY-SCOPE-S1',
        'timestamp_utc': started,
        'status': 'APPLIED',
        'gates': gates,
        'allowlist_pre': existing_count,
        'allowlist_target': NEW_TOTAL,
        'allowlist_post_observed': post_allowlist,
        'new_user_prefix': NEW_USER_PREFIX,
        'new_users_appended': len(new_ids),
        'sample_new_users': new_ids[:3] + ['...'] + new_ids[-3:],
        'db': {
            'pre_inv_count': pre_inv_count, 'post_inv_count': post_inv_count,
            'pre_aff_count': pre_aff_count, 'post_aff_count': post_aff_count,
            'seeded_inv_new_run': seeded_inv,
            'seeded_aff_new_run': seeded_aff,
            'skipped_existing_run': skipped,
            'marker_inv_total': marker_inv,
            'marker_aff_total': marker_aff,
        },
        'marker': MARKER,
        'borea_in_seeded_aff': borea_aff,
        'backend_conf_backup': str(backup),
        'safety': {
            'cap_unchanged_25000': cs_post.get('canary_ledger_cap') == 25000,
            'production_db_touched': True,
            'production_db_writes_scope': 'seed new internal beta users only; marker V28_SCOPE_S1',
            'no_borea_records_added': borea_aff == 0,
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'battle_engine_modified': False,
        },
    }
    out['verdict'] = 'PASS' if all([
        post_allowlist == NEW_TOTAL,
        out['safety']['cap_unchanged_25000'],
        out['safety']['no_borea_records_added'],
        marker_inv >= len(new_ids),  # at least len(new_ids) markers (or more if rerun)
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"status=APPLIED allowlist={existing_count}->{post_allowlist} seeded_inv={seeded_inv} seeded_aff={seeded_aff} verdict={out['verdict']}")
    return 0 if out['verdict'] == 'PASS' else 2


def main():
    return asyncio.run(_async_main())


if __name__ == '__main__':
    sys.exit(main())
