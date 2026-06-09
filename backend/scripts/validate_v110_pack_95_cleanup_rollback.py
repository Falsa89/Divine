#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_cleanup_rollback_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('requires_apply_flag') == '--apply'
assert d.get('requires_marker_match') == 'pack_95_test_artifact=true'
assert d.get('does_not_touch_production') is True
script_path = os.path.join(R, d['cleanup_script'])
assert os.path.exists(script_path)
src = open(script_path).read()
assert '--apply' in src and 'pack_95_test_artifact' in src
print('[v110 PACK_95_CLEANUP_ROLLBACK] OK refuse_by_default --apply_required marker_required_pack_95_test_artifact')
