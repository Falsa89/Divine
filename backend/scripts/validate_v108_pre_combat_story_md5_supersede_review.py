#!/usr/bin/env python3
import os,sys,json,hashlib
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_combat_story_md5_supersede_review_v1.json')
d=json.load(open(p,encoding='utf-8'))
def md5(rel):
    h=hashlib.md5()
    with open(os.path.join(R,rel),'rb') as f:
        for c in iter(lambda:f.read(65536),b''): h.update(c)
    return h.hexdigest()
for key, rel in (('combat_tsx','frontend/app/combat.tsx'),('story_tsx','frontend/app/story.tsx'),('pre_battle_lobby_tsx','frontend/app/pre-battle-lobby.tsx')):
    sec=d.get(key) or {}
    if not sec.get('superseded',False): print(f'FAIL superseded {key}'); sys.exit(1)
    if sec.get('silent_overwrite',True): print(f'FAIL silent_overwrite {key}'); sys.exit(1)
    hrs=sec.get('historical_references') or []
    if len(hrs)<1: print(f'FAIL no historical {key}'); sys.exit(1)
    if md5(rel)!=sec.get('new_md5',''): print(f'FAIL md5 mismatch {key}'); sys.exit(1)
v100=json.load(open(os.path.join(R,'data/design/closed_alpha/v100_runtime_md5_baseline_v1.json'),encoding='utf-8'))
for f in ('frontend/app/combat.tsx','frontend/app/story.tsx','frontend/app/pre-battle-lobby.tsx'):
    if f not in (v100.get('files') or {}): print(f'FAIL v100 missing {f}'); sys.exit(1)
    if not (v100['files'][f].get('historical_references') or []): print(f'FAIL v100 no hist {f}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','silent_overwrite'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
if not saf.get('old_hash_preserved_as_historical_reference',False): print('FAIL old_hash_preserved'); sys.exit(1)
print('PASS — v108_pre combat/story MD5 supersede review'); sys.exit(0)
