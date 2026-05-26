#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/sf_merge/track_f_navigation_alignment_v1.json')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
HOME = Path('/app/frontend/app/(tabs)/home.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_F_HOME_OVERFLOW_AND_MENU_NAVIGATION_ALIGNED_SAFE'
    fmap = {f['file']: f['md5_post'] for f in d['files_changed']}
    assert md5(MENU) == fmap['frontend/app/(tabs)/menu.tsx']
    assert md5(HOME) == fmap['frontend/app/(tabs)/home.tsx']
    menu_t = MENU.read_text()
    home_t = HOME.read_text()
    # menu non deve avere entry 'Oggetti Esclusivi' attiva
    assert "label: 'Oggetti Esclusivi'" not in menu_t, 'menu still has Esclusivi entry'
    # menu non deve linkare a /economy
    assert "route: '/economy'" not in menu_t, 'menu still routes /economy'
    # menu deve avere Hub Anime
    assert 'Hub Anime' in menu_t, 'menu missing Hub Anime entry'
    # home overflow non deve linkare a /economy o /exclusive
    assert "router.push('/economy' as any)" not in home_t, 'home still pushes /economy'
    assert "router.push('/exclusive' as any)" not in home_t, 'home still pushes /exclusive'
    # home deve linkare a /soul-forge dalla voce economy/hub-anime
    assert "router.push('/soul-forge' as any)" in home_t, 'home missing /soul-forge consolidated entry'
    print('[PASS] SF-MERGE Track F navigation aligned')
    return 0
if __name__=='__main__': sys.exit(main())
