#!/usr/bin/env python3
"""v94 — Real formation integration validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v94_real_formation_integration_result_v1.json')
LOBBY = os.path.join(ROOT, 'frontend', 'app', 'pre-battle-lobby.tsx')

def fail(m): print(f"FAIL v94_real_formation_integration: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(R): fail(f"missing: {R}")
    if not os.path.isfile(LOBBY): fail(f"missing lobby")
    with open(R) as f: d = json.load(f)
    chain = d.get('source_resolution_chain') or []
    for v in ('saved_formation', 'local_cached_formation', 'safe_fallback_formation'):
        if v not in chain: fail(f"chain missing: {v}")
    saf = d.get('safety') or {}
    if saf.get('db_writes') != 0: fail("safety.db_writes must be 0")
    if saf.get('formation_mutation') is not False: fail("safety.formation_mutation must be false")
    # lobby must reference source label
    with open(LOBBY) as f: lobby = f.read()
    if 'resolvePlayerFormation' not in lobby: fail("lobby missing resolvePlayerFormation()")
    if 'source: ' not in lobby: fail("lobby must render team source label")
    print("PASS v94_real_formation_integration")

if __name__ == '__main__': main()
