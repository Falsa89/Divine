#!/usr/bin/env python3
# Pack 81 - Track 10: runtime smoke /api/user/heroes (HTTP probe).
import os, json, urllib.request, urllib.error, sys, time, random, string

def _req(method, url, headers=None, body=None):
    data = body.encode('utf-8') if body else None
    req = urllib.request.Request(url, headers=headers or {}, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, dict(r.headers), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        try: body_s = e.read().decode('utf-8')
        except Exception: body_s = ''
        return e.code, dict(e.headers), body_s
    except Exception as e:
        return -1, {}, str(e)

BASE = 'http://127.0.0.1:8001'
# 1) no auth -> 401
st, _h, _b = _req('GET', f'{BASE}/api/user/heroes?server_id=s1')
assert st == 401, f'no-auth must be 401, got {st}'
st, _h, _b = _req('GET', f'{BASE}/api/user/heroes')
assert st == 401, f'no-auth no-server must be 401, got {st}'
# 2) Crea utente effimero e prova i 3 percorsi headers
rand = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
email = f'qa_p81_smoke_{rand}@test.com'
pwd = 'testpass12345'
st, _h, body = _req('POST', f'{BASE}/api/register', headers={'Content-Type': 'application/json'}, body=json.dumps({'email': email, 'password': pwd, 'username': f'qap81{rand}'}))
assert st == 200, f'register failed: {st} {body[:200]}'
tok = json.loads(body).get('token')
assert tok
auth = {'Authorization': f'Bearer {tok}'}
# 2a) no server_id
st, h, body = _req('GET', f'{BASE}/api/user/heroes', headers=auth)
assert st == 200
assert h.get('x-server-scope') == 'account_wide_legacy_DEPRECATED', f'no-server scope wrong: {h}'
assert h.get('x-filter-applied') == 'false'
assert h.get('x-blocker') == 'SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING'
assert h.get('x-canonical-decision') == 'user_heroes_are_server_scoped'
# 2b) server_id=s1 ma PSP non esiste
st, h, body = _req('GET', f'{BASE}/api/user/heroes?server_id=s1', headers=auth)
assert st == 200
assert h.get('x-server-scope') == 'server_scoped'
assert h.get('x-filter-applied') == 'false'
assert h.get('x-blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert h.get('x-server-id') == 's1'
body_json = json.loads(body)
assert isinstance(body_json, list) and len(body_json) == 0, f'no-PSP body must be empty list, got {body[:120]}'
print('[v110 PACK_81_USER_HEROES_RUNTIME_SMOKE] OK 401_gating no_server_id_deprecated server_id_no_psp_blocker_empty body_static_filter_correct')
