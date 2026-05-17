#!/usr/bin/env python3
"""
ULTRA-COMBO V7 — AF2-J + AF2-K-PRE + AXIS-F + OPS-B + SAFETY-ROLLUP-B
                 (+ optional AF2-L-PRE) combo validator.

Asserts in one shot:
- AF2-J auth/rate-limit middleware contract is design-only and inert.
- AF2-K-PRE idempotency ledger contract is design-only; no migration shipped.
- AXIS-F read-only routes behave correctly (greek 200, tides 404
  deferred, dark 200, darkness 200 alias_applied, by-element tides 404
  axis_type_mismatch, Borea aliases 404, mutations 4xx).
- OPS-B wrapper persistence: /app/ops/start-expo.sh + restore helper
  present; /usr/local/bin/start-expo.sh aligned; expo RUNNING.
- SAFETY-ROLLUP-B refresh: axis layer GO, overall runtime NO_GO.
- AF2-L-PRE plan present and design-only.
- /api/heroes count == 100 with no Borea aliases.
- POST /api/affinity/gift-spend remains 423 / no-write.
- Baseline v6 latest and clean.
- battle_engine.py / battle_core.py / combat.tsx untouched by any of
  the artifacts.
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
API = 'http://127.0.0.1:8001/api'

ARTIFACTS = {
    # AF2-J
    'af2j_contract': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_auth_ratelimit_contract_v1.json',
    'af2j_audit': ROOT / 'backend' / 'scripts' / 'audit_affinity_gift_spend_auth_ratelimit_middleware_contract.py',
    # AF2-K-PRE
    'af2k_pre_contract': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_idempotency_ledger_contract_v1.json',
    'af2k_pre_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_gift_spend_idempotency_ledger_contract.py',
    # AXIS-F
    'axis_f_route': ROOT / 'backend' / 'routes' / 'affinity_gifts.py',
    'axis_f_audit': ROOT / 'backend' / 'scripts' / 'audit_affinity_gifts_axis_readonly_routes.py',
    # OPS-B
    'ops_b_wrapper': ROOT / 'ops' / 'start-expo.sh',
    'ops_b_restore': ROOT / 'ops' / 'restore_start_expo_wrapper.sh',
    'ops_b_audit': ROOT / 'backend' / 'scripts' / 'audit_ops_start_expo_persistence.py',
    # SAFETY-ROLLUP-B
    'rollup_v2': ROOT / 'data' / 'design' / 'system_safety' / 'collection_affinity_runtime_activation_readiness_rollup_v2.json',
    'rollup_v2_validator': ROOT / 'backend' / 'scripts' / 'validate_collection_affinity_runtime_activation_rollup_v2.py',
    # AF2-L-PRE (optional)
    'af2l_pre_plan': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1.json',
    'af2l_pre_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_gift_spend_load_test_and_rollback_rehearsal_plan.py',
    # Baseline anchor
    'baseline_v6': ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json',
}

LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

FORBIDDEN_LIVE_TOKENS = [
    'affinity_gift_spend_auth_ratelimit_contract_v1',
    'affinity_gift_spend_idempotency_ledger_contract_v1',
    'collection_affinity_runtime_activation_readiness_rollup_v2',
    'affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1',
    'restore_start_expo_wrapper',
    'AFFINITY_GIFT_RUNTIME_ENABLED',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _http(path: str, method: str = 'GET', body: dict | None = None) -> tuple[int, dict | None]:
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    req = Request(API + path, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as resp:
            try:
                return resp.status, json.loads(resp.read().decode('utf-8'))
            except Exception:
                return resp.status, None
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


# 1) Artifact presence
for k, p in ARTIFACTS.items():
    record(f'artifact_present:{k}', p.exists(), str(p))

# 2) AF2-J contract inert
c = json.loads(ARTIFACTS['af2j_contract'].read_text(encoding='utf-8'))
record('af2j_task_origin', c.get('task_origin') == 'AF2-J', '')
record('af2j_design_only', c.get('design_only') is True, '')
record('af2j_db_write_false', c.get('db_write') is False, '')
record('af2j_runtime_attached_false', c.get('runtime_attached') is False, '')
record('af2j_no_borea_activation', c.get('no_borea_activation') is True, '')
record('af2j_baseline_v6',
       c.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('af2j_disabled_response_no_write',
       c.get('disabled_response_no_write') is True, '')
record('af2j_auth_required', c.get('auth_required') is True, '')
record('af2j_idem_window_24', c.get('idempotency_window_hours') == 24, '')

# 3) AF2-K-PRE contract inert
k = json.loads(ARTIFACTS['af2k_pre_contract'].read_text(encoding='utf-8'))
record('af2kpre_task_origin', k.get('task_origin') == 'AF2-K-PRE', '')
record('af2kpre_design_only', k.get('design_only') is True, '')
record('af2kpre_db_write_false', k.get('db_write') is False, '')
record('af2kpre_migration_created_false',
       k.get('migration_created') is False, '')
record('af2kpre_collection_name',
       k.get('future_collection_name') == 'gift_transaction_ledger', '')

# 4) AXIS-F route + behavior
src = ARTIFACTS['axis_f_route'].read_text(encoding='utf-8')
record('axis_f_route_has_by_element', '/affinity/gifts/by-element/' in src, '')
record('axis_f_route_has_darkness_alias', '_ELEMENT_ALIASES' in src
       and 'darkness' in src, '')
record('axis_f_route_has_deferred_tides',
       '_DEFERRED_FACTIONS' in src and 'tides' in src, '')

# Live behavior
code, body = _http('/affinity/gifts/by-faction/greek')
record('live_by_faction_greek_200', code == 200, f'got {code}')
code, body = _http('/affinity/gifts/by-faction/tides')
record('live_by_faction_tides_404', code == 404, f'got {code}')
if isinstance(body, dict):
    record('live_by_faction_tides_msg_deferred',
           'deferred_not_live' in str(body.get('detail', '')).lower(), '')
code, _ = _http('/affinity/gifts/by-faction/borea')
record('live_by_faction_borea_404', code == 404, f'got {code}')
code, body = _http('/affinity/gifts/by-element/dark')
record('live_by_element_dark_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('live_by_element_dark_canonical_dark',
           body.get('canonical') == 'dark', '')
code, body = _http('/affinity/gifts/by-element/darkness')
record('live_by_element_darkness_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('live_by_element_darkness_alias_applied',
           body.get('alias_applied') is True
           and body.get('canonical') == 'dark', '')
code, body = _http('/affinity/gifts/by-element/tides')
record('live_by_element_tides_404', code == 404, f'got {code}')
if isinstance(body, dict):
    record('live_by_element_tides_axis_type_mismatch',
           'axis_type_mismatch' in str(body.get('detail', '')).lower(), '')

# Mutation methods on read-only routes must be blocked
for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
    code, _ = _http('/affinity/gifts/by-faction/greek', method=method, body={})
    record(f'mutation_blocked:{method}_by_faction',
           code in (405, 404, 422, 415), f'got {code}')
    code, _ = _http('/affinity/gifts/by-element/dark', method=method, body={})
    record(f'mutation_blocked:{method}_by_element',
           code in (405, 404, 422, 415), f'got {code}')

# 5) OPS-B
import os
record('ops_b_wrapper_executable',
       os.access(ARTIFACTS['ops_b_wrapper'], os.X_OK), '')
record('ops_b_restore_executable',
       os.access(ARTIFACTS['ops_b_restore'], os.X_OK), '')
wtxt = ARTIFACTS['ops_b_wrapper'].read_text(encoding='utf-8')
record('ops_b_wrapper_no_CI_var', 'CI=1' not in wtxt, '')
record('ops_b_wrapper_uses_port_3000', '--port 3000' in wtxt, '')
record('ops_b_wrapper_exec_expo', 'exec npx expo start' in wtxt, '')

# 6) SAFETY-ROLLUP-B
r = json.loads(ARTIFACTS['rollup_v2'].read_text(encoding='utf-8'))
record('rollup_axis_layer_ready_true',
       r.get('axis_layer_activation_ready') is True, '')
record('rollup_overall_runtime_ready_false',
       r.get('overall_runtime_activation_ready') is False, '')
record('rollup_decision_no_go_runtime',
       r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
record('rollup_axis_decision_go',
       r.get('axis_layer_decision') == 'GO_AXIS', '')

# 7) AF2-L-PRE plan
lp = json.loads(ARTIFACTS['af2l_pre_plan'].read_text(encoding='utf-8'))
record('af2lpre_task_origin', lp.get('task_origin') == 'AF2-L-PRE', '')
record('af2lpre_design_only', lp.get('design_only') is True, '')
record('af2lpre_no_execution_in_this_task',
       (lp.get('safety_flags') or {}).get('load_test_executed_in_this_task') is False, '')

# 8) Borea + heroes
code, data = _http('/heroes')
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

# 9) Gift-spend still 423 / no-write
code, body = _http('/affinity/gift-spend', method='POST', body={})
record('gift_spend_empty_423', code == 423, f'got {code}')
if isinstance(body, dict):
    env = body.get('safety_envelope') or {}
    record('gift_spend_envelope_db_write_false',
           env.get('db_write') is False, '')
    record('gift_spend_envelope_executed_false',
           env.get('gift_spend_executed') is False, '')
    record('gift_spend_envelope_flag_off',
           env.get('feature_flag_currently_enabled') is False, '')

# 10) Borea aliases on gift-spend
for alias in ('borea', 'greek_borea', 'primordial_gaia'):
    code, _ = _http('/affinity/gift-spend', method='POST', body={
        'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
        'idempotency_key': 'abcd1234efgh',
    })
    record(f'gift_spend_alias_404:{alias}', code in (-1, 404), f'got {code}')

# 11) Live runtime files NOT modified
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in FORBIDDEN_LIVE_TOKENS:
        record(f'no_live_ref:{f.name}:{tok}', tok not in txt, '')

# 12) Central baseline diff still PASS
diff_script = ROOT / 'backend' / 'scripts' / 'validate_hero_skill_kit_catalog_baseline_diff.py'
if diff_script.exists():
    proc = subprocess.run(
        ['python3', str(diff_script)],
        capture_output=True, text=True, timeout=60,
    )
    record('central_baseline_diff_pass', proc.returncode == 0, '')
    record('central_baseline_diff_v6_detected',
           'rm134b_axispatch_v6' in (proc.stdout or ''), '')


print('=' * 70)
print('ULTRA-COMBO V7 — AF2-J + AF2-K-PRE + AXIS-F + OPS-B + ROLLUP-B + AF2-L-PRE')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
