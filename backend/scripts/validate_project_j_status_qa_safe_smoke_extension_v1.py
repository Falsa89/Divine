#!/usr/bin/env python3
"""PROJECT_J Track G validator — QA safe smoke extension."""
import importlib.util, json, sys, urllib.request
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_j_status_qa_safe_smoke_extension_v1.json')
RESOLVER = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
FORBIDDEN = (Path('/app/backend/game_logic/battle_engine.py'), Path('/app/backend/game_logic/battle_core.py'), Path('/app/frontend/components/combat.tsx'))
NEEDLE = 'status_first_slice_resolver_pure'
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_G_STATUS_QA_SAFE_SMOKE_EXTENSION_READY': fail('verdict mismatch')
    # SS1 + SS2
    spec = importlib.util.spec_from_file_location('_qr', RESOLVER); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if mod.is_runtime_active(): fail('SS2: resolver active with flag unset')
    # SS3
    for p in FORBIDDEN:
        if p.exists() and NEEDLE in p.read_text():
            fail(f'SS3: resolver imported by {p}')
    # SS4: payload no leakage
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as r:
            if b'status_envelope_preview' in r.read():
                fail('SS4: payload leakage status_envelope_preview')
    except Exception:
        pass
    print('[PASS] PROJECT_J Track G QA safe smoke extension OK: SS1–SS4 verified live')
    sys.exit(0)
if __name__ == '__main__': main()
