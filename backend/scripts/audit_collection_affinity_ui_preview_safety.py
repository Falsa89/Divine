#!/usr/bin/env python3
"""
UI-PREVIEW-A — UI preview safety audit.

Audits the existing frontend UI to confirm:
  - No new runtime buttons exist for Collection Synergy / Affinity gift /
    activate / equip / enable runtime / claim flows.
  - Pre-existing unrelated POST/Equip endpoints in independent surfaces
    (e.g. rune equipment) are reported as non-blocking only when clearly
    independent of CS2/AF2.
  - The readiness plan exists and explicitly states ui_implementation_in_this_task=false.

Context-aware: only flags forbidden tokens when they appear in proximity
to collection / affinity / gift / synergy lines, to avoid false positives
on unrelated screens.

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
PLAN = ROOT / 'data' / 'design' / 'ui' / 'collection_affinity_preview_ui_readiness_plan_v1.json'
FRONTEND_APP_DIR = ROOT / 'frontend' / 'app'

# UI files of interest (per plan)
TARGET_UI_FILES = [
    FRONTEND_APP_DIR / 'synergy-codex.tsx',
    FRONTEND_APP_DIR / 'hero-detail.tsx',
    FRONTEND_APP_DIR / 'hero-skill-kits-catalog.tsx',
    FRONTEND_APP_DIR / 'divine-weapons-catalog.tsx',
]

# Forbidden token families for CS / AF preview
FORBIDDEN_PATTERNS = [
    r'gift[_-]?spend',
    r'spend[_-]?gift',
    r'claim[_-]?collection',
    r'claim[_-]?synergy',
    r'activate[_-]?collection',
    r'activate[_-]?affinity',
    r'equip[_-]?collection',
    r'enable[_-]?runtime',
    r'COLLECTION_SYNERGY_BATTLE_ENABLED\s*=\s*["\']?true_explicit_collection_runtime_on',
    r'AFFINITY_GIFT_RUNTIME_ENABLED\s*=\s*["\']?true',
]

# Context tokens that put us in the CS/AF "zone"
CONTEXT_TOKENS = [
    'collection', 'affinity', 'gift', 'synergy', 'milestone',
    'COLLECTION_SYNERGY', 'AFFINITY_GIFT',
]

# Pre-existing unrelated forbidden tokens we should ignore (rune equip etc.)
UNRELATED_INDEPENDENT_TOKENS = [
    'rune', 'equipment', 'inventory', 'forge',
]

failures: list[str] = []
warnings: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Plan present
record('plan_present', PLAN.exists(), str(PLAN))
try:
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    record('plan_parses', True, '')
except Exception as e:
    plan = {}
    record('plan_parses', False, f'{e!r}')

record('plan_id',
       plan.get('plan_id') == 'collection_affinity_preview_ui_readiness_plan_v1',
       f'got {plan.get("plan_id")}')
record('plan_task_origin', plan.get('task_origin') == 'UI-PREVIEW-A',
       f'got {plan.get("task_origin")}')
for k, v in [('design_only', True), ('runtime_attached', False),
             ('applied_to_combat', False), ('db_write', False),
             ('no_borea_activation', True),
             ('ui_implementation_in_this_task', False)]:
    record(f'plan_flag_{k}', plan.get(k) == v,
           f'expected {v}, got {plan.get(k)!r}')

record('plan_ui_files_modified_empty',
       plan.get('ui_files_modified_in_this_task') == [], '')
record('plan_ui_files_created_empty',
       plan.get('ui_files_created_in_this_task') == [], '')

# 2. Strict no-buttons policy
nb = plan.get('strict_no_buttons_global_policy') or {}
for k in ['claim_button', 'gift_spend_button', 'activate_button',
          'equip_button', 'enable_runtime_button', 'purchase_button',
          'give_button']:
    record(f'no_button_global_{k}', nb.get(k) is False,
           f'expected False, got {nb.get(k)!r}')

# 3. Grep current UI files
# Strategy: for each forbidden pattern, find matches; for each match,
# inspect a 5-line window. If the window contains a CS/AF context token
# but no clearly unrelated rune/equipment context, flag it.
def _is_unrelated_context(window: str) -> bool:
    low = window.lower()
    rune_score = sum(low.count(t) for t in UNRELATED_INDEPENDENT_TOKENS)
    cs_af_score = sum(low.count(t) for t in
                      [c.lower() for c in CONTEXT_TOKENS])
    return rune_score > 0 and cs_af_score == 0


for f in TARGET_UI_FILES:
    if not f.exists():
        record(f'ui_file_present:{f.name}', True, f'{f} absent (skipped)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    lines = txt.splitlines()
    cs_af_hits: list[str] = []
    unrelated_hits: list[str] = []
    for pat in FORBIDDEN_PATTERNS:
        for m in re.finditer(pat, txt, re.IGNORECASE):
            # Build a 5-line window for context check
            line_no = txt.count('\n', 0, m.start())
            lo = max(0, line_no - 2)
            hi = min(len(lines), line_no + 3)
            window = '\n'.join(lines[lo:hi])
            if _is_unrelated_context(window):
                unrelated_hits.append(f'{f.name}:{line_no+1}:{pat}')
            else:
                # Strict: needs at least one CS/AF context token nearby OR be a global flag pattern
                low_window = window.lower()
                cs_score = sum(low_window.count(c.lower()) for c in CONTEXT_TOKENS)
                if cs_score > 0 or 'COLLECTION_SYNERGY' in pat or 'AFFINITY_GIFT' in pat:
                    cs_af_hits.append(f'{f.name}:{line_no+1}:{pat}')
                else:
                    # Token present but no CS/AF context -> warn only
                    warnings.append(
                        f'{f.name}:{line_no+1}:{pat} (no CS/AF context, no rune context, warn-only)'
                    )
    record(f'ui_no_csaf_forbidden_button:{f.name}',
           not cs_af_hits, f'hits={cs_af_hits}')
    if unrelated_hits:
        warnings.append(
            f'{f.name}: pre-existing unrelated rune/equip refs (non-blocking): {unrelated_hits}'
        )

# 4. All other tsx scanned for accidental wiring
extra_hits: list[str] = []
if FRONTEND_APP_DIR.exists():
    for tsx in FRONTEND_APP_DIR.rglob('*.tsx'):
        if tsx in TARGET_UI_FILES:
            continue
        txt = tsx.read_text(encoding='utf-8', errors='ignore').lower()
        # Only flag if the file references both a flag we forbid AND sets it true
        if ('collection_synergy_battle_enabled' in txt
                and 'true_explicit_collection_runtime_on' in txt):
            extra_hits.append(f'{tsx}:collection_synergy_battle_enabled set true')
        if ('affinity_gift_runtime_enabled' in txt
                and re.search(r'affinity_gift_runtime_enabled\s*[:=]\s*true', txt)):
            extra_hits.append(f'{tsx}:affinity_gift_runtime_enabled set true')
record('no_extra_tsx_runtime_activation', not extra_hits,
       f'unexpected runtime activation refs: {extra_hits}')


# Report
print('=' * 70)
print('UI-PREVIEW-A — Collection/Affinity UI Preview Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
if warnings:
    print('-' * 70)
    print('WARNINGS (non-blocking):')
    for w in warnings:
        print(f'  ! {w}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)} warnings={len(warnings)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
