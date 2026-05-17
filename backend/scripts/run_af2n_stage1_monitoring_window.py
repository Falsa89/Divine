#!/usr/bin/env python3
"""AF2-N-STAGE1-MONITORING-WINDOW — Extended live monitoring under Stage1 expanded allowlist.

Read-mostly. NEVER inserts ledger rows for new allowlist members
(probes only use unauth user_ids for the spend probes, plus an idempotent
replay against the existing canary tx).

Samples 60 cycles (override via --samples) at 100ms interval.
Aborts and returns non-zero if any invariant trigger fires.
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/af2n_stage1_monitoring_window_result_v1.json')


def _get(p):
    t0 = time.monotonic()
    try:
        with urlopen(API + p, timeout=6) as r: body = r.read(); code = r.status
    except HTTPError as e:
        try: body = e.read()
        except: body = b''
        code = e.code
    except URLError: body = b''; code = -1
    return code, body, (time.monotonic() - t0) * 1000.0


def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    t0 = time.monotonic()
    try:
        with urlopen(req, timeout=6) as r: body = r.read(); code = r.status
    except HTTPError as e:
        try: body = e.read()
        except: body = b''
        code = e.code
    except URLError: body = b''; code = -1
    return code, body, (time.monotonic() - t0) * 1000.0


def pct(s, q):
    if not s: return 0.0
    s = sorted(s); k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', type=int, default=60)
    ap.add_argument('--interval-ms', type=int, default=100)
    args = ap.parse_args(argv)
    samples = max(30, min(200, args.samples))

    triggers = []
    latencies = {'health':[], 'heroes':[], 'status':[], 'spend_empty':[], 'spend_borea':[], 'spend_nonal':[], 'spend_replay':[]}
    codes = {k: {} for k in latencies}
    any_5xx = 0
    initial_allowlist_size = None; initial_ledger_total = None
    started = time.monotonic()

    for i in range(samples):
        for label, getter in [('health', '/health'), ('heroes', '/heroes'),
                              ('status', '/affinity/gift-spend/canary-status')]:
            code, body, ms = _get(getter)
            latencies[label].append(ms); codes[label][str(code)] = codes[label].get(str(code), 0) + 1
            if isinstance(code, int) and 500 <= code < 600:
                any_5xx += 1; triggers.append((i, '5xx', f'{getter}={code}'))
            if label == 'heroes' and code == 200:
                try:
                    d = json.loads(body.decode())
                    arr = d if isinstance(d, list) else (d.get('heroes') or [])
                    if len(arr) != 100:
                        triggers.append((i, 'api_heroes_not_100', f'count={len(arr)}'))
                    ids = {h.get('id') for h in arr if isinstance(h, dict)}
                    leak = ids & {'borea','greek_borea','primordial_gaia'}
                    if leak: triggers.append((i, 'borea_in_heroes', f'leaked={sorted(leak)}'))
                except Exception as e:
                    triggers.append((i, 'heroes_parse_error', repr(e)))
            if label == 'status' and code == 200:
                try:
                    sd = json.loads(body.decode())
                    if initial_allowlist_size is None:
                        initial_allowlist_size = sd.get('canary_allowlist_size')
                        initial_ledger_total = sd.get('ledger_total_rows')
                    if sd.get('feature_flag_currently_enabled') is not True:
                        triggers.append((i, 'feature_flag_off_unexpected', ''))
                    if sd.get('ledger_total_rows', 0) > sd.get('canary_ledger_cap', 0):
                        triggers.append((i, 'ledger_exceeds_cap', f"rows={sd.get('ledger_total_rows')} cap={sd.get('canary_ledger_cap')}"))
                    for k in ('applied_to_combat','battle_runtime_attached','inventory_mutation_enabled','affinity_points_mutation_enabled','buffs_enabled'):
                        if sd.get(k) is not False:
                            triggers.append((i, 'safety_flag_violation', f'{k}={sd.get(k)}'))
                except Exception as e:
                    triggers.append((i, 'status_parse_error', repr(e)))

        code, _, ms = _post('/affinity/gift-spend', {})
        latencies['spend_empty'].append(ms); codes['spend_empty'][str(code)] = codes['spend_empty'].get(str(code), 0) + 1
        if code != 423: triggers.append((i, 'spend_empty_unexpected', f'got {code}'))

        code, _, ms = _post('/affinity/gift-spend',
            {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'})
        latencies['spend_borea'].append(ms); codes['spend_borea'][str(code)] = codes['spend_borea'].get(str(code), 0) + 1
        if code != 404: triggers.append((i, 'borea_not_404', f'got {code}'))

        code, _, ms = _post('/affinity/gift-spend',
            {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':f'stg1rnd{i}','user_id':'unauth_user_xxx'})
        latencies['spend_nonal'].append(ms); codes['spend_nonal'][str(code)] = codes['spend_nonal'].get(str(code), 0) + 1
        if code == 200: triggers.append((i, 'unauthorized_successful_spend', 'non-allowlist got 200'))

        code, body, ms = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key':'canary_idem_0001','user_id':'user_canary_001'})
        latencies['spend_replay'].append(ms); codes['spend_replay'][str(code)] = codes['spend_replay'].get(str(code), 0) + 1
        if code != 200: triggers.append((i, 'replay_not_200', f'got {code}'))
        try:
            j = json.loads(body.decode())
            if j.get('ledger_row_inserted') is True:
                triggers.append((i, 'idempotency_duplicate_inserted', f'tx={j.get("tx_id")}'))
        except Exception: pass
        time.sleep(args.interval_ms / 1000.0)

    try:
        from pymongo import MongoClient
        coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger']
        total = coll.count_documents({})
        canary = coll.count_documents({'canary': True})
        bad_inv = coll.count_documents({'inventory_mutated': True})
        bad_pts = coll.count_documents({'affinity_points_mutated': True})
        bad_buf = coll.count_documents({'buffs_activated': True})
        bad_btl = coll.count_documents({'battle_wiring_attached': True})
        bad_brea = coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}})
    except Exception as e:
        total = canary = bad_inv = bad_pts = bad_buf = bad_btl = bad_brea = -1
        triggers.append((-1, 'mongo_unreachable', repr(e)))

    if total >= 0 and canary != total:
        triggers.append((-1, 'non_canary_rows_present', f'total={total} canary={canary}'))
    for nm, v in (('inventory_mut',bad_inv),('points_mut',bad_pts),('buffs',bad_buf),('battle_wire',bad_btl),('borea_hero',bad_brea)):
        if isinstance(v, int) and v > 0:
            triggers.append((-1, f'{nm}_violation', f'count={v}'))

    elapsed = round(time.monotonic() - started, 3)
    summary = {
        'result_id': 'af2n_stage1_monitoring_window_result_v1',
        'task_origin': 'AF2-N-STAGE1-MONITORING-WINDOW',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'samples': samples, 'elapsed_seconds': elapsed,
        'codes': codes,
        'p50_latency_ms': {k: round(pct(v, 0.5), 2) for k, v in latencies.items()},
        'p95_latency_ms': {k: round(pct(v, 0.95), 2) for k, v in latencies.items()},
        'any_5xx_total': any_5xx,
        'initial_allowlist_size': initial_allowlist_size,
        'observed_allowlist_size_must_be_50': initial_allowlist_size == 50,
        'initial_ledger_total': initial_ledger_total,
        'ledger_total_rows': total, 'ledger_canary_rows': canary,
        'ledger_inventory_mutation_count': bad_inv,
        'ledger_affinity_points_mutation_count': bad_pts,
        'ledger_buffs_activation_count': bad_buf,
        'ledger_battle_wiring_count': bad_btl,
        'ledger_borea_hero_count': bad_brea,
        'triggers_fired': [{'sample': s, 'trigger': t, 'detail': d} for s, t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS' if not triggers else 'FAIL',
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'AF2-N stage1 monitoring: samples={samples}, 5xx={any_5xx}, triggers={len(triggers)}, status={summary["overall_status"]}')
    print(f'Result: {RESULT}')
    return 0 if not triggers else 1

if __name__ == '__main__':
    sys.exit(main())
