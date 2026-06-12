#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Mutating route allowlist/blocklist audit.

Catalogizza ogni route mutating (POST/PUT/PATCH/DELETE) nel backend in
categorie:
  - allowed_safe (strict server-scoped, controlled rewards, ecc.)
  - legacy_quarantined (path con guard 423 di quarantena)
  - requires_future_pack (deferred)
  - dev_only (sotto kill switch dev_test)

NON disabilita route, solo cataloga. Stampa la mappa.
"""
import os, re, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router_files = []
for root, _, files in os.walk(os.path.join(R, 'backend/routes')):
    for f in files:
        if f.endswith('.py'):
            router_files.append(os.path.join(root, f))
router_files.append(os.path.join(R, 'backend/server.py'))
router_files.append(os.path.join(R, 'backend/battle_engine.py'))
router_files.append(os.path.join(R, 'backend/game_systems.py'))

MUTATING = re.compile(r"@(?:app|router)\.(post|put|patch|delete)\((\"|')([^\"']+)(\"|')")
buckets = {'allowed_safe': [], 'legacy_quarantined': [], 'requires_future_pack': [], 'dev_only': [], 'uncategorized': []}
QUARANTINE_TOKENS = (
    'GACHA_LIVE_DISABLED_PRE_QA', 'GUILD_LEGACY_QUARANTINED',
    'ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED', 'TEAM_FORMATION_LEGACY_QUARANTINED',
    'QUARANTINED', 'quarantine',
)
SAFE_PREFIXES = ('/economy/strict', '/tower/strict', '/controlled-rewards', '/guild/strict',
                 '/playable-loop', '/competitive-guards', '/rewards/claim', '/daily-login',
                 '/daily-quest', '/equipment-strict', '/forge/strict')
FUTURE_PACK_TOKENS = ('AUTORIZZO_V110_', 'DEFERRED', 'deferred_next_step')

for fp in router_files:
    if not os.path.exists(fp): continue
    c = open(fp).read()
    for m in MUTATING.finditer(c):
        verb, _, path, _ = m.groups()
        full_path = path if path.startswith('/') else '/' + path
        # Heuristic categorization.
        start = m.start()
        snippet = c[start:start + 1500]
        if any(tok in snippet for tok in QUARANTINE_TOKENS):
            buckets['legacy_quarantined'].append((verb.upper(), full_path, os.path.relpath(fp, R)))
        elif any(full_path.startswith(p) for p in SAFE_PREFIXES):
            buckets['allowed_safe'].append((verb.upper(), full_path, os.path.relpath(fp, R)))
        elif any(tok in snippet for tok in FUTURE_PACK_TOKENS):
            buckets['requires_future_pack'].append((verb.upper(), full_path, os.path.relpath(fp, R)))
        elif 'dev_test' in snippet.lower() or 'qa_only' in snippet.lower():
            buckets['dev_only'].append((verb.upper(), full_path, os.path.relpath(fp, R)))
        else:
            buckets['uncategorized'].append((verb.upper(), full_path, os.path.relpath(fp, R)))

# Output catalog to docs.
out_path = os.path.join(R, 'docs/divine/112_PRE_QA_STABILIZATION_110_MUTATING_ROUTE_ALLOWLIST.md')
lines = ['# Pre-QA Stabilization 110 — Mutating Route Allowlist / Blocklist\n']
for cat in ('allowed_safe', 'legacy_quarantined', 'requires_future_pack', 'dev_only', 'uncategorized'):
    entries = buckets[cat]
    lines.append(f'\n## {cat} ({len(entries)})\n')
    lines.append('| Verb | Path | File |')
    lines.append('|------|------|------|')
    for verb, path, file in sorted(set(entries)):
        lines.append(f'| {verb} | `{path}` | `{file}` |')
open(out_path, 'w').write('\n'.join(lines))

totals = {k: len(v) for k, v in buckets.items()}
# Invariants: must have at least the four quarantine entries.
Q_REQUIRED = {'/api/gacha/pull', '/api/gacha/pull10', '/achievements/claim', '/team/update-formation'}
found_q_paths = {p for _, p, _ in buckets['legacy_quarantined']}
missing = Q_REQUIRED - found_q_paths
assert not missing, f'quarantine paths missing in catalog: {missing}'
print(f'[v110 PRE_QA_110_MUTATING_ROUTE_ALLOWLIST] OK totals={json.dumps(totals)} allowlist_doc={out_path}')
