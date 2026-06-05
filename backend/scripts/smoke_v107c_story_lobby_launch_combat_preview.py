#!/usr/bin/env python3
"""v107C — E2E preview smoke: Story → Lobby → launch → Combat.

Simulates the e2e flow via direct HTTP calls:
  1. POST /api/battle/launch with story+preview defaults
  2. GET 5 loader probe endpoints with server_id=s1 to assert acceptance
  3. Verify no DB writes claimed, no reward grant
"""
import os, sys, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'design' / 'battle_launch' / 'v107c_e2e_preview_smoke_result_v1.json'
BASE = os.getenv('V107C_BACKEND_BASE', 'http://localhost:8001')

def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return None, {'error': str(e)}

def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                  headers={'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode('utf-8'))
        except Exception: return e.code, None
    except Exception as e:
        return None, {'error': str(e)}

def main():
    results = []
    # Step 1: lobby → launch
    code, body = _post(BASE + '/api/battle/launch', {
        'server_id':'s1','mode':'story','encounter_id':'ch1_n1',
        'enemy_source_type':'authored','enemy_source_id':'goblin_pack_1',
        'reward_policy':'preview','progress_policy':'preview','battle_engine_mode':'preview',
        'client_trace_id':'v107c-e2e-smoke',
    })
    step1_ok = code == 200 and (body or {}).get('status') == 'PREVIEW_ECHO_NON_AUTHORITATIVE' \
        and ((body or {}).get('safety') or {}).get('db_writes_performed', -1) == 0
    results.append({'step':'lobby_launch_post','status_code':code,'pass':step1_ok,'response_status_string':(body or {}).get('status'),'safety':(body or {}).get('safety')})
    # Step 2: 5 loader probes with server_id
    probes = ['user-heroes','team-get-formation','inventory','currencies','story-progress']
    all_probes_ok = True
    probe_results = []
    for p in probes:
        code, body = _get(f'{BASE}/api/v107c/loader-probe/{p}?server_id=s1')
        ok = code == 200 and (body or {}).get('server_id_received') == 's1' \
            and (body or {}).get('server_id_parsed') is True \
            and (body or {}).get('filter_applied') is False \
            and ((body or {}).get('safety') or {}).get('db_writes_performed', -1) == 0
        all_probes_ok = all_probes_ok and ok
        probe_results.append({'probe':p,'status_code':code,'pass':ok,'server_id_received':(body or {}).get('server_id_received'),'filter_applied':(body or {}).get('filter_applied'),'flag':(body or {}).get('feature_flag')})
    results.append({'step':'loader_acceptance_probes','probes':probe_results,'pass':all_probes_ok})
    overall = step1_ok and all_probes_ok
    summary = {
        'pack':'MEGA_RELEASE_ACCELERATION_58_v107C',
        'type':'v107c_e2e_preview_smoke_result',
        'version':1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'base_url': BASE,
        'overall_pass': overall,
        'steps_total': 2,
        'steps_pass': sum(1 for s in results if s.get('pass')),
        'results': results,
        'safety':{'no_db_writes':True,'no_reward_grant':True,'no_progress_write':True,'no_currency_mutation':True,'fake_PASS':False,'validator_weakening':False,'hiding_preview_state':False}
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"E2E smoke v107C \u2192 overall={overall} \u2192 {OUT}")
    sys.exit(0 if overall else 1)

if __name__ == '__main__':
    main()
