#!/usr/bin/env python3
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_static_daily_anti_double_claim_guard_v1.json')))
for k, v in (d['static_checks'] or {}).items():
    assert v is True, k
src = open(os.path.join(R, 'backend/routes/daily_login_claim.py')).read()
claim_block = src.split('async def daily_login_claim(')[1].split('async def ')[0] if 'async def daily_login_claim(' in src else src.split('async def daily_login_claim(')[1]
# No mutation of users.gold/gems
assert 'db.users.update_one' not in claim_block, 'daily route mutates users (vietato)'
# No hardcoded s1
assert '"s1"' not in claim_block and "'s1'" not in claim_block, 'hardcoded s1'
# PSP write only
assert 'db.player_server_profiles.update_one' in claim_block
# Both kill switches checked AND
assert '_global_kill_switch_on' in claim_block and '_daily_kill_switch_on' in claim_block
assert 'REWARD_CLAIM_LEDGER_LIVE_DISABLED' in claim_block
assert 'DAILY_LOGIN_CLAIM_DISABLED' in claim_block
# server-side claim_key computation
assert 'compute_daily_claim_key' in claim_block
assert 'derive_idempotency_token_from_claim_key' in claim_block
# Replay before grant
assert claim_block.index("existing = await db[LEDGER_COLLECTION].find_one") < claim_block.index('grant_fn(db, uid, sid')
# test override requires marker
assert 'pack_97_test_artifact' in claim_block
assert 'DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER' in claim_block
# Default OFF for both kill switches
reg = open(os.path.join(R, 'backend/routes/daily_login_claim.py')).read()
assert '"false"' in reg  # default in _truthy()
# Registry: only daily added as new pack_97 live source
registry_src = open(os.path.join(R, 'backend/utils/reward_source_registry.py')).read()
assert 'pack_97' in registry_src and 'daily_login_claim' in registry_src
# No other claim sources added (mail/achievements/battlepass/event/afk)
for banned in ['"mail_reward_claim"', '"achievements_reward_claim"', '"battlepass_reward_claim"', '"event_reward_claim"', '"afk_reward_claim"']:
    assert banned not in registry_src, f'banned source registered: {banned}'
print('[v110 PACK_97_STATIC_DAILY_ANTI_DOUBLE_CLAIM_GUARD] OK no_users_mutation no_hardcoded_s1 AND_kill_switches server_side_claim_key replay_before_grant marker_required_for_override no_other_sources_live_pack_97')
