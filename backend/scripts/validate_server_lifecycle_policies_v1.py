#!/usr/bin/env python3
"""SLC-A: Validate lifecycle policy files (read-only)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path('/app/data/design/server_lifecycle')
OUT = Path(ROOT, '_validate_server_lifecycle_policies_v1_result.json')
FILES = [
    'account_server_data_scope_policy_v1.json',
    'server_entity_schema_v1.json',
    'server_profile_schema_v1.json',
    'server_opening_cadence_policy_v1.json',
    'global_real_world_event_override_policy_v1.json',
    'server_merge_eligibility_policy_v1.json',
    'event_banner_recovery_classification_policy_v1.json',
    'merged_mature_calendar_policy_v1.json',
]


def main():
    errs=[]; data={}
    for fn in FILES:
        p=ROOT/fn
        if not p.exists(): errs.append(f'missing:{fn}'); continue
        try: data[fn]=json.loads(p.read_text())
        except Exception as e: errs.append(f'parse:{fn}:{e}')
    for fn, d in data.items():
        if not d.get('design_only'): errs.append(f'{fn}:not_design_only')
        if d.get('runtime_attached'): errs.append(f'{fn}:runtime_attached')
        if d.get('battle_runtime_attached'): errs.append(f'{fn}:battle_attached')
    asp = data.get('account_server_data_scope_policy_v1.json', {})
    gp = asp.get('global_principles') or {}
    if not gp.get('progression_is_server_bound'): errs.append('asp:progression_not_server_bound')
    if not gp.get('free_currency_must_be_server_bound'): errs.append('asp:free_curr_not_server_bound')
    if not gp.get('paid_currency_can_be_account_wide'): errs.append('asp:paid_curr_not_account_wide')
    if 'account_wide' not in asp or 'server_bound' not in asp or 'mixed' not in asp:
        errs.append('asp:missing_top_level_sections')
    # opening cadence
    oc = data.get('server_opening_cadence_policy_v1.json', {})
    if not (oc.get('initial_cadence') or {}).get('weekly'): errs.append('cadence:not_weekly')
    if (oc.get('capacity_rules') or {}).get('target_real_active_users') != 200: errs.append('cadence:target_capacity_not_200')
    # overrides
    ov = data.get('global_real_world_event_override_policy_v1.json', {})
    if not any(e for e in (ov.get('override_events') or {}) if 'christmas' == e):
        errs.append('override:christmas_missing')
    # precedence has P0..P4
    prio = {p.get('priority') for p in (ov.get('precedence_order') or [])}
    for need in ('P0','P1','P2','P3','P4'):
        if need not in prio: errs.append(f'override:missing_priority:{need}')
    # merge eligibility
    mel = data.get('server_merge_eligibility_policy_v1.json', {})
    if (mel.get('eligibility_inputs') or {}).get('server_age_threshold_days_min', 0) < 60:
        errs.append('merge:age_threshold_too_low')
    # recovery classification
    rec = data.get('event_banner_recovery_classification_policy_v1.json', {})
    classes = set((rec.get('classes') or {}).keys())
    for c in ('must_catch_up','optional_catch_up','compress','skip'):
        if c not in classes: errs.append(f'recovery:missing_class:{c}')
    if not (rec.get('classification_rules') or {}).get('recover_missed_critical_milestones_not_skipped_weeks'):
        errs.append('recovery:invariant_missing')

    out = {
        'task_origin':'SLC-A-VALIDATE-POLICIES',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'files_checked': FILES,
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} errors={len(errs)}")
    for e in errs[:20]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())
