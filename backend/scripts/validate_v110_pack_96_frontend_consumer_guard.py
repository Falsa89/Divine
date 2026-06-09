#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_frontend_consumer_guard_v1.json')))
assert d.get('frontend_claim_consumer_status') == 'NO_FRONTEND_UNLOCK_IN_PACK_96'
assert d.get('no_false_success_on_blocker') is True
assert d.get('no_silent_s1_for_claim_paths') is True
print('[v110 PACK_96_FRONTEND_CONSUMER_GUARD] OK no_frontend_unlock no_false_success no_silent_s1')
