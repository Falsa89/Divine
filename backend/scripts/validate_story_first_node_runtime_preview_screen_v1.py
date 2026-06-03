#!/usr/bin/env python3
"""v66 Track C — Story First Node Runtime Preview Screen validator (deeplink-only, no forbidden imports)."""
from __future__ import annotations
import os, sys, json, re
ROOT='/app'
SCREEN=os.path.join(ROOT,'frontend/app/story-first-node-runtime-preview.tsx')
C=os.path.join(ROOT,'data/design/story/story_first_node_runtime_preview_screen_contract_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_first_node_runtime_preview_screen_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/394_STORY_FIRST_NODE_RUNTIME_PREVIEW_SCREEN.md')
F=[]
def f(m): F.append(m)
for p in (SCREEN,C,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(SCREEN):
    src=open(SCREEN).read()
    # Forbidden imports (real import statements only)
    forbidden_imports=[
        r"from\s+['\"](?:\.{1,2}/)?story['\"]",
        r"from\s+['\"](?:\.{1,2}/)?combat['\"]",
        r"from\s+['\"](?:\.{1,2}/)?\./story\.tsx['\"]",
        r"from\s+['\"]@/story['\"]",
        r"from\s+['\"]@/combat['\"]",
        r"from\s+['\"][^'\"]*battle_engine[^'\"]*['\"]",
        r"from\s+['\"]react-native-reanimated['\"]",
        r"from\s+['\"]@react-native-async-storage/async-storage['\"]",
    ]
    for pat in forbidden_imports:
        if re.search(pat, src):
            f(f'screen forbidden import pattern matched: {pat}')
    # No API calls
    if 'fetch(' in src or 'axios' in src.lower():
        f('screen contains API call (fetch/axios)')
    if '/api/story/battle' in src or '/api/battle/simulate' in src:
        f('screen references forbidden api endpoint')
    # Must export default
    if 'export default function' not in src and 'export default' not in src:
        f('screen has no default export')
    # Must have at least one Text component (RN)
    if '<Text' not in src: f('screen has no <Text> element')
    # Must declare preview-only invariants
    for kw in ('PREVIEW ONLY','runtime_runner_payload_v1_draft','story_alpha_node_001'):
        if kw not in src: f(f'screen missing keyword: {kw}')
if os.path.exists(C):
    d=json.load(open(C))
    for k,v in (('deeplink_only',True),('public_menu_routed',False),
                ('imports_story_tsx',False),('imports_combat_tsx',False),
                ('imports_battle_engine',False),('uses_async_storage',False),
                ('uses_reanimated',False),('no_api_calls',True),
                ('db_writes',0)):
        if d.get(k)!=v: f(f'screen contract {k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN'); sys.exit(1)
print('[PASS] PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN'); sys.exit(0)
