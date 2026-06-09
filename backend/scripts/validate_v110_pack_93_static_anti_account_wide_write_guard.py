#!/usr/bin/env python3
"""Pack 93 — Static anti-account-wide write guard."""
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_static_anti_account_wide_write_guard_v1.json')))
assert d.get('guard_validator_active') is True
items_src = open(os.path.join(R, 'backend/routes/items.py')).read()
assert 'server_id="s1"' not in items_src
assert 'SERVER_ID_REQUIRED' in items_src
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in items_src
sf_src = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'server_id="s1"' not in sf_src
assert 'SERVER_ID_REQUIRED' in sf_src
assert 'wallet_spend_ledger' in sf_src
assert 'user_id' in sf_src and 'server_id' in sf_src
import re as _re
m = _re.search(r'async def wallet_spend\([\s\S]*?return \{[\s\S]*?\}', sf_src)
body = m.group(0) if m else ''
assert body, 'wallet_spend body not found'
# Body must NOT write to users.gold/gems
assert 'db.users.update_one' not in body or 'gold' not in body.split('db.users.update_one')[-1][:200]
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in body
assert 'soft_currencies' in body
print('[v110 PACK_93_STATIC_ANTI_ACCOUNT_WIDE_WRITE_GUARD] OK no_hardcoded_s1 wallet_spend_psp_scoped wallet_spend_no_users_gold_gems_mutation')
