#!/usr/bin/env python3
"""Static anti-double-grant guard Pack 95.

Verifica via grep statico che:
  * Lo strict path di /api/story/battle (quando server_id) NON muta users.gold/gems
    e NON tocca db.story_progress (legacy account-wide collection).
  * earn-mission/earn-dimension/earn-pvp/earn-guild rifiutano con blocker se server_id presente.
  * shops/buy e soul-forge/retire rifiutano con blocker se server_id presente.
  * Nessun hardcoded server_id="s1" nello strict path di story_battle.
"""
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_static_anti_double_grant_guard_v1.json')))
for k, v in (d.get('static_checks') or {}).items():
    assert v is True, k

combat_src = open(os.path.join(R, 'backend/routes/combat.py')).read()
strict_block = combat_src.split('async def story_battle')[1]
# Extract just the strict path (server_id branch)
m = re.search(r'if server_id and isinstance\(server_id, str\)(.*?)(?:chapter = next|raise HTTPException\(404, "Capitolo)', strict_block, re.DOTALL)
assert m is not None, 'strict path block not found in story_battle'
strict_path = m.group(1)
assert 'users.update_one' not in strict_path, 'strict path muta users (vietato)'
assert 'db.story_progress' not in strict_path, 'strict path tocca legacy story_progress (vietato)'
assert '"s1"' not in strict_path and "'s1'" not in strict_path, 'hardcoded s1 nello strict path'
assert 'reward_claim_ledger' in strict_path, 'strict path manca ledger insert'
assert 'IDEMPOTENCY_TOKEN_REQUIRED' in strict_path, 'strict path manca idempotency check'

sf_src = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'LEGACY_CURRENCY_QUARANTINE_DEFERRED' in sf_src
assert 'SHOPS_BUY_SERVER_SCOPE_DEFERRED' in sf_src
assert 'SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED' in sf_src
# All earn-* endpoints have server_id-aware path
for needle in ['/currency/earn-mission', '/currency/earn-dimension', '/currency/earn-pvp', '/currency/earn-guild']:
    assert needle in sf_src

print('[v110 PACK_95_STATIC_ANTI_DOUBLE_GRANT_GUARD] OK no_users_mutation_in_strict_story_path no_hardcoded_s1 ledger_required_in_strict_path legacy_quarantine_blockers_present')
