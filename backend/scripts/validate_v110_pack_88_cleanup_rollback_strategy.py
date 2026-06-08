#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_cleanup_rollback_strategy_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('dry_run_default') is True
assert d.get('deletes_only_marked_pack_88_test_artifacts') is True
assert d.get('no_deletion_of_real_production_data') is True
safety = d.get('production_safety', {})
for k in ('refuse_if_target_count_zero','refuse_if_no_explicit_apply_flag','refuse_if_target_appears_real_user'):
    assert safety.get(k) is True
script = os.path.join(R, d.get('cleanup_script', ''))
assert os.path.exists(script), f'cleanup script not found: {script}'
src = open(script).read()
assert '--apply' in src
assert 'pack88_test_user_' in src
print('[v110 PACK_88_CLEANUP_ROLLBACK_STRATEGY] OK refuse_by_default dry_run_default no_real_data_deletion script_exists_with_apply')
