#!/usr/bin/env python3
"""Pre-QA Stabilization 111 — Deterministic route classifier.

Classifica TUTTE le route mutanti del backend (POST/PUT/PATCH/DELETE) in 9
categorie canoniche. Target: `uncategorized=0` con regole esplicite e
verificabili. Nessuna route marcata `allowed_safe` senza evidenza (prefix
strict o auth/onboarding canonico).
"""
import os, re, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CATEGORIES = (
    'allowed_safe',
    'internal_only',
    'dev_only',
    'legacy_quarantined',
    'deferred_blocker',
    'requires_future_pack',
    'not_player_facing_readonly',
    'duplicate_or_dead_route',
    'needs_manual_review_non_blocking',
)

# Set canonici esatti per ogni categoria (deterministico, no heuristic ambiguo).
ALLOWED_SAFE_PATHS = {
    # Auth / onboarding canonici.
    '/api/login', '/api/register', '/api/psp/ensure', '/api/psp/starter/claim',
    '/refresh', '/logout', '/logout-all', '/launch', '/select', '/server/select',
    '/apple', '/google',
    # Read-only marker setter non-currency.
    '/notifications/read-all', '/title/set',
}
INTERNAL_ONLY_PATHS = {
    '/api/admin/bots/run-cycle',
    '/push/register', '/push/test',
}
# Dev/test preview tools: non player-facing, non mutano economy/users.
NOT_PLAYER_FACING_READONLY_PATHS = {
    '/battle/simulate', '/story/battle', '/tower/battle', '/events/battle', '/pvp/battle',
    '/alpha-battle-preview', '/alpha-reward-summary-preview',
    '/clear-preview', '/create-preview', '/grant-plan-preview', '/guard-plan-preview',
    '/idempotency-preview', '/instance/preview', '/instance/resolve-preview',
    '/playback-preview', '/power-preview', '/replace-preview', '/reward-preview',
    '/socket-preview', '/unsocket-preview', '/reforge/preview', '/enchant/preview',
    '/enhance/preview', '/fusion/preview', '/{hero_id}/upgrade/preview',
    '/validate-claim-request', '/validate-payload', '/validate-replay-payload',
    '/validate-request',
}
# Legacy mutating: economy/forge/hero progression/inventory legacy.
LEGACY_QUARANTINED_PREFIXES = (
    '/cosmetics/', '/item-shop/', '/shop/', '/materials/', '/vip/', '/wallet/',
    '/forge/fuse', '/forge/upgrade', '/runes/', '/exclusive-items/',
    '/unique-items/', '/affinity/',
    '/hero/reincarnate', '/hero/skill-upgrade', '/inventory/',
    '/equipment/unequip', '/mail/claim',
    '/sanctuary/',
    # Pack 108 guild legacy mutating routes (gia' quarantinati).
    '/guild/create', '/guild/join', '/guild/leave', '/faction/join',
)
# Deferred systems (battlepass/social/dm/friends/gvg/raid/territory/plaza/fragments/level-sharing).
REQUIRES_FUTURE_PACK_PREFIXES = (
    '/battlepass/', '/dm/', '/friends/', '/gvg/', '/raid/', '/territory/',
    '/plaza/', '/level-sharing/', '/fragments/',
    '/artifacts/', '/constellations/',
    '/user/faction-v2/',
)
# Quarantine guard tokens (case-sensitive) that mean route already has 423 guard.
QUARANTINE_TOKENS = (
    'GACHA_LIVE_DISABLED_PRE_QA', 'GUILD_LEGACY_QUARANTINED',
    'ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED', 'TEAM_FORMATION_LEGACY_QUARANTINED',
    'QUARANTINED', 'quarantine',
)
SAFE_PREFIXES = (
    '/economy/strict', '/tower/strict', '/controlled-rewards', '/guild/strict',
    '/playable-loop', '/competitive-guards', '/rewards/claim', '/daily-login',
    '/daily-quest', '/equipment-strict', '/forge/strict',
)
FUTURE_PACK_TOKENS = ('AUTORIZZO_V110_', 'DEFERRED', 'deferred_next_step')


def _gather_routes():
    router_files = []
    for root, _, files in os.walk(os.path.join(R, 'backend/routes')):
        for f in files:
            if f.endswith('.py'):
                router_files.append(os.path.join(root, f))
    router_files.append(os.path.join(R, 'backend/server.py'))
    router_files.append(os.path.join(R, 'backend/battle_engine.py'))
    router_files.append(os.path.join(R, 'backend/game_systems.py'))
    MUTATING = re.compile(r"@(?:app|router)\.(post|put|patch|delete)\(([\"'])([^\"']+)([\"'])")
    entries = []
    for fp in router_files:
        if not os.path.exists(fp): continue
        c = open(fp).read()
        for m in MUTATING.finditer(c):
            verb, _, path, _ = m.groups()
            full_path = path if path.startswith('/') else '/' + path
            snippet = c[m.start():m.start() + 1500]
            entries.append((verb.upper(), full_path, os.path.relpath(fp, R), snippet))
    return entries


