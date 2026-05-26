#!/usr/bin/env python3
# INLINE_CONFIRM Track B — Modal/KAV removed from confirm path.
import json, sys, hashlib, re
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_b_modal_removed_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_MODAL_CONFIRM_PATH_REMOVED_SAFE'
    assert md5(F) == d['soul_forge_tsx_md5_post']
    t = F.read_text()
    # No Modal import from react-native
    # Look for the import block
    import_match = re.search(r"from 'react-native';", t)
    assert import_match, 'react-native import block missing'
    head = t[:import_match.end()]
    assert 'Modal' not in head, 'Modal still imported from react-native'
    assert 'KeyboardAvoidingView' not in head, 'KeyboardAvoidingView still imported'
    assert 'Platform' not in head, 'Platform still imported (no longer needed)'
    # No <Modal element
    assert '<Modal ' not in t and '<Modal\n' not in t and '<Modal>' not in t, '<Modal> element still rendered'
    # No KeyboardAvoidingView element
    assert '<KeyboardAvoidingView' not in t, '<KeyboardAvoidingView> still rendered'
    # No confirmOpen state
    assert 'setConfirmOpen' not in t, 'setConfirmOpen still referenced'
    assert 'useState(false)' in t  # sanity check that state pattern still works elsewhere
    print('[PASS] INLINE_CONFIRM Track B modal/KAV path removed')
    return 0
if __name__ == '__main__': sys.exit(main())
