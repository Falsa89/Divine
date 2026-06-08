#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
s = d.get('canonical_fresh_start_sot', {})
stmt = s.get('statement', '')
for must in ('nuovo server', 'iniziare il gioco da ZERO'):
    assert must in stmt, f'SOT missing token: {must}'
fs = s.get('fresh_start_schema', {})
assert fs.get('player_level') == 1
assert fs.get('player_exp') == 0
for must in ('roster','team_formation','story_progress','soft_currencies','onboarding_state'):
    assert must in fs, f'fresh_start_schema missing: {must}'
forbidden = s.get('forbidden_S1_to_S2_copy', [])
for must in ('roster','user_heroes','player_level','player_exp','team','story_progress','inventory','equipment'):
    assert must in forbidden, f'forbidden_S1_to_S2_copy missing: {must}'
print('[v110 PACK_85_CANONICAL_FRESH_START_SOT] OK statement_complete fresh_schema_level=1_exp=0 forbidden_S1_to_S2_copy_complete')
