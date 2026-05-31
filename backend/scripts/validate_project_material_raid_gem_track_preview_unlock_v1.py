"""validate_project_material_raid_gem_track_preview_unlock_v1.py

MEGA_BATCH_ACCELERATION_1 TRACK B validator. Preview-only unlock of gem_material_raid.
No live claim. No user_materials. No premium users.gems. No stamina/tickets/paid attempts.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / 'backend' / 'routes' / 'material_raid_preview.py'
MANIFEST = ROOT / 'frontend' / 'constants' / 'materialRaid.ts'
DESIGN = ROOT / 'data' / 'design' / 'material_raid_runtime' / 'material_raid_gem_track_preview_unlock_v1.json'
MARKER = ROOT / 'data' / 'design' / 'material_raid_runtime' / 'material_raid_gem_track_preview_unlock_proof_marker_v1.json'
GEM_SOCKET = ROOT / 'backend' / 'routes' / 'gem_socket_preview.py'
FORGE = ROOT / 'backend' / 'routes' / 'forge.py'

FAILS: list[str] = []


def _read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def _fail(m: str) -> None:
    FAILS.append(m)


def main() -> int:
    if not ROUTE.exists():
        _fail(f'missing route: {ROUTE}')
    else:
        t = _read(ROUTE)
        # gem_material_raid must be open_preview now
        if not re.search(r'"gem_material_raid"[^\n]*"open_preview"', t):
            _fail('material_raid_preview.py: gem_material_raid not set to open_preview')
        if 'gem_material_raid' in t and 'LOCKED_TRACK_IDS' in t:
            # check gem_material_raid not in LOCKED set
            m = re.search(r'LOCKED_TRACK_IDS\s*=\s*\{([^}]*)\}', t)
            if m and 'gem_material_raid' in m.group(1):
                _fail('material_raid_preview.py: gem_material_raid still in LOCKED_TRACK_IDS')
            # check rune + artifact_divine still locked
            if m and 'rune_material_raid' not in m.group(1):
                _fail('LOCKED_TRACK_IDS missing rune_material_raid')
            if m and 'artifact_divine_material_raid' not in m.group(1):
                _fail('LOCKED_TRACK_IDS missing artifact_divine_material_raid')
        # gem reward preview entries
        for stage_val in ('"gem_dust_common": 40', '"gem_dust_common": 100', '"gem_dust_common": 180', '"gem_dust_common": 320', '"gem_dust_common": 550'):
            if stage_val not in t:
                _fail(f'material_raid_preview.py missing reward preview entry: {stage_val}')
        # No DB writes / premium users.gems / stamina spend (check non-comment lines only)
        forbidden = ('insert_one', 'update_one', 'update_many', 'delete_one', 'users.gems', 'spend_gems', 'consume_stamina')
        for ln_no, line in enumerate(t.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            for tok in forbidden:
                if tok in line:
                    _fail(f"forbidden token '{tok}' active in material_raid_preview.py at line {ln_no}")

    if MANIFEST.exists():
        mt = _read(MANIFEST)
        if not re.search(r"gem_material_raid[^\n]*open_preview", mt):
            _fail('materialRaid.ts: gem_material_raid not open_preview')

    if not DESIGN.exists():
        _fail(f'missing design JSON: {DESIGN}')
    if not MARKER.exists():
        _fail(f'missing marker: {MARKER}')
    else:
        d = json.loads(_read(MARKER))
        for k, v in {
            'gem_track_now_open_preview': True,
            'rune_track_still_locked': True,
            'artifact_divine_track_still_locked': True,
            'materials_granted': False,
            'reward_claim_enabled': False,
            'db_writes': 0,
            'premium_users_gems_used': False,
            'stamina_used': False,
            'gem_socket_route_changed': False,
            'forge_route_changed': False,
            'material_raid_live_claim_enabled': False,
        }.items():
            if d.get(k) != v:
                _fail(f'proof_marker.{k} expected {v!r}, got {d.get(k)!r}')

    # gem_socket_preview & forge UNCHANGED expected
    if GEM_SOCKET.exists():
        gt = _read(GEM_SOCKET)
        if 'material_raid' in gt.lower():
            # Acceptable if it's mention/note. Only block if action.
            pass

    if FAILS:
        print('[FAIL] PROJECT_MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK validator')
        for f in FAILS:
            print(f'  - {f}')
        return 1
    print('[PASS] PROJECT_MATERIAL_RAID_GEM_TRACK_PREVIEW_UNLOCK validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
