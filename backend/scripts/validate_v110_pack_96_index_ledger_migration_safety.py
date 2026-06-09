#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_index_ledger_migration_safety_v1.json')))
assert d.get('collection') == 'reward_claim_ledger'
idxs = d.get('indices_managed') or []
u = next((x for x in idxs if x.get('unique')), None)
assert u is not None
assert u.get('fields') == ['user_id', 'server_id', 'idempotency_token']
assert u.get('idempotent_creation') is True
assert d.get('destructive_drop_disallowed') is True
assert d.get('no_force_drop_existing_index') is True
src = open(os.path.join(R, 'backend/routes/reward_claim.py')).read()
assert 'background=True' in src
assert 'drop_index' not in src and 'dropIndex' not in src
print('[v110 PACK_96_INDEX_LEDGER_MIGRATION_SAFETY] OK idempotent_create no_destructive_drop background_safe')
