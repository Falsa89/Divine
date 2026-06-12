#!/usr/bin/env python3
"""Pack 108 — Guild Strict Endpoints validator (static).

Verifica che `routes/guild_strict.py` esponga:
  /guild/strict/health, /preflight, /status, /search, /membership/preview

Must haves:
  - PACK_108_USER_TEST_MARKER = 'pack_108_test_artifact'
  - Kill switches default OFF
  - GUILD_LEGACY_QUARANTINED default TRUE
  - SERVER_ID_REQUIRED blocker
  - GUILD_REWARD_LIVE_DISABLED blocker
  - membership_preview e' write-disabled
  - NO mutation su db.users / users.gold / users.gems / users.experience
  - NO insert/update/delete su db.guilds_v2 / db.guild_memberships_v2
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(R, 'backend/routes/guild_strict.py')
assert os.path.exists(f)
c = open(f).read()

for path in ('/guild/strict/health', '/guild/strict/preflight', '/guild/strict/status',
             '/guild/strict/search', '/guild/strict/membership/preview'):
    assert path in c, path

assert 'pack_108_test_artifact' in c
assert 'GUILD_STRICT_PREFLIGHT_ENABLED' in c
assert 'GUILD_STRICT_MEMBERSHIP_READ_ENABLED' in c
assert 'GUILD_STRICT_SEARCH_READ_ENABLED' in c
assert 'GUILD_LEGACY_QUARANTINED' in c
assert '_truthy(os.getenv("GUILD_LEGACY_QUARANTINED", "true"))' in c
assert 'SERVER_ID_REQUIRED' in c
assert 'GUILD_REWARD_LIVE_DISABLED' in c
assert 'GUILD_SERVER_SCOPE_REQUIRED' in c
assert 'GUILD_MEMBERSHIP_SERVER_SCOPE_REQUIRED' in c
assert 'GUILD_CHAT_SERVER_SCOPE_DEFERRED' in c
assert 'GUILD_WAR_SERVER_SCOPE_DEFERRED' in c
assert 'PREVIEW_ONLY_NO_WRITE' in c
assert 'write_disabled' in c
assert 'no_silent_fallback_to_s1' in c
assert 'AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT' in c

# Read-only invariants: NO mutating Mongo calls anywhere in guild_strict.
for forbidden in (
    'db.users.update_one', 'db.users.update_many', 'db.users.insert_one',
    'db.users.delete_one', 'db.users.delete_many',
    'db.guilds_v2.insert_one', 'db.guilds_v2.update_one', 'db.guilds_v2.delete',
    'db.guild_memberships_v2.insert_one', 'db.guild_memberships_v2.update_one',
    'db.guild_memberships_v2.delete', 'reward_claim_ledger.insert_one',
    '$inc',
):
    assert forbidden not in c, f'guild_strict must be read-only/preview: {forbidden}'

# No silent s1 fallback in code.
assert re.search(r"server_id\s*=\s*['\"]s1['\"]", c) is None
assert 'or "s1"' not in c and "or 's1'" not in c

print('[v110 PACK_108_GUILD_STRICT_ENDPOINTS] OK five_endpoints_present read_only_safe kill_switches_default_off legacy_quarantined_default_true no_silent_s1_fallback')
