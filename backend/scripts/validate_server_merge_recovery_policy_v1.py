#!/usr/bin/env python3
"""SLC-A: Validate merge recovery + catch-up pool policy (read-only)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path('/app/data/design/server_lifecycle')
OUT = Path(ROOT, '_validate_server_merge_recovery_policy_v1_result.json')
MR  = ROOT/'merge_recovery_season_policy_v1.json'
CP  = ROOT/'merge_catch_up_pool_schema_v1.json'
MM  = ROOT/'merged_mature_calendar_policy_v1.json'


def main():
    errs=[]
    if not MR.exists(): errs.append('mr:missing'); print('FAIL'); return 2
    if not CP.exists(): errs.append('cp:missing'); print('FAIL'); return 2
    if not MM.exists(): errs.append('mm:missing'); print('FAIL'); return 2
    mr = json.loads(MR.read_text())
    cp = json.loads(CP.read_text())
    mm = json.loads(MM.read_text())
    if mr.get('default_duration_days') not in range(14, 22): errs.append('mr:bad_default_duration')
    rng = mr.get('configurable_duration_days_range') or []
    if not (isinstance(rng,list) and len(rng)==2 and rng[0]==14 and rng[1]>=14):
        errs.append('mr:bad_range')
    if mr.get('key_invariant','') != 'Recover missed critical milestones, not skipped weeks.':
        errs.append('mr:key_invariant_missing_or_wrong')
    if not (mr.get('behavior_rules') or {}).get('do_not_inherit_oldest_calendar_blindly'):
        errs.append('mr:must_not_inherit_oldest_blindly')
    if not (mr.get('behavior_rules') or {}).get('do_not_replay_weeks'):
        errs.append('mr:must_not_replay_weeks')
    if not (mr.get('behavior_rules') or {}).get('works_for_10_plus_server_merges_via_milestone_pool_not_week_replay'):
        errs.append('mr:10plus_merge_rule_missing')
    # catch-up pool
    req = set(cp.get('required_fields') or [])
    for f in ['merge_group_id','source_server_ids','target_server_id','baseline_progress_index','missed_milestone_ids','recovery_class','banner_pool','shop_pool','compressed_rewards','start_at','end_at','max_parallel_banners','pity_policy','purchase_limit_policy']:
        if f not in req: errs.append(f'cp:missing_field:{f}')
    if not cp.get('design_only'): errs.append('cp:not_design_only')
    # mature
    if not (mm.get('entry_criteria') or {}).get('merge_recovery_window_completed'):
        errs.append('mm:entry_criteria_missing')
    if not (mm.get('reseed_rules') or {}).get('new_server_rush_not_replayed'):
        errs.append('mm:new_server_rush_must_not_replay')

    out = {
        'task_origin':'SLC-A-VALIDATE-MERGE-RECOVERY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} errors={len(errs)}")
    for e in errs[:20]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())
