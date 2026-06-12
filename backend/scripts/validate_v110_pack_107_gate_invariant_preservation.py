#!/usr/bin/env python3
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY
# Tutte le source da Pack 95 a Pack 106 ancora live.
for s in ('qa_controlled_soft_currency_claim','daily_login_claim','daily_quest_completion_claim','tower_floor_completion_claim','shop_buy_strict_claim','soul_forge_retire_strict_claim','equipment_equip_strict_claim','equipment_unequip_strict_claim','equipment_upgrade_strict_claim','forge_craft_strict_claim','equipment_fusion_strict_claim','mail_claim_controlled','achievement_claim_controlled','daily_weekly_reward_claim'):
    assert s in REWARD_SOURCE_REGISTRY, f'pack <= 106 source removed: {s}'
    assert REWARD_SOURCE_REGISTRY[s]['live'] is True
for f in ('backend/routes/tower_strict.py','backend/routes/economy_strict.py','backend/routes/controlled_rewards.py','backend/routes/competitive_guards.py','backend/routes/combat.py','backend/routes/daily_quest_claim.py'):
    assert os.path.exists(os.path.join(R, f)), f'route missing: {f}'
print('[v110 PACK_107_GATE_INVARIANT_PRESERVATION] OK pack_95_to_106_sources_preserved pack_101_to_106_routes_preserved')
