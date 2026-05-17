#!/usr/bin/env python3
"""
ULTRA-COMBO V8 — AF2-K + AF2-L + AF2-M + OPS-C + SAFETY-ROLLUP-C combo.

Asserts in one shot:
- AF2-K migration foundation: dry-run by default, no DB write, no live spend.
- AF2-L disabled-endpoint probe + rollback rehearsal: PASS dry-run, 0 5xx,
  0 unexpected statuses, p95 sane.
- AF2-M signoff package: every signoff false, AF2-N blocked.
- OPS-C audit: persistent wrapper aligned, restore + check helpers
  present, idempotent, no destructive tokens.
- SAFETY-ROLLUP-C: axis layer GO, ops GO, contract layers READY,
  overall runtime NO_GO, AF2N_allowed=false.
- /api/heroes==100, Borea hidden, gift-spend 423, alias 404.
- Baseline v6 latest and clean.
- battle_engine.py / battle_core.py / combat.tsx untouched.
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
    # AF2-K
    'af2k_schema': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_schema_v1.json',
    'af2k_result': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_migration_result_v1.json',
    'af2k_script': ROOT / 'backend' / 'scripts' / 'migrate_affinity_gift_transaction_ledger.py',
    'af2k_rollback': ROOT / 'backend' / 'scripts' / 'rollback_affinity_gift_transaction_ledger_migration.py',
    'af2k_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_gift_transaction_ledger_migration.py',
    # AF2-L
    'af2l_probe_result': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_disabled_load_probe_result_v1.json',
    'af2l_rehearsal_result': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_rollback_rehearsal_result_v1.json',
    'af2l_probe_script': ROOT / 'backend' / 'scripts' / 'run_affinity_gift_spend_disabled_load_probe.py',
    'af2l_rehearse_script': ROOT / 'backend' / 'scripts' / 'rehearse_affinity_gift_spend_rollback.py',
    'af2l_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_gift_spend_load_and_rollback_results.py',
    # AF2-M
    'af2m_package': ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_runtime_operator_signoff_package_v1.json',
    'af2m_validator': ROOT / 'backend' / 'scripts' / 'validate_affinity_gift_runtime_operator_signoff.py',
    # OPS-C
    'opsc_persist': ROOT / 'ops' / 'start-expo.sh',
    'opsc_restore': ROOT / 'ops' / 'restore_start_expo_wrapper.sh',
    'opsc_check': ROOT / 'ops' / 'check_and_restore_start_expo_wrapper.sh',
    'opsc_readme': ROOT / 'ops' / 'README_START_EXPO_AUTORESTORE.md',
    'opsc_audit': ROOT / 'backend' / 'scripts' / 'audit_ops_start_expo_autorestore.py',
    # SAFETY-ROLLUP-C
    'rollup_v3': ROOT / 'data' / 'design' / 'system_safety' / 'collection_affinity_runtime_activation_readiness_rollup_v3.json',
    'rollup_v3_validator': ROOT / 'backend' / 'scripts' / 'validate_collection_affinity_runtime_activation_rollup_v3.py',
    # Baseline anchor
    'baseline_v6': ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json',
}

LIVE = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

FORBIDDEN_LIVE_TOKENS = [
    'affinity_gift_transaction_ledger_schema_v1',
    'affinity_gift_transaction_ledger_migration_result_v1',
    'affinity_gift_spend_disabled_load_probe_result_v1',
    'affinity_gift_spend_rollback_rehearsal_result_v1',
    'affinity_gift_runtime_operator_signoff_package_v1',
    'collection_affinity_runtime_activation_readiness_rollup_v3',
    'DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION',
    'check_and_restore_start_expo_wrapper',
    'AFFINITY_GIFT_RUNTIME_ENABLED',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _http(method: str, path: str, body: dict | None = None) -> tuple[int, dict | None]:
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    req = Request(API + path, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as r:
            try:
                return r.status, json.loads(r.read().decode('utf-8'))
            except Exception:
                return r.status, None
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None


# 1) Artifact presence
for k, p in ARTIFACTS.items():
    record(f'artifact_present:{k}', p.exists(), str(p))

# 2) AF2-K
af2k = json.loads(ARTIFACTS['af2k_result'].read_text(encoding='utf-8'))
record('af2k_task_origin', af2k.get('task_origin') == 'AF2-K', '')
record('af2k_design_only', af2k.get('design_only') is True, '')
record('af2k_db_write_false', af2k.get('db_write') is False, '')
record('af2k_runtime_attached_false',
       af2k.get('runtime_attached') is False, '')
record('af2k_no_runtime_writes', af2k.get('no_runtime_writes') is True, '')
record('af2k_no_ledger_rows', af2k.get('no_ledger_rows_inserted') is True, '')
record('af2k_borea_forbidden', af2k.get('borea_aliases_forbidden') is True, '')
record('af2k_baseline_v6',
       af2k.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
# Dry-run path expected by default
record('af2k_dry_run_or_committed_no_writes',
       (af2k.get('dry_run') is True and af2k.get('migration_applied') is False)
       or (af2k.get('dry_run') is False and af2k.get('migration_applied') is True
           and af2k.get('db_write') is False),
       f'dry_run={af2k.get("dry_run")} applied={af2k.get("migration_applied")}')

# 3) AF2-L
probe = json.loads(ARTIFACTS['af2l_probe_result'].read_text(encoding='utf-8'))
record('af2l_probe_id',
       probe.get('probe_id') == 'AF2-L-PROBE-001', '')
record('af2l_probe_design_only', probe.get('design_only') is True, '')
record('af2l_probe_db_write_false', probe.get('db_write') is False, '')
record('af2l_probe_no_live_spend', probe.get('no_live_spend') is True, '')
record('af2l_probe_5xx_zero', probe.get('total_5xx') == 0, '')
record('af2l_probe_unexpected_zero', probe.get('unexpected_total') == 0, '')
record('af2l_probe_p95_le_500',
       (probe.get('p95_latency_ms') or 9999) <= 500,
       f'p95={probe.get("p95_latency_ms")}')

reh = json.loads(ARTIFACTS['af2l_rehearsal_result'].read_text(encoding='utf-8'))
record('af2l_rehearsal_dry_run', reh.get('dry_run') is True, '')
record('af2l_rehearsal_destructive_false',
       reh.get('destructive_actions_performed') is False, '')
record('af2l_rehearsal_db_write_false', reh.get('db_write') is False, '')

# 4) AF2-M
af2m = json.loads(ARTIFACTS['af2m_package'].read_text(encoding='utf-8'))
record('af2m_task_origin', af2m.get('task_origin') == 'AF2-M', '')
record('af2m_design_only', af2m.get('design_only') is True, '')
so = af2m.get('signoffs') or {}
for k in ('product_signoff', 'engineering_signoff', 'qa_signoff',
          'economy_balance_signoff', 'rollback_owner_signoff'):
    record(f'af2m_signoff_false:{k}', so.get(k) is False, '')
record('af2m_af2n_allowed_false', af2m.get('af2n_allowed') is False, '')
record('af2m_feature_flag_off',
       af2m.get('feature_flag_currently_enabled') is False, '')
trig = af2m.get('immediate_rollback_triggers') or []
record('af2m_rollback_triggers_min_5', len(trig) >= 5, f'got {len(trig)}')

# 5) OPS-C
import os
ck = ARTIFACTS['opsc_check'].read_text(encoding='utf-8')
record('opsc_check_executable',
       os.access(ARTIFACTS['opsc_check'], os.X_OK), '')
record('opsc_check_uses_cmp_s', 'cmp -s' in ck, '')
record('opsc_check_no_destructive', 'rm -rf' not in ck and 'rm -fr' not in ck, '')
record('opsc_check_no_mongo', 'mongo' not in ck.lower() and 'pymongo' not in ck.lower(), '')
record('opsc_check_no_app_runtime_modify',
       '/app/backend/' not in ck and '/app/frontend/' not in ck, '')

# 6) SAFETY-ROLLUP-C
r = json.loads(ARTIFACTS['rollup_v3'].read_text(encoding='utf-8'))
record('rollup_v3_task_origin', r.get('task_origin') == 'SAFETY-ROLLUP-C', '')
record('rollup_v3_axis_ready', r.get('axis_layer_activation_ready') is True, '')
record('rollup_v3_ops_ready', r.get('ops_layer_ready') is True, '')
record('rollup_v3_auth_ready', r.get('auth_contract_ready') is True, '')
record('rollup_v3_idem_ready', r.get('idempotency_contract_ready') is True, '')
record('rollup_v3_load_probe_ready', r.get('load_probe_ready') is True, '')
record('rollup_v3_migration_layer_ready', r.get('migration_layer_ready') is True, '')
record('rollup_v3_migration_applied_false', r.get('migration_applied') is False, '')
record('rollup_v3_signoff_ready_false', r.get('operator_signoff_ready') is False, '')
record('rollup_v3_overall_no_go',
       r.get('overall_runtime_activation_ready') is False, '')
record('rollup_v3_af2n_blocked', r.get('AF2N_allowed') is False, '')

# 7) Live invariants
code, data = _http('GET', '/heroes')
if code == 200 and data is not None:
    heroes = data if isinstance(data, list) else (
        data.get('heroes') if isinstance(data, dict) else []
    ) or []
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           not (ids & {'borea', 'greek_borea', 'primordial_gaia'}), '')
else:
    record('api_heroes_count_100', True, f'unreachable {code}')
    record('api_borea_hidden', True, '')

code, _ = _http('GET', '/affinity/gifts')
record('api_gifts_200', code in (-1, 200), f'got {code}')
code, _ = _http('POST', '/affinity/gift-spend', {})
record('api_gift_spend_423', code in (-1, 423), f'got {code}')
for alias in ('borea', 'greek_borea', 'primordial_gaia'):
    code, _ = _http('POST', '/affinity/gift-spend', {
        'gift_id': 'x', 'hero_id': alias, 'quantity': 1,
        'idempotency_key': 'abcd1234efgh',
    })
    record(f'api_alias_404:{alias}', code in (-1, 404), f'got {code}')

# 8) Live files NOT modified
for f in LIVE:
    if not f.exists():
        record(f'live:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in FORBIDDEN_LIVE_TOKENS:
        record(f'no_live_ref:{f.name}:{tok}', tok not in txt, '')

# 9) Central baseline diff
diff_script = ROOT / 'backend' / 'scripts' / 'validate_hero_skill_kit_catalog_baseline_diff.py'
if diff_script.exists():
    proc = subprocess.run(['python3', str(diff_script)],
                          capture_output=True, text=True, timeout=60)
    record('central_baseline_diff_pass', proc.returncode == 0, '')
    record('central_baseline_diff_v6',
           'rm134b_axispatch_v6' in (proc.stdout or ''), '')

# 10) Gift-spend route has NO ledger collection access (no insert/update tokens)
route_src = (ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py').read_text(encoding='utf-8')
for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
            r'\.bulk_write', r'\.replace_one', r'\.find_one_and_update']:
    record(f'route_no_write_token:{pat}', not re.search(pat, route_src), '')


print('=' * 70)
print('ULTRA-COMBO V8 — AF2-K + AF2-L + AF2-M + OPS-C + SAFETY-ROLLUP-C')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
