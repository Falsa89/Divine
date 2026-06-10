#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_daily_quest_endpoint_v1.json')))
assert d['endpoint']=='POST /api/daily-quest/claim'
assert d['both_kill_switches_default_off'] is True
assert d['and_logic_required_for_executable'] is True
assert d['completion_proof_required_for_real_users'] is True
assert d['completion_proof_blocker']=='DAILY_QUEST_COMPLETION_REQUIRED'
assert d['writes_only_to_psp_soft_currencies'] is True and d['writes_to_users_gold_gems'] is False
assert d['approval_received']=='AUTORIZZO_V110_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_PACK_98'
src=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
for n in ['REWARD_CLAIM_LEDGER_LIVE_DISABLED','DAILY_QUEST_CLAIM_DISABLED','PLAYER_SERVER_PROFILE_REQUIRED','DAILY_QUEST_COMPLETION_REQUIRED','TEST_COMPLETION_PROOF_FORBIDDEN_FOR_NON_TEST_USER','QUEST_ID_NOT_WHITELISTED','compute_quest_claim_key','partialFilterExpression','ux_user_server_claimkey_daily_quest_pack98','_slc_pack_98_daily_quest_claim','pack_98_test_artifact']:
    assert n in src, n
print('[v110 PACK_98_DAILY_QUEST_ENDPOINT] OK both_AND completion_proof_required marker_required quest_whitelist psp_only_write')
