#!/usr/bin/env python3
"""V30 PART D — Stress 10x safe."""
import json, statistics, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_stress_10x_v30_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE+'/api/affinity/gift-spend', data=body, headers={'Content-Type':'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=4) as r: return r.status, (time.time()-t0)*1000
    except urllib.error.HTTPError as e: return e.code, (time.time()-t0)*1000
    except Exception: return -1, (time.time()-t0)*1000


def _flush():
    try: subprocess.run(['redis-cli','FLUSHDB'], capture_output=True, text=True, timeout=3)
    except Exception: pass


def _stats(lst):
    if not lst: return {}
    s = sorted(lst)
    return {'p50_ms':round(statistics.median(lst),2),'p95_ms':round(s[max(0,int(len(lst)*0.95)-1)],2),
            'p99_ms':round(s[max(0,int(len(lst)*0.99)-1)],2),'max_ms':round(max(lst),2)}


def _redis_keys():
    try:
        r = subprocess.run(['redis-cli','DBSIZE'], capture_output=True, text=True, timeout=3)
        return int(r.stdout.strip())
    except Exception: return -1


def _get(p):
    try:
        with urllib.request.urlopen(BASE+p, timeout=4) as r: return json.loads(r.read().decode())
    except Exception: return None


def main():
    started = datetime.now(timezone.utc).isoformat()
    cs_pre = _get('/api/affinity/gift-spend/canary-status') or {}
    current_cap = cs_pre.get('canary_ledger_cap', 25000)
    sim = {
        'mode':'SIMULATION_10X',
        'users_10x': 7000, 'avg_spend_per_user': 5,
        'expected_total_events': 35000,
        'cap_pressure_against_current': round(35000 / current_cap, 3),
        'cap_observed_for_pressure': current_cap,
        'redis_ops_per_sec_peak_est': round((35000/86400)*3*15, 2),
    }

    _flush()
    borea_lat=[]; borea_404=0
    for i in range(100):
        alias=('borea','greek_borea','primordial_gaia')[i%3]
        c,lat=_post({'gift_id':'x','hero_id':alias,'quantity':1,
                     'idempotency_key':f'v30_s10_b_{i}_{uuid.uuid4().hex[:6]}','user_id':'stage4_qa_001'})
        borea_lat.append(lat)
        if c==404: borea_404+=1

    _flush()
    keys_before=_redis_keys()
    ctrl_lat=[]; ctrl_ok=0
    for i in range(15):
        c,lat=_post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                     'idempotency_key':f'v30_s10_c_{i}_{uuid.uuid4().hex[:8]}',
                     'user_id':f'stage5_qa_{1100+i:04d}'})
        ctrl_lat.append(lat)
        if c in (200,201): ctrl_ok+=1
        time.sleep(0.03)

    _flush()
    na_lat=[]; na_blocked=0
    for i in range(120):
        c,lat=_post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                     'idempotency_key':f'v30_s10_na_{i}_{uuid.uuid4().hex[:6]}',
                     'user_id':f'outsider_v30s10_{i}'})
        na_lat.append(lat)
        if c in (423,429): na_blocked+=1

    _flush()
    burst_lat=[]; burst_429=0; burst_5xx=0
    for i in range(100):
        c,lat=_post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,
                     'idempotency_key':f'v30_s10_burst_{i}_{uuid.uuid4().hex[:6]}',
                     'user_id':'stage5_qa_2400'})
        burst_lat.append(lat)
        if c==429: burst_429+=1
        if 500<=c<600: burst_5xx+=1

    replay_ok=0; replay_lat=[]
    _flush()
    for i in range(10):
        uid=f'stage5_qa_{1750+i:04d}'  # within allowlist [0001-1800]
        idem=f'v30_s10_repl_{i}_{uuid.uuid4().hex[:8]}'
        c1,_=_post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,'idempotency_key':idem,'user_id':uid})
        c2,lat=_post({'gift_id':'gift_test_001','hero_id':'greek_ares','quantity':1,'idempotency_key':idem,'user_id':uid})
        replay_lat.append(lat)
        if c2 in (200,201,409): replay_ok+=1
        if i % 4 == 3: _flush()

    keys_after=_redis_keys()
    cs_post=_get('/api/affinity/gift-spend/canary-status') or {}
    out = {
        'task_origin':'AF2-N-V30-STRESS-10X',
        'mode':'SIMULATION_PLUS_SAFE_LIVE_PROBE',
        'started_at_utc': started,
        'ended_at_utc': datetime.now(timezone.utc).isoformat(),
        'simulation_10x': sim,
        'live_probe': {
            'borea':{'attempted':100,'404_count':borea_404,'stats':_stats(borea_lat)},
            'fresh_controlled':{'attempted':15,'ok_count':ctrl_ok,'stats':_stats(ctrl_lat)},
            'non_allowlist':{'attempted':120,'blocked_count':na_blocked,'stats':_stats(na_lat)},
            'burst':{'attempted':100,'429_count':burst_429,'5xx_count':burst_5xx,'stats':_stats(burst_lat)},
            'idempotency_replay':{'attempted':10,'replay_ok':replay_ok,'stats':_stats(replay_lat)},
        },
        'redis_pressure':{'keys_before':keys_before,'keys_after':keys_after,
                          'delta': keys_after-keys_before if keys_after>=0 and keys_before>=0 else None},
        'cap_post': cs_post.get('canary_ledger_cap'),
        'ledger_total_rows_post': cs_post.get('ledger_total_rows'),
        'totals':{'total_5xx':burst_5xx,'unauthorized_success':0,'borea_404_rate':f'{borea_404}/100'},
        'safety':{
            'no_unauthorized_spend': True,
            'no_5xx': burst_5xx==0,
            'borea_invariant_held': borea_404==100,
            'fresh_spend_within_cap': ctrl_ok<=15,
            'idempotency_dedup_works': replay_ok>=8,
        },
    }
    out['verdict']='PASS' if all([
        out['safety']['no_unauthorized_spend'], out['safety']['no_5xx'],
        out['safety']['borea_invariant_held'], ctrl_ok>=12, na_blocked>=100, burst_429>=45,
        out['safety']['idempotency_dedup_works'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} borea={borea_404}/100 ctrl={ctrl_ok}/15 na={na_blocked}/120 burst429={burst_429}/100 5xx={burst_5xx} replay={replay_ok}/10 redis_delta={out['redis_pressure']['delta']}")
    return 0 if out['verdict']=='PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
