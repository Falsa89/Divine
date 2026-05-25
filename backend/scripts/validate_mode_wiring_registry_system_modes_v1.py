#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK B
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/mode_feature_wiring_registry_system_modes_v1.json')
SAFE_PREVIEWS = Path('/app/frontend/app/safe-previews.tsx')
REQUIRED_FIELDS = ['mode_id','display_name','category','frontend_entry_points','frontend_status','backend_endpoints_current','backend_endpoints_expected','backend_status','legacy_paths_detected','risk_level','risk_reason','smoke_required','next_action','owner_pack_recommendation']
EXPECTED = ['artifact','housing','status_codex','status_runtime_first_slice','status_runtime_second_slice','server_profiles','af2n_affinity_gift','soul_forge','equipment','forge','unique_items','guild','gvg','raids','safe_previews','approval_matrix_live_gates']

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_B_SYSTEM_MODE_WIRING_REGISTRY_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_B_SYSTEM_MODE_WIRING_REGISTRY_APPROVAL'] == 'true'
    modes = d['modes']
    ids = [m['mode_id'] for m in modes]
    for exp in EXPECTED:
        assert exp in ids, f'missing system mode: {exp}'
    for m in modes:
        for f in REQUIRED_FIELDS:
            assert f in m, f"mode {m.get('mode_id')} missing field {f}"
    # Anti-leak: status second slice must remain PENDING_APPROVAL
    ss = next(m for m in modes if m['mode_id'] == 'status_runtime_second_slice')
    assert ss['backend_status'] == 'PENDING_APPROVAL'
    assert ss['frontend_status'] == 'HIDDEN_INTENTIONAL'
    # Anti-leak: artifact PENDING_APPROVAL
    art = next(m for m in modes if m['mode_id'] == 'artifact')
    assert art['backend_status'] == 'PENDING_APPROVAL'
    # safe-previews route still exists
    assert SAFE_PREVIEWS.exists()
    print(f"[PASS] Track B system mode registry READY \u2014 modes={len(modes)}, locked_preview={sum(1 for m in modes if m['frontend_status']=='LOCKED_PREVIEW')}")
    return 0
if __name__ == '__main__': sys.exit(main())
