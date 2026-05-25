#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_locked_preview_dual_read_copy_v1.json')
SRV = Path('/app/frontend/app/servers.tsx')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_SERVERS_LOCKED_PREVIEW_DUAL_READ_COPY_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 1
    assert d['flag_flips'] == 0
    assert d['global_markers']['TRACK_E_SERVERS_LOCKED_PREVIEW_DUAL_READ_COPY_APPROVAL'] == 'true'
    # File must exist and contain the new section text
    assert SRV.exists()
    src = SRV.read_text()
    assert 'Server attuale' in src, "new 'Server attuale' section missing in servers.tsx"
    assert 'Anteprima dual-read in preparazione' in src
    # MUST NOT reintroduce forbidden substrings
    assert '/api/server/select' not in src
    assert '/api/servers' not in src
    assert 'Server Selezionato' not in src
    assert 'selectServer' not in src
    # MD5 verification
    md5 = hashlib.md5(SRV.read_bytes()).hexdigest()
    assert md5 == d['post_pack_md5'], f'servers.tsx MD5 drift: expected {d["post_pack_md5"]} got {md5}'
    assert d['pre_pack_md5'] != d['post_pack_md5']
    # Copy safety claims
    cs = d['copy_claim_safety']
    assert cs['fake_availability_claim'] is False
    assert cs['new_profiles_live_claim'] is False
    assert cs['no_implication_of_active_switching'] is True
    print(f"[PASS] DUAL-READ Track E locked-preview copy READY \u2014 md5={md5[:8]}")
    return 0
if __name__ == '__main__': sys.exit(main())
