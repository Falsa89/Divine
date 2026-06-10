#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_reward_payload_guard_v1.json')))
assert d['fixed_reward_server_side'] == {'mission_coins': 10, 'honor': 5}
assert d['client_payload_ignored'] is True
assert d['no_pulls'] is True and d['no_hero_grants'] is True and d['no_equipment_grants'] is True
assert d['no_premium_or_hard_currency_grants'] is True
assert d['amount_cap_per_key'] == 100
import sys; sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import _grant_daily_login_to_psp, _PremiumGrantBlocked, _RewardTypeNotAllowed
out = _grant_daily_login_to_psp(None, 'uid', 'sid', {'gold': 999999})  # payload should be IGNORED
assert out == {'soft_currencies.mission_coins': 10, 'soft_currencies.honor': 5}, out
print('[v110 PACK_97_REWARD_PAYLOAD_GUARD] OK fixed_reward_server_side client_payload_ignored no_pulls no_hero no_equipment')
