#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track C validator (artifacts redirect).
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_c_artifact_lock_v1.json')
F = Path('/app/frontend/app/artifacts.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_C_ARTIFACT_CONSTELLATION_SURFACE_LOCKED_TO_PREVIEW_SAFE'
    assert d['strategy'] == 'redirect_to_safe_preview'
    assert d['redirect_target'] == '/artifacts-preview'
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    pr = d['product_rule_check']
    assert pr['artifact_remains_account_wide_collection'] is True
    assert pr['artifact_not_equipment'] is True
    assert pr['artifact_not_divine_weapon'] is True
    text = F.read_text()
    # Verifica che il file ora sia un redirect-only screen (nessuna chiamata live)
    forbidden = ['/api/artifacts/pull', '/api/artifacts/fuse', '/api/constellations/pull', '/api/constellations/equip']
    for tok in forbidden:
        assert tok not in text, f'forbidden token {tok} still in artifacts.tsx'
    assert "router.replace('/artifacts-preview')" in text or 'router.replace("/artifacts-preview")' in text
    assert md5(F) == d['artifacts_tsx_md5_post']
    print('[PASS] BATCH1-V2 Track C artifacts redirect')
    return 0
if __name__ == '__main__': sys.exit(main())