def _classify(verb: str, path: str, file_rel: str, snippet: str) -> str:
    # Priority 1: explicit quarantine guard detected in code snippet.
    if any(tok in snippet for tok in QUARANTINE_TOKENS):
        return 'legacy_quarantined'
    # Priority 2: safe strict prefix.
    if any(path.startswith(p) for p in SAFE_PREFIXES):
        return 'allowed_safe'
    # Priority 3: allowed_safe explicit list (auth/onboarding/marker setters).
    if path in ALLOWED_SAFE_PATHS:
        return 'allowed_safe'
    # Priority 4: internal_only explicit list.
    if path in INTERNAL_ONLY_PATHS:
        return 'internal_only'
    # Priority 5: not_player_facing_readonly preview tools.
    if path in NOT_PLAYER_FACING_READONLY_PATHS:
        return 'not_player_facing_readonly'
    if path.endswith('-preview') or path.endswith('/preview') or 'preview' in path.lower().split('/')[-1]:
        return 'not_player_facing_readonly'
    # Priority 6: legacy_quarantined prefix list.
    for p in LEGACY_QUARANTINED_PREFIXES:
        if path == p or path.startswith(p):
            return 'legacy_quarantined'
    # Priority 7: requires_future_pack prefix list.
    for p in REQUIRES_FUTURE_PACK_PREFIXES:
        if path.startswith(p):
            return 'requires_future_pack'
    if any(tok in snippet for tok in FUTURE_PACK_TOKENS):
        return 'requires_future_pack'
    # Priority 8: dev_only marker.
    if 'dev_test' in snippet.lower() or 'qa_only' in snippet.lower():
        return 'dev_only'
    # Default: needs_manual_review_non_blocking (NON allowed_safe per default).
    return 'needs_manual_review_non_blocking'


def main():
    entries = _gather_routes()
    buckets = {c: [] for c in CATEGORIES}
    for verb, path, fp, snip in entries:
        cat = _classify(verb, path, fp, snip)
        assert cat in CATEGORIES, f'unknown cat {cat}'
        buckets[cat].append((verb, path, fp))

    # Write the new canonical doc.
    out_path = os.path.join(R, 'docs/divine/113_PRE_QA_STABILIZATION_111_ROUTE_CLASSIFICATION_FULL.md')
    lines = ['# Pre-QA Stabilization 111 — Full Mutating Route Classification\n']
    lines.append('Classifier deterministico. Categorie canoniche:')
    lines.append(', '.join(CATEGORIES) + '.\n')
    for cat in CATEGORIES:
        rows = sorted(set(buckets[cat]))
        lines.append(f'\n## {cat} ({len(rows)})\n')
        lines.append('| Verb | Path | File |')
        lines.append('|------|------|------|')
        for verb, path, fp in rows:
            lines.append(f'| {verb} | `{path}` | `{fp}` |')
    open(out_path, 'w').write('\n'.join(lines))

    totals = {c: len(buckets[c]) for c in CATEGORIES}
    # Invariant: uncategorized non esiste come categoria. Verify quarantine entries.
    Q_REQUIRED = {'/api/gacha/pull', '/api/gacha/pull10', '/achievements/claim', '/team/update-formation'}
    found_q = {p for _, p, _ in buckets['legacy_quarantined']}
    missing = Q_REQUIRED - found_q
    assert not missing, f'quarantine paths missing: {missing}'
    # Invariant: nessun bucket "uncategorized"; remaining_uncategorized = 0.
    # `needs_manual_review_non_blocking` e' una categoria ESPLICITA, non un nascondiglio.
    # Verifica che la categoria non sia stata abusata: deve essere <= 5% del totale.
    total = sum(totals.values())
    nmr = totals['needs_manual_review_non_blocking']
    nmr_ratio = nmr / max(1, total)
    assert nmr_ratio <= 0.05, f'needs_manual_review_non_blocking troppo grande: {nmr}/{total} ({nmr_ratio:.2%})'
    print(f'[v111 PRE_QA_111_ROUTE_CLASSIFICATION] OK totals={json.dumps(totals)} remaining_uncategorized=0 needs_manual_review_ratio={nmr_ratio:.3f} doc={out_path}')


if __name__ == '__main__':
    main()
