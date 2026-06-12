#!/usr/bin/env python3
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, FORBIDDEN_REWARD_TYPES
# No new Pack 107 reward source registrata: il pack e' audit/guard-only.
pack_107_sources = [k for k, v in REWARD_SOURCE_REGISTRY.items() if v.get('pack_origin') == 'pack_107']
assert len(pack_107_sources) == 0, f'pack_107 must NOT introduce new reward sources, got: {pack_107_sources}'
assert 'gems' in FORBIDDEN_REWARD_TYPES
# Static check: competitive_guards.py non muta nulla
src = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()
for forbidden in ('db.users.update_one','db.users.insert_one','db.users.delete_one','db.player_server_profiles.update_one','$inc','reward_claim_ledger.insert_one'):
    assert forbidden not in src, f'competitive_guards must be read-only audit: {forbidden}'
print('[v110 PACK_107_DATA_INVARIANTS] OK no_new_reward_sources gems_forbidden competitive_guards_read_only_no_mutation')
