#!/usr/bin/env python3
"""v65 Track F — QA matrix + v66 readiness validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
QA=os.path.join(ROOT,'data/design/qa/material_raid_first_controlled_live_staging_claim_qa_matrix_v1.json')
R=os.path.join(ROOT,'data/design/release_acceleration/material_raid_v65_to_v66_readiness_report_v1.json')
MK=os.path.join(ROOT,'data/design/qa/material_raid_v65_qa_readiness_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/390_MATERIAL_RAID_v65_QA_AND_v66_READINESS.md')
F=[]
def f(m): F.append(m)
for p in (QA,R,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(QA):
    d=json.load(open(QA))
    ch=d.get('checks') or []
    if len(ch)<20: f('qa checks count too low')
    must={'approval_phrase_received','approval_checksum_verified','scope_locked_to_material_only',
          'allowlist_max_5_users','per_user_cap_1','total_cap_10',
          'premium_currency_blocked','gacha_blocked','shop_blocked','vip_blocked',
          'battle_pass_blocked','broad_rollout_blocked','public_claim_blocked',
          'apply_default_dry_run','isolated_staging_marker_required',
          'no_pymongo_motor_redis_in_script','no_server_py_change',
          'no_battle_engine_change','no_frontend_tsx_change',
          'rollback_plan_present','observation_metrics_complete',
          'blocked_result_includes_failed_gate','v66_readiness_report_present'}
    got={c.get('name') for c in ch}
    miss=must-got
    if miss: f(f'qa missing checks: {sorted(miss)}')
    sev=d.get('severity_summary') or {}
    if (sev.get('P0') or 0) < 18: f('qa P0 count too low')
if os.path.exists(R):
    d=json.load(open(R))
    if 'BLOCKED_NOT_APPLIED_SAFE' not in (d.get('v65_apply_result') or '')  and 'PASS' not in (d.get('v65_apply_result') or ''):
        f(f'readiness v65_apply_result unexpected: {d.get("v65_apply_result")}')
    if d.get('v65_side_effects') is not False: f('readiness v65_side_effects!=false')
    if d.get('v65_db_writes')!=0: f('readiness v65_db_writes!=0')
    if d.get('material_raid_next_wave_gated') is not True: f('readiness material_raid_next_wave_gated!=true')
    if d.get('material_raid_broad_rollout_allowed') is not False: f('readiness broad_rollout_allowed!=false')
    nx=d.get('next_recommended_if_clean_or_safely_blocked') or []
    if 'story_runtime_adapter_and_first_node_v66' not in nx:
        f('readiness missing v66 next_recommended')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-v65-QA-AND-v66-READINESS'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-v65-QA-AND-v66-READINESS'); sys.exit(0)
