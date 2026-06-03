#!/usr/bin/env python3
"""Validator: PROJECT-GUIDE-CODEX-RUNTIME-PLAN (v54 Track E)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PLAN = os.path.join(ROOT, 'data/design/release_acceleration/guide_codex_runtime_plan_v1.json')
ENTRIES = os.path.join(ROOT, 'data/design/release_acceleration/alpha_codex_entries_v1.json')
SCREEN = os.path.join(ROOT, 'frontend/app/alpha-codex.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/guide_codex_runtime_plan_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(PLAN): fail('missing plan')
else:
    p = json.load(open(PLAN))
    if p.get('public_sync_tag') != TAG: fail('plan public_sync_tag mismatch')
    if p.get('mode') != 'static_deeplink_only': fail('plan mode != static_deeplink_only')
    if p.get('backend_required') is not False: fail('plan backend_required != false')
    if p.get('mutation') is not False: fail('plan mutation != false')
    if p.get('home_menu_mandatory_routing') is not False: fail('plan home_menu_mandatory_routing != false')
    if p.get('text_language') != 'it': fail('plan text_language != it')
    sc = p.get('alpha_codex_screen') or {}
    if sc.get('path') != 'frontend/app/alpha-codex.tsx': fail('plan screen path mismatch')
    if sc.get('route') != '/alpha-codex': fail('plan screen route mismatch')
    if sc.get('deeplink_only') is not True: fail('plan screen deeplink_only != true')
    if sc.get('calls_backend') is not False: fail('plan screen calls_backend != false')

if not os.path.exists(ENTRIES): fail('missing entries')
else:
    e = json.load(open(ENTRIES))
    if e.get('public_sync_tag') != TAG: fail('entries public_sync_tag mismatch')
    if e.get('text_language') != 'it': fail('entries text_language != it')
    ids = {it.get('id') for it in (e.get('entries') or [])}
    needed = {'material_raid_alpha_loop','visual_preview','reward_preview_no_claim','bug_reporting','asset_placeholder_vs_final_art'}
    if not needed.issubset(ids): fail(f'entries ids missing: {sorted(needed - ids)}')

if not os.path.exists(SCREEN): fail('missing alpha-codex.tsx screen')
else:
    s = open(SCREEN).read()
    for needle in ('export default function AlphaCodexScreen', 'useRouter', 'Alpha Codex', 'deeplink-only'):
        if needle not in s: fail(f'screen missing needle: {needle}')
    for forb in (
        'import pymongo','from pymongo','import motor','from motor','import redis','from redis',
        'AsyncIOMotorClient(','MongoClient(',
        "fetch('/api/battle/simulate", 'fetch("/api/battle/simulate',
        "fetch('/api/story/battle", 'fetch("/api/story/battle',
        'AsyncStorage.setItem(', 'AsyncStorage.removeItem(',
    ):
        if forb in s: fail(f'screen forbidden token: {forb}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','guide_codex_runtime_plan_marker_v1'),
        ('track','E'),
        ('public_sync_tag',TAG),
        ('screen_path','frontend/app/alpha-codex.tsx'),
        ('screen_route','/alpha-codex'),
        ('deeplink_only',True),
        ('home_menu_mandatory_routing',False),
        ('backend_required',False),
        ('mutation',False),
        ('text_language','it'),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-GUIDE-CODEX-RUNTIME-PLAN validator')
    sys.exit(1)
print('[PASS] PROJECT-GUIDE-CODEX-RUNTIME-PLAN validator')
sys.exit(0)
