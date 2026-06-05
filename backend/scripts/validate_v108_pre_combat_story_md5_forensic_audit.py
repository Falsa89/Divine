#!/usr/bin/env python3
import os,sys,json,hashlib
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_combat_story_md5_forensic_audit_v1.json')
d=json.load(open(p,encoding='utf-8'))
def md5(rel):
    h=hashlib.md5()
    with open(os.path.join(R,rel),'rb') as f:
        for c in iter(lambda:f.read(65536),b''): h.update(c)
    return h.hexdigest()
for key, rel in (('combat_tsx','frontend/app/combat.tsx'),('story_tsx','frontend/app/story.tsx'),('pre_battle_lobby_tsx','frontend/app/pre-battle-lobby.tsx')):
    sec=d.get(key) or {}
    if md5(rel)!=sec.get('new_md5',''): print(f'FAIL md5 mismatch {key}'); sys.exit(1)
    if len(sec.get('protecting_validators') or [])<2: print(f'FAIL prot list {key}'); sys.exit(1)
    if not sec.get('why_previously_protected') or not sec.get('why_approved_now') or not sec.get('rollback_plan'): print(f'FAIL fields {key}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','battle_engine_formula_rewrite'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre combat/story MD5 forensic audit'); sys.exit(0)
