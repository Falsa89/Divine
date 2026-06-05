#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_route_menu_exposure_safety_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('new_player_facing_routes_exposed_v107c',-1)!=0: print('FAIL new routes'); sys.exit(1)
if d.get('new_menu_items_exposed_v107c',-1)!=0: print('FAIL menu items'); sys.exit(1)
if not d.get('hidden_intentional_routes_unchanged',False): print('FAIL hidden'); sys.exit(1)
if not d.get('alpha_menu_preview_unchanged',False): print('FAIL alpha-menu'); sys.exit(1)
if not d.get('qa_routes_not_promoted',False): print('FAIL qa_routes'); sys.exit(1)
if d.get('new_backend_routers_added_v107c',-1)!=1: print('FAIL new_backend_routers'); sys.exit(1)
if not d.get('new_backend_routers_are_runtime_infra',False): print('FAIL infra'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','new_route_exposure','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print('PASS \u2014 v107C route/menu exposure safety (0 player-facing, 1 infra probe router)'); sys.exit(0)
