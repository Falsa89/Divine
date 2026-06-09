#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_cleanup_rollback_kill_switch_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('requires_apply_flag') == '--apply'
assert d.get('requires_marker_match') == 'pack_96_test_artifact=true'
assert d.get('does_not_touch_production') is True
assert d.get('kill_switch_env') == 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
script_path = os.path.join(R, d['cleanup_script'])
assert os.path.exists(script_path)
src = open(script_path).read()
assert '--apply' in src and 'pack_96_test_artifact' in src and 'reset-kill-switch' in src
print('[v110 PACK_96_CLEANUP_ROLLBACK_KILL_SWITCH] OK refuse_by_default apply_required kill_switch_reset_supported')
