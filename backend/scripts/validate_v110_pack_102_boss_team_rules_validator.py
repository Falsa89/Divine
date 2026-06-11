#!/usr/bin/env python3
"""Pack 102 — Boss team rules: boss/major boss = team boss, leader rarity >= tier, mini-spike multipli di 5 non 10."""
import os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, 'backend'))
from data.tower_floor_catalog_v1 import TOWER_FLOOR_CATALOG_V1
for f in TOWER_FLOOR_CATALOG_V1:
    fid = f['floor']
    ftype = f['floor_type']
    team = f['enemy_team']
    assert len(team) == 6
    if fid in (50, 100):
        assert ftype == 'major_boss_team', f'floor {fid} should be major_boss_team'
        assert f['boss_leader_slot'] == 0
        assert team[0]['is_boss_leader'] is True
        assert team[0]['native_rarity'] >= 5
        if fid == 100:
            assert team[0]['native_rarity'] == 6
    elif fid % 10 == 0:
        assert ftype == 'boss_team', f'floor {fid} should be boss_team'
        assert f['boss_leader_slot'] == 0
        assert team[0]['is_boss_leader'] is True
        assert team[0]['native_rarity'] >= f['tier']
    elif fid % 5 == 0:
        assert ftype == 'mini_spike', f'floor {fid} should be mini_spike'
        assert f['boss_leader_slot'] is None
    else:
        assert ftype == 'normal', f'floor {fid} should be normal'
        assert f['boss_leader_slot'] is None
# Nessuna entry deve avere "boss_monster" o "raid_boss" o stringhe simili
# che indichino boss singolo
for f in TOWER_FLOOR_CATALOG_V1:
    for slot in f['enemy_team']:
        for forbidden_role in ['boss_monster','raid_boss','single_boss']:
            assert slot.get('role') != forbidden_role, f'floor {f["floor"]} has true boss monster'
print('[v110 PACK_102_BOSS_TEAM_RULES_VALIDATOR] OK boss_floors_have_leader major_boss_50_100 mini_spike_5_15_etc no_true_boss_monster')
