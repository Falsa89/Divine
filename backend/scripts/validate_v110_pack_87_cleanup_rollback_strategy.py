#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_cleanup_rollback_strategy_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('dry_run_default') is True
assert d.get('deletes_only_marked_pack_87_test_artifacts') is True
assert d.get('no_deletion_of_real_production_psp_or_user_heroes') is True
safety = d.get('production_safety', {})
for k in ('refuse_if_target_count_zero','refuse_if_no_explicit_apply_flag','refuse_if_target_appears_real_user','refuse_if_starter_marker_attached_to_real_user_heroes'):
    assert safety.get(k) is True, f'production_safety.{k} must be true'
script = os.path.join(R, d.get('cleanup_script', ''))
assert os.path.exists(script), f'cleanup script not found: {script}'
src = open(script).read()
assert '--apply' in src, 'cleanup script must require explicit --apply flag'
assert 'pack87_test_user_' in src, 'cleanup script must scope to pack87 test users'
assert 'server_scoped_starter_flow_pack_87' in src, 'cleanup script must reference creation_source marker'
print('[v110 PACK_87_CLEANUP_ROLLBACK_STRATEGY] OK refuse_by_default dry_run_default no_real_user_heroes_deletion script_exists_with_apply_flag')
