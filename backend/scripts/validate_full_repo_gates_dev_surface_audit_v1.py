#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track F validator (audit-only).
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/gates_locked_preview_dev_surface_audit_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_GATES_LOCKED_PREVIEW_AND_DEV_SURFACE_AUDIT_READY'
    assert len(d['locked_previews']) >= 4
    assert len(d['inert_503_endpoints']) >= 1
    ids = {g['id'] for g in d['gate_findings']}
    for must in ('GATE-SERVER-PROFILES', 'GATE-HOUSING', 'GATE-ARTIFACT-LIVE',
                 'GATE-AF2-N', 'DEV-EXPOSURE-MENU'):
        assert must in ids, f'missing gate: {must}'
    print(f"[PASS] FULL-REPO Track F gates \u2014 locked={len(d['locked_previews'])} dev={len(d['dev_screens'])} inert={len(d['inert_503_endpoints'])}")
    return 0
if __name__ == '__main__': sys.exit(main())
