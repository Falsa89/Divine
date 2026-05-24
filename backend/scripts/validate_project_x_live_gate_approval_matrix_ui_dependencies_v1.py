#!/usr/bin/env python3
# PROJECT_X TRACK F — LIVE GATE APPROVAL MATRIX UI DEPENDENCIES VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_live_gate_approval_matrix_ui_dependencies_v1.json')
VALID_UI_VIS = {'hidden_until_approved', 'locked_card_coming_soon', 'player_visible_active', 'dev_admin_only'}

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_F_LIVE_GATE_APPROVAL_MATRIX_UI_DEPENDENCIES_READY'
    assert m['audit_only'] is True
    assert m['approval_spoofing'] is False
    assert isinstance(m['gates'], list) and len(m['gates']) >= 6
    for g in m['gates']:
        assert 'name' in g
        assert 'signatures_required' in g
        assert g['ui_visibility'] in VALID_UI_VIS, f'invalid ui_visibility for {g["name"]}: {g["ui_visibility"]}'
    # No spoofed approvals
    for g in m['gates']:
        if g['name'] != 'Gacha/pricing/economy live':
            assert g['current_signatures'] == 0 or g['current_signatures'] is None
    print(f'[PASS] PROJECT_X Track F live gate matrix READY — gates={len(m["gates"])}, locked_cards={len(m["locked_cards_safe_to_show"])}, hidden={len(m["hidden_from_player_until_approved"])}, no_spoofing=True')
    return 0

if __name__ == '__main__':
    sys.exit(main())
