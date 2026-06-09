#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_story_progress_write_strict_v1.json')))
assert d.get('endpoint') == 'POST /api/story/battle'
assert d.get('server_id_required_for_strict_write') is True
assert d.get('idempotency_token_required') is True
assert d.get('writes_to_users_story_progress_when_server_id') is False
assert d.get('grants_user_gold_gems_when_server_id') is False
assert d.get('replay_idempotent') is True
assert d.get('approval_received') == 'AUTORIZZO_V110_REWARD_LEDGER_STORY_WRITE_LEGACY_GUARDS_TEST_ONLY_PACK_95'
src = open(os.path.join(R, 'backend/routes/combat.py')).read()
strict = src.split('async def story_battle')[1].split('async def')[0]
assert 'pack_95_strict_story_progress_write' in strict
assert 'reward_claim_ledger' in strict
assert 'IDEMPOTENCY_TOKEN_REQUIRED' in strict
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in strict
assert 'player_server_profiles' in strict and 'story_progress' in strict
# strict path block: extract only the `if server_id ...` branch body
import re as _re
m = _re.search(r'if server_id and isinstance\(server_id, str\)(.*?)\n        chapter = next\(', strict, _re.DOTALL)
assert m is not None, 'strict path block not found'
strict_block = m.group(1)
# Strict path MUST NOT mutate users.gold/gems and MUST NOT write to legacy db.story_progress
assert 'db.users.update_one' not in strict_block, 'strict path mutates users (vietato)'
assert 'db.story_progress' not in strict_block, 'strict path tocca legacy story_progress (vietato)'
assert '"s1"' not in strict_block and "'s1'" not in strict_block, 'hardcoded s1 nello strict path'
print('[v110 PACK_95_STORY_PROGRESS_WRITE_STRICT] OK strict_server_scope idempotency_required no_users_gold_gems_grant no_users_story_progress')
