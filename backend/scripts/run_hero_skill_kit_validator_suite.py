#!/usr/bin/env python3
"""
RM1.31-B — Hero Skill Kit Validator Suite Runner
─────────────────────────────────────────────────────────────────────────
Single command to run all Hero Skill Kit / Divine Weapon / Status-resolver
validators sequentially. Read-only orchestrator. NO catalog/DB/runtime
writes.

Exit 0 only if every REQUIRED validator passes; exit 1 if any fails.
Optional validators that are missing are reported and do not fail the
suite unless they are listed as required.

Usage:
    python3 run_hero_skill_kit_validator_suite.py
    python3 run_hero_skill_kit_validator_suite.py --json-out /tmp/suite.json
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path('/app/backend/scripts')
SAFE_REPORT_DIRS = (Path('/app/backend/reports'), Path('/tmp'))

REQUIRED = [
    ('RM1.28-A', 'validate_5star_passive_advanced_source.py'),
    ('RM1.28-B', 'audit_5star_skill_kits_crosslinks.py'),
    ('RM1.28-C', 'audit_5star_legacy_status_tags.py'),
    ('RM1.28-D', 'validate_5star_legacy_status_tags_normalized.py'),
    ('RM1.28-E', 'validate_5star_manual_review_residuals_resolved.py'),
    ('RM1.29',   'audit_6star_skill_kits_crosslinks.py'),
    ('RM1.30-A', 'validate_6star_catalog_safety_metadata.py'),
    ('RM1.30-B', 'audit_6star_effect_tags_taxonomy.py'),
    ('RM1.30-C', 'audit_hero_skill_kit_catalog_consolidation.py'),
    ('RM1.27-A', 'validate_divine_weapon_catalog.py'),
    ('RM1.27-D', 'audit_divine_weapon_crosslinks.py'),
    ('RM1.32-A', 'validate_5star_balance_foundation.py'),
    ('RM1.32-B', 'validate_6star_balance_foundation.py'),
    ('RM1.32-C2', 'validate_foundation_numeric_trim_rm132c2.py'),
]
OPTIONAL = [
    ('RM1.31-C', 'validate_status_resolver_contract.py'),
    ('RM1.32-C', 'audit_balance_foundation_boss_pvp_caps.py'),
    ('RM1.33-A', 'audit_skill_kit_runtime_adapter_safety.py'),
    ('RM1.33-B', 'audit_skill_kit_runtime_adapter_wiretest.py'),
    ('RM1.33-C', 'audit_skill_kit_runtime_debug_endpoint_safety.py'),
    ('RM1.33-D', 'validate_runtime_debug_snapshot_contract.py'),
    ('RM1.33-E', 'audit_skill_kit_runtime_debug_coverage_safety.py'),
    ('RM1.33-F', 'validate_runtime_debug_6star_ultimate_snapshots.py'),
    ('RM1.33-G', 'validate_runtime_debug_5star_snapshot_rejections.py'),
    ('RM1.34', 'validate_boss_family_resistance_table.py'),
    ('RM1.34-B', 'validate_boss_element_faction_matrix.py'),
    ('RM1.34-C', 'validate_boss_enrage_phase_policy_table.py'),
    ('RM1.34-D', 'audit_boss_policy_cross_table_consistency.py'),
    ('RM1.34-E', 'validate_boss_policy_scenario_fixture_seed.py'),
    ('RM1.33-H', 'validate_divine_weapon_preview_catalog_only_fixture.py'),
    ('CS2-A', 'audit_collection_synergies_v2_readiness.py'),
    ('AF2-A', 'audit_affinity_phase2_gift_catalog_readiness.py'),
    ('CS2/AF2-COMBO', 'validate_collection_affinity_readiness_combo.py'),
    ('CS2-B', 'audit_collection_synergy_preview_resolver_safety.py'),
    ('AF2-B', 'validate_affinity_phase2_economy_cap_policy.py'),
    ('AXIS-A', 'audit_canonical_faction_element_axes.py'),
    ('UI-PREVIEW-A', 'audit_collection_affinity_ui_preview_safety.py'),
    ('STACK-A', 'audit_cross_system_progression_stack_safety.py'),
    ('MEGA-COMBO', 'validate_collection_affinity_axis_stack_combo.py'),
    ('CS2-C', 'audit_collection_synergy_ui_preview_contract.py'),
    ('AF2-C', 'validate_affinity_gift_inventory_schema.py'),
    ('STACK-B', 'audit_global_modifier_cap_resolver_safety.py'),
    ('AXIS-B', 'audit_canonical_axis_alias_helper_safety.py'),
    ('MEGA-COMBO-2', 'validate_cs2c_af2c_stackb_axisb_combo.py'),
    ('CS2-D', 'audit_collection_synergy_preview_ui_stub.py'),
    ('AF2-D', 'validate_affinity_phase2_migration_plan_draft.py'),
    ('AF2-E', 'audit_affinity_gifts_readonly_endpoint_safety.py'),
    ('STACK-C', 'validate_global_modifier_cap_resolver_edge_cases.py'),
    ('AXIS-C', 'audit_canonical_axis_dynamic_preview.py'),
    ('MEGA-COMBO-3', 'validate_cs2d_af2d_af2e_stackc_axisc_combo.py'),
]
BASELINE_DIFF = ('RM1.32-PRE', 'validate_hero_skill_kit_catalog_baseline_diff.py')


def run_one(script: Path, extra_args: list[str] | None = None) -> dict:
    if not script.exists():
        return {'present': False, 'exit_code': None, 'duration_s': 0.0, 'tail': '<missing>'}
    t0 = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(
            ['python3', str(script)] + (extra_args or []),
            capture_output=True, text=True, timeout=60,
        )
        tail = (proc.stdout or proc.stderr or '').strip().splitlines()
        tail = tail[-3:] if tail else ['<no output>']
        return {
            'present': True,
            'exit_code': proc.returncode,
            'duration_s': (datetime.now(timezone.utc) - t0).total_seconds(),
            'tail': '\n        '.join(tail),
        }
    except subprocess.TimeoutExpired:
        return {'present': True, 'exit_code': 124, 'duration_s': 60.0, 'tail': '<TIMEOUT>'}
    except Exception as e:
        return {'present': True, 'exit_code': -1, 'duration_s': 0.0, 'tail': f'<ERROR: {e}>'}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='run_hero_skill_kit_validator_suite')
    ap.add_argument('--json-out', help='Path under /app/backend/reports or /tmp to write the full report JSON')
    ap.add_argument('--include-baseline-diff', action='store_true',
                    help='Also run RM1.32-PRE baseline diff validator (off by default — baselines intentionally change in approved tasks)')
    ap.add_argument('--allow-changed', action='append', default=[],
                    help='Forwarded to baseline diff validator (only used with --include-baseline-diff). Repeatable.')
    args = ap.parse_args(argv)

    results: list[dict] = []
    any_required_fail = False

    print('RM1.31-B — Hero Skill Kit Validator Suite Runner')
    print('=' * 70)
    print(f'{"TASK":10s} {"SCRIPT":54s} {"EXIT":>5s}')
    print('-' * 70)
    for task, name in REQUIRED:
        r = run_one(SCRIPTS_DIR / name)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        if status != 'PASS':
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': True, 'status': status, **r})

    print('-- optional --')
    for task, name in OPTIONAL:
        r = run_one(SCRIPTS_DIR / name)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        # Optional: don't fail suite if MISS, but fail if explicit FAIL
        if r['present'] and r['exit_code'] not in (0, None):
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': False, 'status': status, **r})
    if args.include_baseline_diff:
        print('-- baseline diff (RM1.32-PRE) --')
        task, name = BASELINE_DIFF
        extra: list[str] = []
        for p in (args.allow_changed or []):
            extra.extend(['--allow-changed', p])
        r = run_one(SCRIPTS_DIR / name, extra_args=extra)
        status = 'PASS' if r['present'] and r['exit_code'] == 0 else ('FAIL' if r['present'] else 'MISS')
        if r['present'] and r['exit_code'] not in (0, None):
            any_required_fail = True
        print(f'{task:10s} {name:54s} {r["exit_code"]!s:>5s}  [{status}]')
        results.append({'task': task, 'script': name, 'required': True, 'status': status, **r})
    print('=' * 70)

    overall = 'PASS' if not any_required_fail else 'FAIL'
    n_pass = sum(1 for r in results if r['status'] == 'PASS')
    n_fail = sum(1 for r in results if r['status'] == 'FAIL')
    n_miss = sum(1 for r in results if r['status'] == 'MISS')
    print(f'Overall: {overall}  (pass={n_pass}, fail={n_fail}, miss={n_miss})')

    if args.json_out:
        out = Path(args.json_out).resolve()
        if not any(str(out).startswith(str(s.resolve())) for s in SAFE_REPORT_DIRS):
            print(f'REJECTED --json-out: "{out}" outside allowed dirs {[str(s) for s in SAFE_REPORT_DIRS]}')
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            'suite': 'RM1.31-B',
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'overall': overall,
            'counts': {'pass': n_pass, 'fail': n_fail, 'miss': n_miss},
            'results': results,
        }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'JSON report written: {out}')

    return 0 if overall == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
