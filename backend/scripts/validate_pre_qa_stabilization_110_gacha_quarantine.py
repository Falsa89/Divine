#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Gacha quarantine static validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
srv = open(os.path.join(R, 'backend/server.py')).read()
for token in ('GACHA_LIVE_DISABLED_PRE_QA', 'GACHA_LIVE_ENABLED', 'no_gems_spend',
              'no_hero_grant', 'no_account_wide_user_heroes_mutation',
              'gacha_server_scope_required', 'AUTORIZZO_V110_GACHA_LIVE_PACK_NEXT'):
    assert token in srv, f'server.py missing {token}'
# Both endpoints have the guard.
assert srv.count('GACHA_LIVE_DISABLED_PRE_QA') >= 2, 'both pull and pull10 must have quarantine'
# UI tab guard.
layout = open(os.path.join(R, 'frontend/app/(tabs)/_layout.tsx')).read()
assert 'EXPO_PUBLIC_GACHA_UI_ENABLED' in layout
assert 'href: null' in layout
# Gacha screen lock.
gacha = open(os.path.join(R, 'frontend/app/(tabs)/gacha.tsx')).read()
assert 'GACHA_LIVE_DISABLED_PRE_QA' in gacha
assert 'gacha-locked-pre-qa' in gacha
print('[v110 PRE_QA_110_GACHA_QUARANTINE] OK gacha_pull_pull10_quarantined ui_tab_hidden screen_locked')
