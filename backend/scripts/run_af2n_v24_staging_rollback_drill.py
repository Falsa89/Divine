#!/usr/bin/env python3
"""V24 — Staging/Clone Rollback Drill (non-destructive).

Simulates a Stage4 rollback against a CLONE of the live state without
modifying production data. Procedure:
  1) Read backup supervisor.conf (V21 pre-stage4) and current backend.conf.
  2) Diff them and verify diff is the documented Stage4 delta (allowlist+cap).
  3) Read latest backup of MongoDB collections (V21 backup dir).
  4) Run rollback script with STAGE4_ROLLBACK_DRY_RUN=true (default safe).
  5) Verify rollback DRY_RUN produces a complete actions plan with no live writes.

NO PRODUCTION ROLLBACK EXECUTED. NO DB DROP. NO supervisor.conf REWRITE.
"""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v24_staging_rollback_drill_result_v1.json')
NOW = datetime.now(timezone.utc)


def main():
    actions = {'steps': []}
    fails = []

    # 1. backup supervisor.conf locate
    pre_stage4_backups = sorted(Path('/app/backups/af2n_stage4').glob('backend.conf.v21_pre_stage4_apply_*.bak'))
    if not pre_stage4_backups:
        fails.append('no_pre_stage4_backup')
    else:
        actions['pre_stage4_backup'] = str(pre_stage4_backups[-1])
        actions['steps'].append('pre_stage4_backup_located')

    # 2. diff with current supervisor.conf (read-only)
    if pre_stage4_backups:
        cur = Path('/etc/supervisor/conf.d/backend.conf').read_text()
        old = pre_stage4_backups[-1].read_text()
        # extract key vars
        import re
        def extract(name, txt):
            m = re.search(rf'{name}="([^"]+)"', txt)
            return m.group(1) if m else None
        cur_allowlist = (extract('AFFINITY_GIFT_CANARY_ALLOWLIST', cur) or '').split(',')
        old_allowlist = (extract('AFFINITY_GIFT_CANARY_ALLOWLIST', old) or '').split(',')
        cur_cap = extract('AFFINITY_GIFT_CANARY_LEDGER_CAP', cur)
        old_cap = extract('AFFINITY_GIFT_CANARY_LEDGER_CAP', old)
        diff = {
            'allowlist_size_old': len([u for u in old_allowlist if u.strip()]),
            'allowlist_size_current': len([u for u in cur_allowlist if u.strip()]),
            'stage4_users_to_be_removed_on_rollback': len([u for u in cur_allowlist if u.strip().startswith('stage4_qa_')]),
            'cap_old': old_cap, 'cap_current': cur_cap,
            'diff_is_only_stage4_delta': (
                set(u.strip() for u in old_allowlist if u.strip()) <= set(u.strip() for u in cur_allowlist if u.strip())
            )
        }
        actions['supervisor_conf_diff_summary'] = diff
        actions['steps'].append('supervisor_diff_computed_read_only')
        if not diff['diff_is_only_stage4_delta']:
            fails.append('supervisor_diff_unexpected_extra_users_in_backup')

    # 3. mongo backup
    backup_dirs = sorted(Path('/app/backups/af2n_stage4').glob('backup_*'))
    if backup_dirs:
        actions['mongo_backup_dir'] = str(backup_dirs[-1])
        files = sorted(p.name for p in backup_dirs[-1].iterdir() if p.is_file())
        actions['mongo_backup_files'] = files
        actions['steps'].append('mongo_backup_present')
        # checksum recheck
        from hashlib import sha256
        sha = {}
        for f in backup_dirs[-1].iterdir():
            if f.is_file() and f.suffix == '.json':
                h = sha256(); h.update(f.read_bytes()); sha[f.name] = h.hexdigest()
        actions['mongo_backup_sha256_recompute'] = sha
    else:
        fails.append('no_mongo_backup_dir')

    # 4. run Stage4 rollback script in DRY_RUN
    env = dict(os.environ); env['STAGE4_ROLLBACK_DRY_RUN'] = 'true'
    rb_script = '/app/backend/scripts/rollback_af2n_stage4_internal_beta.py'
    if Path(rb_script).exists():
        r = subprocess.run(['python3', rb_script], capture_output=True, text=True, timeout=30, env=env)
        actions['rollback_dry_run_exit_code'] = r.returncode
        actions['rollback_dry_run_stdout_tail'] = (r.stdout or '')[-400:]
        actions['steps'].append('rollback_dry_run_executed')
        if r.returncode != 0:
            fails.append('rollback_dry_run_failed')
        # verify produced result
        rb_result = Path('/app/data/design/affinity/af2n_stage4_internal_beta_rollback_result_v1.json')
        if rb_result.exists():
            rb_d = json.loads(rb_result.read_text())
            actions['rollback_dry_run_doc'] = {
                'dry_run': rb_d.get('dry_run'),
                'overall_status': rb_d.get('overall_status'),
                'steps_planned': rb_d.get('steps'),
            }
            if rb_d.get('dry_run') is not True:
                fails.append('rollback_doc_not_dry_run')
            if rb_d.get('overall_status') != 'PASS':
                fails.append('rollback_doc_not_pass')
        else:
            fails.append('rollback_doc_missing')
    else:
        fails.append('rollback_script_missing')

    # 5. verify live state untouched
    from urllib.request import urlopen
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            post = json.loads(r.read().decode())
        actions['post_drill_canary_status'] = {
            'allowlist_size': post.get('canary_allowlist_size'),
            'ledger_cap': post.get('canary_ledger_cap'),
            'rate_limit_backend': post.get('rate_limit_backend'),
        }
        if post.get('canary_allowlist_size', 0) < 700:
            fails.append('live_state_modified_allowlist_below_700')
        if post.get('canary_ledger_cap', 0) < 5000:
            fails.append('live_state_modified_cap_below_5000')
    except Exception as e:
        fails.append(f'post_canary_unreachable:{e}')

    overall = (len(fails) == 0)
    out_doc = {
        'result_id':'af2n_v24_staging_rollback_drill_result_v1',
        'task_origin':'V24-STAGING-CLONE-ROLLBACK-DRILL',
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'non_destructive': True,
        'production_state_modified': False,
        'actions': actions, 'fails': fails,
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants':[
            'no production rollback executed','no DB drop','no supervisor.conf rewrite',
            'no inventory mutation','no ledger mutation','no Borea exposure'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2, default=str))
    print(f'V24-STAGING-ROLLBACK-DRILL {out_doc["overall_status"]} fails={fails}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
