#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_reward_claim_ledger_design_v1.json')))
assert d.get('live_in_pack_93') is False
assert d.get('reward_live') is False
assert d.get('wallet_spend_ledger_live_in_pack_93') is True
assert d.get('wallet_spend_ledger_collection') == 'wallet_spend_ledger'
doc = os.path.join(R, d['design_doc']); assert os.path.exists(doc)
src = open(doc).read()
assert 'reward_claim_ledger' in src and 'idempotency_token' in src and 'AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE' in src
assert d.get('approval_string_proposed_for_live_execute') == 'AUTORIZZO_V110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE'
print('[v110 PACK_93_REWARD_CLAIM_LEDGER_DESIGN] OK design_doc_present pre_live_only wallet_spend_live_test_only')
