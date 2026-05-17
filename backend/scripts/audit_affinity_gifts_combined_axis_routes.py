#!/usr/bin/env python3
"""AXIS-G — Audit: combined read-only routes (element + faction)."""
from __future__ import annotations
import json, sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
failures: list[str] = []; checks: list[tuple[str,bool,str]] = []
def record(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

def _http(path, method='GET', body=None):
    payload = None; headers = {}
    if body is not None:
        payload = json.dumps(body).encode(); headers = {'Content-Type':'application/json'}
    req = Request(API + path, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as r:
            try: return r.status, json.loads(r.read().decode())
            except: return r.status, None
    except HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except: return e.code, None
    except URLError: return -1, None

# combined routes: dark + greek
code, body = _http('/affinity/gifts/by-element/dark/by-faction/greek')
record('dark_greek_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('dark_greek_design_only', body.get('design_only') is True, '')
    record('dark_greek_canonical_dark', body.get('canonical_element') == 'dark', '')
    record('dark_greek_faction', body.get('faction_id') == 'greek', '')
    record('dark_greek_count_ge_0', isinstance(body.get('count'), int), '')

# darkness alias
code, body = _http('/affinity/gifts/by-element/darkness/by-faction/greek')
record('darkness_greek_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('darkness_greek_alias_true', body.get('alias_applied') is True, '')
    record('darkness_greek_canonical_dark', body.get('canonical_element') == 'dark', '')

# reverse order: greek + fire
code, body = _http('/affinity/gifts/by-faction/greek/by-element/fire')
record('greek_fire_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('greek_fire_canonical_fire', body.get('canonical_element') == 'fire', '')
    record('greek_fire_faction_greek', body.get('faction_id') == 'greek', '')

# fire + greek (combined element-first)
code, _ = _http('/affinity/gifts/by-element/fire/by-faction/greek')
record('fire_greek_200', code == 200, f'got {code}')

# tides faction -> 404 deferred
code, body = _http('/affinity/gifts/by-element/dark/by-faction/tides')
record('dark_tides_404', code == 404, f'got {code}')
if isinstance(body, dict):
    record('dark_tides_deferred', 'deferred_not_live' in str(body.get('detail','')).lower(), '')

# borea faction -> 404 forbidden
code, _ = _http('/affinity/gifts/by-element/dark/by-faction/borea')
record('dark_borea_404', code == 404, f'got {code}')
code, _ = _http('/affinity/gifts/by-element/dark/by-faction/greek_borea')
record('dark_greek_borea_404', code == 404, f'got {code}')

# faction-in-element position -> 404 axis_type_mismatch
code, body = _http('/affinity/gifts/by-element/tides/by-faction/greek')
record('tides_greek_axis_mismatch_404', code == 404, f'got {code}')
if isinstance(body, dict):
    record('tides_greek_axis_mismatch_msg', 'axis_type_mismatch' in str(body.get('detail','')).lower(), '')
code, _ = _http('/affinity/gifts/by-element/greek/by-faction/fire')
record('greek_in_element_404', code == 404, f'got {code}')

# Mutation methods blocked
for m in ('POST','PUT','PATCH','DELETE'):
    code, _ = _http('/affinity/gifts/by-element/dark/by-faction/greek', method=m, body={})
    record(f'mut_blocked:{m}', code in (405, 404, 422, 415), f'got {code}')

print('='*70); print('AXIS-G — Combined Read-Only Routes Audit'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
