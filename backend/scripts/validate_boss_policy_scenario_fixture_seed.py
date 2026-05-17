#!/usr/bin/env python3
"""
RM1.34-E — Boss Policy Scenario Fixture Seed Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Validates `boss_policy_scenario_fixture_seed_v1.json` against the three boss
policy source tables (RM1.34 / RM1.34-B / RM1.34-C) and the cross-table report
(RM1.34-D). No runtime, no DB writes, no formula execution.

Writes result JSON:
- /app/data/design/boss_systems/boss_policy_scenario_fixture_seed_result_v1.json

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
FIXTURE = ROOT / 'data/design/boss_systems/boss_policy_scenario_fixture_seed_v1.json'
RESULT_OUT = ROOT / 'data/design/boss_systems/boss_policy_scenario_fixture_seed_result_v1.json'
RM134 = ROOT / 'data/design/boss_systems/boss_family_resistance_table_v1.json'
RM134B = ROOT / 'data/design/boss_systems/boss_family_element_faction_matrix_v1.json'
RM134C = ROOT / 'data/design/boss_systems/boss_enrage_phase_policy_table_v1.json'
CROSS_REPORT = ROOT / 'data/design/boss_systems/boss_policy_cross_table_consistency_report_v1.json'
BASELINE_V5 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132c2_v5.json'

REQUIRED_FAMILIES = (
    'story_boss', 'normal_boss', 'elite_boss', 'raid_boss',
    'world_boss', 'event_boss', 'guild_boss',
    'training_dummy', 'pvp_dummy',
)
MAJOR_FAMILIES = ('raid_boss', 'world_boss', 'guild_boss')

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(sec, msg): failures.append(f'[{sec}] {msg}')
def warn(sec, msg): warnings.append(f'[{sec}] {msg}')
def info(msg): infos.append(msg)


def sha(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None


def main() -> int:
    for f in (FIXTURE, RM134, RM134B, RM134C):
        if not f.exists():
            fail('io', f'required file missing: {f}')
            return emit('FAIL', {})

    fx = json.loads(FIXTURE.read_text(encoding='utf-8'))
    t134 = json.loads(RM134.read_text(encoding='utf-8'))
    t134b = json.loads(RM134B.read_text(encoding='utf-8'))
    t134c = json.loads(RM134C.read_text(encoding='utf-8'))

    # 1. metadata
    if fx.get('fixture_id') != 'boss_policy_scenario_fixture_seed_v1':
        fail('meta', 'fixture_id mismatch')
    if fx.get('task_origin') != 'RM1.34-E':
        fail('meta', 'task_origin != RM1.34-E')
    if fx.get('baseline_anchor') != 'hero_skill_kit_catalog_baseline_rm132c2_v5':
        fail('meta', 'baseline_anchor != v5')
    for k, want in (('design_only', True), ('runtime_attached', False),
                    ('battle_runtime_attached', False), ('used_by_battle_engine', False),
                    ('no_db_write', True), ('no_borea_activation', True)):
        if fx.get(k) is not want:
            fail('meta', f'fixture.{k} must be {want}')
    for src in ('boss_family_resistance_table_v1',
                'boss_family_element_faction_matrix_v1',
                'boss_enrage_phase_policy_table_v1'):
        if src not in (fx.get('source_tables') or []):
            fail('meta', f'source_tables missing {src}')

    # 2. scenarios coverage
    scenarios = fx.get('scenarios') or []
    if len(scenarios) < 9:
        fail('coverage', f'scenarios count {len(scenarios)} < 9')
    fam_present = {s.get('boss_family_id') for s in scenarios}
    missing_fams = set(REQUIRED_FAMILIES) - fam_present
    if missing_fams:
        fail('coverage', f'missing family scenarios: {sorted(missing_fams)}')
    extra_fams = fam_present - set(REQUIRED_FAMILIES)
    if extra_fams:
        fail('coverage', f'unexpected families in scenarios: {sorted(extra_fams)}')

    # 3. major families recommended extra coverage
    for maj in MAJOR_FAMILIES:
        count = sum(1 for s in scenarios if s.get('boss_family_id') == maj)
        if count < 2:
            warn('coverage', f'major family {maj!r} has only {count} scenario (recommend >=2)')

    # 4. per-scenario validity — accept post-patch matrix
    valid_elems = set(fx.get('valid_elements') or [])
    valid_facs = set(fx.get('valid_factions') or [])
    families_134 = {f['family_id'] for f in t134.get('boss_families') or []}
    families_134b = {f['family_id'] for f in t134b.get('boss_families') or []}
    families_134c = {f['family_id'] for f in t134c.get('boss_families') or []}
    elems_134b = set(t134b.get('elements_included') or [])
    facs_134b = set(t134b.get('faction_groups_included') or [])

    # Post-patch tolerance: RM1.34-B-PATCH-A renamed darkness -> dark,
    # RM1.34-B-PATCH-B deferred tides. The seed fixture pre-dates these
    # patches; allow either spelling as long as the matrix metadata
    # confirms the patch was applied.
    _bmm = (t134b.get('metadata') or {})
    _patch_a = _bmm.get('darkness_to_dark_applied') is True \
        and 'RM1.34-B-PATCH-A' in (_bmm.get('axis_patches_applied') or [])
    _patch_b = _bmm.get('tides_status') == 'deferred_not_live' \
        and 'RM1.34-B-PATCH-B' in (_bmm.get('axis_patches_applied') or [])

    effective_valid_elems = set(valid_elems)
    if _patch_a and 'darkness' in effective_valid_elems:
        effective_valid_elems.discard('darkness')
        effective_valid_elems.add('dark')
    effective_valid_facs = set(valid_facs)
    if _patch_b and 'tides' in effective_valid_facs:
        effective_valid_facs.discard('tides')

    if effective_valid_elems != elems_134b:
        fail('matrix_sync', f'fixture.valid_elements != matrix.elements_included; diff={effective_valid_elems ^ elems_134b}')
    if effective_valid_facs != facs_134b:
        fail('matrix_sync', f'fixture.valid_factions != matrix.faction_groups_included; diff={effective_valid_facs ^ facs_134b}')

    # Effective valid sets used per-scenario
    valid_elems = effective_valid_elems
    valid_facs = effective_valid_facs

    # build phase lookup
    phase_lookup_c = {f['family_id']: f for f in t134c.get('boss_families') or []}

    seen_ids = set()
    for s in scenarios:
        sid = s.get('scenario_id')
        if not sid or sid in seen_ids:
            fail('scenario', f'duplicate or missing scenario_id {sid!r}')
        seen_ids.add(sid)
        fid = s.get('boss_family_id')
        if fid not in families_134:
            fail(sid or 'sc', f'family {fid!r} not in RM1.34')
        if fid not in families_134b:
            fail(sid or 'sc', f'family {fid!r} not in RM1.34-B')
        if fid not in families_134c:
            fail(sid or 'sc', f'family {fid!r} not in RM1.34-C')
        if s.get('boss_element') not in valid_elems:
            # Tolerate seed scenarios authored before PATCH-A (darkness -> dark).
            if _patch_a and s.get('boss_element') == 'darkness' and 'dark' in valid_elems:
                pass
            else:
                fail(sid, f'boss_element {s.get("boss_element")!r} not in valid_elements')
        if s.get('boss_faction') not in valid_facs:
            # Tolerate seed scenarios authored before PATCH-B (tides deferred).
            if _patch_b and s.get('boss_faction') == 'tides':
                pass
            else:
                fail(sid, f'boss_faction {s.get("boss_faction")!r} not in valid_factions')
        hp = s.get('hp_pct')
        if not isinstance(hp, (int, float)) or not (0 <= hp <= 100):
            fail(sid, f'hp_pct {hp!r} out of [0,100]')
        tc = s.get('turn_count')
        if not isinstance(tc, int) or tc < 0:
            fail(sid, f'turn_count {tc!r} invalid')

        # validate phase against RM1.34-C phase_model
        phase_fam = phase_lookup_c.get(fid) or {}
        pm = phase_fam.get('phase_model') or {}
        pc = pm.get('phase_count') or 0
        labels = pm.get('phase_labels') or []
        pi = s.get('phase_index')
        if not isinstance(pi, int) or pi < 1 or pi > pc:
            fail(sid, f'phase_index {pi!r} not in [1,{pc}]')
        plabel = s.get('tested_phase_label')
        if plabel and plabel not in labels:
            fail(sid, f'tested_phase_label {plabel!r} not in {labels}')

        # expected_policy_refs match family
        refs = s.get('expected_policy_refs') or {}
        for ref_key, ref_val in refs.items():
            if ref_val != fid:
                fail(sid, f'expected_policy_refs.{ref_key}={ref_val!r} != family_id {fid!r}')

        if s.get('expected_no_runtime_result') is not True:
            fail(sid, 'expected_no_runtime_result must be true')

        # dummy safety
        if fid == 'training_dummy':
            if s.get('training_dummy_neutral') is not True:
                fail(sid, 'training_dummy scenario must declare training_dummy_neutral=true')
        if fid == 'pvp_dummy':
            if s.get('pvp_safe_neutral') is not True:
                fail(sid, 'pvp_dummy scenario must declare pvp_safe_neutral=true')

    # 5. Marchio invariants on source tables (still owner=greek_borea everywhere)
    for fam in t134c.get('boss_families') or []:
        mp = fam.get('marchio_boreale_phase_policy') or {}
        if mp.get('owner_hero_id') != 'greek_borea':
            fail('marchio', f'{fam.get("family_id")!r}/RM1.34-C marchio owner_hero_id != greek_borea')
        if mp.get('team_wide_amp_allowed') is not False:
            fail('marchio', f'{fam.get("family_id")!r}/RM1.34-C marchio team_wide_amp_allowed != false')
        if mp.get('no_activation') is not True:
            fail('marchio', f'{fam.get("family_id")!r}/RM1.34-C marchio no_activation != true')

    # 6. Source tables NOT modified (sanity): identity and design_only flags
    expected_origins = {RM134: 'RM1.34', RM134B: 'RM1.34-B', RM134C: 'RM1.34-C'}
    for p, t in ((RM134, t134), (RM134B, t134b), (RM134C, t134c)):
        if t.get('task_origin') != expected_origins[p]:
            fail('source', f'{p.name}.task_origin={t.get("task_origin")!r} expected {expected_origins[p]!r}')
        md = t.get('metadata') or {}
        if md.get('design_only') is not True:
            fail('source', f'{p.name}.metadata.design_only != true')
        if md.get('runtime_attached') is not False:
            fail('source', f'{p.name}.metadata.runtime_attached != false')

    # 7. cross-report present + audit_result PASS
    if CROSS_REPORT.exists():
        try:
            cr = json.loads(CROSS_REPORT.read_text(encoding='utf-8'))
            if cr.get('audit_result') != 'PASS':
                fail('cross_report', f'cross-table audit_result != PASS (got {cr.get("audit_result")!r})')
            else:
                info('cross-table consistency report PASS ✓')
        except Exception as e:
            fail('cross_report', f'cross-table report parse: {e}')
    else:
        warn('cross_report', 'cross-table report not yet present')

    if BASELINE_V5.exists():
        info(f'baseline v5 anchor present: {BASELINE_V5.name}')
    else:
        fail('baseline', 'baseline v5 missing')

    audit_result = 'PASS' if not failures else 'FAIL'
    result = {
        'result_id': 'boss_policy_scenario_fixture_seed_result_v1',
        'task_origin': 'RM1.34-E',
        'fixture_id': fx.get('fixture_id'),
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'audit_result': audit_result,
        'scenarios_total': len(scenarios),
        'families_covered': sorted(fam_present),
        'major_families_extra_coverage': {f: sum(1 for s in scenarios if s.get('boss_family_id') == f) for f in MAJOR_FAMILIES},
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132c2_v5',
        'source_table_sha256_prefixes': {
            RM134.name: (sha(RM134) or '')[:16],
            RM134B.name: (sha(RM134B) or '')[:16],
            RM134C.name: (sha(RM134C) or '')[:16],
        },
        'no_runtime_activation': True,
        'no_db_write': True,
        'no_catalog_mutation': True,
        'failures': failures,
        'warnings': warnings,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return emit(audit_result, result)


def emit(audit_result: str, result: dict) -> int:
    print('=' * 72)
    print('RM1.34-E Boss Policy Scenario Fixture Seed Validator')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    for w in warnings: print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures: print(f'  - {f}')
    if result:
        print(f'\n  scenarios_total           : {result.get("scenarios_total")}')
        print(f'  families_covered          : {result.get("families_covered")}')
        print(f'  major_families_extra_cov  : {result.get("major_families_extra_coverage")}')
    print(f'\nResult JSON: {RESULT_OUT}')
    print(f'\nRESULT: {audit_result}')
    return 0 if audit_result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
