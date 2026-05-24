#!/usr/bin/env python3
# PROJECT_Y TRACK A — TARGET SELECTION VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_safe_preview_target_selection_v1.json')
XPACK_BACKLOG = Path('/app/data/design/frontend/project_x_frontend_safe_preview_backlog_v1.json')

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_A_FRONTEND_SAFE_PREVIEW_TARGET_SELECTION_READY'
    assert XPACK_BACKLOG.exists(), 'Pack X backlog source missing'
    assert m['menu_mutation_planned'] is False
    assert m['new_bottom_tab_planned'] is False
    assert m['backend_mutation_planned'] is False
    assert m['db_writes_planned'] is False
    sel = m['targets_selected_for_pack_y']
    assert len(sel) >= 3
    for t in sel:
        assert t['included'] is True
        f = Path(t['file_to_create'])
        assert f.exists(), f'planned file not on disk: {f}'
    print(f'[PASS] PROJECT_Y Track A target selection READY — selected={len(sel)}, deferred={len(m["targets_deferred_to_project_y2"])}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
