#!/usr/bin/env python3
"""
STACK-F — Validator for debuff (negative pct) semantics.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

ROOT = Path('/app')
FIXTURES = ROOT / 'data' / 'design' / 'system_safety' / 'global_modifier_cap_resolver_debuff_semantics_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


sys.path.insert(0, str(ROOT / 'backend'))
from data import global_modifier_cap_resolver as gmcr  # type: ignore

os.environ.pop('GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED', None)
record('flag_off', gmcr.is_global_modifier_cap_resolver_enabled() is False, '')

record('fixtures_present', FIXTURES.exists(), str(FIXTURES))
fx = json.loads(FIXTURES.read_text(encoding='utf-8'))
record('fixtures_min_8_cases', len(fx.get('cases') or []) >= 8, '')
record('fixtures_floor_neg50', fx.get('debuff_floor_pct') == -50, '')

for c in fx.get('cases') or []:
    cid = c.get('id')
    try:
        r = gmcr.preview_combined_cap(
            mock_sources=c.get('mock_sources'),
            context=c.get('context', 'pvp'),
        )
        record(f'{cid}:no_exception', True, '')
    except Exception as e:
        record(f'{cid}:no_exception', False, f'{e!r}')
        continue
    record(f'{cid}:is_disabled_envelope',
           r.get('is_disabled_global_cap_result') is True, '')
    for k in ['runtime_attached', 'applied_to_combat', 'db_write']:
        record(f'{cid}:envelope_{k}_false', r.get(k) is False, '')

    e = c.get('expected') or {}
    if 'additive_sum_pct_preview' in e:
        exp = e['additive_sum_pct_preview']; got = r.get('additive_sum_pct_preview')
        record(f'{cid}:additive_sum',
               isinstance(got, (int, float)) and abs(got - exp) < 1e-6,
               f'expected {exp}, got {got}')
    if 'debuff_count' in e:
        exp = e['debuff_count']; got = r.get('debuff_count')
        record(f'{cid}:debuff_count', got == exp, f'expected {exp}, got {got}')
    if 'debuff_sum_pct_preview' in e:
        exp = e['debuff_sum_pct_preview']; got = r.get('debuff_sum_pct_preview')
        record(f'{cid}:debuff_sum',
               isinstance(got, (int, float)) and abs(got - exp) < 1e-6,
               f'expected {exp}, got {got}')
    if 'borea_locked_filtered_count' in e:
        exp = e['borea_locked_filtered_count']; got = r.get('borea_locked_filtered_count')
        record(f'{cid}:borea_filtered_count', got == exp, f'expected {exp}, got {got}')
    if 'multiplicative_rejected_count' in e:
        exp = e['multiplicative_rejected_count']; got = r.get('multiplicative_rejected_count')
        record(f'{cid}:mult_count', got == exp, f'expected {exp}, got {got}')
    if 'clamped_pct_preview_equals' in e:
        exp = e['clamped_pct_preview_equals']; got = r.get('clamped_pct_preview')
        record(f'{cid}:clamp_equals',
               isinstance(got, (int, float)) and abs(got - exp) < 1e-6,
               f'expected {exp}, got {got}')
    if 'first_debuff_clamped_pct' in e:
        debs = r.get('mock_sources_debuffs') or []
        clamped0 = debs[0].get('clamped_pct') if debs else None
        exp = e['first_debuff_clamped_pct']
        record(f'{cid}:first_debuff_clamped',
               isinstance(clamped0, (int, float)) and abs(clamped0 - exp) < 1e-6,
               f'expected {exp}, got {clamped0}')
    record(f'{cid}:debuff_never_converted_to_buff',
           r.get('debuff_never_converted_to_buff') is True, '')

# Resolver source
RSRC = (ROOT / 'backend' / 'data' / 'global_modifier_cap_resolver.py').read_text(encoding='utf-8')
record('resolver_source_handles_debuff',
       'debuff_floor_pct' in RSRC and 'mock_sources_debuffs' in RSRC, '')
record('resolver_payload_has_debuff_policy',
       'debuff_policy' in RSRC, '')

print('=' * 70)
print('STACK-F — Debuff Semantics Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
