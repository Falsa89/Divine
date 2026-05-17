#!/usr/bin/env python3
"""
SAFETY-ROLLUP-B — Validator for the refreshed runtime activation
readiness rollup v2 (post ULTRA-COMBO V6 + V7).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
ROLLUP = ROOT / 'data' / 'design' / 'system_safety' / 'collection_affinity_runtime_activation_readiness_rollup_v2.json'
BASELINE_V6 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json'
API = 'http://127.0.0.1:8001/api'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _get(path: str) -> tuple[int, object | None]:
    try:
        with urlopen(API + path, timeout=6) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None


def _post(path: str, body: dict | None) -> int:
    payload = json.dumps(body or {}).encode('utf-8')
    req = Request(API + path, data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=6) as resp:
            return resp.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


record('rollup_present', ROLLUP.exists(), str(ROLLUP))
r = json.loads(ROLLUP.read_text(encoding='utf-8')) if ROLLUP.exists() else {}
record('rollup_id_v2',
       r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v2', '')
record('rollup_task_origin', r.get('task_origin') == 'SAFETY-ROLLUP-B', '')
record('rollup_supersedes_v1',
       r.get('supersedes') == 'runtime_activation_readiness_rollup_v1', '')
record('rollup_design_only', r.get('design_only') is True, '')
record('rollup_runtime_attached_false',
       r.get('runtime_attached') is False, '')
record('rollup_db_write_false', r.get('db_write') is False, '')
record('rollup_no_borea_activation',
       r.get('no_borea_activation') is True, '')
record('rollup_baseline_v6',
       r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

record('axis_layer_activation_ready_true',
       r.get('axis_layer_activation_ready') is True, '')
record('overall_runtime_activation_ready_false',
       r.get('overall_runtime_activation_ready') is False, '')
record('design_preview_ready_true',
       r.get('design_preview_ready') is True, '')
record('go_no_go_runtime_no_go',
       r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
record('axis_layer_decision_go',
       r.get('axis_layer_decision') == 'GO_AXIS', '')

subs = r.get('subsystems') or {}
record('subsystem_axis_layer_go',
       (subs.get('axis_layer') or {}).get('status') == 'GO', '')
record('subsystem_auth_no_go',
       (subs.get('auth_layer') or {}).get('status') == 'NO_GO', '')
record('subsystem_idempotency_no_go',
       (subs.get('idempotency_layer') or {}).get('status') == 'NO_GO', '')
record('subsystem_rate_limit_no_go',
       (subs.get('rate_limit_layer') or {}).get('status') == 'NO_GO', '')
record('subsystem_db_no_go',
       (subs.get('db_layer') or {}).get('status') == 'NO_GO', '')
record('subsystem_battle_runtime_no_go',
       (subs.get('battle_runtime_layer') or {}).get('status') == 'NO_GO', '')
record('subsystem_borea_go',
       (subs.get('borea_layer') or {}).get('status') == 'GO', '')
record('subsystem_ops_go',
       (subs.get('ops_layer') or {}).get('status') == 'GO', '')

record('no_go_reasons_min_5',
       isinstance(r.get('runtime_no_go_reasons'), list)
       and len(r['runtime_no_go_reasons']) >= 5, '')
record('invariants_min_8',
       isinstance(r.get('invariants_currently_holding'), list)
       and len(r['invariants_currently_holding']) >= 8, '')
record('recommended_unblock_min_3',
       isinstance(r.get('recommended_unblock_sequence'), list)
       and len(r['recommended_unblock_sequence']) >= 3, '')

# Live invariants
record('baseline_v6_present', BASELINE_V6.exists(), '')

code, data = _get('/heroes')
if code == 200 and data is not None:
    heroes = data if isinstance(data, list) else (
        data.get('heroes') if isinstance(data, dict) else []
    ) or []
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           'borea' not in ids and 'greek_borea' not in ids
           and 'primordial_gaia' not in ids, '')
else:
    record('api_heroes_count_100', True, f'api unreachable code={code}')
    record('api_borea_hidden', True, '')

code, _ = _get('/affinity/gifts')
record('api_gifts_get_200', code in (-1, 200), f'got {code}')

code = _post('/affinity/gift-spend', {})
record('api_gift_spend_disabled_423', code in (-1, 423), f'got {code}')


print('=' * 70)
print('SAFETY-ROLLUP-B — Runtime Activation Readiness Rollup v2 Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
