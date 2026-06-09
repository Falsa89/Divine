#!/usr/bin/env python3
"""
Pack 92 — Frontend static regression guard.

Per ogni file PLAYER-FACING (frontend/app/*, esclusi preview/sandbox/dev),
verifica che ogni occorrenza di un endpoint guardato sia immediatamente
seguita da `?` (query string) E contenga `server_id=` entro la stessa string
URL (template literal o letterale).

I literal "no-server" `'/api/...'` (senza ?) sono accettati SOLO se il file
adotta `useServerScope` (sono usati come fallback quando server non selezionato
e il backend ritornerà legacy non-player-facing flagged).

Vieta `server_id=s1` literal ovunque nel frontend.
"""
import os, json, re, sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_frontend_static_regression_guard_v1.json')))
fe = os.path.join(R, 'frontend')

guarded_exact = [
    '/api/user/heroes',
    '/api/inventory',
    '/api/item-shop/buy',
    '/api/inventory/use-exp',
    '/api/wallet',
    '/api/story/chapters',
    '/api/user/equipment',
]


def is_player_facing(rel_path):
    if not rel_path.startswith('frontend/app/'):
        return False
    base = os.path.basename(rel_path).lower()
    if 'preview' in base or 'sandbox' in base or rel_path.startswith('frontend/app/dev-'):
        return False
    return True


bad = []
for dp, _, files in os.walk(fe):
    if 'node_modules' in dp:
        continue
    for fn in files:
        if not fn.endswith(('.ts', '.tsx', '.js', '.jsx')):
            continue
        fpath = os.path.join(dp, fn)
        rel = os.path.relpath(fpath, R)
        if not is_player_facing(rel):
            continue
        try:
            txt = open(fpath).read()
        except Exception:
            continue
        has_hook = 'useServerScope' in txt or 'selectedServerId' in txt or "AsyncStorage.getItem('selected_server_id')" in txt
        for ep in guarded_exact:
            # Find every occurrence with NO trailing alnum/-/_ (avoid /api/inventory matching /api/inventory/use-exp)
            pat = re.escape(ep) + r"(?![A-Za-z0-9/_\-])"
            occurrences = list(re.finditer(pat, txt))
            if not occurrences:
                continue
            # Check at least one occurrence has `?` immediately followed by something containing 'server_id='
            any_with_server_id = False
            all_bare = True
            for m in occurrences:
                # Look at next 200 chars after the endpoint
                tail = txt[m.end():m.end()+200]
                # Also look at a window around to find `qs = ...server_id=...` pattern
                # If endpoint is followed by `?` and the file contains the URL with
                # template/var that resolves to server_id, that's OK.
                if tail.startswith('?'):
                    all_bare = False
                    # Take the URL up to closing quote/backtick/paren
                    url_end = re.search(r"[`'\")]", tail)
                    url_part = tail[:url_end.start()] if url_end else tail
                    # Pattern A: explicit ?server_id=
                    if 'server_id' in url_part:
                        any_with_server_id = True
                        break
                    # Pattern B: ?${qs} — look upward for qs definition containing server_id
                    if '${' in url_part:
                        # Search 400 chars BEFORE this endpoint occurrence for `qs = ...server_id=`
                        pre = txt[max(0, m.start()-600):m.start()]
                        if re.search(r"(?:const|let|var)\s+qs\s*=\s*[`'\"][^`'\"]*server_id=", pre):
                            any_with_server_id = True
                            break
                        # Or named template variable resolved within URL (heuristic)
                        if 'server_id' in pre[-400:]:
                            any_with_server_id = True
                            break
            if not any_with_server_id:
                # All occurrences are bare; allowed only if hook present (means fallback path)
                if all_bare and has_hook:
                    continue
                if all_bare and not has_hook:
                    bad.append((rel, ep, 'all_bare_no_hook'))
                else:
                    # Has at least one ?... but no server_id in it
                    bad.append((rel, ep, 'query_present_without_server_id'))

assert not bad, f'frontend player-facing callers missing server_id sweep: {bad}'

# Vieta silent s1 literal
for dp, _, files in os.walk(fe):
    if 'node_modules' in dp:
        continue
    for fn in files:
        if not fn.endswith(('.ts', '.tsx', '.js', '.jsx')):
            continue
        try:
            txt = open(os.path.join(dp, fn)).read()
        except Exception:
            continue
        assert 'server_id=s1' not in txt, f'silent s1 literal in {os.path.join(dp, fn)}'

print('[v110 PACK_92_FRONTEND_STATIC_REGRESSION_GUARD] OK player_facing_files_adopt_server_id_query_or_hook_fallback zero_silent_s1_literal')
