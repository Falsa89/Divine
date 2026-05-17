#!/usr/bin/env python3
"""AF2-N-STAGE1-ROLLBACK-READINESS — Validator."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage1_rollback_readiness_result_v1.json')
STAGE1_SCRIPT = Path('/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py')
CANARY_ROLLBACK_SCRIPT = Path('/app/ops/rollback_af2n_canary.sh')
BACKUPS_DIR = Path('/app/backups')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_stage1_rollback_readiness_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-STAGE1-ROLLBACK-READINESS', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('db_write_false', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('primary_script_exists', STAGE1_SCRIPT.exists(), str(STAGE1_SCRIPT))
rec('fallback_script_exists', CANARY_ROLLBACK_SCRIPT.exists(), str(CANARY_ROLLBACK_SCRIPT))
rec('backup_path_present', isinstance(r.get('latest_backup_path'), str)
    and Path(r['latest_backup_path']).exists(), f"path={r.get('latest_backup_path')}")
rec('pre_stage1_backups', r.get('pre_stage1_backups_present') is True, '')
rec('dry_run_pass', (r.get('rollback_dry_run_result') or {}).get('verdict') == 'PASS', '')
rec('triggers_min_8', len(r.get('abort_triggers_that_would_force_rollback') or []) >= 8, '')
rec('procedure_min_5', len(r.get('rollback_procedure') or []) >= 5, '')
rec('rollback_not_executed', r.get('rollback_executed') is False, '')

# Live dry-run
try:
    p = subprocess.run(['python3', str(STAGE1_SCRIPT), '--dry-run'],
                       capture_output=True, text=True, timeout=15)
    rec('live_dry_run_exit_0', p.returncode == 0, f'rc={p.returncode}, out={p.stdout.strip()}')
except Exception as e:
    rec('live_dry_run_exit_0', False, repr(e))

sf = r.get('safety_flags') or {}
rec('sf_broad_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')

print('='*70); print('AF2-N-STAGE1-ROLLBACK-READINESS — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
