#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_backup_rollback_preflight_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('dry_run_default') is True
assert d.get('no_irreversible_changes_in_this_pack') is True
script = os.path.join(R, d.get('cleanup_script', ''))
assert os.path.exists(script), f'cleanup script not found: {script}'
src = open(script).read()
assert '--apply' in src
assert 'pack89_test_user_' in src
print('[v110 PACK_89_BACKUP_ROLLBACK_PREFLIGHT] OK refuse_by_default dry_run_default no_irreversible_changes script_exists')
