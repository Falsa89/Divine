#!/usr/bin/env python3
"""
CS2-C — Collection Synergy UI preview contract audit.

Validates the design contract file and confirms that:
  - the contract is design-only / inert
  - no UI stub was created in this task
  - the strict no-mutation policy is documented
  - existing UI files do not contain any CS-context mutation buttons
  - Borea hidden handling is enforced

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
CONTRACT = ROOT / 'data' / 'design' / 'ui' / 'collection_synergy_preview_screen_contract_v1.json'
FRONTEND_APP = ROOT / 'frontend' / 'app'
OPTIONAL_STUB = FRONTEND_APP / 'collection-synergies-preview.tsx'

EXISTING_UI_FILES = [
    FRONTEND_APP / 'synergy-codex.tsx',
    FRONTEND_APP / 'hero-detail.tsx',
]

CONTEXT_TOKENS = ['collection', 'synergy', 'milestone']
FORBIDDEN_PATTERNS_CTX = [
    r'collection[_-]?claim',
    r'collection[_-]?activate',
    r'collection[_-]?spend',
    r'collection[_-]?equip',
    r'enable[_-]?collection[_-]?runtime',
    r'apply[_-]?collection[_-]?buff',
    r'COLLECTION_SYNERGY_BATTLE_ENABLED\s*=\s*["\']?true_explicit_collection_runtime_on',
]
MUTATION_FETCH_PATTERNS = [
    r'method:\s*["\']POST["\']',
    r'method:\s*["\']PUT["\']',
    r'method:\s*["\']PATCH["\']',
    r'method:\s*["\']DELETE["\']',
    r'fetch\([^)]*POST',
    r'axios\.(post|put|patch|delete)\s*\(',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Contract present
record('contract_present', CONTRACT.exists(), str(CONTRACT))
try:
    c = json.loads(CONTRACT.read_text(encoding='utf-8'))
    record('contract_parses', True, '')
except Exception as e:
    c = {}
    record('contract_parses', False, f'{e!r}')

# 2. Identity
record('contract_id', c.get('contract_id') == 'collection_synergy_preview_screen_contract_v1',
       f'got {c.get("contract_id")}')
record('task_origin', c.get('task_origin') == 'CS2-C', f'got {c.get("task_origin")}')
for k, v in [('design_only', True), ('runtime_attached', False),
             ('applied_to_combat', False), ('db_write', False),
             ('no_borea_activation', True),
             ('ui_implementation_in_this_task', False)]:
    record(f'contract_flag_{k}', c.get(k) == v,
           f'expected {v}, got {c.get(k)!r}')

# 3. Data sources documented (CS2-A + CS2-B)
ds = [d.get('id') for d in (c.get('data_sources') or []) if isinstance(d, dict)]
for required in ['cs2a_readiness_plan', 'cs2b_resolver_preview_output']:
    record(f'data_source_present:{required}', required in ds, f'got {ds}')

# 4. Screen goals
sg = [g.get('id') for g in (c.get('screen_goals') or []) if isinstance(g, dict)]
for required in ['show_collection_categories', 'show_milestone_model',
                 'show_cap_policy', 'show_locked_future_badges',
                 'show_borea_locked_state', 'show_readonly_disclaimer']:
    record(f'screen_goal:{required}', required in sg, f'got {sg}')

# 5. Forbidden actions
fa = c.get('forbidden_ui_actions') or []
for required in ['claim', 'activate', 'spend', 'equip', 'enable_runtime',
                 'apply_buff', 'POST', 'PUT', 'PATCH', 'DELETE']:
    record(f'forbidden_ui_action:{required}', required in fa, f'got {fa}')

# 6. Borea hidden handling
bh = c.get('borea_hidden_handling') or {}
record('borea_legacy_blocked',
       set(bh.get('legacy_aliases_blocked') or []) >= {'borea', 'primordial_gaia'}, '')
record('borea_greek_borea_status',
       bh.get('greek_borea_status') == 'catalog_only_hidden_until_global_unlock', '')

# 7. UI stub: if created, must be strictly read-only.
if OPTIONAL_STUB.exists():
    txt = OPTIONAL_STUB.read_text(encoding='utf-8', errors='ignore')
    # Mutation HTTP methods
    mut_hits = []
    for pat in MUTATION_FETCH_PATTERNS:
        for m in re.finditer(pat, txt, re.IGNORECASE):
            mut_hits.append(f'{OPTIONAL_STUB.name}:{pat}')
    record('optional_stub_no_mutation_fetch', not mut_hits, f'hits={mut_hits}')
    # Forbidden CS action tokens
    cs_hits = []
    for pat in FORBIDDEN_PATTERNS_CTX:
        for m in re.finditer(pat, txt, re.IGNORECASE):
            cs_hits.append(f'{OPTIONAL_STUB.name}:{pat}')
    record('optional_stub_no_forbidden_cs_action', not cs_hits, f'hits={cs_hits}')
else:
    record('optional_stub_not_created', True, 'plan-only (preferred)')

# 8. Existing UI files: context-aware grep
def _has_cs_ctx(window: str) -> bool:
    low = window.lower()
    return any(t in low for t in CONTEXT_TOKENS)


for f in EXISTING_UI_FILES:
    if not f.exists():
        record(f'ui_file_present:{f.name}', True, f'{f} absent (skipped)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    lines = txt.splitlines()
    hits = []
    for pat in FORBIDDEN_PATTERNS_CTX:
        for m in re.finditer(pat, txt, re.IGNORECASE):
            line_no = txt.count('\n', 0, m.start())
            lo = max(0, line_no - 2)
            hi = min(len(lines), line_no + 3)
            window = '\n'.join(lines[lo:hi])
            if _has_cs_ctx(window):
                hits.append(f'{f.name}:{line_no+1}:{pat}')
    record(f'existing_ui_no_cs_mutation:{f.name}', not hits, f'hits={hits}')

# 9. No new runtime endpoint
ROUTES_DIR = ROOT / 'backend' / 'routes'
endpoint_hits = []
if ROUTES_DIR.exists():
    for py in ROUTES_DIR.rglob('*.py'):
        if not py.is_file():
            continue
        t = py.read_text(encoding='utf-8', errors='ignore')
        for pat in [r'/api/synergies/collection/(claim|spend|activate|enable)']:
            if re.search(pat, t):
                endpoint_hits.append(f'{py}:{pat}')
record('no_new_runtime_collection_endpoint', not endpoint_hits,
       f'hits={endpoint_hits}')


print('=' * 70)
print('CS2-C — Collection Synergy UI Preview Contract Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
