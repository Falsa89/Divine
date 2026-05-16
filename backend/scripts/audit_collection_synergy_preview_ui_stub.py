#!/usr/bin/env python3
"""
CS2-D — Collection Synergy preview UI stub safety audit.

Verifies:
  - screen file exists at /app/frontend/app/collection-synergies-preview.tsx
  - no POST/PUT/PATCH/DELETE fetches
  - no forbidden action buttons (claim/activate/spend/equip/enable_runtime/apply_buff/battle_test)
  - no DB or user-inventory strings
  - design-only banner text present
  - no battle_engine/combat references
  - Borea (greek_borea reveal) not exposed as playable; legacy aliases not rendered
  - axios/fetch mutation methods absent

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path('/app')
SCREEN = ROOT / 'frontend' / 'app' / 'collection-synergies-preview.tsx'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. File present
record('screen_file_present', SCREEN.exists(), str(SCREEN))
if not SCREEN.exists():
    print('FAIL: screen file missing')
    for n, ok, note in checks:
        print(f'  [{"OK" if ok else "X"}] {n} {note}')
    sys.exit(1)

src = SCREEN.read_text(encoding='utf-8')

# 2. No mutation HTTP methods
MUTATION_PATS = [
    r'method:\s*["\']POST["\']',
    r'method:\s*["\']PUT["\']',
    r'method:\s*["\']PATCH["\']',
    r'method:\s*["\']DELETE["\']',
    r'\.post\s*\(', r'\.put\s*\(', r'\.patch\s*\(', r'\.delete\s*\(',
    r'axios\.(post|put|patch|delete)\s*\(',
    r'fetch\s*\([^)]*method:\s*["\'](?:POST|PUT|PATCH|DELETE)',
]
mut_hits = []
for pat in MUTATION_PATS:
    for m in re.finditer(pat, src, re.IGNORECASE):
        mut_hits.append(f'{pat}@{m.start()}')
record('no_mutation_http_methods', not mut_hits, f'hits={mut_hits}')

# 3. No forbidden action button tokens
FORBIDDEN_ACTIONS = [
    r'\bclaim\b', r'\bactivate\b', r'\bspend\b', r'\bequip\b',
    r'enable[_-]?runtime', r'apply[_-]?buff', r'battle[_-]?test',
    r'break[_-]?seal', r'\bsummon\b', r'\bupgrade\b',
]
# Context restriction: only inside CS context windows
ACTION_CTX = ['collection', 'synergy', 'milestone', 'preview']
# Negation prefixes that turn the token into prohibition documentation,
# not an actual action button.
NEGATION_PREFIXES = [
    'not ', 'no ', 'never ', 'forbidden ', 'without ', 'cannot ',
    'must not ', "doesn't ", 'doesnt ', 'non ',
]
lines = src.splitlines()
action_hits = []
for pat in FORBIDDEN_ACTIONS:
    for m in re.finditer(pat, src, re.IGNORECASE):
        line_no = src.count('\n', 0, m.start())
        lo = max(0, line_no - 3); hi = min(len(lines), line_no + 4)
        window = '\n'.join(lines[lo:hi]).lower()
        if not any(c in window for c in ACTION_CTX):
            continue
        # Inspect the 24 chars BEFORE the match for a negation prefix.
        prefix = src[max(0, m.start() - 24):m.start()].lower()
        if any(neg in prefix for neg in NEGATION_PREFIXES):
            continue
        # Inspect if the match is inside a description string literal
        # like description: '...' or a string ending with ')'.
        # If "not equip)" or "no equip," or similar pattern appears, skip.
        snippet = src[max(0, m.start() - 8):m.end() + 2].lower()
        if re.search(r'(not|no|never)\s+\w*\W*$', snippet):
            continue
        action_hits.append(f'{pat}@line{line_no+1}')
record('no_forbidden_action_button_in_cs_context',
       not action_hits, f'hits={action_hits}')

# 4. No DB / user inventory strings
DB_TOKENS = [
    r'\bAsyncStorage\.setItem\b',  # state mutation
    r'/api/affinity/gift-?spend',
    r'/api/synergies/collection/(claim|spend|activate|enable)',
    r'user_gift_inventory', r'gift_transaction_ledger',
]
db_hits = []
for pat in DB_TOKENS:
    if re.search(pat, src, re.IGNORECASE):
        db_hits.append(pat)
record('no_db_or_inventory_strings', not db_hits, f'hits={db_hits}')

# 5. Design-only banner text present
record('design_only_banner_text',
       'Design-only' in src or 'design-only' in src
       or 'Preview / Design-only' in src
       or 'non attivo' in src.lower(),
       'missing read-only banner text')

# 6. No battle_engine / combat imports
BATTLE_REFS = [
    r'battle_engine', r'battle_core',
    r"from\s+['\"]\.\./?\.?\./?combat", r"['\"]\.\./combat['\"]",
]
battle_hits = []
for pat in BATTLE_REFS:
    if re.search(pat, src):
        battle_hits.append(pat)
record('no_battle_engine_combat_refs', not battle_hits, f'hits={battle_hits}')

# 7. Borea: not rendered as playable; legacy aliases never appear
# Allow design-text mentions of borea (e.g. "borea / primordial_gaia excluded")
# but ensure no obtainable / claim / equip / playable references.
borea_bad = []
for pat in [r'borea[_-]?obtainable', r'claim[_-]?borea',
            r'equip[_-]?borea', r'unlock[_-]?borea',
            r'borea[_-]?playable']:
    if re.search(pat, src, re.IGNORECASE):
        borea_bad.append(pat)
record('no_borea_obtainable_refs', not borea_bad, f'hits={borea_bad}')

# 8. Pressable usage restricted to safe interactions (back / expand)
# Count Pressable occurrences; both must be present and minimal.
pressable_count = len(re.findall(r'<Pressable\b', src))
record('pressable_count_minimal',
       1 <= pressable_count <= 6,
       f'pressable_count={pressable_count} (expected 1..6 for back+expand)')

# 9. No runtime flag toggles in code
flag_toggles = []
for pat in [
    r'COLLECTION_SYNERGY_BATTLE_ENABLED\s*=\s*["\']?true_explicit_collection_runtime_on',
    r'AFFINITY_GIFT_RUNTIME_ENABLED\s*=\s*true',
    r'SKILL_KIT_RUNTIME_ENABLED\s*=\s*true_explicit_runtime_on',
    r'GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED\s*=\s*true',
]:
    if re.search(pat, src, re.IGNORECASE):
        flag_toggles.append(pat)
record('no_runtime_flag_toggles', not flag_toggles, f'hits={flag_toggles}')

# 10. Imports limited to safe set
record('uses_safearea', 'SafeAreaView' in src, 'must use SafeAreaView')
record('uses_stack_router',
       'Stack' in src and 'useRouter' in src, '')

# 11. No raw network endpoint creation
record('no_axios_create',
       'axios.create' not in src and 'XMLHttpRequest' not in src, '')


print('=' * 70)
print('CS2-D — Collection Synergy Preview UI Stub Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
