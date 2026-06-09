#!/usr/bin/env python3
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_frontend_static_regression_guard_v1.json')))
assert d.get('guard_active') is True
# Actually do the grep
fe = os.path.join(R, 'frontend')
bad = []
for dp, _, files in os.walk(fe):
    if 'node_modules' in dp: continue
    for fn in files:
        if not fn.endswith(('.ts','.tsx','.js','.jsx')): continue
        try:
            txt = open(os.path.join(dp,fn)).read()
        except Exception:
            continue
        # Look for buy/use-exp mutation calls
        for pat in (r"/api/item-shop/buy", r"/api/inventory/use-exp"):
            for m in re.finditer(pat + r"[^?'\"`)]*['\"`)]", txt):
                snippet = m.group(0)
                # If the URL ends without ?server_id=... it's a violation
                if 'server_id' not in snippet:
                    bad.append((os.path.relpath(os.path.join(dp,fn), R), snippet))
assert not bad, f'frontend mutation callers missing server_id: {bad}'
# Also assert no naive silent 's1' literal in frontend api urls
for dp, _, files in os.walk(fe):
    if 'node_modules' in dp: continue
    for fn in files:
        if not fn.endswith(('.ts','.tsx','.js','.jsx')): continue
        try:
            txt = open(os.path.join(dp,fn)).read()
        except Exception:
            continue
        assert 'server_id=s1' not in txt, f'silent s1 literal in {os.path.join(dp,fn)}'
print('[v110 PACK_91_FRONTEND_STATIC_REGRESSION_GUARD] OK zero_callers_missing_server_id zero_silent_s1_literal')
