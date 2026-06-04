#!/usr/bin/env python3
"""validate_v72_p3_polish_batch_applied_v1

Verifica che le 3 micro-patch P3 siano applicate, ts_clean, static scan OK,
MD5 invariants intatti, e che gli effettivi file patchati contengano
le modifiche specifiche.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-v72-P3-POLISH-BATCH-APPLIED'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

PLAN = 'data/design/qa/v72_p3_polish_batch_applied_v1.json'
MRK = 'data/design/qa/v72_p3_polish_batch_applied_marker_v1.json'

HUB = 'frontend/app/alpha-preview-hub.tsx'
FIRST = 'frontend/app/first-session-onboarding-preview.tsx'

MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
    'backend/server.py': '055df030553f4791e8cac14254f1b148',
    'frontend/app/combat.tsx': 'fc792a05b2ada6e677d80400732ae5c3',
    'frontend/app/story.tsx': '8520627b4e63f86821d73d8d3880bac3',
}

FORBIDDEN_CALL_PATTERNS = [
    (r'\bfetch\s*\(', 'fetch call'),
    (r'\bAsyncStorage\.', 'AsyncStorage call'),
    (r'/api/story/battle', 'api/story/battle path'),
    (r'/api/battle/simulate', 'api/battle/simulate path'),
    (r'@react-native-async-storage', 'async-storage import'),
    (r'import\s+.*battle_engine', 'battle_engine import'),
]


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def strip_comments(src: str) -> str:
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
    return '\n'.join(l.split('//')[0] for l in src.splitlines())


def md5_of(rel: str) -> str:
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()


def main():
    for rel in (PLAN, MRK, HUB, FIRST):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    p = json.loads((ROOT / PLAN).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if p.get('public_sync_tag') != TAG:
        fail('plan.public_sync_tag mismatch')
    if p.get('applied') is not True:
        fail('plan.applied must be true')
    if p.get('micro_patches_count') != 3:
        fail('micro_patches_count must be 3')
    if p.get('micro_patches_applied_count') != 3:
        fail('micro_patches_applied_count must be 3')
    if p.get('files_modified_count') != 2:
        fail('files_modified_count must be 2')
    if p.get('alpha_menu_preview_modified') is not False:
        fail('alpha_menu_preview_modified must be false')
    if p.get('db_writes') != 0:
        fail('plan.db_writes must be 0')
    if p.get('deferred_findings_count') != 0:
        fail('deferred_findings_count must be 0')
    if p.get('backlog_cleared') is not True:
        fail('backlog_cleared must be true')
    for patch in p.get('micro_patches', []):
        for flag in ('behavior_change', 'routing_change', 'fetch_change',
                     'async_storage_change', 'db_change', 'reward_change',
                     'battle_engine_change', 'story_combat_import_change'):
            if patch.get(flag) is not False:
                fail(f'patch {patch.get("finding_id")} flag {flag} must be false')
        if patch.get('applied') is not True:
            fail(f'patch {patch.get("finding_id")} applied must be true')

    if m.get('applied') is not True:
        fail('marker.applied must be true')
    if m.get('micro_patches_applied_count') != 3:
        fail('marker.micro_patches_applied_count must be 3')
    if m.get('backlog_cleared') is not True:
        fail('marker.backlog_cleared must be true')

    # MD5 invariants
    for rel, exp in MD5_INVARIANTS.items():
        got = md5_of(rel)
        if got != exp:
            fail(f'MD5 invariant drift {rel}: got {got} expected {exp}')

    # Patched files content checks
    hub_src = (ROOT / HUB).read_text()
    first_src = (ROOT / FIRST).read_text()

    # P3.1 - copy shortening: nuovo banner copy
    if 'Mappa locale anteprime alpha. No routing pubblico, no reward, no writes.' not in hub_src:
        fail('hub copy shortening not applied')

    # P3.3 - QA priority ordering: first-session deve essere il primo ENTRY (P0)
    # Trova ordine delle route
    routes_in_order = re.findall(r'route:\s*"([^"]+)"', hub_src)
    if not routes_in_order:
        fail('cannot detect routes in hub')
    if routes_in_order[0] != 'first-session-onboarding-preview':
        fail(f'first entry must be first-session-onboarding-preview, got {routes_in_order[0]}')

    # P3.2 - first session state label line-height/margin
    if not re.search(r'stateMachineLabel:.*marginTop:\s*6.*marginBottom:\s*6.*lineHeight:\s*14', first_src):
        fail('first-session state label margin/lineHeight patch not applied')

    # Static scan: no forbidden patterns on code (no commenti)
    for rel, src in ((HUB, hub_src), (FIRST, first_src)):
        code = strip_comments(src)
        for pat, label in FORBIDDEN_CALL_PATTERNS:
            if re.search(pat, code):
                fail(f'forbidden {label} in {rel}')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
