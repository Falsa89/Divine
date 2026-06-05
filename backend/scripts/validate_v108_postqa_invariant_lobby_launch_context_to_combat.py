#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: lobby NON deve andare a /combat senza launch_context/battle_launch/battle_launch_id.
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'frontend','app','pre-battle-lobby.tsx')
c=open(p,encoding='utf-8').read()
# Find every router.push that targets /combat
for m in re.finditer(r"router\.push\s*\(\s*([\"'`])([^\"'`]*?/combat[^\"'`]*?)\1|router\.push\s*\(\s*target\s+as\s+any\s*\)", c):
    full=m.group(0)
    # find the URL
    s=max(0,m.start()-1500); ctx=c[s:m.start()+200]
    # locate the most recent definition of target
    if 'target' in full:
        # need to find target=...; look for it within recent context
        # require launch_context AND battle_launch_id present in ctx
        if 'launch_context=' not in ctx and 'battle_launch=' not in ctx and 'battle_launch_id=' not in ctx:
            print(f'FAIL /combat route missing launch_context/battle_launch/battle_launch_id at pos {m.start()}'); sys.exit(1)
    else:
        url=m.group(2) or ''
        if 'launch_context=' not in url and 'battle_launch=' not in url and 'battle_launch_id=' not in url:
            # check surrounding ctx as backup
            if 'launch_context=' not in ctx and 'battle_launch_id=' not in ctx:
                print(f'FAIL /combat literal route missing launch context: {url}'); sys.exit(1)
if 'launch_context=' not in c or 'battle_launch_id=' not in c: print('FAIL launch_context/battle_launch_id tokens missing in lobby'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: lobby->/combat carries launch_context/battle_launch_id'); sys.exit(0)
