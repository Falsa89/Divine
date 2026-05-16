#!/usr/bin/env python3
"""
CS2-B — Safety audit for the Collection Synergy preview resolver skeleton.

Verifies:
  - feature flag default is False
  - common truthy tokens (true/1/yes/on/TRUE) do NOT enable the runtime
  - disabled result helper returns the canonical inert envelope
  - preview functions return applied_to_combat=False, runtime_attached=False,
    db_write=False and never live numeric buffs
  - battle_engine.py / combat.tsx / battle_core.py do NOT import this resolver
  - no Borea activation, no DB writes are introduced

Read-only. Never mutates catalogs/DB/runtime.
Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

ROOT = Path('/app')
RESOLVER_PATH = ROOT / 'backend' / 'data' / 'collection_synergy_preview_resolver.py'

# Live runtime files which MUST NOT import the resolver
LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

# Common truthy tokens that must NOT enable the runtime
COMMON_TRUTHY = ['true', '1', 'yes', 'on', 'TRUE', 'True', 'enabled']

failures: list[str] = []
warnings: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Import resolver
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import collection_synergy_preview_resolver as csr  # type: ignore
    record('import_resolver', True, '')
except Exception as e:
    record('import_resolver', False, f'cannot import resolver: {e!r}')
    print('FAIL: cannot import resolver; aborting audit')
    for n, ok, note in checks:
        print(f'  [{ "OK" if ok else "X" }] {n} {note}')
    sys.exit(1)


# 2. Flag default false (env not set)
os.environ.pop('COLLECTION_SYNERGY_BATTLE_ENABLED', None)
record('flag_default_off', csr.is_collection_synergy_runtime_enabled() is False,
       'expected False when env not set')


# 3. Common truthy tokens must keep flag False
for t in COMMON_TRUTHY:
    os.environ['COLLECTION_SYNERGY_BATTLE_ENABLED'] = t
    ok = csr.is_collection_synergy_runtime_enabled() is False
    record(f'flag_truthy_token_rejected:{t}', ok,
           f'token "{t}" must not enable runtime')
os.environ.pop('COLLECTION_SYNERGY_BATTLE_ENABLED', None)


# 4. Disabled result envelope
d = csr.get_disabled_collection_runtime_result()
record('disabled_result_shape', isinstance(d, dict), 'must be dict')
for k, v in (('enabled', False), ('runtime_attached', False),
             ('battle_runtime_attached', False), ('applied_to_combat', False),
             ('db_write', False), ('is_disabled_collection_runtime_result', True)):
    record(f'disabled_result_{k}', d.get(k) == v, f'expected {k}={v}, got {d.get(k)!r}')


# 5. Preview functions inert
cats = csr.preview_collection_synergy_categories()
record('preview_categories_runtime_attached_false',
       cats.get('runtime_attached') is False, '')
record('preview_categories_applied_to_combat_false',
       cats.get('applied_to_combat') is False, '')
record('preview_categories_db_write_false',
       cats.get('db_write') is False, '')
record('preview_categories_has_count',
       isinstance(cats.get('count'), int), 'count must be int')

pol = csr.preview_collection_milestone_policy()
record('preview_policy_runtime_attached_false',
       pol.get('runtime_attached') is False, '')
record('preview_policy_applied_to_combat_false',
       pol.get('applied_to_combat') is False, '')
record('preview_policy_db_write_false',
       pol.get('db_write') is False, '')

mock = csr.preview_collection_synergy_for_mock_roster([
    'greek_athena', 'greek_zeus', 'borea', 'primordial_gaia',
])
record('preview_mock_runtime_attached_false',
       mock.get('runtime_attached') is False, '')
record('preview_mock_applied_to_combat_false',
       mock.get('applied_to_combat') is False, '')
record('preview_mock_db_write_false',
       mock.get('db_write') is False, '')
record('preview_mock_no_buffs',
       mock.get('computed_buffs') is None, 'computed_buffs must be None')
record('preview_mock_forbidden_filtered',
       'borea' in mock.get('forbidden_filtered_out', []) and
       'primordial_gaia' in mock.get('forbidden_filtered_out', []),
       'forbidden hero ids must be filtered out')


# 6. Live battle files must not reference the resolver
tokens = [
    'collection_synergy_preview_resolver',
    'preview_collection_synergy_categories',
    'preview_collection_milestone_policy',
    'preview_collection_synergy_for_mock_roster',
    'get_disabled_collection_runtime_result',
]
for f in LIVE_FILES:
    if not f.exists():
        # If battle_engine.py is absent, no harm; just record absence
        record(f'live_file_present:{f.name}', True, f'{f} absent (skipped grep)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in tokens:
        ok = re.search(re.escape(tok), txt) is None
        record(f'no_runtime_import:{f.name}:{tok}', ok,
               f'token "{tok}" found in {f}' if not ok else '')


# 7. Manifest sanity
m = getattr(csr, 'ADAPTER_MANIFEST', {})
record('manifest_writes_to_db_false', m.get('writes_to_db') is False, '')
record('manifest_writes_to_catalogs_false', m.get('writes_to_catalogs') is False, '')
record('manifest_writes_to_runtime_false', m.get('writes_to_runtime') is False, '')
record('manifest_imported_by_battle_engine_false',
       m.get('imported_by_battle_engine') is False, '')
record('manifest_imported_by_combat_tsx_false',
       m.get('imported_by_combat_tsx') is False, '')
record('manifest_applied_to_combat_false',
       m.get('applied_to_combat') is False, '')
record('manifest_no_borea_activation_true',
       m.get('no_borea_activation') is True, '')


# 8. Report
print('=' * 70)
print('CS2-B — Collection Synergy Preview Resolver Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
