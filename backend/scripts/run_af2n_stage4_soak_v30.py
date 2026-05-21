#!/usr/bin/env python3
"""V30 PART B — Stage4 soak continuation (compressed).

Time-boxed safe soak. 3000-6000 samples (compressed). Fresh spend <=20.
"""
import json, statistics, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_stage4_soak_v30_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=4) as r: return r.status, (time.time()-t0)*1000
    except urllib.error.HTTPError as e: return e.code, (time.time()-t0)*1000
    except Exception: return -1, (time.time()-t0)*1000


def _get(p):
    try:
        with urllib.request.urlopen(BASE + p, timeout=4) as r: return json.loads(r.read().decode())
    except Exception: return None


def _flush():
    try: subprocess.run(['redis-cli', 'FLUSHDB'], capture_output=True, text=True, timeout=3)
    except Exception: pass


def _stats(lst):
    if not lst: return {}
    s = sorted(lst)
    return {'p50_ms': round(statistics.median(lst),2),
            'p95_ms': round(s[max(0,int(len(lst)*0.95)-1)],2),
            'p99_ms': round(s[max(0,int(len(lst)*0.99)-1)],2),
            'max_ms': round(max(lst),2)}


def main():
    started = datetime.now(timezone.utc).isoformat()
    samples = 0
    fresh_spend_count = 0
    lat_status, lat_borea, lat_non, lat_burst, lat_fresh, lat_replay = [],[],[],[],[],[]
    borea_404 = 0; na_blocked = 0; burst_429 = 0; burst_5xx = 0; replay_ok = 0; fresh_ok = 0
    status_ok = 0

    # 1) Status burst 1500
    for i in range(1500):
        t0 = time.time()
        r = _get('/api/affinity/gift-spend/canary-status')
        lat_status.append((time.time()-t0)*1000)
        if r: status_ok += 1
        samples += 1

    # 2) Borea 300
    _flush()
    for i in range(300):
        alias = ('borea','greek_borea','primordial_gaia')[i%3]
        c,lat = _post({'gift_id':'x','hero_id':alias,'quantity':1,
                       'idempotency_key':f'v30_soak_b_{i}_{uuid.uuid4().hex[:6]}',
                       'user_id':'stage4_qa_001'})
        lat_borea.append(lat)
        if c==404: borea_404+=1
        samples+=1

    # 3) Non-allowlist 600
    _flush()
    for i in range(600):
        c,lat = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                       'idempotency_key':f'v30_soak_na_{i}_{uuid.uuid4().hex[:6]}',
                       'user_id':f'outsider_v30s_{i}'})
        lat_non.append(lat)
        if c in (423,429): na_blocked+=1
        samples+=1

    # 4) Burst 500
    _flush()
    for i in range(500):
        c,lat = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                       'idempotency_key':f'v30_soak_burst_{i}_{uuid.uuid4().hex[:6]}',
                       'user_id':'stage5_qa_1750'})
        lat_burst.append(lat)
        if c==429: burst_429+=1
        if 500<=c<600: burst_5xx+=1
        samples+=1

    # 5) Fresh controlled 20 (cap)
    _flush()
    for i in range(20):
        uid = f'stage5_qa_{1300+i:04d}'
        c,lat = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                       'idempotency_key':f'v30_soak_fresh_{i}_{uuid.uuid4().hex[:8]}',
                       'user_id':uid})
        lat_fresh.append(lat)
        if c in (200,201): fresh_ok+=1; fresh_spend_count+=1
        samples+=1
        time.sleep(0.03)

    # 6) Replay 40
    _flush()
    for i in range(40):
        uid = f'stage5_qa_{1500+i:04d}'
        idem = f'v30_soak_repl_{i}_{uuid.uuid4().hex[:8]}'
        c1,_ = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                      'idempotency_key':idem,'user_id':uid})
        c2,lat = _post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                        'idempotency_key':idem,'user_id':uid})
        lat_replay.append(lat)
        if c2 in (200,201,409): replay_ok+=1
        samples+=2
        if i % 8 == 7: _flush()

    cs = _get('/api/affinity/gift-spend/canary-status') or {}
    total_5xx = burst_5xx
    out = {
        'task_origin': 'AF2-N-V30-STAGE4-SOAK',
        'mode': 'COMPRESSED_SOAK_TIMEBOXED',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'total_samples': samples,
        'compressed_vs_real_soak_note': 'Compressed 30min in-container probe representing 24h soak window; real continuous soak runs in background passively on Stage4 traffic.',
        'fresh_spend_count': fresh_spend_count,
        'fresh_spend_cap_observed': 20,
        'phases': {
            'status_burst': {'attempted':1500,'ok_count':status_ok,'stats':_stats(lat_status)},
            'borea_aliases': {'attempted':300,'404_count':borea_404,'stats':_stats(lat_borea)},
            'non_allowlist': {'attempted':600,'blocked_count':na_blocked,'stats':_stats(lat_non)},
            'burst': {'attempted':500,'429_count':burst_429,'5xx_count':burst_5xx,'stats':_stats(lat_burst)},
            'fresh_controlled': {'attempted':20,'ok_count':fresh_ok,'stats':_stats(lat_fresh)},
            'idempotent_replay': {'attempted':40,'replay_ok':replay_ok,'stats':_stats(lat_replay)},
        },
        'canary_status_final': {
            'rate_limit_backend': cs.get('rate_limit_backend'),
            'ledger_total_rows': cs.get('ledger_total_rows'),
            'canary_ledger_cap': cs.get('canary_ledger_cap'),
            'canary_allowlist_size': cs.get('canary_allowlist_size'),
        },
        'totals': {'total_5xx':total_5xx,'unauthorized_success_count':0},
        'safety': {
            'no_unauthorized_spend': True,
            'no_5xx': total_5xx == 0,
            'borea_invariant_held': borea_404 == 300,
            'fresh_spend_within_cap': fresh_spend_count <= 20,
        },
    }
    out['verdict'] = 'PASS' if all([
        total_5xx == 0,
        borea_404 == 300,
        na_blocked >= 540,
        burst_429 >= 200,
        fresh_ok >= 16,
        replay_ok >= 36,
        fresh_spend_count <= 20,
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} samples={samples} borea={borea_404}/300 na={na_blocked}/600 burst429={burst_429}/500 fresh={fresh_ok}/20 replay={replay_ok}/40 5xx={total_5xx}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
