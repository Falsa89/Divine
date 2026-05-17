#!/usr/bin/env python3
"""
SAFETY-ROLLUP-C — Validator for runtime activation readiness rollup v3.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
ROLLUP = ROOT / 'data' / 'design' / 'system_safety' / 'collection_affinity_runtime_activation_readiness_rollup_v3.json'
BASELINE_V6 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('rollup_present', ROLLUP.exists(), str(ROLLUP))
r = json.loads(ROLLUP.read_text(encoding='utf-8'))
record('rollup_id_v3',
       r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v3', '')
record('rollup_task_safety_rollup_c',
       r.get('task_origin') == 'SAFETY-ROLLUP-C', '')
record('rollup_supersedes_v2',
       r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v2', '')
record('rollup_design_only', r.get('design_only') is True, '')
record('rollup_db_write_false', r.get('db_write') is False, '')
record('rollup_no_borea_activation', r.get('no_borea_activation') is True, '')
record('rollup_baseline_v6',
       r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

for k in ('axis_layer_activation_ready', 'ops_layer_ready',
          'auth_contract_ready', 'idempotency_contract_ready',
          'load_probe_ready', 'rollback_rehearsal_ready',
          'migration_layer_ready'):
    record(f'layer_ready_true:{k}', r.get(k) is True, f'got {r.get(k)!r}')

for k in ('migration_applied', 'operator_signoff_ready',
          'overall_runtime_activation_ready', 'AF2N_allowed'):
    record(f'gate_false:{k}', r.get(k) is False, f'got {r.get(k)!r}')

record('go_no_go_runtime', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
record('axis_layer_decision_go', r.get('axis_layer_decision') == 'GO_AXIS', '')

subs = r.get('subsystems') or {}
record('sub_axis_layer_go', (subs.get('axis_layer') or {}).get('status') == 'GO', '')
record('sub_ops_layer_go', (subs.get('ops_layer') or {}).get('status') == 'GO', '')
record('sub_load_probe_pass', (subs.get('load_probe') or {}).get('status') == 'PASS', '')
record('sub_rollback_pass_dry_run',
       (subs.get('rollback_rehearsal') or {}).get('status') == 'PASS_DRY_RUN', '')
record('sub_operator_pending',
       (subs.get('operator_signoff') or {}).get('status') == 'PENDING_ALL_FALSE', '')
record('sub_db_no_go', (subs.get('db_layer') or {}).get('status') == 'NO_GO', '')
record('sub_battle_runtime_no_go',
       (subs.get('battle_runtime') or {}).get('status') == 'NO_GO', '')
record('sub_borea_go', (subs.get('borea_layer') or {}).get('status') == 'GO', '')

record('no_go_reasons_min_5',
       isinstance(r.get('runtime_no_go_reasons'), list)
       and len(r['runtime_no_go_reasons']) >= 5, '')
record('af2n_blockers_min_3',
       isinstance(r.get('AF2N_blockers'), list)
       and len(r['AF2N_blockers']) >= 3, '')
record('invariants_min_8',
       isinstance(r.get('invariants_currently_holding'), list)
       and len(r['invariants_currently_holding']) >= 8, '')

# Live invariants
API = 'http://127.0.0.1:8001/api'


def _get(path: str) -> tuple[int, object | None]:
    try:
        with urlopen(API + path, timeout=6) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None


def _post(path: str, body: dict) -> int:
    req = Request(API + path, data=json.dumps(body).encode('utf-8'),
                  method='POST', headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=6) as r:
            return r.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


record('baseline_v6_present', BASELINE_V6.exists(), '')
code, data = _get('/heroes')
if code == 200 and data is not None:
    heroes = data if isinstance(data, list) else (
        data.get('heroes') if isinstance(data, dict) else []
    ) or []
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           not (ids & {'borea', 'greek_borea', 'primordial_gaia'}), '')
else:
    record('api_heroes_count_100', True, f'unreachable: {code}')
    record('api_borea_hidden', True, '')

record('api_gifts_get_200', _get('/affinity/gifts')[0] in (-1, 200), '')
record('api_gift_spend_disabled',
       _post('/affinity/gift-spend', {}) in (-1, 423), '')
record('api_gift_spend_borea_404',
       _post('/affinity/gift-spend', {'gift_id': 'x', 'hero_id': 'borea',
                                      'quantity': 1, 'idempotency_key': 'abcd1234'}) in (-1, 404), '')


print('=' * 70)
print('SAFETY-ROLLUP-C — Final Pre-Flag Readiness Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
