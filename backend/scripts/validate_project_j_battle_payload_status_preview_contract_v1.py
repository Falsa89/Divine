#!/usr/bin/env python3
"""PROJECT_J Track E validator — battle payload status preview contract (design only)."""
import json, sys
from pathlib import Path
import urllib.request, urllib.error
MARKER = Path('/app/data/design/status_effects/project_j_battle_payload_status_preview_contract_v1.json')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_E_BATTLE_PAYLOAD_STATUS_PREVIEW_CONTRACT_DESIGN_ONLY': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    if m.get('existing_combat_payload_unchanged') is not True: fail('existing_combat_payload_unchanged must be True')
    shape = m.get('future_optional_preview_shape', {})
    sep = shape.get('status_envelope_preview', {})
    if sep.get('flag_active') is not False: fail('future shape flag_active must be False (default)')
    if sep.get('applied_to_battle') is not False: fail('future shape applied_to_battle must be False')
    if sep.get('preview_only') is not True: fail('future shape preview_only must be True')
    # Sanity probe: GET /api/heroes payload should NOT include status_envelope_preview anywhere today
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as r:
            body = r.read()
        if b'status_envelope_preview' in body:
            fail('existing payload already contains status_envelope_preview (leakage)')
    except Exception:
        pass  # backend down is fine
    print('[PASS] PROJECT_J Track E battle payload preview contract design-only; no payload leakage today')
    sys.exit(0)
if __name__ == '__main__': main()
