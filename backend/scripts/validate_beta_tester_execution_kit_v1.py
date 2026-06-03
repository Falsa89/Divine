#!/usr/bin/env python3
"""Validator: PROJECT-BETA-TESTER-EXECUTION-KIT (v54 Track D)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
KIT = os.path.join(ROOT, 'data/design/qa/beta_tester_execution_kit_v1.json')
DOC = os.path.join(ROOT, 'docs/divine/313_BETA_TESTER_EXECUTION_KIT.md')
MARKER = os.path.join(ROOT, 'data/design/qa/beta_tester_execution_kit_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(KIT): fail('missing kit JSON')
else:
    k = json.load(open(KIT))
    if k.get('public_sync_tag') != TAG: fail('kit public_sync_tag mismatch')
    if k.get('mode') != 'docs_only': fail('kit mode != docs_only')
    if k.get('text_language') != 'it': fail('kit text_language != it')
    sessions = k.get('sessions') or []
    lengths = sorted(s.get('length_minutes') for s in sessions)
    if lengths != [30, 60, 90]: fail(f'kit sessions lengths != [30,60,90] got {lengths}')
    fields = set((k.get('bug_template') or {}).get('fields') or [])
    for needed in ('title','severity','reproduction_steps','expected','actual','device','screenshot_or_video_url'):
        if needed not in fields: fail(f'kit bug_template missing field {needed}')
    sev = k.get('severity') or {}
    for lvl in ('P0','P1','P2','P3'):
        if lvl not in sev: fail(f'kit severity missing {lvl}')
    smoke = k.get('daily_smoke_checklist') or []
    if len(smoke) < 10: fail(f'kit daily_smoke_checklist too short: {len(smoke)}')
    focus = set(k.get('focus_areas') or [])
    for needed in ('material_raid_loop','visual_preview','reward_preview','story','heroes','navigation','rotation','performance','crash'):
        if needed not in focus: fail(f'kit focus_areas missing {needed}')

if not os.path.exists(DOC): fail('missing doc 313')
else:
    d = open(DOC).read()
    for needle in ('Beta Tester Execution Kit', 'Severity', 'Daily smoke', 'P0', 'P1', 'P2', 'P3', 'Material Raid'):
        if needle not in d: fail(f'doc 313 missing needle: {needle}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','beta_tester_execution_kit_marker_v1'),
        ('track','D'),
        ('public_sync_tag',TAG),
        ('mode','docs_only'),
        ('text_language','it'),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-BETA-TESTER-EXECUTION-KIT validator')
    sys.exit(1)
print('[PASS] PROJECT-BETA-TESTER-EXECUTION-KIT validator')
sys.exit(0)
