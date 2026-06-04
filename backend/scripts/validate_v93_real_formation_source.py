#!/usr/bin/env python3
"""v93 — Real formation source validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v93_real_formation_source_audit_v1.json')
DOC = os.path.join(ROOT, 'docs', 'divine', '93_REAL_FORMATION_SOURCE_AND_TEAM_EDITOR_WIRING.md')
LOBBY = os.path.join(ROOT, 'frontend', 'app', 'pre-battle-lobby.tsx')

def fail(m): print(f"FAIL v93_real_formation_source: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(AUDIT): fail(f"missing audit: {AUDIT}")
    if not os.path.isfile(DOC): fail(f"missing doc: {DOC}")
    if not os.path.isfile(LOBBY): fail(f"missing lobby: {LOBBY}")
    with open(AUDIT) as f: data = json.load(f)
    impl = data.get('v93_implementation') or {}
    if not impl.get('ui_label_required'): fail("ui_label_required must be true")
    for v in ['saved_formation', 'local_cached_formation', 'safe_fallback_formation']:
        if v not in (impl.get('ui_label_values') or []):
            fail(f"audit ui_label_values missing {v}")
    if impl.get('writes_to_db') is not False: fail("writes_to_db must be false")
    with open(LOBBY) as f: lobby = f.read()
    for tok in ['resolvePlayerFormation', 'safe_fallback_formation', 'fallback_used']:
        if tok not in lobby: fail(f"lobby missing token: {tok}")
    # source label rendered
    if 'source: ' not in lobby: fail("lobby must render team source label")
    print("PASS v93_real_formation_source")

if __name__ == '__main__': main()
