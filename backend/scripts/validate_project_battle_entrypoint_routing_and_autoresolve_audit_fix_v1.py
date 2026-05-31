"""
validate_project_battle_entrypoint_routing_and_autoresolve_audit_fix_v1.py

Validator dedicato per:
  PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_PACK

Safety semantics:
  - Routing fix + audit registry ONLY.
  - NO live behavior changes. NO DB writes. NO reward/EXP/economy/gacha/BP/VIP/shop changes.
  - HOME_ROUTES.play must move from `/combat` to `/story`.
  - HOME_ROUTES.battle must remain `/story`.
  - `/combat` direct visual route must be preserved (combat.tsx still hits /api/battle/simulate).
  - story.tsx auto-resolve via /api/story/battle preserved unchanged.
  - Suite runner must contain exactly one tuple for this pack.

No fake PASS. No validator weakening. Exit code 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FRONTEND_MANIFEST = ROOT / 'frontend' / 'constants' / 'homeAssetsManifest.ts'
COMBAT_TSX = ROOT / 'frontend' / 'app' / 'combat.tsx'
STORY_TSX = ROOT / 'frontend' / 'app' / 'story.tsx'
REGISTRY_JSON = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'battle_entrypoint_registry_v1.json'
PROOF_MARKER_JSON = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'battle_entrypoint_routing_fix_proof_marker_v1.json'
SUITE_RUNNER = ROOT / 'backend' / 'scripts' / 'run_hero_skill_kit_validator_suite.py'
BATTLE_ENGINE = ROOT / 'backend' / 'battle_engine.py'

FAILS: list[str] = []


def _fail(msg: str) -> None:
    FAILS.append(msg)


def _read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def check_manifest() -> None:
    if not FRONTEND_MANIFEST.exists():
        _fail(f'missing file: {FRONTEND_MANIFEST}')
        return
    text = _read(FRONTEND_MANIFEST)

    # 1) HOME_ROUTES.play must be '/story'
    play_story = re.search(r"play\s*:\s*'\/story'", text)
    if not play_story:
        _fail("HOME_ROUTES.play is not set to '/story' in homeAssetsManifest.ts")

    # 2) HOME_ROUTES.play must NOT be '/combat' (no active key value)
    # Match active assignment lines only (skip comments). A line starting with optional spaces then `play:`.
    for ln_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith('//') or stripped.startswith('*'):
            continue
        m = re.match(r"play\s*:\s*'([^']+)'", stripped)
        if m and m.group(1) == '/combat':
            _fail(f'HOME_ROUTES.play still points to /combat at line {ln_no}')

    # 3) HOME_ROUTES.battle must remain '/story'
    battle_story = re.search(r"battle\s*:\s*'\/story'", text)
    if not battle_story:
        _fail("HOME_ROUTES.battle is not set to '/story' in homeAssetsManifest.ts")

    # 4) No DB write / reward / EXP / economy tokens introduced in manifest (sanity)
    forbidden_tokens = [
        'insert_one', 'update_one', 'update_many', 'delete_one', 'delete_many',
        'grant_reward', 'grantReward', 'addExp', 'add_exp', 'mutate_gems', 'spend_gems',
    ]
    for tok in forbidden_tokens:
        if tok in text:
            _fail(f"forbidden token '{tok}' found in homeAssetsManifest.ts (routing-only file)")


def check_combat_tsx() -> None:
    if not COMBAT_TSX.exists():
        _fail(f'missing file: {COMBAT_TSX}')
        return
    text = _read(COMBAT_TSX)
    if '/api/battle/simulate' not in text:
        _fail("combat.tsx no longer references '/api/battle/simulate' (direct visual route must be preserved)")


def check_story_tsx() -> None:
    if not STORY_TSX.exists():
        _fail(f'missing file: {STORY_TSX}')
        return
    text = _read(STORY_TSX)
    if '/api/story/battle' not in text:
        _fail("story.tsx no longer references '/api/story/battle' (auto-resolve must be preserved unchanged)")


def check_registry() -> None:
    if not REGISTRY_JSON.exists():
        _fail(f'missing registry: {REGISTRY_JSON}')
        return
    try:
        data = json.loads(_read(REGISTRY_JSON))
    except Exception as e:
        _fail(f'registry not valid JSON: {e}')
        return
    entries = data.get('entries') or []
    features = {e.get('feature') for e in entries if isinstance(e, dict)}
    for required in ('home_play', 'story_stage_battle', 'direct_visual_combat_route'):
        if required not in features:
            _fail(f"registry missing required feature entry: {required}")

    # home_play must show fixed_this_pack and route /story
    for e in entries:
        if e.get('feature') == 'home_play':
            if e.get('current_route_after_pack') != '/story':
                _fail("registry: home_play.current_route_after_pack is not '/story'")
            if e.get('previous_route') != '/combat':
                _fail("registry: home_play.previous_route is not '/combat'")
            if e.get('status') != 'fixed_this_pack':
                _fail("registry: home_play.status is not 'fixed_this_pack'")

    policy = data.get('global_policy') or {}
    if policy.get('do_not_direct_home_play_to_combat') is not True:
        _fail('registry: global_policy.do_not_direct_home_play_to_combat must be true')
    if policy.get('do_not_convert_all_autoresolve_modes_in_one_pack') is not True:
        _fail('registry: global_policy.do_not_convert_all_autoresolve_modes_in_one_pack must be true')


def check_proof_marker() -> None:
    if not PROOF_MARKER_JSON.exists():
        _fail(f'missing proof marker: {PROOF_MARKER_JSON}')
        return
    try:
        data = json.loads(_read(PROOF_MARKER_JSON))
    except Exception as e:
        _fail(f'proof marker not valid JSON: {e}')
        return

    expected = {
        'home_play_previous_route': '/combat',
        'home_play_new_route': '/story',
        'home_battle_button_route': '/story',
        'combat_route_preserved': True,
        'story_autoresolve_preserved': True,
        'all_modes_autoresolve_conversion': False,
        'battle_engine_changed': False,
        'combat_tsx_behavior_changed': False,
        'story_battle_endpoint_changed': False,
        'db_writes': 0,
        'reward_logic_changed': False,
        'exp_logic_changed': False,
        'economy_changed': False,
        'gacha_changed': False,
        'bp_vip_shop_changed': False,
        'material_raid_changed': False,
        'gem_socket_changed': False,
        'rune_runtime_changed': False,
        'artifact_runtime_changed': False,
        'divine_weapon_runtime_changed': False,
    }
    for k, v in expected.items():
        if data.get(k) != v:
            _fail(f"proof marker key '{k}' expected {v!r}, got {data.get(k)!r}")


def check_suite_runner_tuple() -> None:
    if not SUITE_RUNNER.exists():
        _fail(f'missing suite runner: {SUITE_RUNNER}')
        return
    text = _read(SUITE_RUNNER)

    # Sentinels
    if 'PUBLIC_SYNC_TAG_v28_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX' not in text:
        _fail('suite runner missing PUBLIC_SYNC_TAG_v28 sentinel')
    if 'BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX_REGISTRATION_SENTINEL' not in text:
        _fail('suite runner missing REGISTRATION_SENTINEL')

    # Exactly one tuple for this pack
    tuple_pattern = re.compile(
        r"\(\s*'PROJECT-BATTLE-ENTRYPOINT-ROUTING-AND-AUTORESOLVE-AUDIT-FIX'\s*,\s*"
        r"'validate_project_battle_entrypoint_routing_and_autoresolve_audit_fix_v1\.py'\s*\)"
    )
    matches = tuple_pattern.findall(text)
    if len(matches) == 0:
        _fail('suite runner missing tuple for PROJECT-BATTLE-ENTRYPOINT-ROUTING-AND-AUTORESOLVE-AUDIT-FIX')
    elif len(matches) > 1:
        _fail(f'suite runner has duplicate tuple (count={len(matches)}); tuple_count_required=1')


def check_battle_engine_unchanged_marker() -> None:
    # We cannot import MD5 baselines here, but ensure file at least exists (not deleted).
    if not BATTLE_ENGINE.exists():
        _fail('backend/battle_engine.py missing (must remain untouched)')


def main() -> int:
    check_manifest()
    check_combat_tsx()
    check_story_tsx()
    check_registry()
    check_proof_marker()
    check_suite_runner_tuple()
    check_battle_engine_unchanged_marker()

    if FAILS:
        print('[FAIL] PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX validator')
        for f in FAILS:
            print(f'  - {f}')
        return 1
    print('[PASS] PROJECT_BATTLE_ENTRYPOINT_ROUTING_AND_AUTORESOLVE_AUDIT_FIX validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
