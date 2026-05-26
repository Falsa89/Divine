#!/usr/bin/env python3
# FORGE_CRASH Track B — frontend crash-proofing + response normalization.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_b_response_normalization_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_FRONTEND_FORGE_CRASH_PROOFING_FIXED_SAFE'
    assert md5(F) == d['soul_forge_tsx_md5_post']
    t = F.read_text()
    # Helper present
    assert 'normalizeForgeResponse' in t, 'normalize helper missing'
    # Aliases accepted (at least gained_essence + gained + new_balance + balance)
    assert 'gained_essence' in t and 'essence_gained' in t and 'soul_essence_gained' in t
    assert 'new_balance' in t and 'new_soul_essence' in t
    # Double-submit guard
    assert 'if (forging) return;' in t, 'double submit guard missing'
    # Snapshot pattern
    assert 'heroIdsSnapshot' in t, 'snapshot of hero ids missing'
    # Visible error state
    assert 'forgeError' in t and 'setForgeError' in t, 'forgeError state missing'
    assert 'postSuccessWarn' in t and 'setPostSuccessWarn' in t, 'postSuccessWarn state missing'
    # Defensive balance render
    assert 'Number.isFinite(balance)' in t, 'defensive balance render missing'
    # Defensive result render
    assert 'Number(result.gained) || 0' in t, 'defensive result.gained render missing'
    assert 'Number(result.newBalance) || 0' in t, 'defensive result.newBalance render missing'
    # refreshUser wrapped in try/catch
    assert 'try {\n        await refreshUser();\n      } catch' in t, 'refreshUser must be wrapped in try/catch'
    # No reward formula changes
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    print('[PASS] FORGE_CRASH Track B frontend crash-proofing')
    return 0
if __name__ == '__main__': sys.exit(main())
