#!/usr/bin/env python3
"""Pack 101 — Tower reward quarantine: nessuna source live tower nel registry."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
reg=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
# Nessuna source player-facing live per tower deve esistere
for forbidden in ['tower_claim_live','tower_battle_reward_live','tower_floor_reward_live']:
    assert forbidden not in reg, f'forbidden tower live source: {forbidden}'
# Confirm reward sources player-facing live limitate a daily_login + daily_quest
allowed=['daily_login_claim','daily_quest_completion_claim']
for src in allowed:
    assert src in reg, src
print('[v110 PACK_101_TOWER_REWARD_QUARANTINE] OK no_tower_live_source only_daily_login_and_daily_quest_live')
