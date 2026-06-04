#!/usr/bin/env python3
"""v93 — Team editor wiring validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v93_team_editor_wiring_audit_v1.json')
LOBBY = os.path.join(ROOT, 'frontend', 'app', 'pre-battle-lobby.tsx')
EDITOR = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'battle.tsx')

def fail(m): print(f"FAIL v93_team_editor_wiring: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(AUDIT): fail(f"missing: {AUDIT}")
    if not os.path.isfile(EDITOR): fail(f"missing target editor: {EDITOR}")
    with open(AUDIT) as f: data = json.load(f)
    if data.get('target_status') != 'PRESENT_AND_FUNCTIONAL': fail("target_status must be PRESENT_AND_FUNCTIONAL")
    if data.get('v93_decision') != 'WIRED_OK_NO_BLOCKER': fail("v93_decision must be WIRED_OK_NO_BLOCKER")
    with open(LOBBY) as f: lobby = f.read()
    if "router.push('/(tabs)/battle'" not in lobby: fail("Modify Team button must route to /(tabs)/battle")
    print("PASS v93_team_editor_wiring")

if __name__ == '__main__': main()
