#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_cleanup_rollback_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('dry_run_default') is True
assert d.get('requires_apply_flag') is True
assert d.get('production_users_protected') is True
script_p = os.path.join(R, d['cleanup_script']); assert os.path.exists(script_p)
src = open(script_p).read()
assert '--apply' in src and 'pack_92_test_artifact' in src and 'pack92_test_user_' in src
print('[v110 PACK_92_CLEANUP_ROLLBACK_STRATEGY] OK refuse_by_default dry_run apply_flag_required marker_scoped')
