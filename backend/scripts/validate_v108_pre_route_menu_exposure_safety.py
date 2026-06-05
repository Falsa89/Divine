#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_route_menu_exposure_safety_v1.json')
d=json.load(open(p,encoding='utf-8'))
for k in ('new_qa_routes_exposed_as_production','new_player_facing_routes_exposed_v108_pre','new_menu_items_exposed_v108_pre','new_backend_routers_added_v108_pre'):
    if d.get(k,-1)!=0: print(f'FAIL {k}'); sys.exit(1)
for k in ('story_flow_is_preview_non_authoritative','auto_resolve_visible_is_labeled_qa','hidden_intentional_routes_unchanged','alpha_menu_preview_unchanged','qa_routes_not_promoted'):
    if not d.get(k,False): print(f'FAIL {k}'); sys.exit(1)
if d.get('hidden_preview_warning_present',True): print('FAIL hidden warning'); sys.exit(1)
if d.get('confusing_production_claim_present',True): print('FAIL confusing claim'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','new_route_exposure','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre route/menu exposure safety (0 changes, story preview gated, QA labeled)'); sys.exit(0)
