#!/usr/bin/env python3
"""
STACK-A — Cross-system progression stack safety audit.

Audits that every progression system currently in scope is inert and that
the cross-system stack safety report enumerates the future risks and cap
requirements properly.

Systems audited (design-only, no runtime introspection):
  - Collection Synergies V2 (CS2-A readiness + CS2-B preview resolver)
  - Affinity Phase 2 (AF2-A gift draft + AF2-B economy/cap policy)
  - Divine Weapons (RM1.27 / RM1.33-H preview fixture)
  - Skill Kit (RM1.33-A runtime adapter OFF)
  - Boss policies (RM1.34 / B / C / D)

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
REPORT = ROOT / 'data' / 'design' / 'system_safety' / 'cross_system_progression_stack_safety_report_v1.json'
CS2A = ROOT / 'data' / 'design' / 'synergies' / 'collection_synergies_v2_readiness_plan_v1.json'
CS2B = ROOT / 'backend' / 'data' / 'collection_synergy_preview_resolver.py'
AF2A = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'
AF2B = ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_economy_cap_policy_draft_v1.json'
ADAPTER = ROOT / 'backend' / 'data' / 'skill_kit_runtime_adapter.py'
BATTLE_ENGINE = ROOT / 'backend' / 'battle_engine.py'
BATTLE_CORE = ROOT / 'backend' / 'battle_core.py'
COMBAT_TSX = ROOT / 'frontend' / 'app' / 'combat.tsx'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding='utf-8'))


# 1. Report present + structure
record('report_present', REPORT.exists(), str(REPORT))
try:
    report = _load_json(REPORT)
    record('report_parses', True, '')
except Exception as e:
    report = {}
    record('report_parses', False, f'{e!r}')

record('report_id',
       report.get('report_id') == 'cross_system_progression_stack_safety_report_v1',
       f'got {report.get("report_id")}')
record('report_task_origin', report.get('task_origin') == 'STACK-A', '')
for k, v in [('design_only', True), ('runtime_attached', False),
             ('applied_to_combat', False), ('db_write', False),
             ('no_borea_activation', True)]:
    record(f'report_flag_{k}', report.get(k) == v,
           f'expected {v}, got {report.get(k)!r}')

# 2. Inertness assertions
ia = report.get('current_inertness_assertions') or {}
for k, v in [
    ('no_live_stat_source_from_collection', True),
    ('no_live_stat_source_from_affinity', True),
    ('divine_weapons_catalog_runtime_attached', False),
    ('skill_kit_runtime_enabled_default', False),
    ('boss_policies_design_only', True),
    ('runtime_adapter_off', True),
    ('battle_engine_imports_runtime_adapter', False),
    ('combat_tsx_imports_runtime_adapter', False),
    ('borea_hidden_invariant_holds', True),
    ('api_heroes_count_invariant_100', True),
]:
    record(f'inertness_{k}', ia.get(k) == v,
           f'expected {v}, got {ia.get(k)!r}')

# 3. Cap recommendations
cr = report.get('cap_recommendations_future_only') or {}
record('cap_collection_total_le_15',
       cr.get('collection_total_cap_pct') is not None
       and cr.get('collection_total_cap_pct') <= 15, '')
record('cap_collection_per_category_le_5',
       cr.get('collection_per_category_cap_pct') is not None
       and cr.get('collection_per_category_cap_pct') <= 5, '')
record('cap_affinity_pvp_total_le_6',
       cr.get('affinity_pvp_total_cap_pct') is not None
       and cr.get('affinity_pvp_total_cap_pct') <= 6, '')
record('cap_affinity_pvp_per_source_le_2',
       cr.get('affinity_pvp_per_source_cap_pct') is not None
       and cr.get('affinity_pvp_per_source_cap_pct') <= 2, '')
record('cap_dw_global_le_10',
       cr.get('divine_weapon_global_cap_pct_future') is not None
       and cr.get('divine_weapon_global_cap_pct_future') <= 10, '')
record('cap_dw_pvp_le_5',
       cr.get('divine_weapon_pvp_cap_pct_future') is not None
       and cr.get('divine_weapon_pvp_cap_pct_future') <= 5, '')

# 4. Risks enumerated
risks = report.get('stacking_risks_if_all_activated_later') or []
risk_ids = {r.get('id') for r in risks if isinstance(r, dict)}
for required in ['additive_summed_buffs', 'multiplicative_stacking',
                 'axis_mismatch_runtime_drift', 'borea_hidden_leak']:
    record(f'risk_documented:{required}', required in risk_ids, '')

# 5. Borea locked across systems
bl = report.get('borea_locked_across_systems') or {}
for k in ['collection_synergy_v2', 'affinity_phase_2', 'divine_weapons',
          'skill_kit', 'boss_policies']:
    record(f'borea_locked_{k}', bl.get(k) is True, '')

# 6. Confirm each system source exists and is inert (best-effort grep)
record('cs2a_plan_present', CS2A.exists(), str(CS2A))
record('cs2b_resolver_present', CS2B.exists(), str(CS2B))
record('af2a_gift_draft_present', AF2A.exists(), str(AF2A))
record('af2b_policy_present', AF2B.exists(), str(AF2B))
record('skill_kit_runtime_adapter_present', ADAPTER.exists(), str(ADAPTER))

# 7. Confirm battle_engine.py / combat.tsx do NOT import the new resolver
for f in [BATTLE_ENGINE, BATTLE_CORE, COMBAT_TSX]:
    if not f.exists():
        record(f'live_file_present:{f.name}', True, f'{f} absent (skipped)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in ['collection_synergy_preview_resolver',
                'affinity_phase2_economy_cap_policy_draft',
                'preview_collection_synergy_categories']:
        ok = tok not in txt
        record(f'no_import_in_{f.name}:{tok}', ok,
               f'token "{tok}" found in {f}' if not ok else '')

# 8. Skill kit runtime adapter default OFF (text inspect)
if ADAPTER.exists():
    adapter_text = ADAPTER.read_text(encoding='utf-8')
    record('skill_kit_runtime_enabled_default_off_in_source',
           'SKILL_KIT_RUNTIME_ENABLED' in adapter_text
           and 'true_explicit_runtime_on' in adapter_text, '')

# 9. Global modifier cap resolver requirement documented
gmcr = report.get('global_modifier_cap_resolver_requirement') or {}
record('global_cap_resolver_required_before_runtime',
       gmcr.get('required_before_any_runtime_on') is True, '')
record('global_cap_resolver_currently_not_implemented',
       gmcr.get('currently_implemented') is False, '')


# Report
print('=' * 70)
print('STACK-A — Cross-System Progression Stack Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
