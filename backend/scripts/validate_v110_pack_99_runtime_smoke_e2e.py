#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_99_daily_quest_runtime_tracker_home_unlock/v110_pack_99_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'smoke result missing - run smoke first'
d=json.load(open(p))
assert d['real_smoke_executed'] is True
assert d['required_missing']==[]
assert d['no_premium_grant'] is True
assert d['no_double_daily_quest_reward'] is True
assert d['no_reward_live_general'] is True
assert d['no_reward_grant_on_completion'] is True
assert d['completion_via_tracker_enforced'] is True
assert d['client_cannot_fake_completion'] is True
assert d['release_readiness_claimed'] is False
for k in [
    'tracker_default_off_and_health_clean',
    'claim_blocked_before_tracker_completion',
    'tracker_complete_first_success',
    'no_reward_grant_on_completion_verified',
    'claim_after_tracker_completion_success',
    'tracker_state_transitioned_to_claimed',
    'replay_claim_no_double_grant',
    'tracker_complete_forbidden_for_non_test_user',
    'pack_97_daily_login_still_works',
    'pack_96_premium_block_preserved',
    'pack_95_story_strict_preserved',
    'pack_94_equipment_loader_preserved',
    'pack_93_wallet_split_preserved',
    'tracker_kill_switch_disable_re_blocks',
    'kill_switches_restored_to_original', 'cleanup_ok',
]:
    assert d['proofs'].get(k) is True, k
print('[v110 PACK_99_RUNTIME_SMOKE_E2E_VALIDATOR] OK tracker_enforced no_double no_premium pack_93_98_preserved cleanup')
