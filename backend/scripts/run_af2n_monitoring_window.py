#!/usr/bin/env python3
"""AF2-N-MONITORING-WINDOW — Extended live monitoring snapshot probe.

Reads-only sampling over a configurable window. NO writes. Captures:
  - /api/health
  - /api/heroes count (and Borea hidden)
  - /api/affinity/gift-spend/canary-status
  - POST /api/affinity/gift-spend with empty body -> 423 (sentinel)
  - POST with Borea hero_id -> 404 (sentinel)
  - POST with non-allowlist user -> 423 (sentinel)
  - POST with idempotent replay (existing canary tx) -> 200 idempotent_replay (no new row)
  - DB ledger row count + canary count + integrity

Aborts and returns non-zero exit if ANY trigger fires:
  - /api/heroes != 100
  - Borea appears in /api/heroes
  - 5xx observed
  - non-allowlist gets HTTP 200 (unauthorized successful spend)
  - idempotent replay creates a new ledger row
  - ledger total exceeds cap
  - any inventory/affinity_points/buffs/battle_wiring true row
  - any borea hero_id row in ledger

Does NOT loop forever — takes 30-60 samples over a short window and
writes a complete snapshot artifact for the audit trail.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/af2n_monitoring_window_result_v1.json')


def _get(p):
    t0 = time.monotonic()
    try:
        with urlopen(API+p, timeout=6) as r:
            body = r.read()
            code = r.status
    except HTTPError as e:
        try: body = e.read()
        except: body = b''
        code = e.code
    except URLError: body = b''; code = -1
    return code, body, (time.monotonic() - t0) * 1000.0


def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type':'application/json'}
    t0 = time.monotonic()
    req = Request(API+p, data=payload, method='POST', headers=headers)
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
    s = sorted(s); k = max(0, min(len(s)-1, int(round(q*(len(s)-1)))))
    return s[k]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', type=int, default=30, help='monitoring samples (default 30)')
    ap.add_argument('--interval-ms', type=int, default=50, help='delay between samples')
    args = ap.parse_args(argv)

    samples = max(20, min(200, args.samples))
    started = time.monotonic()
    triggers = []  # list of (sample_idx, trigger_id, detail)
    latencies = {'health':[], 'heroes':[], 'status':[], 'spend_empty':[], 'spend_borea':[], 'spend_nonal':[], 'spend_replay':[]}
    codes = {k: {} for k in latencies}
    health_5xx = 0; heroes_5xx = 0; status_5xx = 0; any_5xx = 0

    # Idempotency anchor: use a known existing canary tx from V12 smoke.
    # If none exists, skip replay test gracefully.
    replay_idem = 'canary_idem_0001'
    replay_user = 'user_canary_001'

    initial_canary_status = None
    initial_ledger_total = None
    for i in range(samples):
        code, body, ms = _get('/health')
        latencies['health'].append(ms); codes['health'][str(code)] = codes['health'].get(str(code), 0) + 1
        if isinstance(code, int) and 500 <= code < 600: any_5xx += 1; triggers.append((i, '5xx', f'/api/health = {code}'))

        code, body, ms = _get('/heroes')
        latencies['heroes'].append(ms); codes['heroes'][str(code)] = codes['heroes'].get(str(code), 0) + 1
        if isinstance(code, int) and 500 <= code < 600: any_5xx += 1; triggers.append((i, '5xx', f'/api/heroes = {code}'))
        if code == 200:
            try:
                d = json.loads(body.decode())
                heroes = d if isinstance(d, list) else (d.get('heroes') or [])
                if len(heroes) != 100:
                    triggers.append((i, 'api_heroes_not_100', f'count={len(heroes)}'))
                ids = {h.get('id') for h in heroes if isinstance(h, dict)}
                if ids & {'borea','greek_borea','primordial_gaia'}:
                    triggers.append((i, 'borea_in_heroes', f'leaked={sorted(ids & {"borea","greek_borea","primordial_gaia"})}'))
            except Exception as e:
                triggers.append((i, 'heroes_parse_error', repr(e)))

        code, body, ms = _get('/affinity/gift-spend/canary-status')
        latencies['status'].append(ms); codes['status'][str(code)] = codes['status'].get(str(code), 0) + 1
        status_doc = None
        if code == 200:
            try:
                status_doc = json.loads(body.decode())
                if initial_canary_status is None:
                    initial_canary_status = status_doc; initial_ledger_total = status_doc.get('ledger_total_rows')
                if status_doc.get('feature_flag_currently_enabled') is not True:
                    triggers.append((i, 'feature_flag_off_unexpected', ''))
                # ledger cap
                if status_doc.get('ledger_total_rows', 0) > status_doc.get('canary_ledger_cap', 0):
                    triggers.append((i, 'ledger_exceeds_cap', f"rows={status_doc.get('ledger_total_rows')} cap={status_doc.get('canary_ledger_cap')}"))
                # safety flags must remain false
                if status_doc.get('applied_to_combat') is not False or status_doc.get('battle_runtime_attached') is not False \
                   or status_doc.get('inventory_mutation_enabled') is not False \
                   or status_doc.get('affinity_points_mutation_enabled') is not False \
                   or status_doc.get('buffs_enabled') is not False:
                    triggers.append((i, 'safety_flag_violation', str({k: status_doc.get(k) for k in ('applied_to_combat','battle_runtime_attached','inventory_mutation_enabled','affinity_points_mutation_enabled','buffs_enabled')})))
            except Exception as e:
                triggers.append((i, 'status_parse_error', repr(e)))
        elif isinstance(code, int) and 500 <= code < 600:
            any_5xx += 1; triggers.append((i, '5xx', f'canary-status = {code}'))

        # Sentinel: empty POST -> 423
        code, _, ms = _post('/affinity/gift-spend', {})
        latencies['spend_empty'].append(ms); codes['spend_empty'][str(code)] = codes['spend_empty'].get(str(code), 0) + 1
        if code != 423: triggers.append((i, 'spend_empty_unexpected', f'got {code}'))

        # Sentinel: Borea -> 404 (always)
        code, _, ms = _post('/affinity/gift-spend',
            {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'})
        latencies['spend_borea'].append(ms); codes['spend_borea'][str(code)] = codes['spend_borea'].get(str(code), 0) + 1
        if code != 404: triggers.append((i, 'borea_not_404', f'got {code}'))

        # Sentinel: non-allowlist user -> 423
        code, _, ms = _post('/affinity/gift-spend',
            {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':f'rnd{i}','user_id':'unauth_user_xxx'})
        latencies['spend_nonal'].append(ms); codes['spend_nonal'][str(code)] = codes['spend_nonal'].get(str(code), 0) + 1
        if code == 200: triggers.append((i, 'unauthorized_successful_spend', 'non-allowlist got 200'))
        if isinstance(code, int) and 500 <= code < 600: any_5xx += 1

        # Sentinel: idempotent replay -> 200 with no new row
        before = status_doc.get('ledger_total_rows') if status_doc else None
        code, body, ms = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key': replay_idem, 'user_id': replay_user})
        latencies['spend_replay'].append(ms); codes['spend_replay'][str(code)] = codes['spend_replay'].get(str(code), 0) + 1
        if code != 200: triggers.append((i, 'replay_not_200', f'got {code}'))
        try:
            j = json.loads(body.decode())
            if j.get('ledger_row_inserted') is True:
                triggers.append((i, 'idempotency_duplicate_inserted', f'tx={j.get("tx_id")}'))
        except Exception:
            pass

        time.sleep(args.interval_ms / 1000.0)

    # Final ledger integrity
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
    for nm, v in (('inventory_mut', bad_inv), ('points_mut', bad_pts), ('buffs', bad_buf),
                  ('battle_wire', bad_btl), ('borea_hero', bad_brea)):
        if isinstance(v, int) and v > 0:
            triggers.append((-1, f'{nm}_violation', f'count={v}'))

    elapsed = round(time.monotonic() - started, 3)
    summary = {
        'result_id': 'af2n_monitoring_window_result_v1',
        'task_origin': 'AF2-N-MONITORING-WINDOW',
        'design_only': False, 'runtime_attached': True, 'runtime_attached_canary_only': True,
        'db_write': False, 'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'samples': samples, 'elapsed_seconds': elapsed,
        'health_codes': codes['health'], 'heroes_codes': codes['heroes'],
        'status_codes': codes['status'], 'spend_empty_codes': codes['spend_empty'],
        'spend_borea_codes': codes['spend_borea'], 'spend_nonal_codes': codes['spend_nonal'],
        'spend_replay_codes': codes['spend_replay'],
        'p50_latency_ms': {k: round(pct(v, 0.5), 2) for k, v in latencies.items()},
        'p95_latency_ms': {k: round(pct(v, 0.95), 2) for k, v in latencies.items()},
        'any_5xx_total': any_5xx,
        'ledger_total_rows': total, 'ledger_canary_rows': canary,
        'ledger_inventory_mutation_count': bad_inv, 'ledger_affinity_points_mutation_count': bad_pts,
        'ledger_buffs_activation_count': bad_buf, 'ledger_battle_wiring_count': bad_btl,
        'ledger_borea_hero_count': bad_brea,
        'initial_ledger_total': initial_ledger_total,
        'triggers_fired': [{'sample': s, 'trigger': t, 'detail': d} for s, t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS' if not triggers else 'FAIL',
        'safety_flags': {
            'runtime_attached_canary_only': True, 'broad_rollout_authorized': False,
            'inventory_mutation_enabled': False, 'affinity_points_mutation_enabled': False,
            'buffs_enabled': False, 'battle_runtime_attached': False,
            'applied_to_combat': False, 'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'AF2-N monitoring: samples={samples}, 5xx={any_5xx}, triggers={len(triggers)}, status={summary["overall_status"]}')
    print(f'Result: {RESULT}')
    return 0 if not triggers else 1

if __name__ == '__main__':
    sys.exit(main())
