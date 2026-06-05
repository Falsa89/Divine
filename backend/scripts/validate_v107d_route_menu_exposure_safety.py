#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107d_route_menu_exposure_safety_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
for k in ('new_player_facing_routes_exposed_v107d','new_menu_items_exposed_v107d','new_backend_routers_added_v107d'):
    if d.get(k,-1)!=0: print(f'FAIL {k}'); sys.exit(1)
for k in ('hidden_intentional_routes_unchanged','alpha_menu_preview_unchanged','qa_routes_not_promoted'):
    if not d.get(k,False): print(f'FAIL {k}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','new_route_exposure','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D route/menu exposure safety (0 changes)'); sys.exit(0)
