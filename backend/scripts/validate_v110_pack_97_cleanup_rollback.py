#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_cleanup_rollback_v1.json')))
assert d['refuse_by_default'] is True
assert d['requires_apply_flag'] == '--apply'
assert d['requires_marker_match'] == 'pack_97_test_artifact=true'
assert d['does_not_touch_production'] is True
assert d['kill_switches_reset_supported'] is True
for ks in ('REWARD_CLAIM_LEDGER_LIVE_ENABLED', 'DAILY_LOGIN_CLAIM_ENABLED'):
    assert ks in d['kill_switch_env_vars']
script_path = os.path.join(R, d['cleanup_script'])
assert os.path.exists(script_path)
src = open(script_path).read()
assert '--apply' in src and 'pack_97_test_artifact' in src and '--reset-kill-switches' in src
print('[v110 PACK_97_CLEANUP_ROLLBACK] OK refuse_by_default kill_switches_reset_supported')
