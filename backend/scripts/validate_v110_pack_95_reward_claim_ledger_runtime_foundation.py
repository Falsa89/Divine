#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_reward_claim_ledger_runtime_foundation_v1.json')))
assert d.get('collection') == 'reward_claim_ledger'
assert 'user_id' in d.get('idempotency_key_fields') and 'server_id' in d.get('idempotency_key_fields') and 'idempotency_token' in d.get('idempotency_key_fields')
assert d.get('replay_safe') is True
assert d.get('no_double_grant') is True
assert d.get('no_reward_live_by_default') is True
src = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert 'reward_claim_ledger' in src
assert '_slc_pack_95_reward_claim_ledger' in src
assert '_slc_pack_95_no_live_grant' in src
print('[v110 PACK_95_REWARD_CLAIM_LEDGER_RUNTIME_FOUNDATION] OK collection_present idempotency_check replay_safe no_live_grant')
