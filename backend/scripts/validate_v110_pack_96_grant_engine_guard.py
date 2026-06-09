#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_grant_engine_guard_v1.json')))
g = d.get('grant_engine_rules') or {}
assert 'player_server_profiles.soft_currencies.*' in (g.get('allowed_targets') or [])
assert 'users.gold' in (g.get('disallowed_targets') or [])
assert 'users.gems' in (g.get('disallowed_targets') or [])
assert g.get('premium_grants_pre_grant_block') is True
assert g.get('premium_blocker') == 'PREMIUM_GRANT_BLOCKED'
assert 'gems' in d.get('forbidden_reward_types')
assert d.get('no_hero_equipment_in_pack_96') is True
import sys; sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import _grant_soft_currency_to_psp, _PremiumGrantBlocked, _RewardTypeNotAllowed
try:
    _grant_soft_currency_to_psp(None, 'uid', 'sid', {'gems': 1})
    assert False, 'gems should be blocked'
except _PremiumGrantBlocked:
    pass
try:
    _grant_soft_currency_to_psp(None, 'uid', 'sid', {'gold': 999999})
    assert False, 'amount cap should block'
except _RewardTypeNotAllowed:
    pass
try:
    _grant_soft_currency_to_psp(None, 'uid', 'sid', {'unknown_currency': 1})
    assert False, 'unknown reward type should block'
except _RewardTypeNotAllowed:
    pass
print('[v110 PACK_96_GRANT_ENGINE_GUARD] OK premium_blocked amount_cap_enforced unknown_reward_blocked psp_only_target')
