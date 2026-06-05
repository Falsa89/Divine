#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: legacy mutation watchlist deve esistere e contenere endpoint chiave.
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','postqa','v108_postqa_legacy_mutation_watchlist_v1.json')
if not os.path.isfile(p): print('FAIL watchlist missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
eps=[e.get('endpoint') for e in (d.get('endpoints') or [])]
required=['/api/story/battle','/api/tower/battle','/api/pvp/battle','/api/events/battle','/api/raid/attack','/api/gvg/end-war','/api/friends/gift','/api/gacha/pull','/api/hero/gain-exp','/api/hero/levelup','/api/fusion/star-up','/api/shop/buy','/api/battlepass/buy-premium','/api/vip/add-spend','/api/mail/claim','/api/achievements/claim','/api/cosmetics/buy','/api/battle/simulate']
missing=[e for e in required if e not in eps]
if missing: print(f'FAIL watchlist missing endpoints: {missing}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('reward_grant','progress_live_write','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print(f'PASS — v108_POSTQA_A invariant: mutation watchlist complete ({len(eps)} endpoints)'); sys.exit(0)
