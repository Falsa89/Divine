#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_cleanup_rollback_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('dry_run_default') is True
assert d.get('requires_apply_flag') is True
assert d.get('deletes_only_marked_or_pattern_matching') is True
assert d.get('production_users_protected') is True
script_p = os.path.join(R, d['cleanup_script'])
assert os.path.exists(script_p)
src = open(script_p).read()
assert '--apply' in src
assert 'pack_91_test_artifact' in src
assert 'pack91_test_user_' in src
print('[v110 PACK_91_CLEANUP_ROLLBACK] OK refuse_by_default dry_run_default apply_flag_required marker_scoped')
