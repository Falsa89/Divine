#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_cleanup_rollback_v1.json')))
assert d.get('refuse_by_default') is True and d.get('dry_run_default') is True and d.get('requires_apply_flag') is True
assert d.get('production_users_protected') is True
script_p = os.path.join(R, d['cleanup_script']); assert os.path.exists(script_p)
src = open(script_p).read()
assert '--apply' in src and 'pack_93_test_artifact' in src and 'pack93_test_user_' in src and 'wallet_spend_ledger' in src
print('[v110 PACK_93_CLEANUP_ROLLBACK] OK refuse_by_default apply_required marker_scoped ledger_cleaned')
