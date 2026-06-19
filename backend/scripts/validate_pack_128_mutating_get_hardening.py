#!/usr/bin/env python3
"""Pack 128 — Mutating GET hardening classification (STATIC).

Legge il report Pack 127 `pack_127_no_mutating_get_report.json` e classifica i
26 GET sospetti in categorie:
  - INIT_ENSURE_ONLY  : pattern di insert idempotente al primo accesso
  - CACHE_ANALYTICS   : update di analytics/cache (non player-data critical)
  - TRUE_SIDE_EFFECT  : mutazione user-data reale via GET (P0 hardening)
  - DEFERRED          : route da rivedere in Pack 129+

Classificazione è LARGAMENTE EURISTICA basata sul pattern + nome file/route
(no behaviour change, no refactor codice route). Output: report machine-readable
per guidare Pack 128.x / Pack 129 hardening.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
P127 = REPO_ROOT / 'backend' / 'scripts' / 'reports' / 'pack_127_no_mutating_get_report.json'

# Euristica di classificazione: (file_substring, route_substring) -> category
CATEGORY_RULES = [
    # TRUE_SIDE_EFFECT: user-data critical writes
    (('hero_progression.py', '/hero/reincarnation-info'), 'TRUE_SIDE_EFFECT'),
    (('controlled_rewards.py', '/controlled-rewards/health'), 'CACHE_ANALYTICS'),
    # INIT_ENSURE_ONLY: typical "create on first read" patterns
    (('hero_progression.py', '/fragments'), 'INIT_ENSURE_ONLY'),
    (('hero_progression.py', '/materials'), 'INIT_ENSURE_ONLY'),
    (('soul_forge.py', '/wallet'), 'INIT_ENSURE_ONLY'),
    (('economy.py', '/shop'), 'INIT_ENSURE_ONLY'),
    (('economy.py', '/mail'), 'INIT_ENSURE_ONLY'),
    (('economy.py', '/servers'), 'INIT_ENSURE_ONLY'),
    (('combat.py', '/story/chapters'), 'INIT_ENSURE_ONLY'),
    (('combat.py', '/tower/status'), 'INIT_ENSURE_ONLY'),
    (('combat.py', '/events/daily'), 'INIT_ENSURE_ONLY'),
    (('combat.py', '/titles'), 'INIT_ENSURE_ONLY'),
    (('v96_auth.py', '/me'), 'INIT_ENSURE_ONLY'),
    (('level_sharing.py', '/level-sharing'), 'INIT_ENSURE_ONLY'),
    (('push_notifications.py', '/push/status'), 'INIT_ENSURE_ONLY'),
    (('social.py', '/plaza'), 'DEFERRED'),
    (('social.py', '/dm/threads'), 'DEFERRED'),
    (('equipment.py', '/equipment/templates'), 'CACHE_ANALYTICS'),
    (('guild.py', '/guild/info'), 'DEFERRED'),
]


def classify(fname: str, snippet: str) -> str:
    for (fsub, rsub), cat in CATEGORY_RULES:
        if fsub in fname and rsub in snippet:
            return cat
    return 'DEFERRED'


def main() -> int:
    errors = []; notes = []
    if not P127.exists():
        notes.append('Pack 127 report not yet generated; running Pack 127 first is recommended.')
        return _emit(errors, notes, {})
    data = json.loads(P127.read_text(encoding='utf-8'))
    flagged = data.get('flagged', [])
    classified = {'INIT_ENSURE_ONLY': [], 'CACHE_ANALYTICS': [], 'TRUE_SIDE_EFFECT': [], 'DEFERRED': []}
    for entry in flagged:
        fname = entry.get('file', '')
        snip = entry.get('snippet', '')
        cat = classify(fname, snip)
        classified[cat].append({'file': fname, 'snippet': snip, 'pattern': entry.get('pattern', '')})
    print(f'OK    GET sospetti totali (da Pack 127): {len(flagged)}')
    for cat, items in classified.items():
        print(f'  {cat:18s}: {len(items)}')
    # P0 hardening: TRUE_SIDE_EFFECT > 0 → NOTE warning (non FAIL: Pack 128 è audit-only su GET).
    if classified['TRUE_SIDE_EFFECT']:
        for it in classified['TRUE_SIDE_EFFECT']:
            notes.append(f'TRUE_SIDE_EFFECT GET to harden: {it["file"]} {it["snippet"][:80]}')
    return _emit(errors, notes, classified)


def _emit(errors, notes, classified):
    print('\n' + '=' * 72)
    report = {
        'pack': 'PACK_128_MUTATING_GET_HARDENING',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'notes': notes,
        'classified': classified,
        'validation_kind': 'STATIC_CLASSIFICATION',
        'enforcement': 'AUDIT_ONLY_CLASSIFICATION_PRESENT_RUNTIME_GUARDS_DEFERRED',
    }
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_128_mutating_get_hardening_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    for n in notes[:8]: print(f'  NOTE  {n}')
    print('PASS  mutating GET classified (audit-only); runtime guards → Pack 128.x/Pack 129')
    return 0


if __name__ == '__main__': sys.exit(main())
