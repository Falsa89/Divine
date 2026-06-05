#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: preview branch NON deve chiamare /api/battle/simulate.
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'frontend','app','combat.tsx')
c=open(p,encoding='utf-8').read()
if 'PREVIEW_REWARD_LOCK_ACTIVE' not in c: print('FAIL missing PREVIEW_REWARD_LOCK_ACTIVE token'); sys.exit(1)
# startBattle deve avere il guard PREVIEW_REWARD_LOCK_ACTIVE BEFORE la call a /api/battle/simulate.
m=re.search(r'const\s+startBattle\s*=\s*async\s*\(\)\s*=>\s*\{(.*?)/api/battle/simulate', c, re.DOTALL)
if not m: print('FAIL startBattle->simulate block not found'); sys.exit(1)
block=m.group(1)
if 'PREVIEW_REWARD_LOCK_ACTIVE' not in block: print('FAIL preview guard missing before /api/battle/simulate'); sys.exit(1)
if not re.search(r'if\s*\(\s*PREVIEW_REWARD_LOCK_ACTIVE', block): print('FAIL preview guard not in if-statement'); sys.exit(1)
if 'return' not in block.split('PREVIEW_REWARD_LOCK_ACTIVE',1)[1].split('/api/battle/simulate',1)[0]: print('FAIL early-return missing inside preview gate'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: preview branch does NOT call /api/battle/simulate'); sys.exit(0)
