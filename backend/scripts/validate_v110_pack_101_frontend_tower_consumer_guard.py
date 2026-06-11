#!/usr/bin/env python3
"""Pack 101 — Frontend Tower Strict consumer guard."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f=os.path.join(R,'frontend/src/components/TowerStrictConsumer.tsx')
assert os.path.exists(f), 'TowerStrictConsumer missing'
src=open(f).read()
for needle in [
    'EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED',
    "const UI_ENABLED = UI_FLAG === 'true';",
    'if (!UI_ENABLED && !forceVisible) return null;',
    '/api/tower/strict/status?server_id=',
    '/api/tower/strict/battle/preview?server_id=',
    'useServerScope',
    'useAuth',
    'Reward in quarantena',
]:
    assert needle in src, needle

# NESSUNA chiamata al path legacy (cerchiamo solo le esatte URL legacy isolate
# - non `/api/tower/strict/status` che inizia con /api/tower/strict/.)
forbidden_legacy_urls = [
    '/api/tower/status?',  # legacy con query
    "'/api/tower/status'",  # legacy senza query (stringa singolo apice)
    '"/api/tower/status"',  # doppio apice
    '`${BACKEND}/api/tower/status`',  # template letterale
    "'/api/tower/battle'",
    '"/api/tower/battle"',
    '`${BACKEND}/api/tower/battle`',
]
for forb in forbidden_legacy_urls:
    assert forb not in src, f'frontend legacy tower call leak: {forb}'

# .env frontend default OFF
env=os.path.join(R,'frontend/.env')
if os.path.exists(env):
    et=open(env).read()
    for ln in et.splitlines():
        if ln.startswith('EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED=') and ln.split('=',1)[1].strip().lower()=='true':
            assert False, 'EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED must remain default OFF'
print('[v110 PACK_101_FRONTEND_TOWER_CONSUMER_GUARD] OK ui_default_off strict_only no_legacy_call psp_required quarantine_message_visible')
