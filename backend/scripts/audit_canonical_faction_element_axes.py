#!/usr/bin/env python3
"""
AXIS-A — Canonical Faction x Element Axis Consistency Audit.

Compares the canonical axes used by:
  - the live roster (via /api/heroes when reachable, fallback to character bible source)
  - the Boss Family x Element/Faction Resistance Matrix (RM1.34-B)
  - the Affinity Phase 2 gift catalog draft (AF2-A)
  - the Collection Synergies V2 readiness draft (CS2-A)

Asserts that the canonical_faction_element_axis_resolution_plan_v1.json
exists, documents the dark/darkness mismatch and the tides faction
mismatch, and proposes alias coverage + a runtime activation gate.

This audit PASSES if the mismatches are documented and the plan resolves
them via alias map + non-mutation of source tables. It does NOT mutate
RM1.34-B or AF2-A. It does NOT touch DB/runtime.

Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

ROOT = Path('/app')
PLAN = ROOT / 'data' / 'design' / 'shared' / 'canonical_faction_element_axis_resolution_plan_v1.json'
BOSS_MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
GIFT_DRAFT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'
CS2A_PLAN = ROOT / 'data' / 'design' / 'synergies' / 'collection_synergies_v2_readiness_plan_v1.json'

API_HEROES = os.environ.get('AUDIT_HEROES_URL', 'http://127.0.0.1:8001/api/heroes')

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding='utf-8'))


# 1. Plan present
record('plan_present', PLAN.exists(), str(PLAN))
try:
    plan = _load_json(PLAN)
    record('plan_parses', True, '')
except Exception as e:
    plan = {}
    record('plan_parses', False, f'{e!r}')

record('plan_id',
       plan.get('plan_id') == 'canonical_faction_element_axis_resolution_plan_v1',
       f'got {plan.get("plan_id")}')
record('plan_task_origin', plan.get('task_origin') == 'AXIS-A',
       f'got {plan.get("task_origin")}')
for k, v in [('design_only', True), ('runtime_attached', False),
             ('applied_to_combat', False), ('no_db_write', True),
             ('no_borea_activation', True)]:
    record(f'plan_flag_{k}', plan.get(k) == v,
           f'expected {v}, got {plan.get(k)!r}')

# 2. Boss matrix axes
boss_elements: list[str] = []
boss_factions: list[str] = []
if BOSS_MATRIX.exists():
    try:
        m = _load_json(BOSS_MATRIX)
        boss_elements = list(m.get('elements_included') or [])
        boss_factions = list(m.get('faction_groups_included') or [])
        record('boss_matrix_loaded', True, '')
    except Exception as e:
        record('boss_matrix_loaded', False, f'{e!r}')
else:
    record('boss_matrix_loaded', False, 'missing')

# 3. Gift draft axes (AF2-A)
gift_factions: list[str] = []
gift_elements: list[str] = []
if GIFT_DRAFT.exists():
    try:
        g = _load_json(GIFT_DRAFT)
        gift_factions = list(g.get('factions_used') or [])
        gift_elements = list(g.get('elements_used') or [])
        record('gift_draft_loaded', True, '')
    except Exception as e:
        record('gift_draft_loaded', False, f'{e!r}')
else:
    record('gift_draft_loaded', False, 'missing')

# 4. CS2-A categories
cs_cats: list[str] = []
if CS2A_PLAN.exists():
    try:
        c = _load_json(CS2A_PLAN)
        cs_cats = [x.get('id') for x in (c.get('proposed_collection_synergy_categories') or [])
                   if isinstance(x, dict)]
        record('cs2a_plan_loaded', True, '')
    except Exception as e:
        record('cs2a_plan_loaded', False, f'{e!r}')
else:
    record('cs2a_plan_loaded', False, 'missing')

# 5. Live roster axes (best-effort via /api/heroes)
roster_factions: set[str] = set()
roster_elements: set[str] = set()
api_ok = False
try:
    with urlopen(API_HEROES, timeout=5) as resp:
        body = resp.read().decode('utf-8')
        data = json.loads(body)
        heroes = data if isinstance(data, list) else (
            data.get('heroes') or data.get('data') or []
        )
        for h in heroes:
            f = (h.get('faction') or h.get('canonical_faction') or '').strip()
            el = (h.get('element') or h.get('canonical_element') or '').strip()
            if f:
                roster_factions.add(f)
            if el:
                roster_elements.add(el)
        record('api_heroes_reachable', True, f'count={len(heroes)}')
        api_ok = True
except (URLError, Exception) as e:
    record('api_heroes_reachable', False, f'fallback to snapshot: {e!r}')

# If API unreachable, use plan snapshot to keep audit usable offline
if not api_ok:
    snap = plan.get('observed_state_snapshot') or {}
    roster_factions = set(snap.get('roster_factions_from_api_heroes') or [])
    roster_elements = set(snap.get('roster_elements_from_api_heroes') or [])

# 6. Confirm documented discrepancies match observed reality
record('element_dark_in_roster', 'dark' in roster_elements,
       'roster must contain "dark"')
# Post-patch tolerance: darkness may be canonical only OR patched to dark
_bm_meta = {}
try:
    import json as _json
    _bm = _json.loads(open('/app/data/design/boss_systems/boss_family_element_faction_matrix_v1.json').read())
    _bm_meta = _bm.get('metadata') or {}
except Exception:
    pass
_darkness_patched = _bm_meta.get('darkness_to_dark_applied') is True \
    and 'RM1.34-B-PATCH-A' in (_bm_meta.get('axis_patches_applied') or [])
_tides_deferred = _bm_meta.get('tides_status') == 'deferred_not_live' \
    and 'RM1.34-B-PATCH-B' in (_bm_meta.get('axis_patches_applied') or [])

record('element_darkness_in_boss_matrix_or_patched',
       ('darkness' in boss_elements) or _darkness_patched,
       'boss matrix must contain "darkness" OR be PATCH-A-applied')
record('element_darkness_NOT_in_roster',
       'darkness' not in roster_elements,
       'roster must NOT contain "darkness"')

record('faction_tides_in_boss_matrix_or_deferred',
       ('tides' in boss_factions) or _tides_deferred,
       'boss matrix must contain "tides" OR be PATCH-B-deferred')
record('faction_tides_NOT_in_roster',
       'tides' not in roster_factions,
       'roster must NOT contain "tides"')
record('faction_tides_NOT_in_gift_draft',
       'tides' not in gift_factions,
       'gift draft must NOT mint tides_*')

# 7. Plan documents discrepancies
docs = plan.get('discrepancies') or []
ids = {d.get('id') for d in docs if isinstance(d, dict)}
record('plan_documents_element_dark_vs_darkness',
       'element_dark_vs_darkness' in ids, '')
record('plan_documents_faction_tides_in_matrix_only',
       'faction_tides_in_matrix_only' in ids, '')

# 8. Plan has alias map covering darkness -> dark
alias_elements = (plan.get('alias_map') or {}).get('elements') or {}
record('alias_map_darkness_to_dark',
       alias_elements.get('darkness') == 'dark',
       f'got {alias_elements.get("darkness")}')
record('alias_map_dark_self', alias_elements.get('dark') == 'dark', '')

# 9. Recommendations exist
record('canonical_element_rec_present',
       isinstance(plan.get('canonical_element_recommendation'), dict), '')
record('canonical_faction_rec_present',
       isinstance(plan.get('canonical_faction_recommendation'), dict), '')
record('canonical_faction_no_mint_tides',
       (plan.get('canonical_faction_recommendation') or {}).get('do_not_mint_gift_entries_for_tides') is True,
       '')

# 10. Activation gate currently blocking
gate = plan.get('activation_gate') or {}
record('activation_gate_currently_blocking',
       gate.get('currently_blocking_runtime_on') is True, '')
record('activation_gate_currently_satisfied_false',
       gate.get('currently_satisfied') is False, '')


# Report
print('=' * 70)
print('AXIS-A — Canonical Faction x Element Axis Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'roster_factions={sorted(roster_factions)}')
print(f'roster_elements={sorted(roster_elements)}')
print(f'boss_matrix_elements={boss_elements}')
print(f'boss_matrix_factions={boss_factions}')
print(f'gift_draft_factions={gift_factions}')
print(f'gift_draft_elements={gift_elements}')
print(f'cs2a_categories={cs_cats}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
