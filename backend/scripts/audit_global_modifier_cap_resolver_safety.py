#!/usr/bin/env python3
"""
STACK-B — Global Modifier Cap Resolver safety audit.

Verifies:
  - feature flag default is False
  - common truthy tokens (true/1/yes/on/TRUE) do NOT enable runtime
  - disabled_result envelope is canonical
  - preview_stack_policy / preview_cap_sources / preview_combined_cap
    all return runtime_attached=False / applied_to_combat=False / db_write=False
  - battle_engine.py / combat.tsx / battle_core.py do NOT import this resolver
  - no DB/API/UI route created
  - cap principles match the cross-system stack safety report
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path('/app')
RESOLVER_PATH = ROOT / 'backend' / 'data' / 'global_modifier_cap_resolver.py'
STACK_REPORT = ROOT / 'data' / 'design' / 'system_safety' / 'cross_system_progression_stack_safety_report_v1.json'
LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]
BACKEND_ROUTES = ROOT / 'backend' / 'routes'
FRONTEND_APP = ROOT / 'frontend' / 'app'

COMMON_TRUTHY = ['true', '1', 'yes', 'on', 'TRUE', 'True', 'enabled']

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Import resolver
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import global_modifier_cap_resolver as gmcr  # type: ignore
    record('import_resolver', True, '')
except Exception as e:
    record('import_resolver', False, f'cannot import: {e!r}')
    for n, ok, note in checks:
        print(f'  [{ "OK" if ok else "X" }] {n} {note}')
    sys.exit(1)

# 2. Flag default OFF
os.environ.pop('GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED', None)
record('flag_default_off',
       gmcr.is_global_modifier_cap_resolver_enabled() is False, '')

# 3. Common truthy tokens rejected
for t in COMMON_TRUTHY:
    os.environ['GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED'] = t
    ok = gmcr.is_global_modifier_cap_resolver_enabled() is False
    record(f'flag_truthy_rejected:{t}', ok, f'token "{t}" must not enable')
os.environ.pop('GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED', None)

# 4. Disabled result envelope
d = gmcr.get_disabled_global_cap_result()
for k, v in [('enabled', False), ('runtime_attached', False),
             ('battle_runtime_attached', False), ('applied_to_combat', False),
             ('db_write', False), ('is_disabled_global_cap_result', True)]:
    record(f'disabled_result_{k}', d.get(k) == v, f'expected {k}={v}, got {d.get(k)!r}')

# 5. preview_stack_policy
psp = gmcr.preview_stack_policy()
for k in ['runtime_attached', 'applied_to_combat', 'db_write']:
    record(f'preview_stack_policy_{k}_false', psp.get(k) is False, '')
record('preview_stack_policy_cap_principles_present',
       isinstance(psp.get('cap_principles'), dict), '')

# 6. preview_cap_sources
pcs = gmcr.preview_cap_sources()
for k in ['runtime_attached', 'applied_to_combat', 'db_write']:
    record(f'preview_cap_sources_{k}_false', pcs.get(k) is False, '')
src_ids = {s.get('id') for s in (pcs.get('sources') or []) if isinstance(s, dict)}
for required in ['collection_synergy_v2', 'affinity_phase_2', 'divine_weapons',
                 'skill_kit_foundation', 'boss_policies']:
    record(f'preview_cap_source_present:{required}', required in src_ids, '')

# 7. preview_combined_cap — never returns live buff
mock = gmcr.preview_combined_cap(
    mock_sources=[
        {'id': 'collection', 'pct': 5},
        {'id': 'affinity', 'pct': 6},
        {'id': 'dw', 'pct': 5},
    ],
    context='pvp',
)
for k in ['runtime_attached', 'applied_to_combat', 'db_write']:
    record(f'preview_combined_cap_{k}_false', mock.get(k) is False, '')
record('preview_combined_cap_is_disabled_envelope',
       mock.get('is_disabled_global_cap_result') is True, '')
record('preview_combined_cap_clamped_pct_preview_not_none',
       mock.get('clamped_pct_preview') is not None, '')
record('preview_combined_cap_clamped_pct_le_target',
       isinstance(mock.get('clamped_pct_preview'), (int, float))
       and isinstance(mock.get('target_cap_pct_preview'), (int, float))
       and mock['clamped_pct_preview'] <= mock['target_cap_pct_preview'],
       'clamped must respect target cap')

# 8. battle_engine / battle_core / combat.tsx do NOT import this resolver
tokens = ['global_modifier_cap_resolver',
          'preview_combined_cap',
          'preview_stack_policy',
          'get_disabled_global_cap_result']
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file_present:{f.name}', True, f'absent (skipped)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in tokens:
        ok = re.search(re.escape(tok), txt) is None
        record(f'no_runtime_import:{f.name}:{tok}', ok,
               f'token found in {f}' if not ok else '')

# 9. No new DB/API/UI surface created
endpoint_hits = []
if BACKEND_ROUTES.exists():
    for py in BACKEND_ROUTES.rglob('*.py'):
        if not py.is_file():
            continue
        t = py.read_text(encoding='utf-8', errors='ignore')
        for pat in [r'/api/global_modifier_cap', r'/api/cap_resolver',
                    r'/api/global_cap']:
            if re.search(pat, t):
                endpoint_hits.append(f'{py}:{pat}')
record('no_new_endpoint', not endpoint_hits, f'hits={endpoint_hits}')

ui_hits = []
if FRONTEND_APP.exists():
    for tsx in FRONTEND_APP.rglob('*.tsx'):
        if not tsx.is_file():
            continue
        t = tsx.read_text(encoding='utf-8', errors='ignore')
        if re.search(r'global_modifier_cap_resolver', t, re.IGNORECASE):
            ui_hits.append(str(tsx))
record('no_ui_reference', not ui_hits, f'hits={ui_hits}')

# 10. Manifest sanity
m = getattr(gmcr, 'ADAPTER_MANIFEST', {})
for k in ['writes_to_db', 'writes_to_catalogs', 'writes_to_runtime',
          'imported_by_battle_engine', 'imported_by_battle_core',
          'imported_by_combat_tsx', 'applied_to_combat']:
    record(f'manifest_{k}_false', m.get(k) is False,
           f'expected False, got {m.get(k)!r}')
record('manifest_no_borea_activation', m.get('no_borea_activation') is True, '')

# 11. Cap principles consistency with stack report
if STACK_REPORT.exists():
    try:
        rep = json.loads(STACK_REPORT.read_text(encoding='utf-8'))
        rep_caps = rep.get('cap_recommendations_future_only') or {}
        record('caps_match_stack:collection_total',
               m.get('cap_principles', {}).get('collection_total_cap_pct')
               == rep_caps.get('collection_total_cap_pct'), '')
        record('caps_match_stack:collection_per_category',
               m.get('cap_principles', {}).get('collection_per_category_cap_pct')
               == rep_caps.get('collection_per_category_cap_pct'), '')
        record('caps_match_stack:affinity_total',
               m.get('cap_principles', {}).get('affinity_pvp_total_cap_pct')
               == rep_caps.get('affinity_pvp_total_cap_pct'), '')
        record('caps_match_stack:dw_global',
               m.get('cap_principles', {}).get('divine_weapon_global_cap_pct_future')
               == rep_caps.get('divine_weapon_global_cap_pct_future'), '')
    except Exception as e:
        record('caps_match_stack_report', False, f'{e!r}')


print('=' * 70)
print('STACK-B — Global Modifier Cap Resolver Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
