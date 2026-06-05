#!/usr/bin/env python3
# v108_POSTQA_A — Runtime invariant: generate_enemy_team() NON deve essere usato da player-facing simulate senza dev/QA gate.
import os,sys,re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
be=os.path.join(R,'backend','battle_engine.py')
c=open(be,encoding='utf-8').read()
# Find simulate_battle_endpoint scope, check if generate_enemy_team is called inside without gate.
import re
m=re.search(r'async def simulate_battle_endpoint\s*\(.*?\n\s+@router\.', c, re.DOTALL)
if not m:
    m=re.search(r'async def simulate_battle_endpoint\s*\(.*?\Z', c, re.DOTALL)
body=m.group(0) if m else ''
if re.search(r'generate_enemy_team\s*\(', body):
    if 'preview' not in body.lower() and 'dev_only' not in body.lower() and 'qa_only' not in body.lower():
        print('FAIL generate_enemy_team used in simulate_battle_endpoint without dev/QA gate'); sys.exit(1)
# Also check preview guard present.
if 'PREVIEW_SIMULATE_MUTATION_BLOCKED' not in c: print('FAIL preview guard token missing in battle_engine.py'); sys.exit(1)
print('PASS — v108_POSTQA_A invariant: no player-facing generate_enemy_team without gate; preview guard present'); sys.exit(0)
