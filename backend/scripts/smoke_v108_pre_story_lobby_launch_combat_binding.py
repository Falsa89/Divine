#!/usr/bin/env python3
"""Smoke statico + runtime per v108_pre: Story -> Lobby -> /api/battle/launch -> Combat.
Non scrive su DB, non concede ricompense, non muta progressi. Solo preview echo.
"""
import os, sys, json, urllib.request, urllib.error
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def read(p): return open(os.path.join(R,p),encoding='utf-8').read()

def check_static():
    errs=[]
    s=read('frontend/app/story.tsx')
    if '/pre-battle-lobby' not in s: errs.append('story.tsx: missing /pre-battle-lobby route')
    if 'Avvia battaglia' not in s: errs.append('story.tsx: missing Avvia battaglia label')
    if 'QA Auto Resolve' not in s: errs.append('story.tsx: missing QA Auto Resolve label')
    c=read('frontend/app/combat.tsx')
    if 'combatLaunchParser' not in c: errs.append('combat.tsx: missing combatLaunchParser import')
    if 'PREVIEW_NON_AUTHORITATIVE' not in c: errs.append('combat.tsx: missing PREVIEW_NON_AUTHORITATIVE label')
    l=read('frontend/app/pre-battle-lobby.tsx')
    for t in ('launchFromLobby','EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED','encounter_id','enemy_source_id'):
        if t not in l: errs.append(f'pre-battle-lobby.tsx: missing {t}')
    return errs

def check_runtime():
    errs=[]
    url='http://127.0.0.1:8001/api/battle/launch'
    payload={'server_id':'s1','mode':'story','encounter_id':'story_1_1','enemy_source_type':'authored','enemy_source_id':'story_1_1','player_team_snapshot':[],'client_trace_id':'v108_pre_smoke'}
    req=urllib.request.Request(url,data=json.dumps(payload).encode('utf-8'),headers={'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=10) as r:
            body=json.loads(r.read().decode('utf-8'))
        st=(body.get('response_status') or body.get('status') or '').upper()
        if 'PREVIEW' not in st and 'ECHO' not in st: errs.append(f'unexpected battle launch status: {st}')
    except Exception as e:
        errs.append(f'battle launch runtime error: {e}')
    return errs

def main():
    se=check_static(); re=check_runtime()
    out={'task':'smoke_v108_pre_story_lobby_launch_combat_binding','static_errors':se,'runtime_errors':re,'static_pass':not se,'runtime_pass':not re,'overall_pass':not se and not re}
    od=os.path.join(R,'data','design','battle_launch'); os.makedirs(od,exist_ok=True)
    op=os.path.join(od,'v108_pre_smoke_result_v1.json')
    open(op,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False))
    print(json.dumps(out,indent=2,ensure_ascii=False))
    return 0 if out['overall_pass'] else 1

if __name__=='__main__': sys.exit(main())
