#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK E
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/unreachable_implemented_mode_audit_v1.json')

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_UNREACHABLE_IMPLEMENTED_MODE_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_E_UNREACHABLE_IMPLEMENTED_MODE_AUDIT_APPROVAL'] == 'true'
    lst = d['unreachable_or_deep_link_only']
    assert isinstance(lst, list) and len(lst) >= 5
    # each item has classification + action
    for item in lst:
        assert 'route' in item and 'classification' in item and 'action' in item
    leg = d['classification_legend']
    for k in ['player_visible_now','locked_preview','dev_admin_only','intentional_hidden','should_be_removed_later','should_be_linked_by_future_pack']:
        assert k in leg, f'missing legend key {k}'
    s = d['summary']
    assert s['critical_issues'] == 0
    print(f"[PASS] Track E unreachable mode audit READY \u2014 items={s['total_unreachable_or_deep_link_only']}, critical={s['critical_issues']}")
    return 0
if __name__ == '__main__': sys.exit(main())
