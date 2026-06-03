#!/usr/bin/env python3
"""v67 Track B — Story Runtime Preview Widening (screen) validator."""
from __future__ import annotations
import os, sys, json, re
ROOT='/app'
SCREEN=os.path.join(ROOT,'frontend/app/story-first-node-runtime-preview.tsx')
C=os.path.join(ROOT,'data/design/story/story_runtime_preview_widening_screen_contract_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_runtime_preview_widening_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/400_STORY_RUNTIME_PREVIEW_WIDENING.md')
F=[]
def f(m): F.append(m)
for p in (SCREEN,C,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(SCREEN):
    src=open(SCREEN).read()
    forbidden=[
        r"from\s+['\"](?:\.{1,2}/)?story['\"]",
        r"from\s+['\"](?:\.{1,2}/)?combat['\"]",
        r"from\s+['\"][^'\"]*battle_engine[^'\"]*['\"]",
        r"from\s+['\"]react-native-reanimated['\"]",
        r"from\s+['\"]@react-native-async-storage/async-storage['\"]",
    ]
    for pat in forbidden:
        if re.search(pat, src): f(f'screen forbidden import: {pat}')
    if 'fetch(' in src or 'axios' in src.lower(): f('screen contains fetch/axios')
    if '/api/story/battle' in src or '/api/battle/simulate' in src:
        f('screen references forbidden api')
    for nid in ('story_alpha_node_001','story_alpha_node_002','story_alpha_node_003'):
        if nid not in src: f(f'screen missing node id reference: {nid}')
    if 'node_id' not in src: f('screen missing node_id query param handling')
    if 'export default function' not in src and 'export default' not in src:
        f('screen no default export')
if os.path.exists(C):
    d=json.load(open(C))
    sn=d.get('supported_nodes') or []
    for nid in ('story_alpha_node_001','story_alpha_node_002','story_alpha_node_003'):
        if nid not in sn: f(f'screen contract supported_nodes missing {nid}')
    for k,v in (('deeplink_only',True),('public_menu_routed',False),
                ('imports_story_tsx',False),('imports_combat_tsx',False),
                ('imports_battle_engine',False),('uses_async_storage',False),
                ('uses_reanimated',False),('no_api_calls',True),('no_claim_button',True),
                ('text_language','italian'),('typescript_check','pass')):
        if d.get(k)!=v: f(f'screen contract {k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-RUNTIME-PREVIEW-WIDENING'); sys.exit(1)
print('[PASS] PROJECT-STORY-RUNTIME-PREVIEW-WIDENING'); sys.exit(0)
