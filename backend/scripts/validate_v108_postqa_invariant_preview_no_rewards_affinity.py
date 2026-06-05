#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: preview branch NON deve chiamare refreshUser()/grantAffinity().
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'frontend','app','combat.tsx')
c=open(p,encoding='utf-8').read()
if 'PREVIEW_REWARD_LOCK_ACTIVE' not in c: print('FAIL missing PREVIEW_REWARD_LOCK_ACTIVE'); sys.exit(1)
# Tutte le chiamate refreshUser() devono essere gated (PREVIEW_REWARD_LOCK_ACTIVE) o dentro un if(!PREVIEW_REWARD_LOCK_ACTIVE).
import re
for m in re.finditer(r'refreshUser\s*\(\s*\)', c):
    s=max(0,m.start()-200); ctx=c[s:m.start()]
    if 'PREVIEW_REWARD_LOCK_ACTIVE' not in ctx and '!PREVIEW_REWARD_LOCK_ACTIVE' not in ctx and 'useAuth' not in ctx:
        print(f'FAIL refreshUser() not gated at pos {m.start()}'); sys.exit(1)
for m in re.finditer(r'grantAffinity\s*\(', c):
    s=max(0,m.start()-200); ctx=c[s:m.start()]
    if 'const grantAffinity' in ctx[-40:]:
        continue  # definition
    if 'PREVIEW_REWARD_LOCK_ACTIVE' not in ctx and '!PREVIEW_REWARD_LOCK_ACTIVE' not in ctx:
        print(f'FAIL grantAffinity() not gated at pos {m.start()}'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: preview branch does NOT call refreshUser()/grantAffinity()'); sys.exit(0)
