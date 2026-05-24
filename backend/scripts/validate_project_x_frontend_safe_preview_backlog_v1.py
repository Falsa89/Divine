#!/usr/bin/env python3
# PROJECT_X TRACK E — FRONTEND SAFE PREVIEW BACKLOG VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_frontend_safe_preview_backlog_v1.json')
REQUIRED_FIELDS = {'id', 'name', 'source_endpoints', 'source_files', 'visibility_class',
                   'data_availability', 'ui_risk', 'implementation_priority',
                   'blockers', 'acceptance_criteria'}

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_E_FRONTEND_SAFE_PREVIEW_IMPLEMENTATION_BACKLOG_READY'
    assert m['audit_only'] is True
    assert m['implementation_deferred_to'] == 'PROJECT_Y_FRONTEND_SAFE_PREVIEW_UI_IMPLEMENTATION_PACK'
    backlog = m['backlog']
    assert len(backlog) >= 6, 'backlog must have at least 6 items'
    for item in backlog:
        missing = REQUIRED_FIELDS - set(item.keys())
        assert not missing, f'item {item.get("id")} missing fields: {missing}'
        assert item['implementation_priority'] in ('P1', 'P2', 'P3', 'P4')
    print(f'[PASS] PROJECT_X Track E preview backlog READY — items={len(backlog)}, P1={sum(1 for x in backlog if x["implementation_priority"]=="P1")}, P2={sum(1 for x in backlog if x["implementation_priority"]=="P2")}, P3={sum(1 for x in backlog if x["implementation_priority"]=="P3")}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
