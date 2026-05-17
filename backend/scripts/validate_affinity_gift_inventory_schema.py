#!/usr/bin/env python3
"""
AF2-C — Validator for the affinity gift inventory schema draft and
anti-exploit policy.

Verifies:
  - schema draft + anti-exploit policy + economy policy + gift catalog all exist
  - all design_only / runtime_attached=false / db_write=false
  - proposed_collections include user_gift_inventory_future,
    gift_transaction_ledger_future, hero_affinity_state_future
  - required integrity constraints present
  - Borea locked
  - tides not minted
  - no adult naming
  - no migration / no endpoint / no UI button created
  - PvP caps inherited (<=2 source / <=6 total)

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
SCHEMA = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_inventory_schema_draft_v1.json'
ANTI = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_anti_exploit_policy_v1.json'
ECONOMY = ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_economy_cap_policy_draft_v1.json'
GIFT_CATALOG = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'

BACKEND_ROUTES = ROOT / 'backend' / 'routes'
FRONTEND_APP = ROOT / 'frontend' / 'app'
MIGRATIONS_DIRS = [ROOT / 'backend' / 'migrations', ROOT / 'migrations']

ENDPOINT_PATTERNS = [
    r'/api/affinity/gift-?spend',
    r'/api/affinity/gift_spend',
    r'/api/affinity/spend',
    r'/api/affinity/inventory',
    r'/api/affinity/grant',
]
UI_BUTTON_PATTERNS = [
    r'gift[_-]?spend[_-]?button', r'spend[_-]?gift[_-]?button',
    r'claim[_-]?gift[_-]?button', r'gift[_-]?inventory[_-]?button',
]
# Adult blacklist: context-aware to exclude *_forbidden / no_adult_* docs
ADULT_BLACKLIST = ['nsfw', 'lewd', 'erotic', 'porn', 'xxx', 'explicit_sex']
ADULT_CONTEXT_REGEX = re.compile(
    r'(?<![a-z_])adult(?![a-z_]*(?:_explicit_naming_forbidden|_blacklist))',
    re.IGNORECASE,
)

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding='utf-8'))


# 1. Files present
record('schema_present', SCHEMA.exists(), str(SCHEMA))
record('anti_exploit_present', ANTI.exists(), str(ANTI))
record('economy_policy_present', ECONOMY.exists(), str(ECONOMY))
record('gift_catalog_present', GIFT_CATALOG.exists(), str(GIFT_CATALOG))

try:
    schema = _load_json(SCHEMA)
    record('schema_parses', True, '')
except Exception as e:
    schema = {}
    record('schema_parses', False, f'{e!r}')

try:
    anti = _load_json(ANTI)
    record('anti_exploit_parses', True, '')
except Exception as e:
    anti = {}
    record('anti_exploit_parses', False, f'{e!r}')

try:
    economy = _load_json(ECONOMY)
    record('economy_parses', True, '')
except Exception as e:
    economy = {}
    record('economy_parses', False, f'{e!r}')

try:
    gift_catalog = _load_json(GIFT_CATALOG)
    record('gift_catalog_parses', True, '')
except Exception as e:
    gift_catalog = {}
    record('gift_catalog_parses', False, f'{e!r}')

# 2. Identity + flags
record('schema_id',
       schema.get('schema_id') == 'affinity_gift_inventory_schema_draft_v1', '')
record('schema_task_origin', schema.get('task_origin') == 'AF2-C', '')
record('anti_id', anti.get('policy_id') == 'affinity_gift_anti_exploit_policy_v1', '')
record('anti_task_origin', anti.get('task_origin') == 'AF2-C', '')

for tag, obj in (('schema', schema), ('anti', anti)):
    for k, v in [('design_only', True), ('runtime_attached', False),
                 ('applied_to_combat', False), ('db_write', False),
                 ('no_borea_activation', True)]:
        record(f'{tag}_flag_{k}', obj.get(k) == v,
               f'expected {v}, got {obj.get(k)!r}')

# 3. Proposed collections
cols = {c.get('name') for c in (schema.get('proposed_collections') or [])
        if isinstance(c, dict)}
for required in ['user_gift_inventory_future', 'gift_transaction_ledger_future',
                 'hero_affinity_state_future']:
    record(f'proposed_collection_present:{required}', required in cols, f'got {cols}')

# 3b. Each proposed collection is_design_only=true / migration_created=false
for c in (schema.get('proposed_collections') or []):
    if not isinstance(c, dict):
        continue
    n = c.get('name')
    record(f'collection_design_only:{n}', c.get('is_design_only') is True, '')
    record(f'collection_no_migration:{n}', c.get('is_migration_created') is False, '')
    record(f'collection_not_runtime_indexed:{n}',
           c.get('is_indexed_in_runtime') is False, '')

# 4. Integrity constraints
ic = schema.get('integrity_constraints') or {}
for k, v in [
    ('no_negative_quantity', True),
    ('ledger_required_for_every_spend', True),
    ('idempotency_key_required_for_spend', True),
    ('server_authoritative', True),
    ('no_client_trusted_gift_grant', True),
    ('borea_gifts_locked_until_visibility_unlock', True),
    ('gift_id_must_exist_in_catalog_draft', True),
    ('tides_gift_ids_must_not_be_minted', True),
    ('stat_buff_live_must_be_false', True),
]:
    record(f'integrity_constraint_{k}', ic.get(k) == v,
           f'expected {v}, got {ic.get(k)!r}')

# 5. Anti-exploit policy required sections
fr = anti.get('future_runtime_requirements') or {}
sp = fr.get('spend_endpoint') or {}
record('anti_spend_auth_required', sp.get('auth_required') is True, '')
record('anti_spend_idempotency_required', sp.get('idempotency_key_required') is True, '')
record('anti_spend_replay_protection', sp.get('replay_protection_required') is True, '')
record('anti_spend_feature_flag_off', sp.get('feature_flag_currently_enabled') is False, '')

al = anti.get('audit_ledger_policy') or {}
record('anti_audit_append_only', al.get('append_only') is True, '')
record('anti_audit_no_delete', al.get('no_delete_no_update') is True, '')

rr = anti.get('refund_rollback_policy') or {}
record('anti_refund_partial_supported', rr.get('support_partial_refund') is True, '')
record('anti_refund_no_double_grant',
       rr.get('must_handle_event_rerun_without_double_grant') is True, '')

# 6. PvP caps inherited
pvp = anti.get('pvp_advantage_caps_inherited_from_af2b') or {}
record('anti_pvp_per_source_le_2',
       isinstance(pvp.get('pvp_cap_per_source_pct'), (int, float))
       and pvp['pvp_cap_per_source_pct'] <= 2, '')
record('anti_pvp_total_le_6',
       isinstance(pvp.get('pvp_cap_total_pct'), (int, float))
       and pvp['pvp_cap_total_pct'] <= 6, '')

# 7. Abuse vectors documented
av_ids = {a.get('id') for a in (anti.get('abuse_vectors_documented') or [])
          if isinstance(a, dict)}
for required in ['double_spend_replay', 'double_grant_via_event_rerun',
                 'client_trusted_grant', 'borea_leak', 'stat_buff_runaway',
                 'negative_quantity_underflow', 'tides_orphan_gift']:
    record(f'abuse_vector_documented:{required}', required in av_ids,
           f'got {av_ids}')

# 8. Premium currency separation + no paid-only
record('anti_no_paid_mandatory',
       anti.get('no_paid_only_mandatory_progression') is True, '')
record('anti_no_adult_top', anti.get('no_adult_or_explicit_gifts') is True, '')
pcs = anti.get('premium_currency_separation') or {}
record('anti_no_paid_mandatory_pcs',
       pcs.get('no_paid_only_mandatory_affinity_progression') is True, '')

# 9. No migration file created in this task
migration_hits: list[str] = []
for d in MIGRATIONS_DIRS:
    if d.exists():
        for f in d.rglob('*'):
            if not f.is_file():
                continue
            n = f.name.lower()
            if 'affinity' in n and ('gift' in n or 'inventory' in n) and 'future' not in n:
                migration_hits.append(str(f))
record('no_affinity_migration_created', not migration_hits,
       f'unexpected migrations: {migration_hits}')

# 10. No endpoint created
# Exclude affinity_gift_spend.py (AF2-G disabled skeleton; future-ready endpoint
# that returns 423 and never writes).
endpoint_hits: list[str] = []
if BACKEND_ROUTES.exists():
    for py in BACKEND_ROUTES.rglob('*.py'):
        if not py.is_file():
            continue
        if py.name == 'affinity_gift_spend.py':
            continue
        t = py.read_text(encoding='utf-8', errors='ignore')
        for pat in ENDPOINT_PATTERNS:
            if re.search(pat, t):
                endpoint_hits.append(f'{py}:{pat}')
record('no_endpoint_created', not endpoint_hits,
       f'unexpected endpoints: {endpoint_hits}')

# 11. No UI gift-spend button
ui_hits: list[str] = []
if FRONTEND_APP.exists():
    for tsx in FRONTEND_APP.rglob('*.tsx'):
        if not tsx.is_file():
            continue
        t = tsx.read_text(encoding='utf-8', errors='ignore')
        for pat in UI_BUTTON_PATTERNS:
            if re.search(pat, t, re.IGNORECASE):
                ui_hits.append(f'{tsx}:{pat}')
record('no_ui_gift_spend_button', not ui_hits, f'unexpected: {ui_hits}')

# 12. No adult naming (context-aware)
for tag, p in (('schema', SCHEMA), ('anti', ANTI)):
    if not p.exists():
        continue
    raw = p.read_text(encoding='utf-8').lower()
    for tok in ADULT_BLACKLIST:
        record(f'no_adult_token:{tag}:{tok}', tok not in raw,
               f'{tag} contains {tok}')
    matches = [m.group(0) for m in ADULT_CONTEXT_REGEX.finditer(p.read_text(encoding='utf-8'))]
    record(f'no_adult_context_token:{tag}', not matches,
           f'unexpected adult matches: {matches}')

# 13. gift_id references / tides not minted in gift catalog
entries = gift_catalog.get('entries') or []
gift_ids = [e.get('id') for e in entries if isinstance(e, dict)]
tides_ids = [g for g in gift_ids if isinstance(g, str) and 'tides_' in g]
record('no_tides_gift_ids_in_catalog', not tides_ids,
       f'unexpected tides_*: {tides_ids}')

# 14. Constraints assertions in schema reference cap policy
record('schema_references_economy_policy',
       schema.get('source_economy_policy_reference') is not None, '')
record('schema_references_catalog',
       schema.get('source_catalog_reference') is not None, '')


print('=' * 70)
print('AF2-C — Affinity Gift Inventory Schema + Anti-Exploit Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
