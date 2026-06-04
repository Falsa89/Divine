#!/usr/bin/env python3
"""
v98 — Bot Progression Runtime Dry-Run Simulator.
USAGE: python3 backend/scripts/simulate_v98_bot_progression_runtime.py [--days N]
No DB writes by default. Gated by V98_BOT_PROGRESSION_RUNTIME_ENABLED=true.
"""
import os, sys, json, random
from datetime import datetime, timedelta

ENABLED = os.getenv('V98_BOT_PROGRESSION_RUNTIME_ENABLED','false').lower()=='true'

ARCHETYPES = {
    'f2p_base':{'level_per_day':0.4,'gold_per_day':400,'gems_per_day':5,'pull_per_week':5},
    'f2p_active':{'level_per_day':2.0,'gold_per_day':800,'gems_per_day':15,'pull_per_week':20},
    'advanced_pull_bot':{'level_per_day':2.5,'gold_per_day':1100,'gems_per_day':30,'pull_per_week':35},
    'spender_like_controlled':{'level_per_day':2.8,'gold_per_day':1500,'gems_per_day':70,'pull_per_week':50},
    'whale_like_limited':{'level_per_day':3.2,'gold_per_day':2200,'gems_per_day':120,'pull_per_week':80}
}

def simulate(archetype, days, hard_cap=60):
    p = ARCHETYPES[archetype]
    state = {'archetype':archetype,'level':1,'gold':0,'gems':0,'pulls':0,'days_simulated':days}
    for _ in range(days):
        state['level'] = min(hard_cap, state['level'] + p['level_per_day'])
        state['gold'] += p['gold_per_day']
        state['gems'] += p['gems_per_day']
        state['pulls'] += int(p['pull_per_week']/7 + random.random()*0.5)
    state['level'] = int(state['level'])
    return state

def main():
    days = 7
    if '--days' in sys.argv:
        days = int(sys.argv[sys.argv.index('--days')+1])
    print(f'v98 bot progression runtime simulator (dry-run, days={days}, ENABLED={ENABLED})')
    print('---')
    results = {}
    for arch in ARCHETYPES:
        results[arch] = simulate(arch, days)
        s = results[arch]
        print(f"  {arch}: lvl={s['level']} gold={s['gold']} gems={s['gems']} pulls={s['pulls']}")
    print('---')
    print('DB writes during simulation: 0')
    print('Runtime apply: {}'.format('ENABLED' if ENABLED else 'GATED_DEFAULT_OFF (no DB mutation)'))
    return 0

if __name__ == '__main__': sys.exit(main())
