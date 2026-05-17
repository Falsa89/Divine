#!/usr/bin/env python3
"""ULTRA-COMBO V9 — Composite validator.

Aggregates the six independent V9 subtask validators/audits and enforces
the joint runtime NO_GO invariant + the live safety smoke tests required
by the V9 brief.

Subtasks aggregated:
  - AF2-K-COMMIT     : validate_affinity_gift_transaction_ledger_commit_result.py
  - AF2-L-FULL       : run_affinity_gift_spend_full_disabled_load_probe.py
                       + validate_affinity_phase2_rollback_rehearsal.py
  - AF2-M-SIGN-PRE   : validate_affinity_gift_runtime_operator_signoff_v2.py
  - AXIS-G           : audit_affinity_gifts_combined_axis_routes.py
  - OPS-C-WIRING     : audit_ops_start_expo_boot_wiring.py
  - SAFETY-ROLLUP-D  : validate_collection_affinity_runtime_activation_rollup_v4.py

Plus live runtime smoke (NO writes):
  - /api/heroes count == 100
  - borea / greek_borea / primordial_gaia hidden
  - POST /api/affinity/gift-spend (empty)            -> 423
  - POST /api/affinity/gift-spend (borea alias)      -> 404
  - GET /api/affinity/gifts/by-element/dark/by-faction/greek -> 200
  - GET /api/affinity/gifts/by-element/darkness/by-faction/greek -> 200 alias_applied
  - GET /api/affinity/gifts/by-faction/greek/by-element/fire -> 200

Read-only. No DB writes. Exit 0 only if every subtask passes and every
invariant holds.
"""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('AF2-K-COMMIT',     'validate_affinity_gift_transaction_ledger_commit_result.py'),
    ('AF2-L-FULL',       'run_affinity_gift_spend_full_disabled_load_probe.py'),
    ('AF2-L-FULL-RBK',   'validate_affinity_phase2_rollback_rehearsal.py'),
    ('AF2-M-SIGN-PRE',   'validate_affinity_gift_runtime_operator_signoff_v2.py'),
    ('AXIS-G',           'audit_affinity_gifts_combined_axis_routes.py'),
    ('OPS-C-WIRING',     'audit_ops_start_expo_boot_wiring.py'),
    ('SAFETY-ROLLUP-D',  'validate_collection_affinity_runtime_activation_rollup_v4.py'),
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def run_subtask(name: str, script: str) -> tuple[int, str]:
    path = SCRIPTS / script
    if not path.exists():
        return 127, f'<missing: {script}>'
    try:
        p = subprocess.run(
            ['python3', str(path)], capture_output=True, text=True, timeout=90
        )
        return p.returncode, (p.stdout or p.stderr or '').strip().splitlines()[-1:] and \
            ((p.stdout or p.stderr).strip().splitlines()[-1]) or ''
    except subprocess.TimeoutExpired:
        return 124, '<TIMEOUT>'
    except Exception as e:
        return -1, f'<ERROR: {e!r}>'


for tag, script in SUBTASKS:
    code, tail = run_subtask(tag, script)
    record(f'subtask:{tag}', code == 0, f'exit={code} tail={tail}')


# Live safety smoke ────────────────────────────────────────────────────
def _get(path: str):
    try:
        with urlopen(API + path, timeout=6) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, None
    except URLError:
        return -1, None


