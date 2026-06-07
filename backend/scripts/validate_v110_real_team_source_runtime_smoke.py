#!/usr/bin/env python3
# Pack 80 — Track E: real team source runtime smoke (HTTP probe localhost).
# Verifica HONEST che la route reale e' raggiungibile e che il gating auth
# e' applicato (401 senza Bearer). NESSUN DB write eseguito dallo smoke.
import os, json, sys, urllib.request, urllib.error

def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode('utf-8'))
        except Exception: body = None
        return e.code, body
    except Exception as e:
        return -1, {'_err': str(e)}

BASE = 'http://127.0.0.1:8001'
# 1) Senza auth e con server_id -> deve gatekeepere 401 onestamente (NO silent bypass)
st1, d1 = _get(f'{BASE}/api/team/get-formation?server_id=s1')
assert st1 == 401, f'noauth+server_id status must be 401 (honest gating); got {st1} body={d1}'
# 2) Senza auth e senza server_id -> ancora 401, NO leak
st2, d2 = _get(f'{BASE}/api/team/get-formation')
assert st2 == 401, f'noauth+no_server_id status must be 401; got {st2} body={d2}'
# 3) Bearer invalido -> 401, NO bypass
st3, d3 = _get(f'{BASE}/api/team/get-formation?server_id=s1', headers={'Authorization': 'Bearer not_a_real_token'})
assert st3 == 401, f'invalid-bearer status must be 401; got {st3} body={d3}'
# Verifica che il modulo route non contenga alcuna mutation (DB write) — controllo statico.
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/v96_team_formation.py')).read()
for forbidden in ('update_one', 'insert_one', 'delete_one', 'replace_one', 'update_many', 'insert_many', 'delete_many'):
    assert forbidden not in src, f'route module contains forbidden DB write call: {forbidden}'
print('[v110 REAL_TEAM_SOURCE_RUNTIME_SMOKE] OK route_reachable=true auth_gating_401_enforced=3/3 no_silent_bypass db_writes=0')
