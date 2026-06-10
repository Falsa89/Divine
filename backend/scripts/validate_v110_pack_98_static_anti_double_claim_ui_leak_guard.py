#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_static_anti_double_claim_ui_leak_guard_v1.json')))
for k,v in (d['static_checks']or{}).items():
    assert v is True, k
src=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
claim=src.split('async def daily_quest_claim(')[1].split('async def ')[0] if 'async def daily_quest_claim(' in src else src.split('async def daily_quest_claim(')[1]
assert 'db.users.update_one' not in claim
assert '"s1"' not in claim and "'s1'" not in claim
assert 'db.player_server_profiles.update_one' in claim
assert '_global_on' in claim and '_quest_on' in claim
assert 'DAILY_QUEST_COMPLETION_REQUIRED' in claim
assert 'pack_98_test_artifact' in claim
assert 'QUEST_ID_WHITELIST' in claim
assert claim.index('existing = await db[LEDGER_COLLECTION].find_one') < claim.index('grant_fn(db, uid, sid')
home_section=open(os.path.join(R,'frontend/src/components/DailyHomeRewardSection.tsx')).read()
assert 'DAILY_HOME_UI_ENABLED' in home_section and 'DAILY_HOME_UNLOCKED' in home_section
print('[v110 PACK_98_STATIC_ANTI_DOUBLE_CLAIM_UI_LEAK_GUARD] OK no_users_mutation no_hardcoded_s1 AND_kill_switches completion_proof_required home_AND_two_flags')
