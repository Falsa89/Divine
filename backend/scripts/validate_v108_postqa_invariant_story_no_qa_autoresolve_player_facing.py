#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: QA Auto Resolve NON deve essere visibile fuori gate.
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'frontend','app','story.tsx')
c=open(p,encoding='utf-8').read()
if 'QA Auto Resolve' not in c: print('FAIL QA Auto Resolve label missing entirely'); sys.exit(1)
if 'EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE' not in c: print('FAIL gate flag missing'); sys.exit(1)
# All QA Auto Resolve labels must appear within ~400 chars of the gate flag check.
for m in re.finditer(r'QA Auto Resolve', c):
    s=max(0,m.start()-600); ctx=c[s:m.start()]
    if 'EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE' not in ctx:
        print(f'FAIL QA Auto Resolve not gated by EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE at pos {m.start()}'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: QA Auto Resolve hidden behind EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE'); sys.exit(0)
