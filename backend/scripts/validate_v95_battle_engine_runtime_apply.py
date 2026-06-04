#!/usr/bin/env python3
"""v95 — Validator: Battle Engine Runtime Apply.

Verifica che la patch runtime in backend/battle_engine.py sia applicata:
- presenza dei helper v95 (_v95_apply_dot_with_stack_policy, _v95_apply_cleanse,
  _v95_has_immunity, _v95_maybe_convert_boss_hardcontrol);
- V95_ENGINE_STATUS_DOT_METADATA["applied_runtime"] == "runtime_apply_active";
- process_status_effects ha la signature estesa (v95_counters);
- battle report extension fields presenti nel modulo.
"""
import os, sys, inspect
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))
import battle_engine as be  # noqa: E402

failures = []

meta = getattr(be, 'V95_ENGINE_STATUS_DOT_METADATA', None)
if not meta:
    failures.append('V95_ENGINE_STATUS_DOT_METADATA missing')
else:
    if meta.get('applied_runtime') != 'runtime_apply_active':
        failures.append(f"applied_runtime != runtime_apply_active (got {meta.get('applied_runtime')})")

for name in ('_v95_apply_dot_with_stack_policy', '_v95_apply_cleanse', '_v95_has_immunity', '_v95_maybe_convert_boss_hardcontrol', '_v95_is_boss'):
    if not hasattr(be, name):
        failures.append(f'helper missing: {name}')

sig = inspect.signature(be.process_status_effects)
if 'v95_counters' not in sig.parameters:
    failures.append('process_status_effects missing v95_counters param')

# expected battle report fields in metadata
for f in ("dot_damage_done", "status_applied_count", "healing_done", "cleanse_count", "status_prevented_by_immunity_count", "taunt_redirect_count"):
    if f not in (meta or {}).get('battle_report_extension_fields', []):
        failures.append(f'metadata missing battle report field: {f}')

if failures:
    print('FAIL — v95 battle engine runtime apply:')
    for x in failures:
        print(' -', x)
    sys.exit(1)
print('PASS — v95 battle engine runtime apply')
sys.exit(0)
