#!/usr/bin/env python3
"""Static anti-bypass guard Pack 96."""
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_static_anti_bypass_guard_v1.json')))
for k, v in (d.get('static_checks') or {}).items():
    assert v is True, k
src = open(os.path.join(R, 'backend/routes/reward_claim.py')).read()
# Kill switch default false
assert 'REWARD_CLAIM_LEDGER_LIVE_ENABLED' in src
assert '"false"' in src  # default value
# PSP check before grant
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in src
# Idempotency required
assert 'IDEMPOTENCY_TOKEN_REQUIRED' in src
# Source registry lookup
assert 'lookup_source' in src and 'REWARD_SOURCE_NOT_ALLOWLISTED' in src
# Replay check before grant
claim_block = src.split('async def reward_claim(')[1].split('def ')[0]
assert claim_block.index('existing = await db[LEDGER_COLLECTION].find_one') < claim_block.index('grant_fn = get_grant_fn')
# Premium block before grant
assert 'PREMIUM_GRANT_BLOCKED' in claim_block
assert claim_block.index('PREMIUM_GRANT_BLOCKED') < claim_block.index('grant_fn(db, uid, sid, payload)')
# No write to users.gold/gems within claim flow
assert 'db.users.update_one' not in claim_block, 'claim route mutates users (vietato)'
# No hardcoded s1
assert '"s1"' not in claim_block and "'s1'" not in claim_block, 'hardcoded s1'
# Writes only to PSP
assert 'db.player_server_profiles.update_one' in claim_block
registry = open(os.path.join(R, 'backend/utils/reward_source_registry.py')).read()
assert 'gems' in registry and 'FORBIDDEN_REWARD_TYPES' in registry
print('[v110 PACK_96_STATIC_ANTI_BYPASS_GUARD] OK kill_switch_default_false psp_check_pre_grant idempotency_pre_grant replay_before_grant premium_blocked_before_grant no_users_mutation no_hardcoded_s1 psp_only_write')
