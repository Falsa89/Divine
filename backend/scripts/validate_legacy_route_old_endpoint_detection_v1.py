#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK C
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/legacy_route_old_endpoint_detection_v1.json')

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_LEGACY_ROUTE_AND_OLD_ENDPOINT_DETECTION_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    assert d['global_markers']['TRACK_C_LEGACY_ROUTE_OLD_ENDPOINT_DETECTION_APPROVAL'] == 'true'
    det = d['detection']
    assert isinstance(det['backend_legacy_or_duplicate_endpoints'], list)
    assert len(det['backend_legacy_or_duplicate_endpoints']) >= 5, 'must enumerate >=5 legacy/duplicates'
    assert isinstance(det['frontend_routes_overlap'], list)
    assert len(det['frontend_routes_overlap']) >= 3
    assert isinstance(det['backend_endpoints_likely_without_frontend'], list)
    assert isinstance(det['frontend_endpoints_likely_without_backend'], list)
    # Spot-check known legacy items remain explicitly documented
    flat = json.dumps(det)
    assert '/api/server/select' in flat
    assert '/api/synergies/team' in flat
    assert '/api/exclusive-items' in flat
    assert 'no renames performed'.lower() in flat.lower()
    print(f"[PASS] Track C legacy/old endpoint detection READY \u2014 legacy={len(det['backend_legacy_or_duplicate_endpoints'])}, overlaps={len(det['frontend_routes_overlap'])}")
    return 0
if __name__ == '__main__': sys.exit(main())
