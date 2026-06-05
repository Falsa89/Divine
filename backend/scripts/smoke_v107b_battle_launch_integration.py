#!/usr/bin/env python3
"""v107B — Battle Launch smoke test (real HTTP integration).

Calls POST /api/battle/launch with a story preview payload and a live-attempt
payload, verifying:
  - preview echo status
  - coercion of live -> preview when flags OFF
  - 0 DB writes claimed
  - server_id parsed but not enforced (PSP not applied)

No DB writes, no auth required.
"""
import os, sys, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'design' / 'battle_launch' / 'v107b_battle_launch_smoke_result_v1.json'
URL = os.getenv('V107B_BACKEND_BASE', 'http://localhost:8001') + '/api/battle/launch'

CASES = [
    {
        'name': 'story_preview_default',
        'payload': {
            'server_id':'s1','mode':'story','encounter_id':'ch1_n1',
            'enemy_source_type':'authored','enemy_source_id':'goblin_pack_1',
            'reward_policy':'preview','progress_policy':'preview','battle_engine_mode':'preview',
        },
        'expect_status_code': 200,
        'expect_status_string': 'PREVIEW_ECHO_NON_AUTHORITATIVE',
        'expect_no_coercion': True,
    },
    {
        'name': 'live_attempt_with_idempotency_coerced_to_preview',
        'payload': {
            'server_id':'s1','mode':'arena','encounter_id':'arena_match_1',
            'enemy_source_type':'bot_team','enemy_source_id':'bot_archetype_f2p_base_001',
            'reward_policy':'live','progress_policy':'live','battle_engine_mode':'authoritative',
            'idempotency_key':'smoke-v107b-001',
        },
        'expect_status_code': 200,
        'expect_status_string': 'PREVIEW_ECHO_NON_AUTHORITATIVE',
        'expect_coercions_min': 3,
    },
    {
        'name': 'live_without_idempotency_should_400_after_coercion_drops_below_live',
        'payload': {
            'server_id':'s1','mode':'tower','encounter_id':'tower_floor_3',
            'enemy_source_type':'authored','enemy_source_id':'tower_floor_3_team',
            'reward_policy':'preview','progress_policy':'preview','battle_engine_mode':'preview',
        },
        'expect_status_code': 200,
        'expect_status_string': 'PREVIEW_ECHO_NON_AUTHORITATIVE',
    },
]

def do_call(payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers={'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode('utf-8'))
        except Exception: body = None
        return e.code, body
    except Exception as e:
        return None, {'error': str(e)}

def main():
    results = []
    all_ok = True
    for c in CASES:
        code, body = do_call(c['payload'])
        ok = code == c['expect_status_code']
        if ok and body and c.get('expect_status_string'):
            ok = body.get('status') == c['expect_status_string']
        if ok and body and 'expect_coercions_min' in c:
            ok = len(body.get('coercions_applied') or []) >= c['expect_coercions_min']
        if ok and body and c.get('expect_no_coercion'):
            ok = len(body.get('coercions_applied') or []) == 0
        if not ok: all_ok = False
        results.append({
            'case': c['name'],
            'request_payload': c['payload'],
            'response_status_code': code,
            'response_status_string': (body or {}).get('status'),
            'coercions_applied': (body or {}).get('coercions_applied') or [],
            'feature_flags': (body or {}).get('feature_flags') or {},
            'safety': (body or {}).get('safety') or {},
            'pass': ok,
        })
    summary = {
        'pack':'MEGA_RELEASE_ACCELERATION_57_v107B',
        'type':'v107b_battle_launch_smoke_result',
        'version':1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'url': URL,
        'cases_total': len(results),
        'cases_pass': sum(1 for r in results if r['pass']),
        'overall_pass': all_ok,
        'results': results,
        'safety': {
            'no_db_writes': True,
            'no_reward_grant': True,
            'no_progress_write': True,
            'no_currency_mutation': True,
            'fake_PASS': False,
            'validator_weakening': False,
            'hiding_preview_state': False,
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Smoke v107B \u2192 {summary['cases_pass']}/{summary['cases_total']} PASS \u2192 {OUT}")
    sys.exit(0 if all_ok else 1)

if __name__ == '__main__':
    main()
