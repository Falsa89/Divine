#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_route_exposure_safety_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('new_player_facing_routes_exposed_v107b',-1)!=0: print('FAIL \u2014 new player-facing routes != 0'); sys.exit(1)
if not d.get('hidden_intentional_routes_unchanged',False): print('FAIL \u2014 hidden routes must be unchanged'); sys.exit(1)
if not d.get('alpha_menu_preview_unchanged',False): print('FAIL \u2014 alpha-menu-preview must be unchanged'); sys.exit(1)
if not d.get('qa_routes_not_promoted',False): print('FAIL \u2014 qa routes must not be promoted'); sys.exit(1)
if d.get('battle_launch_endpoint_is_player_facing',True): print('FAIL \u2014 battle_launch_endpoint should be infra not player-facing'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','new_route_exposure','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print('PASS \u2014 v107B route exposure safety (0 new player-facing routes)'); sys.exit(0)
