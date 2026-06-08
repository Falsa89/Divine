#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_server_ui_copy_cleanup_v1.json')))
assert d.get('honest_about_deferred_loaders') is True
assert d.get('no_release_readiness_claim_in_copy') is True
assert d.get('no_fake_separation_claim') is True
stale = d.get('stale_texts_removed', [])
assert any('SERVER_DATA_ISOLATION_BACKEND_PENDING' in s for s in stale), 'stale text SERVER_DATA_ISOLATION_BACKEND_PENDING must be in removed list'
assert any('tutti i server caricheranno lo stesso account corrente'.lower() in s.lower() for s in stale)
# Static verification: stale texts removed from servers.tsx
src = open(os.path.join(R, 'frontend/app/servers.tsx')).read()
assert 'SERVER_DATA_ISOLATION_BACKEND_PENDING' not in src, 'stale SERVER_DATA_ISOLATION_BACKEND_PENDING must NOT be present'
assert 'Tutti i server caricheranno lo stesso account corrente' not in src, 'stale text must NOT be present'
# New descriptive text present (check key phrase, not verbatim formatting)
key_phrase = 'Pack 85-87 attivi'
assert key_phrase in src, f'new descriptive text key phrase missing in servers.tsx: {key_phrase}'
# Verify additional honest phrases
for phrase in ('account identity condivisa', 'server-scoped', 'fresh-start', 'deferred', 'Nessuna finzione di separazione'):
    assert phrase.lower() in src.lower(), f'honest descriptive phrase missing in servers.tsx: {phrase}'
static = d.get('static_verification', {})
assert static.get('old_text_grep_count_post_pack_87') == 0
assert static.get('new_text_grep_count_post_pack_87') == 1
print('[v110 PACK_87_SERVER_UI_COPY_CLEANUP] OK stale_text_removed new_descriptive_present honest_deferred_loaders no_release_readiness_claim no_fake_separation')
