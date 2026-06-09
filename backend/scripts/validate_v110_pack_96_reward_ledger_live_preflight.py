#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_reward_ledger_live_preflight_v1.json')))
assert d.get('collection') == 'reward_claim_ledger'
idx = d.get('index_strategy') or {}
assert idx.get('unique_index_fields') == ['user_id', 'server_id', 'idempotency_token']
assert idx.get('idempotent_creation') is True
assert idx.get('destructive_drop_disallowed') is True
assert d.get('kill_switch_default') is False
assert d.get('replay_safe') is True
assert d.get('no_production_grant_during_preflight') is True
src = open(os.path.join(R, 'backend/routes/reward_claim.py')).read()
assert 'ensure_reward_claim_ledger_indices' in src
assert 'create_index' in src and 'unique=True' in src
print('[v110 PACK_96_REWARD_LEDGER_LIVE_PREFLIGHT] OK unique_index_idempotent kill_switch_default_false replay_safe')