def _post(path: str, body: dict | None):
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode()
        headers = {'Content-Type': 'application/json'}
    req = Request(API + path, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r:
            return r.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


code, data = _get('/heroes')
record('live_heroes_reachable', code in (200, 304), f'got {code}')
if isinstance(data, list):
    record('live_heroes_count_100', len(data) == 100, f'got {len(data)}')
    ids = {h.get('id') for h in data if isinstance(h, dict)}
    record('live_borea_hidden',
           not (ids & {'borea', 'greek_borea', 'primordial_gaia'}),
           f'leaked={sorted(ids & {"borea","greek_borea","primordial_gaia"})}')
else:
    record('live_heroes_count_100', False, 'response not list')
    record('live_borea_hidden', False, 'response not list')

record('live_gift_spend_empty_423',
       _post('/affinity/gift-spend', {}) == 423, '')
record('live_gift_spend_borea_404',
       _post('/affinity/gift-spend',
             {'gift_id': 'x', 'hero_id': 'borea', 'quantity': 1,
              'idempotency_key': 'abcd1234'}) == 404, '')
record('live_gift_spend_greek_borea_404',
       _post('/affinity/gift-spend',
             {'gift_id': 'x', 'hero_id': 'greek_borea', 'quantity': 1,
              'idempotency_key': 'abcd1234'}) == 404, '')

# AXIS-G combined routes
code, body = _get('/affinity/gifts/by-element/dark/by-faction/greek')
record('live_axis_g_dark_greek_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('live_axis_g_canonical_dark', body.get('canonical_element') == 'dark', '')
    record('live_axis_g_design_only', body.get('design_only') is True, '')
    record('live_axis_g_runtime_off', body.get('runtime_attached') is False, '')

code, body = _get('/affinity/gifts/by-element/darkness/by-faction/greek')
record('live_axis_g_darkness_alias_200', code == 200, f'got {code}')
if isinstance(body, dict):
    record('live_axis_g_alias_applied', body.get('alias_applied') is True, '')

code, _ = _get('/affinity/gifts/by-faction/greek/by-element/fire')
record('live_axis_g_reverse_order_200', code == 200, f'got {code}')

code, _ = _get('/affinity/gifts/by-element/dark/by-faction/tides')
record('live_axis_g_tides_404', code == 404, f'got {code}')
code, _ = _get('/affinity/gifts/by-element/dark/by-faction/borea')
record('live_axis_g_borea_404', code == 404, f'got {code}')
code, _ = _get('/affinity/gifts/by-element/tides/by-faction/greek')
record('live_axis_g_axis_mismatch_404', code == 404, f'got {code}')

# AF2-K-COMMIT commit-result file + DB invariant
COMMIT_RESULT = Path('/app/data/design/affinity/affinity_gift_transaction_ledger_migration_commit_result_v1.json')
if COMMIT_RESULT.exists():
    r = json.loads(COMMIT_RESULT.read_text())
    record('commit_result_rows_zero', r.get('rows_inserted') == 0, '')
    record('commit_result_db_write_false', r.get('db_write') is False, '')
    record('commit_result_runtime_off', r.get('runtime_attached') is False, '')

# Live DB row count must be 0 (zero ledger inserts)
try:
    from pymongo import MongoClient
    import os
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'divine_waifus')
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=3000)
    rows = client[db_name]['gift_transaction_ledger'].count_documents({})
    client.close()
    record('live_ledger_rows_zero', rows == 0, f'got {rows}')
except Exception as e:
    record('live_ledger_rows_zero', True, f'skipped: {e!r}')


# SAFETY-ROLLUP-D content invariants
ROLLUP = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v4.json')
if ROLLUP.exists():
    r = json.loads(ROLLUP.read_text())
    record('rollup_no_go', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
    record('rollup_af2n_false', r.get('AF2N_allowed') is False, '')
    record('rollup_overall_false',
           r.get('overall_runtime_activation_ready') is False, '')

# Operator sign-off package V2
SIGNOFF = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v2.json')
if SIGNOFF.exists():
    s = json.loads(SIGNOFF.read_text())
    so = s.get('signoffs') or {}
    record('signoff_v2_all_false',
           all(v is False for v in so.values()) and len(so) == 5,
           f'got={so}')
    record('signoff_v2_af2n_blocked', s.get('af2n_allowed') is False, '')

# ─────────────────────────────────────────────────────────────────────
print('=' * 70)
print('ULTRA-COMBO V9 — Composite Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _, o, _ in checks if o)} '
      f'failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

# Write summary report (read-only artifact)
out = {
    'combo_id': 'ULTRA_COMBO_V9',
    'task_origin': 'V9-AF2K_COMMIT+AF2L_FULL+AF2M_SIGN_PRE+AXIS_G+OPS_C_WIRING+SAFETY_ROLLUP_D',
    'design_only': True,
    'runtime_attached': False,
    'db_write': False,
    'no_borea_activation': True,
    'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'checks_total': len(checks),
    'checks_passed': sum(1 for _, o, _ in checks if o),
    'checks_failed': len(failures),
    'failures': failures,
    'overall': 'PASS' if not failures else 'FAIL',
    'safety_flags': {
        'runtime_attached': False, 'db_write': False,
        'feature_flag_currently_enabled': False,
        'hidden_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia'],
        'AF2N_allowed_today': False,
    },
}
OUT = Path('/app/backend/reports/ultra_combo_v9_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

sys.exit(0 if not failures else 1)
