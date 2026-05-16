#!/usr/bin/env python3
"""
STACK-C — Edge case validator for global_modifier_cap_resolver.preview_combined_cap.

Runs all fixtures from global_modifier_cap_resolver_edge_case_fixtures_v1.json
against the inert resolver and asserts:
  - resolver flag remains OFF
  - every output is a disabled envelope (runtime_attached/applied_to_combat/db_write = False)
  - no exception raised
  - clamped_pct_preview <= target_cap (when target_cap present)
  - case-specific expected values match
  - resolver source file is not imported by battle_engine/combat/battle_core

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path('/app')
FIXTURES = ROOT / 'data' / 'design' / 'system_safety' / 'global_modifier_cap_resolver_edge_case_fixtures_v1.json'
LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import global_modifier_cap_resolver as gmcr  # type: ignore
    record('resolver_imported', True, '')
except Exception as e:
    record('resolver_imported', False, f'{e!r}')
    print('FAIL: cannot import resolver')
    sys.exit(1)

# Flag must remain OFF
os.environ.pop('GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED', None)
record('flag_off', gmcr.is_global_modifier_cap_resolver_enabled() is False, '')

# Fixtures present
record('fixtures_present', FIXTURES.exists(), str(FIXTURES))
try:
    fx = json.loads(FIXTURES.read_text(encoding='utf-8'))
    record('fixtures_parses', True, '')
except Exception as e:
    fx = {}
    record('fixtures_parses', False, f'{e!r}')

target_cap = fx.get('global_pvp_combined_target_cap_pct', 12)
cases = fx.get('cases') or []
record('fixtures_has_min_12_cases', len(cases) >= 12, f'got {len(cases)}')

for c in cases:
    if not isinstance(c, dict):
        continue
    cid = c.get('id')
    try:
        result = gmcr.preview_combined_cap(
            mock_sources=c.get('mock_sources'),
            context=c.get('context', 'pvp'),
        )
        record(f'{cid}:no_exception', True, '')
    except Exception as e:
        record(f'{cid}:no_exception', False, f'{e!r}')
        continue

    # Disabled envelope
    record(f'{cid}:is_disabled_envelope',
           result.get('is_disabled_global_cap_result') is True, '')
    for k in ['runtime_attached', 'applied_to_combat', 'db_write']:
        record(f'{cid}:envelope_{k}_false', result.get(k) is False, '')

    expected = c.get('expected') or {}

    # additive_sum_pct_preview
    if 'additive_sum_pct_preview' in expected:
        exp_sum = expected['additive_sum_pct_preview']
        got_sum = result.get('additive_sum_pct_preview')
        record(f'{cid}:additive_sum',
               isinstance(got_sum, (int, float))
               and abs(got_sum - exp_sum) < 1e-6,
               f'expected {exp_sum}, got {got_sum}')

    # target_cap presence
    if expected.get('target_cap_pct_preview_is_none'):
        record(f'{cid}:target_cap_is_none',
               result.get('target_cap_pct_preview') is None,
               f'got {result.get("target_cap_pct_preview")}')

    # clamped_pct_preview equals (when specified)
    if 'clamped_pct_preview_equals' in expected:
        exp_clamp = expected['clamped_pct_preview_equals']
        got_clamp = result.get('clamped_pct_preview')
        record(f'{cid}:clamped_equals',
               isinstance(got_clamp, (int, float))
               and abs(got_clamp - exp_clamp) < 1e-6,
               f'expected {exp_clamp}, got {got_clamp}')

    # clamped_pct_preview <= target (when target is numeric)
    if expected.get('clamped_pct_preview_le_target'):
        got_clamp = result.get('clamped_pct_preview')
        tgt = result.get('target_cap_pct_preview')
        if isinstance(tgt, (int, float)) and isinstance(got_clamp, (int, float)):
            record(f'{cid}:clamped_le_target',
                   got_clamp <= tgt,
                   f'got clamp={got_clamp} > target={tgt}')
        else:
            # No target -> trivially passes
            record(f'{cid}:clamped_le_target', True,
                   f'no numeric target (clamp={got_clamp}, target={tgt})')

# Global invariants
gi = fx.get('global_invariants') or {}
record('global_inv_feature_flag_off',
       gi.get('feature_flag_currently_enabled') is False, '')
record('global_inv_all_cases_disabled',
       gi.get('all_cases_disabled_envelope') is True, '')

# Resolver not imported by live runtime files
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    ok = 'global_modifier_cap_resolver' not in txt and 'preview_combined_cap' not in txt
    record(f'no_runtime_import:{f.name}', ok, f'token found' if not ok else '')


print('=' * 70)
print('STACK-C — Global Modifier Cap Resolver Edge Case Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
