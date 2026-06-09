#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_legacy_claim_bridge_guards_v1.json')))
for entry in d.get('legacy_paths_preserved') or []:
    assert entry.get('endpoint')
assert d.get('no_legacy_bypass_without_ledger') is True
assert d.get('all_new_grants_must_route_via_rewards_claim_endpoint') is True
sf = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'LEGACY_CURRENCY_QUARANTINE_DEFERRED' in sf
assert 'SHOPS_BUY_SERVER_SCOPE_DEFERRED' in sf
assert 'SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED' in sf
combat = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert 'pack_95_strict_story_progress_write' in combat
print('[v110 PACK_96_LEGACY_CLAIM_BRIDGE_GUARDS] OK pack_94_95_legacy_quarantine_preserved no_bypass_without_ledger')
