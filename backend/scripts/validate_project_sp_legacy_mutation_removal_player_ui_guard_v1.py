#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_legacy_mutation_removal_player_ui_guard_v1.json')
FE_APP = Path('/app/frontend/app')
FE_COMP = Path('/app/frontend/components')
FE_UTILS = Path('/app/frontend/utils')
FORBIDDEN_IN_PLAYER_UI = [
    '/api/server/select',
    'selectServer',
    'select_server',
    'Server Selezionato',
]
def scan_dir(d):
    hits = []
    if not d.exists(): return hits
    for f in d.rglob('*'):
        if f.is_file() and f.suffix in ('.ts','.tsx','.js','.jsx'):
            try:
                txt = f.read_text(errors='ignore')
            except Exception:
                continue
            for pat in FORBIDDEN_IN_PLAYER_UI:
                if pat in txt:
                    hits.append((str(f), pat))
    return hits
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_LEGACY_MUTATION_REMOVAL_FROM_PLAYER_UI_GUARD_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_C_LEGACY_MUTATION_REMOVAL_PLAYER_UI_GUARD_APPROVAL'] == 'true'
    # Live scan across frontend player UI dirs
    hits = scan_dir(FE_APP) + scan_dir(FE_COMP) + scan_dir(FE_UTILS)
    assert len(hits) == 0, f'forbidden legacy mutation hits found in player UI: {hits}'
    # Sanity: backend legacy endpoint still exists (intact, not deleted by this pack)
    econ = Path('/app/backend/routes/economy.py').read_text()
    assert '/server/select' in econ, 'backend legacy endpoint must remain intact (audit-scope)'
    print(f'[PASS] SP UI-LOCK Track C legacy mutation removal guard \u2014 0 hits in player UI')
    return 0
if __name__ == '__main__': sys.exit(main())
