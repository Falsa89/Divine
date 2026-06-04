#!/usr/bin/env python3
"""v93 — Full 15-mode playability matrix validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MX = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v93_full_mode_playability_matrix_v1.json')
REQ_IDS = {'story', 'tower', 'arena', 'training', 'raid', 'event',
           'crepuscolo_dei_titani', 'assalto_del_ragnarok', 'guild_war', 'guild_raid',
           'server_boss', 'faction_boss', 'territory', 'war_avatar_mode', 'event_avatar_mode'}
REQ_FIELDS = {'mode_id', 'menu_path', 'source_path', 'lobby_path', 'team_source',
              'enemy_source', 'avatar_placeholder_status', 'battle_path',
              'expected_mobile_test', 'blocker', 'safety_flags', 'current_status'}

def fail(m): print(f"FAIL v93_full_mode_playability_matrix: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(MX): fail(f"missing matrix: {MX}")
    with open(MX) as f: data = json.load(f)
    if data.get('random_opponents_allowed') is not False: fail("random_opponents_allowed must be false")
    modes = data.get('modes') or []
    ids = {m.get('mode_id') for m in modes}
    miss = REQ_IDS - ids
    if miss: fail(f"missing mode_ids: {sorted(miss)}")
    for m in modes:
        for k in REQ_FIELDS:
            if k not in m: fail(f"mode {m.get('mode_id')} missing field: {k}")
        sf = m.get('safety_flags') or {}
        if sf.get('reward_live', False) is not False:
            fail(f"{m.get('mode_id')}.safety_flags.reward_live must be false")
    print("PASS v93_full_mode_playability_matrix")

if __name__ == '__main__': main()
