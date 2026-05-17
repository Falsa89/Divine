#!/usr/bin/env python3
"""
STACK-D — Validator for multiplicative rejection in
global_modifier_cap_resolver.preview_combined_cap.

Runs every fixture in
`global_modifier_cap_resolver_multiplicative_rejection_fixtures_v1.json`
and asserts:
  - resolver flag remains OFF
  - every output is a disabled envelope (is_disabled_global_cap_result=true,
    runtime_attached/applied_to_combat/db_write = False)
  - multiplicative sources are NOT included in additive_sum_pct_preview
  - rejected count matches expected
  - clamped_pct_preview behavior matches expected
  - no exception
  - resolver source file is not imported by battle_engine / battle_core / combat.tsx
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path('/app')
FIXTURES = ROOT / 'data' / 'design' / 'system_safety' / 'global_modifier_cap_resolver_multiplicative_rejection_fixtures_v1.json'
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

record('fixtures_design_only', fx.get('design_only') is True, '')
record('fixtures_runtime_attached_false', fx.get('runtime_attached') is False, '')
record('fixtures_min_10_cases', len(fx.get('cases') or []) >= 10, '')

# Validate resolver source carries the rejection policy
RESOLVER_SRC = ROOT / 'backend' / 'data' / 'global_modifier_cap_resolver.py'
rsrc = RESOLVER_SRC.read_text(encoding='utf-8') if RESOLVER_SRC.exists() else ''
record('resolver_source_handles_multiplicative',
       'multiplicative' in rsrc.lower(), '')
record('resolver_source_has_rejected_field',
       'mock_sources_rejected_multiplicative' in rsrc, '')

# Run each case
for c in fx.get('cases') or []:
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
    # additive_sum
    if 'additive_sum_pct_preview' in expected:
        exp = expected['additive_sum_pct_preview']
        got = result.get('additive_sum_pct_preview')
        record(f'{cid}:additive_sum',
               isinstance(got, (int, float)) and abs(got - exp) < 1e-6,
               f'expected {exp}, got {got}')

    # multiplicative_rejected_count
    if 'multiplicative_rejected_count' in expected:
        exp = expected['multiplicative_rejected_count']
        got = result.get('multiplicative_rejected_count')
        record(f'{cid}:rejected_count', got == exp,
               f'expected {exp}, got {got}')

    # target_cap is None
    if expected.get('target_cap_pct_preview_is_none'):
        record(f'{cid}:target_cap_is_none',
               result.get('target_cap_pct_preview') is None,
               f'got {result.get("target_cap_pct_preview")}')

    # clamped_pct_preview equals
    if 'clamped_pct_preview_equals' in expected:
        exp = expected['clamped_pct_preview_equals']
        got = result.get('clamped_pct_preview')
        record(f'{cid}:clamped_equals',
               isinstance(got, (int, float)) and abs(got - exp) < 1e-6,
               f'expected {exp}, got {got}')

    # clamped_pct_preview <= target
    if expected.get('clamped_pct_preview_le_target'):
        got = result.get('clamped_pct_preview')
        tgt = result.get('target_cap_pct_preview')
        if isinstance(tgt, (int, float)) and isinstance(got, (int, float)):
            record(f'{cid}:clamped_le_target', got <= tgt,
                   f'got clamp={got} > target={tgt}')
        else:
            record(f'{cid}:clamped_le_target', True, 'no numeric target')

    # multiplicative_policy field
    record(f'{cid}:policy_rejected_preview_only',
           result.get('multiplicative_policy') == 'rejected_preview_only', '')
    record(f'{cid}:multiplicative_forbidden_initial',
           result.get('multiplicative_forbidden_in_initial_runtime') is True, '')

# Resolver not imported by live runtime files
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    ok = 'global_modifier_cap_resolver' not in txt and 'preview_combined_cap' not in txt
    record(f'no_runtime_import:{f.name}', ok, f'token found' if not ok else '')


print('=' * 70)
print('STACK-D — Multiplicative Rejection Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
