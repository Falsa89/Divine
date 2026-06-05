#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: initialize_bots/run_bot_cycle('default') NON deve essere attivo senza hard kill switch.
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend','server.py')
if not os.path.isfile(p):
    print('PASS (no server.py present)'); sys.exit(0)
c=open(p,encoding='utf-8').read()
bad_patterns=[r'initialize_bots\s*\(\s*[\"\']default[\"\']', r'run_bot_cycle\s*\(\s*[\"\']default[\"\']']
for bp in bad_patterns:
    for m in re.finditer(bp, c):
        s=max(0,m.start()-300); ctx=c[s:m.end()+200]
        # Check for a kill switch nearby (env flag, BOT_*_DISABLED, etc.)
        if not re.search(r'BOTS?_DISABLED|BOT_KILL_SWITCH|BOT_ENABLED\s*[!=]=|os\.environ.*BOT', ctx):
            print(f'FAIL bot default startup active without kill switch at pos {m.start()}'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: no unguarded bot default startup'); sys.exit(0)
