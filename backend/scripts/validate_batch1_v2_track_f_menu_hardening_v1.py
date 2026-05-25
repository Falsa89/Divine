#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track F validator (menu hardening).
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_f_menu_hardening_v1.json')
F = Path('/app/frontend/app/(tabs)/menu.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_F_MENU_DEV_LEGACY_ROUTE_HARDENING_IMPLEMENTED_SAFE'
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    assert d['route_files_deleted'] == 0
    text = F.read_text()
    # Le voci rimosse non devono più comparire come {label: ..., route: ...}
    forbidden = [
        "label: 'Sprite Test'",
        "label: 'Combat QA Lab",
        "route: '/sprite-test'",
        "route: '/dev-combat-qa-lab'",
    ]
    for tok in forbidden:
        assert tok not in text, f'menu still exposes {tok}'
    # Artefatti & Costellazioni deve puntare a /artifacts-preview
    assert "label: 'Artefatti & Costellazioni'" in text
    assert "route: '/artifacts-preview'" in text
    # Vecchia destinazione /artifacts non deve comparire come route attiva nel menu
    # (potrebbe esistere altrove, ma non come 'route: \'/artifacts\'' nel menu)
    assert "route: '/artifacts'" not in text, 'menu still routes to legacy /artifacts'
    assert md5(F) == d['menu_tsx_md5_post']
    print('[PASS] BATCH1-V2 Track F menu hardening')
    return 0
if __name__ == '__main__': sys.exit(main())
