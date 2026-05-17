#!/usr/bin/env python3
"""
CS2-E — Collection Synergy preview navigation entry audit.

Verifies:
  - the existing CS2-D screen file is present
  - a navigation entry pointing to /collection-synergies-preview exists
    in the central menu (frontend/app/(tabs)/menu.tsx) OR a justified
    plan-only fallback is documented
  - the screen is registered in /app/frontend/app/_layout.tsx
  - the navigation entry does NOT include any mutating button on the
    same line (no claim/activate/spend/equip/upgrade/runtime tokens
    co-located with the route)
  - the screen file remains strictly read-only (re-run of CS2-D core
    checks)
  - no Borea reveal in the menu entry

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path('/app')
SCREEN = ROOT / 'frontend' / 'app' / 'collection-synergies-preview.tsx'
MENU = ROOT / 'frontend' / 'app' / '(tabs)' / 'menu.tsx'
LAYOUT = ROOT / 'frontend' / 'app' / '_layout.tsx'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Screen present
record('screen_present', SCREEN.exists(), str(SCREEN))
src_screen = SCREEN.read_text(encoding='utf-8') if SCREEN.exists() else ''

# 2. Layout registration
record('layout_present', LAYOUT.exists(), str(LAYOUT))
layout_src = LAYOUT.read_text(encoding='utf-8') if LAYOUT.exists() else ''
record('layout_registers_screen',
       'name="collection-synergies-preview"' in layout_src
       or "name='collection-synergies-preview'" in layout_src,
       'Stack.Screen must register collection-synergies-preview')

# 3. Menu entry present
record('menu_present', MENU.exists(), str(MENU))
menu_src = MENU.read_text(encoding='utf-8') if MENU.exists() else ''
record('menu_entry_route_present',
       '/collection-synergies-preview' in menu_src,
       'menu must contain route /collection-synergies-preview')
record('menu_entry_label_present',
       'Sinergie Collezione' in menu_src,
       'menu must contain label "Sinergie Collezione"')

# 4. The menu entry line MUST NOT contain mutating tokens
MUTATING_TOKENS = [
    r"\bclaim\b", r"\bactivate\b", r"\bspend\b", r"\bequip\b",
    r"\bupgrade\b", r"enable[_-]?runtime", r"\bsummon\b",
    r"break[_-]?seal", r"battle[_-]?test",
]
menu_lines = menu_src.splitlines()
entry_lines = [
    (i + 1, ln) for i, ln in enumerate(menu_lines)
    if '/collection-synergies-preview' in ln
]
record('menu_entry_lines_found', len(entry_lines) >= 1,
       f'expected at least 1 entry line; got {len(entry_lines)}')
bad_lines = []
for line_no, ln in entry_lines:
    for pat in MUTATING_TOKENS:
        if re.search(pat, ln, re.IGNORECASE):
            bad_lines.append(f'line {line_no}: {pat} -> {ln.strip()}')
record('menu_entry_no_mutating_tokens', not bad_lines, f'hits={bad_lines}')

# 5. No Borea exposure in menu entry
borea_hits = []
for line_no, ln in entry_lines:
    if re.search(r'borea', ln, re.IGNORECASE):
        borea_hits.append(f'line {line_no}: {ln.strip()}')
record('menu_entry_no_borea_exposure', not borea_hits, f'hits={borea_hits}')

# 6. Recheck strictness on screen (no mutation HTTP, no DB strings)
MUT_PATS = [
    r'method:\s*["\']POST["\']', r'method:\s*["\']PUT["\']',
    r'method:\s*["\']PATCH["\']', r'method:\s*["\']DELETE["\']',
    r'axios\.(post|put|patch|delete)\s*\(',
]
mut_hits = []
for pat in MUT_PATS:
    if re.search(pat, src_screen, re.IGNORECASE):
        mut_hits.append(pat)
record('screen_no_mutation_http', not mut_hits, f'hits={mut_hits}')

DB_PATS = [
    r'/api/affinity/gift-?spend',
    r'/api/synergies/collection/(claim|spend|activate)',
    r'user_gift_inventory', r'gift_transaction_ledger',
]
db_hits = [p for p in DB_PATS if re.search(p, src_screen, re.IGNORECASE)]
record('screen_no_db_strings', not db_hits, f'hits={db_hits}')

# 7. Banner present on screen
record('screen_has_design_only_banner',
       'Design-only' in src_screen or 'design-only' in src_screen
       or 'non attivo' in src_screen.lower(), '')


print('=' * 70)
print('CS2-E — Collection Synergy Preview Navigation Entry Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
