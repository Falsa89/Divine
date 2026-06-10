#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_daily_home_unlock_sot_v1.json')))
assert d['both_flags_default']=='false' and d['and_logic_required_for_render'] is True
assert d['no_render_in_production_default'] is True
home=open(os.path.join(R,'frontend/app/(tabs)/home.tsx')).read()
assert 'DailyHomeRewardSection' in home
assert 'EXPO_PUBLIC_DAILY_HOME_UNLOCK' in open(os.path.join(R,'frontend/src/components/DailyHomeRewardSection.tsx')).read()
print('[v110 PACK_98_DAILY_HOME_UNLOCK_SOT] OK AND_two_flags default_off home_embedded')
