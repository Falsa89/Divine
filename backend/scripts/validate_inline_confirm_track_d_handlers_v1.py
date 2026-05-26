#!/usr/bin/env python3
# INLINE_CONFIRM Track D — crash-proof event handlers.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_d_handlers_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_D_CRASH_PROOF_EVENT_HANDLERS_READY'
    t = F.read_text()
    # requestForge has try/catch
    assert 'const requestForge = () => {\n    try {' in t, 'requestForge missing top-level try/catch'
    # stale selection guard
    assert 'stillAvailable' in t and 'selezione non' in t.lower() or 'selezione non' in t, 'stale selection guard missing'
    # double-submit guard
    assert 'if (forging) return;' in t
    # normalizeForgeResponse preserved
    assert 'normalizeForgeResponse' in t
    # defensive renders preserved
    assert 'Number.isFinite(balance)' in t
    assert 'Number(result.gained) || 0' in t
    assert 'Number(result.newBalance) || 0' in t
    # snapshot pattern
    assert 'heroIdsSnapshot' in t
    # refreshUser wrapped in try/catch
    assert 'try {\n        await refreshUser();\n      } catch' in t
    print('[PASS] INLINE_CONFIRM Track D crash-proof handlers')
    return 0
if __name__ == '__main__': sys.exit(main())
