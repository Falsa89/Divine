#!/usr/bin/env python3
"""V22 — Stage4 Extended Monitoring (compressed window).

400 sample mix:
  - health + canary status polling
  - Borea/greek_borea/primordial_gaia 404 probes
  - non-allowlist 423 probes
  - rate-limit burst 429
  - Stage4 controlled fresh spend (cap <=10)
  - idempotent replay
  - inventory/affinity delta consistency check after each fresh spend
  - ledger consistency
Non-destructive, low-impact. 0 critical 5xx required.
"""
from __future__ import annotations
import json, os, random, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_stage4_extended_monitoring_v22_result.json')
MAX_FRESH = 10


def _post(b):
    payload = json.dumps(b).encode()
    req = Request(API + '/affinity/gift-spend', data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=4) as r:
            return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = None
        return e.code, body
    except URLError: return -1, None


def _get(p):
    try:
        with urlopen(API + p, timeout=4) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def main():
    NOW = datetime.now(timezone.utc)
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']

    samples = []
    counts = {}
    fresh = 0
    inv_aff_checks = []

    # baseline
    code, st0 = _get('/affinity/gift-spend/canary-status')
    if not st0 or st0.get('canary_allowlist_size', 0) < 700:
        out = {'overall_status': 'BLOCKED_NO_STAGE4',
               'reason': 'Stage4 not active',
               'generated_at_utc': NOW.isoformat().replace('+00:00','Z')}
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2))
        print('STAGE4-EXTENDED-MONITOR BLOCKED_NO_STAGE4'); return 0

    def record(code):
        counts[str(code)] = counts.get(str(code), 0) + 1

    # Phase 1: 80 health/status polls
    for i in range(80):
        c, _ = _get('/health'); record(c); samples.append({'kind':'health','code':c})
        if i % 20 == 0:
            c2, _ = _get('/affinity/gift-spend/canary-status'); record(c2); samples.append({'kind':'canary_status','code':c2})

    # Phase 2: 30 Borea 404 probes
    for i in range(30):
        alias = ['borea','greek_borea','primordial_gaia'][i % 3]
        c, _ = _post({'gift_id':'x','hero_id':alias,'quantity':1,
                      'idempotency_key':f'v22ext_borea_{alias}_{i}','user_id':'stage4_qa_001'})
        record(c); samples.append({'kind':f'borea:{alias}','code':c})

    # Phase 3: 80 non-allowlist (different users)
    for i in range(80):
        uid = f'unauth_v22_{i}_{int(time.time())}'
        c, _ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                      'idempotency_key':f'v22ext_unauth_{i}','user_id':uid})
        record(c); samples.append({'kind':'non_allowlist','code':c})

    # Phase 4: rate-limit burst (12 same user)
    burst_user = f'v22ext_burst_{int(time.time())}'
    for i in range(12):
        c, _ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                      'idempotency_key':f'v22ext_burst_{i}','user_id':burst_user})
        record(c); samples.append({'kind':'rate_limit_burst','code':c})

    # Phase 5: Stage4 controlled fresh + idempotent replay + inventory/affinity delta check
    for i in range(MAX_FRESH):
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        gift_id = 'gift_test_001'
        hero_id = 'greek_ares'
        # pre-state
        inv_before = (db['user_gift_inventory'].find_one({'user_id':uid,'gift_id':gift_id}) or {}).get('quantity', 0)
        aff_before = (db['user_affinity_state'].find_one({'user_id':uid,'hero_id':hero_id}) or {}).get('affinity_points', 0)
        key = f'v22ext_fresh_{int(time.time())}_{i}'
        c1, b1 = _post({'gift_id':gift_id,'hero_id':hero_id,'quantity':1,'idempotency_key':key,'user_id':uid})
        record(c1); samples.append({'kind':'stage4_fresh','code':c1,'user_id':uid})
        if c1 == 200: fresh += 1
        c2, b2 = _post({'gift_id':gift_id,'hero_id':hero_id,'quantity':1,'idempotency_key':key,'user_id':uid})
        record(c2); samples.append({'kind':'idem_replay','code':c2,'user_id':uid})
        inv_after = (db['user_gift_inventory'].find_one({'user_id':uid,'gift_id':gift_id}) or {}).get('quantity', 0)
        aff_after = (db['user_affinity_state'].find_one({'user_id':uid,'hero_id':hero_id}) or {}).get('affinity_points', 0)
        inv_aff_checks.append({
            'user_id': uid, 'inv_before': inv_before, 'inv_after': inv_after,
            'aff_before': aff_before, 'aff_after': aff_after,
            'fresh_code': c1, 'replay_code': c2,
            'inv_delta': inv_before - inv_after,
            'aff_delta': aff_after - aff_before,
            'inv_delta_eq_aff_delta': (inv_before - inv_after) == (aff_after - aff_before) if c1 == 200 else True,
        })

    # Phase 6: idempotent replay-only sweeps (replay known keys)
    for i in range(30):
        uid = f'stage4_qa_{random.randint(1, 500):03d}'
        key = f'v22ext_idemsweep_{i}'
        # first POST
        c1, _ = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,'idempotency_key':key,'user_id':uid})
        # replay
        c2, _ = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,'idempotency_key':key,'user_id':uid})
        record(c1); record(c2)
        samples.append({'kind':'idem_sweep_first','code':c1})
        samples.append({'kind':'idem_sweep_replay','code':c2})

    # Phase 7: random non-allow (different IPs effectively same)
    for i in range(80):
        uid = f'unauth_v22_diff_{i}'
        c, _ = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                      'idempotency_key':f'v22ext_nonallow2_{i}','user_id':uid})
        record(c); samples.append({'kind':'non_allow_diff','code':c})

    # post invariants
    code, st1 = _get('/affinity/gift-spend/canary-status')
    inv_neg = db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}})
    borea_rows = db['gift_transaction_ledger'].count_documents({'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}})
    duplicate_idem = list(db['gift_transaction_ledger'].aggregate([
        {'$group': {'_id': {'user_id':'$user_id','key':'$idempotency_key'}, 'cnt':{'$sum':1}}},
        {'$match': {'cnt': {'$gt': 1}}},
        {'$limit': 5},
    ]))

    fails = []
    for bad in ('500','502','503','504'):
        if counts.get(bad, 0) > 0: fails.append(f'5xx_observed:{bad}')
    # Borea probes all must be 404
    for s in samples:
        if s['kind'].startswith('borea:') and s['code'] != 404:
            fails.append(f'borea_not_404:{s["kind"]}:{s["code"]}'); break
    # at least some 429
    if not any(s['kind']=='rate_limit_burst' and s['code']==429 for s in samples):
        fails.append('rate_limit_did_not_trigger')
    # no unauthorized success in non_allowlist phases
    for s in samples:
        if s['kind'] in ('non_allowlist','non_allow_diff') and s['code'] == 200:
            fails.append('non_allowlist_got_200')
            break
    # ledger within cap
    if st1 and st1.get('ledger_total_rows', 0) > st1.get('canary_ledger_cap', 0):
        fails.append('ledger_over_cap')
    if inv_neg > 0: fails.append(f'negative_inventory:{inv_neg}')
    if borea_rows > 0: fails.append(f'borea_rows:{borea_rows}')
    if duplicate_idem: fails.append('duplicate_idempotency_keys')
    # inv/aff delta equality for fresh successes
    for ch in inv_aff_checks:
        if ch['fresh_code'] == 200 and not ch['inv_delta_eq_aff_delta']:
            fails.append(f'inv_aff_delta_mismatch:{ch["user_id"]}'); break

    overall = (len(fails) == 0)
    out_doc = {
        'result_id': 'af2n_stage4_extended_monitoring_v22_result',
        'task_origin': 'V22-AF2N-STAGE4-EXTENDED-MONITORING',
        'started_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'sample_total': len(samples),
        'status_counts': counts,
        'fresh_spends_succeeded': fresh,
        'inv_aff_delta_checks_sample': inv_aff_checks,
        'inv_neg_count': inv_neg,
        'borea_rows_in_ledger': borea_rows,
        'duplicate_idempotency_groups': len(duplicate_idem),
        'post_canary_status': st1,
        'observations_first_30': samples[:30],
        'fails': fails,
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'no broad rollout', 'no public spend UI', 'no battle wiring',
            'no Borea reveal', 'no gacha/roster/catalog mutation'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2, default=str))
    print(f'V22-STAGE4-EXTENDED-MONITOR {out_doc["overall_status"]} samples={len(samples)} fresh={fresh}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
