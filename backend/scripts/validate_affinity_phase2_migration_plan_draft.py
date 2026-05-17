#!/usr/bin/env python3
"""
AF2-D — Validator for affinity_phase2_migration_plan_draft_v1.json.

Verifies:
  - plan file present and parses
  - design_only=true / migration_applied=false / db_write=false
  - target_future_collections contains exactly the three AF2-C collections
  - migration gates enumerated and `currently_satisfied` flags are False
  - no migration file created in backend/migrations or top-level migrations
  - no new POST/PUT/PATCH/DELETE route added (grep backend/routes)
  - no DB write route added
  - schema references AF2-C files
  - Borea locked
  - hidden aliases listed

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
PLAN = ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_migration_plan_draft_v1.json'
SCHEMA = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_inventory_schema_draft_v1.json'
ANTI = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_anti_exploit_policy_v1.json'
BACKEND_ROUTES = ROOT / 'backend' / 'routes'
MIGRATION_DIRS = [
    ROOT / 'backend' / 'migrations',
    ROOT / 'migrations',
    ROOT / 'backend' / 'scripts' / 'migrations',
]

failures: list[str] = []
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

# 2. Identity + flags
record('plan_id',
       plan.get('plan_id') == 'affinity_phase2_migration_plan_draft_v1', '')
record('task_origin', plan.get('task_origin') == 'AF2-D', '')
for k, v in [('design_only', True), ('migration_applied', False),
             ('runtime_attached', False), ('applied_to_combat', False),
             ('db_write', False), ('no_borea_activation', True)]:
    record(f'plan_flag_{k}', plan.get(k) == v,
           f'expected {v}, got {plan.get(k)!r}')

# 3. Target future collections
tfc = plan.get('target_future_collections') or []
names = {c.get('name') for c in tfc if isinstance(c, dict)}
for required in ['user_gift_inventory', 'gift_transaction_ledger',
                 'hero_affinity_state']:
    record(f'target_collection:{required}', required in names, '')
for c in tfc:
    if not isinstance(c, dict):
        continue
    n = c.get('name')
    record(f'target_collection_no_migration:{n}',
           c.get('create_in_migration') is False, '')
    record(f'target_collection_design_only_today:{n}',
           c.get('is_design_only_today') is True, '')
    # Each must have at least one proposed index
    idx = c.get('indexes_future') or []
    record(f'target_collection_has_indexes:{n}', len(idx) >= 1, '')

# 4. Migration gates
gates = plan.get('migration_gates') or []
gate_ids = {g.get('id') for g in gates if isinstance(g, dict)}
for required in ['auth_model_approved', 'endpoint_design_approved',
                 'rollback_tested', 'rate_limits_configured',
                 'borea_visibility_gate_tested', 'economy_finalized',
                 'stack_b_global_cap_resolver_audited']:
    record(f'migration_gate:{required}', required in gate_ids,
           f'missing gate: {required}')
# All gates currently NOT satisfied
for g in gates:
    if not isinstance(g, dict):
        continue
    record(f'gate_not_satisfied:{g.get("id")}',
           g.get('currently_satisfied') is False,
           f'gate must be unsatisfied today')

# 5. Schema references AF2-C files
sr = plan.get('source_references') or {}
record('source_ref_schema_draft',
       sr.get('schema_draft', '').endswith('affinity_gift_inventory_schema_draft_v1.json'), '')
record('source_ref_anti_exploit',
       sr.get('anti_exploit_policy', '').endswith('affinity_gift_anti_exploit_policy_v1.json'), '')

# 6. Borea locked + hidden aliases listed
sf = plan.get('safety_flags') or {}
record('safety_borea_activation_false',
       sf.get('borea_activation_allowed') is False, '')
record('safety_hidden_aliases',
       set(sf.get('hidden_aliases_blocked') or []) >= {'borea', 'primordial_gaia'}, '')

# 7. No migration file created
mig_hits = []
for d in MIGRATION_DIRS:
    if d.exists():
        for f in d.rglob('*'):
            if not f.is_file():
                continue
            n = f.name.lower()
            if 'affinity' in n and ('gift' in n or 'inventory' in n or 'ledger' in n):
                mig_hits.append(str(f))
record('no_affinity_migration_file_created', not mig_hits,
       f'unexpected: {mig_hits}')

# 8. No DB write route / no new POST endpoint for affinity gift spend
# Scope: AF2-D forbids new affinity *gift / inventory / spend / ledger* routes.
# The pre-existing /sanctuary/affinity/gain endpoint (Sanctuary subsystem,
# independent of Phase 2 gift catalog) is NOT in scope and is explicitly excluded.
endpoint_hits = []
if BACKEND_ROUTES.exists():
    for py in BACKEND_ROUTES.rglob('*.py'):
        if not py.is_file():
            continue
        # Skip pre-existing independent sanctuary affinity surface
        if py.name == 'sanctuary.py':
            continue
        # Skip AF2-G disabled gift-spend skeleton (explicitly authorized; always 423, no write).
        if py.name == 'affinity_gift_spend.py':
            continue
        t = py.read_text(encoding='utf-8', errors='ignore')
        # Mutation endpoints on the AF2 gift/inventory/spend paths
        if re.search(
            r'@router\.(post|put|patch|delete)\s*\(\s*["\'][^"\']*'
            r'affinity[^"\']*(?:gift|inventory|spend|ledger|grant)',
            t, re.IGNORECASE,
        ):
            endpoint_hits.append(
                f'{py}: mutation decorator on affinity gift/inventory/spend path'
            )
record('no_affinity_mutation_endpoint', not endpoint_hits,
       f'hits={endpoint_hits}')

# 9. Refs to AF2-C schema/anti present
record('schema_file_present_for_reference', SCHEMA.exists(), '')
record('anti_file_present_for_reference', ANTI.exists(), '')

# 10. Anti-exploit vectors inherited
av = (plan.get('anti_exploit_references_af2c') or {}).get('vectors_inherited') or []
for required in ['double_spend_replay', 'borea_leak', 'tides_orphan_gift']:
    record(f'inherits_anti_vector:{required}', required in av, '')

# 11. Privacy / right_to_erasure documented
ps = plan.get('privacy_safety') or {}
record('privacy_right_to_erasure',
       ps.get('right_to_erasure_supported') is True, '')

# 12. Top-level no-creation flags
record('no_migration_file_created_in_this_task',
       plan.get('no_migration_file_created_in_this_task') is True, '')
record('no_db_write_route_added_in_this_task',
       plan.get('no_db_write_route_added_in_this_task') is True, '')
record('no_endpoint_added_in_this_task',
       plan.get('no_endpoint_added_in_this_task') is True, '')


print('=' * 70)
print('AF2-D — Affinity Phase 2 Migration Plan Draft Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
