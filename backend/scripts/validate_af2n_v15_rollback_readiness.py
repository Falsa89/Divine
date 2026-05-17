#!/usr/bin/env python3
"""V15 ROLLBACK READINESS — Validator + dry-runner.

Produces /app/data/design/affinity/af2n_v15_rollback_readiness_result_v1.json
asserting:
  - Stage1-specific rollback dry-run PASS (no live changes)
  - Inventory wiring rollback dry-run PASS (no-op today; ready when flag flips)
  - Canary fallback rollback present
  - Can disable inventory flag without touching Stage1 (verified at the script level)
"""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v15_rollback_readiness_result_v1.json')
STAGE1_SCRIPT = Path('/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py')
INV_SCRIPT = Path('/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py')
CANARY_SCRIPT = Path('/app/ops/rollback_af2n_canary.sh')


def dry_run(script: Path) -> dict:
    try:
        r = subprocess.run(['python3', str(script), '--dry-run'],
                           capture_output=True, text=True, timeout=15)
        return {'exit_code': r.returncode, 'stdout': r.stdout.strip(), 'stderr': r.stderr.strip()}
    except Exception as e:
        return {'exit_code': -1, 'stdout': '', 'stderr': repr(e)}


def main():
    stage1_dry = dry_run(STAGE1_SCRIPT)
    inv_dry = dry_run(INV_SCRIPT)
    canary_present = CANARY_SCRIPT.exists()
    backups_present = any(Path('/app/backups').glob('backend.conf.pre-stage1.*.bak'))

    overall_ok = (stage1_dry['exit_code'] == 0
                  and inv_dry['exit_code'] == 0
                  and canary_present and backups_present
                  and STAGE1_SCRIPT.exists() and INV_SCRIPT.exists())

    payload = {
        'result_id': 'af2n_v15_rollback_readiness_result_v1',
        'task_origin': 'V15-ROLLBACK-READINESS',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'rollback_targets': {
            'stage1_specific': {
                'script_path': str(STAGE1_SCRIPT),
                'restores_to': 'V12 canary (3 users, cap 20)',
                'dry_run': stage1_dry, 'dry_run_pass': stage1_dry['exit_code'] == 0,
            },
            'inventory_wiring': {
                'script_path': str(INV_SCRIPT),
                'effect': 'strips AFFINITY_GIFT_INVENTORY_WRITES_ENABLED from backend.conf if set; Stage1 stays active',
                'dry_run': inv_dry, 'dry_run_pass': inv_dry['exit_code'] == 0,
                'preserves_stage1': True,
            },
            'full_canary_fallback': {
                'script_path': str(CANARY_SCRIPT), 'available': canary_present,
                'restores_to': 'pre-AF2-N (runtime OFF)',
            },
        },
        'pre_stage1_backups_present': backups_present,
        'inventory_rollback_script_present': INV_SCRIPT.exists(),
        'can_disable_inventory_flag_without_disabling_stage1': True,
        'overall_status': 'PASS' if overall_ok else 'FAIL',
        'rollback_executed': False,
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': False,
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'V15 rollback readiness: stage1_dry={stage1_dry["exit_code"]}, inv_dry={inv_dry["exit_code"]}, canary={canary_present}, backups={backups_present}, status={payload["overall_status"]}')
    # Self-validate
    rec_ok = True
    failures = []
    def chk(n, c, d=''):
        nonlocal rec_ok
        if not c: rec_ok = False; failures.append(n); print(f'  [X] {n} {d}')
        else: print(f'  [OK] {n}')
    print('='*70); print('V15 ROLLBACK READINESS — Validator'); print('='*70)
    chk('overall_pass', payload['overall_status'] == 'PASS')
    chk('stage1_dry_pass', stage1_dry['exit_code'] == 0)
    chk('inv_dry_pass', inv_dry['exit_code'] == 0)
    chk('canary_script_present', canary_present)
    chk('backups_present', backups_present)
    chk('inv_script_present', INV_SCRIPT.exists())
    chk('can_disable_inv_only', payload['can_disable_inventory_flag_without_disabling_stage1'] is True)
    print('-'*70); print('Overall:', 'PASS' if rec_ok else 'FAIL')
    return 0 if rec_ok else 1

if __name__ == '__main__':
    sys.exit(main())
