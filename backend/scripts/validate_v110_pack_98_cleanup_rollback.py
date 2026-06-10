#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_cleanup_rollback_v1.json')))
assert d['refuse_by_default'] is True and d['requires_apply_flag']=='--apply'
assert d['requires_marker_match']=='pack_98_test_artifact=true'
for ks in ('REWARD_CLAIM_LEDGER_LIVE_ENABLED','DAILY_LOGIN_CLAIM_ENABLED','DAILY_QUEST_CLAIM_ENABLED'):
    assert ks in d['kill_switch_env_vars']
script=os.path.join(R,d['cleanup_script']); assert os.path.exists(script)
src=open(script).read()
assert '--apply' in src and 'pack_98_test_artifact' in src and '--reset-kill-switches' in src
print('[v110 PACK_98_CLEANUP_ROLLBACK] OK refuse_by_default 3_kill_switches_reset_supported')
