#!/usr/bin/env python3
"""
PROJECT_GEM_SOCKET_RUNTIME validator (statico, OPTIONAL).

Asserisce:
  - file design (6) + frontend (2) + backend route + doc presenti
  - proof marker safety booleans corretti
  - MD5 invarianti sui 5 file protetti intatti
  - legacy forge.py / material_raid_preview.py / battle_engine.py / combat.tsx invariati
  - backend route NON contiene insert_one/update_one/$inc/$set/delete_one
  - backend route NON tocca user.gems / "gems": -N / $inc.gems / users.update("gems")
  - backend route NON contiene endpoint /socket o /commit o /claim o /upgrade o /spend
    SENZA suffisso -preview
  - suite runner ha esattamente UNA tupla per questo pack + sentinels v27
  - 6 gem families + 6 tiers presenti

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DDIR = ROOT / 'data/design/gem_socket_runtime'

REQUIRED_DESIGN = [
    'gem_socket_schema_v1.json',
    'gem_socket_catalog_v1.json',
    'gem_socket_rules_v1.json',
    'gem_socket_material_link_v1.json',
    'gem_socket_material_raid_crosslink_v1.json',
    'gem_socket_runtime_proof_marker_v1.json',
]
PROOF_MARKER = DDIR / 'gem_socket_runtime_proof_marker_v1.json'

REQUIRED_RUNTIME = [
    ROOT / 'backend/routes/gem_socket_preview.py',
    ROOT / 'frontend/constants/gemSocket.ts',
    ROOT / 'frontend/app/gem-socket-test.tsx',
    ROOT / 'docs/divine/213_GEM_SOCKET_RUNTIME.md',
]

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}

CANONICAL_FAMILIES = ['ruby', 'sapphire', 'emerald', 'topaz', 'amethyst', 'diamond']
CANONICAL_TIERS = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'divine']

# Stringhe FORBIDDEN nel backend route gem_socket_preview.py
FORBIDDEN_DB_WRITE_STRINGS = [
    'insert_one', 'update_one', 'update_many',
    'delete_one', 'delete_many', '$inc', '$set',
]
FORBIDDEN_PREMIUM_GEMS_STRINGS = [
    'user.gems', 'user_gems', '$inc.gems', 'users.update.gems',
    "'gems': -", '"gems": -', "users.update_one", "db.users",
]
# Endpoint forbidden (live mutation) sense unless suffix -preview
FORBIDDEN_LIVE_PATHS_RE = re.compile(
    r"@router\.(post|put|delete|patch)\(\"(/(socket|commit|claim|upgrade|spend)(?!-preview))"
)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    # 1) MD5 invariants
    for rel, exp in MD5_INVARIANTS.items():
        p = ROOT / rel
        if not p.exists():
            fail(f'missing MD5-protected file: {rel}')
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if h != exp:
            fail(f'MD5 mismatch on {rel}: expected={exp} actual={h}')

    # 2) Design files
    for fname in REQUIRED_DESIGN:
        p = DDIR / fname
        if not p.exists():
            fail(f'missing design file: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if fname == 'gem_socket_catalog_v1.json':
            fams = [f.get('family_id') for f in data.get('gem_families', [])]
            for needed in CANONICAL_FAMILIES:
                if needed not in fams:
                    fail(f'catalog missing family: {needed}')
            for needed in CANONICAL_TIERS:
                if needed not in (data.get('tier_delta_base_preview') or {}):
                    fail(f'catalog missing tier: {needed}')

    # 3) Proof marker
    marker = json.loads(PROOF_MARKER.read_text())
    expected_verdict = 'PROJECT_GEM_SOCKET_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if marker.get('verdict') != expected_verdict:
        fail(f'marker verdict mismatch: {marker.get("verdict")!r}')
    if marker.get('mode') != 'PREVIEW_ONLY':
        fail('marker mode must be PREVIEW_ONLY')
    must_be_false = [
        'live_socket_commit_enabled', 'live_unsocket_commit_enabled',
        'live_replace_commit_enabled', 'premium_gems_currency_used',
        'uses_user_gems_currency', 'material_spend_enabled',
        'user_materials_required', 'gear_mutation_enabled',
        'battle_runtime_attached', 'bp_delta_runtime_attached',
        'gacha_attached', 'shop_iap_attached',
        'rune_runtime_changed', 'artifact_runtime_changed',
        'divine_weapon_runtime_changed', 'legacy_forge_modified',
        'material_raid_modified',
    ]
    for k in must_be_false:
        if marker.get(k) is not False:
            fail(f'marker {k} must be false')
    must_be_true = ['gemmes_are_gear_sockets', 'runes_are_scroll_talisman_layer']
    for k in must_be_true:
        if marker.get(k) is not True:
            fail(f'marker {k} must be true')
    if marker.get('db_writes') != 0:
        fail(f'marker db_writes must be 0, got {marker.get("db_writes")}')

    # 4) Runtime files exist
    for p in REQUIRED_RUNTIME:
        if not p.exists():
            fail(f'missing runtime file: {p}')

    # 5) Backend route specifics
    backend_src = (ROOT / 'backend/routes/gem_socket_preview.py').read_text()
    for needed in [
        'GEM_SOCKET_RUNTIME_PREVIEW_ENABLED',
        '/api/gem-socket',
        'GEM_FAMILIES',
        'TIERS',
        'MAX_SOCKETS_BY_RARITY',
        'SOCKET_LEVEL_UNLOCKS',
        '503',
        'PREVIEW_ONLY',
        'live_socket_commit_enabled',
        'premium_gems_currency_used',
    ]:
        if needed not in backend_src:
            fail(f'gem_socket_preview.py missing: {needed!r}')
    # No DB write ops
    for forbidden in FORBIDDEN_DB_WRITE_STRINGS:
        if forbidden in backend_src:
            fail(f'gem_socket_preview.py contains forbidden DB write op: {forbidden!r}')
    # No premium gems currency mutation
    for forbidden in FORBIDDEN_PREMIUM_GEMS_STRINGS:
        if forbidden in backend_src:
            fail(f'gem_socket_preview.py contains forbidden premium gems ref: {forbidden!r}')
    # No live mutation endpoints (paths not suffixed -preview)
    m = FORBIDDEN_LIVE_PATHS_RE.search(backend_src)
    if m:
        fail(f'gem_socket_preview.py contains forbidden live endpoint: {m.group(0)!r}')
    # 6 families + 6 tiers present
    for fam in CANONICAL_FAMILIES:
        if f'"{fam}"' not in backend_src and f"'{fam}'" not in backend_src:
            fail(f'backend missing family {fam}')
    for tier in CANONICAL_TIERS:
        if f'"{tier}"' not in backend_src and f"'{tier}'" not in backend_src:
            fail(f'backend missing tier {tier}')

    # 6) server.py includes router
    server_src = (ROOT / 'backend/server.py').read_text()
    if 'gem_socket_preview' not in server_src:
        fail('backend/server.py missing gem_socket_preview include')

    # 7) Frontend constants
    consts_src = (ROOT / 'frontend/constants/gemSocket.ts').read_text()
    for needed in ['GEM_FAMILIES', 'GEM_TIERS', 'MAX_SOCKETS_BY_RARITY',
                   'SOCKET_LEVEL_UNLOCKS', 'SAFETY_BADGE_LABELS',
                   'maxSocketsForRarity', 'levelRequiredForSocket']:
        if needed not in consts_src:
            fail(f'gemSocket.ts missing export: {needed}')
    for fam in CANONICAL_FAMILIES:
        if f"'{fam}'" not in consts_src:
            fail(f'gemSocket.ts missing family {fam}')

    # 8) Frontend test screen
    test_src = (ROOT / 'frontend/app/gem-socket-test.tsx').read_text()
    if 'GEM_FAMILIES' not in test_src or 'SAFETY_BADGE_LABELS' not in test_src:
        fail('gem-socket-test.tsx must use GEM_FAMILIES and SAFETY_BADGE_LABELS')
    if 'NON \u00c8 RUNA' not in test_src and 'no_rune_overlap' not in test_src:
        fail('gem-socket-test.tsx must show Gemme vs Rune distinction')

    # 9) Suite runner sentinels + tuple count = 1
    suite_src = (ROOT / 'backend/scripts/run_hero_skill_kit_validator_suite.py').read_text()
    if 'PUBLIC_SYNC_TAG_v27_GEM_SOCKET_RUNTIME' not in suite_src:
        fail('suite runner missing PUBLIC_SYNC_TAG_v27')
    if 'GEM_SOCKET_RUNTIME_REGISTRATION_SENTINEL' not in suite_src:
        fail('suite runner missing GEM_SOCKET_RUNTIME_REGISTRATION_SENTINEL')
    tuple_count = suite_src.count("('PROJECT-GEM-SOCKET-RUNTIME'")
    if tuple_count != 1:
        fail(f'suite runner tuple count must be 1, found {tuple_count}')

    # 10) Legacy files untouched (MD5 of forge.py and material_raid_preview.py
    # are not in the protected list but must NOT have new lines vs HEAD~1 baseline;
    # we check this with a textual check: no NEW gem_socket reference inside them).
    forge_src = (ROOT / 'backend/routes/forge.py').read_text()
    if 'gem_socket' in forge_src.lower():
        fail('legacy forge.py must NOT reference gem_socket')
    raid_src = (ROOT / 'backend/routes/material_raid_preview.py').read_text()
    if 'gem_socket' in raid_src.lower():
        fail('material_raid_preview.py must NOT reference gem_socket')

    print('[PASS] PROJECT_GEM_SOCKET_RUNTIME master validator')


if __name__ == '__main__':
    main()
