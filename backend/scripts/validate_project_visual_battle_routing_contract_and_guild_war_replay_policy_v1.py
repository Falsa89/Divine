"""
validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1.py

Validator dedicato per:
  PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_PACK

Safety semantics:
  - DESIGN_CONTRACT_AUDIT_ONLY.
  - No runtime battle conversion. No DB writes. No reward/EXP/economy changes.
  - Contract/Registry/Policy/Roadmap/Proof Marker/Doc/Validator/Suite tuple ONLY.

Asserts the contract JSON files exist with required canonical policy keys,
that registry v2 includes the canonical mode entries with the expected desired
states, that Guild War policy enforces autoresolve+replay link with reward-safe
guards, that proof marker booleans match design-only no-runtime semantics, and
that frontend/backend runtime files protected by this pack remain consistent
with the expected current state (homeAssetsManifest play=/story, battle=/story;
story.tsx still calls /api/story/battle; combat.tsx still calls /api/battle/simulate;
battle_engine.py present).

No fake PASS. No validator weakening. Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BVR_DIR = ROOT / 'data' / 'design' / 'battle_visual_routing'
CONTRACT_JSON = BVR_DIR / 'battle_visual_routing_contract_v1.json'
GUILD_WAR_POLICY_JSON = BVR_DIR / 'guild_war_autoresolve_replay_policy_v1.json'
ROADMAP_JSON = BVR_DIR / 'mode_visual_battle_conversion_roadmap_v1.json'
PROOF_MARKER_JSON = BVR_DIR / 'battle_visual_routing_contract_proof_marker_v1.json'
REGISTRY_V2_JSON = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'battle_entrypoint_registry_v2.json'
DOC_218 = ROOT / 'docs' / 'divine' / '218_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY.md'

MANIFEST = ROOT / 'frontend' / 'constants' / 'homeAssetsManifest.ts'
STORY_TSX = ROOT / 'frontend' / 'app' / 'story.tsx'
COMBAT_TSX = ROOT / 'frontend' / 'app' / 'combat.tsx'
BATTLE_ENGINE = ROOT / 'backend' / 'battle_engine.py'
SUITE_RUNNER = ROOT / 'backend' / 'scripts' / 'run_hero_skill_kit_validator_suite.py'

FAILS: list[str] = []


def _fail(m: str) -> None:
    FAILS.append(m)


def _read(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='replace')


def _load_json(p: Path) -> dict | None:
    if not p.exists():
        _fail(f'missing file: {p}')
        return None
    try:
        return json.loads(_read(p))
    except Exception as e:
        _fail(f'invalid JSON in {p}: {e}')
        return None


def check_contract() -> None:
    d = _load_json(CONTRACT_JSON)
    if not d:
        return
    cp = d.get('canonical_policy') or {}
    must_true = [
        'all_battle_modes_must_show_visual_battle',
        'guild_war_is_only_autoresolve_exception',
        'guild_war_must_provide_replay_or_view_link',
        'home_play_opens_story_hub',
    ]
    for k in must_true:
        if cp.get(k) is not True:
            _fail(f'contract.canonical_policy.{k} must be true')
    vbcr = d.get('visual_battle_contract_requirements') or {}
    for req in (
        'must_not_rerun_rng_for_reward', 'must_not_duplicate_rewards',
        'must_not_duplicate_exp', 'must_not_duplicate_quest_progress',
        'must_not_duplicate_daily_progress', 'must_not_duplicate_achievement_progress',
        'must_preserve_mode_context', 'must_preserve_enemy_payload_or_snapshot',
        'must_have_battle_instance_id_or_request_id', 'must_have_reward_claim_state',
        'must_have_idempotency_guard', 'must_have_result_commit_guard',
        'must_have_replay_viewer_contract',
    ):
        if vbcr.get(req) is not True:
            _fail(f'contract.visual_battle_contract_requirements.{req} must be true')
    payload = d.get('future_visual_battle_payload_contract') or {}
    for k in (
        'battle_instance_id', 'mode_id', 'source_entrypoint',
        'team_snapshot', 'enemy_snapshot', 'formation_snapshot',
        'battle_seed_or_precomputed_log', 'reward_policy',
        'result_commit_policy', 'replay_snapshot_policy',
    ):
        if k not in payload:
            _fail(f'contract.future_visual_battle_payload_contract missing key: {k}')
    if d.get('runtime_activation_allowed_in_this_pack') is not False:
        _fail('contract.runtime_activation_allowed_in_this_pack must be false')


def check_guild_war_policy() -> None:
    d = _load_json(GUILD_WAR_POLICY_JSON)
    if not d:
        return
    expected_top = {
        'is_only_autoresolve_exception': True,
        'autoresolve_allowed': True,
        'visual_battle_live_required': False,
        'replay_or_view_link_required': True,
        'link_must_be_available_after_resolution': True,
        'runtime_activation_allowed_in_this_pack': False,
    }
    for k, v in expected_top.items():
        if d.get(k) != v:
            _fail(f'guild_war_policy.{k} expected {v!r}, got {d.get(k)!r}')
    if d.get('link_target_future') != '/battle-replay':
        _fail("guild_war_policy.link_target_future must be '/battle-replay'")
    sreq = d.get('safety_requirements') or {}
    for k in (
        'must_not_rerun_battle_for_rewards', 'must_not_duplicate_rewards',
        'must_not_duplicate_guild_points', 'must_preserve_battle_snapshot_or_log',
        'must_capture_attacker_defender_snapshots', 'must_capture_result_summary',
        'must_capture_timeline_or_battle_log', 'must_support_expiration_policy',
        'must_support_privacy_policy', 'replay_must_not_modify_war_score',
        'replay_must_not_grant_rewards', 'replay_must_not_leak_private_account_data',
    ):
        if sreq.get(k) is not True:
            _fail(f'guild_war_policy.safety_requirements.{k} must be true')


def check_roadmap() -> None:
    d = _load_json(ROADMAP_JSON)
    if not d:
        return
    phases = d.get('phases') or []
    ids = [p.get('id') for p in phases if isinstance(p, dict)]
    required_ids = [
        'PHASE_0_CONTRACT',
        'PHASE_1_STORY_VISUAL_BATTLE_CONTRACT_AND_PAYLOAD',
        'PHASE_2_STORY_VISUAL_BATTLE_IMPLEMENTATION',
        'PHASE_3_GENERIC_VISUAL_BATTLE_RUNNER',
        'PHASE_4_MODE_BY_MODE_CONVERSION',
        'PHASE_5_GUILD_WAR_AUTORESOLVE_REPLAY_LINK',
        'PHASE_6_REWARD_IDEMPOTENCY_HARDENING',
    ]
    for rid in required_ids:
        if rid not in ids:
            _fail(f'roadmap missing phase: {rid}')
    inv = d.get('global_safety_invariants') or {}
    for k in (
        'never_grant_reward_on_replay_view',
        'never_rerun_battle_for_rewards',
        'reward_grants_must_be_idempotent',
        'all_phases_require_db_write_audit',
    ):
        if inv.get(k) is not True:
            _fail(f'roadmap.global_safety_invariants.{k} must be true')


def check_proof_marker() -> None:
    d = _load_json(PROOF_MARKER_JSON)
    if not d:
        return
    expected = {
        'mode': 'DESIGN_CONTRACT_AUDIT_ONLY',
        'all_battle_modes_must_show_visual_battle': True,
        'guild_war_is_only_autoresolve_exception': True,
        'guild_war_requires_replay_or_view_link': True,
        'home_play_route_changed': False,
        'home_play_expected_route': '/story',
        'home_battle_expected_route': '/story',
        'direct_combat_route_expected': '/combat',
        'story_runtime_changed': False,
        'combat_runtime_changed': False,
        'battle_engine_changed': False,
        'story_battle_endpoint_changed': False,
        'battle_simulate_endpoint_changed': False,
        'mode_runtime_conversion_done': False,
        'db_writes': 0,
        'reward_logic_changed': False,
        'exp_logic_changed': False,
        'quest_daily_achievement_logic_changed': False,
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
        if d.get(k) != v:
            _fail(f'proof_marker.{k} expected {v!r}, got {d.get(k)!r}')


def check_registry_v2() -> None:
    d = _load_json(REGISTRY_V2_JSON)
    if not d:
        return
    entries = d.get('entries') or []
    feat = {e.get('feature'): e for e in entries if isinstance(e, dict)}
    required_features = (
        'home_play', 'story_stage_battle', 'direct_visual_combat_route',
        'guild_war', 'raid', 'tower', 'pvp',
    )
    for rf in required_features:
        if rf not in feat:
            _fail(f'registry_v2 missing feature: {rf}')

    story = feat.get('story_stage_battle') or {}
    if story.get('desired_state') != 'visual_battle_required':
        _fail("registry_v2.story_stage_battle.desired_state must be 'visual_battle_required'")
    if story.get('status') not in ('transitional_debt', 'audit_only_not_changed'):
        _fail(f"registry_v2.story_stage_battle.status unexpected: {story.get('status')}")

    gw = feat.get('guild_war') or {}
    if gw.get('status') != 'allowed_autoresolve_exception':
        _fail("registry_v2.guild_war.status must be 'allowed_autoresolve_exception'")
    if gw.get('replay_link_required') is not True:
        _fail('registry_v2.guild_war.replay_link_required must be true')

    policy = d.get('global_policy') or {}
    must_true = [
        'all_battle_modes_must_show_visual_battle',
        'only_guild_war_can_autoresolve',
        'guild_war_requires_replay_link',
        'do_not_convert_all_modes_in_one_pack',
        'future_visual_wiring_requires_contract',
        'reward_duplication_guard_required',
        'exp_duplication_guard_required',
        'quest_daily_achievement_guard_required',
        'battle_instance_id_required',
        'replay_must_not_grant_rewards',
        'replay_must_not_rerun_battle',
    ]
    for k in must_true:
        if policy.get(k) is not True:
            _fail(f'registry_v2.global_policy.{k} must be true')


def check_doc() -> None:
    if not DOC_218.exists():
        _fail(f'missing doc: {DOC_218}')


def check_runtime_files_unchanged_state() -> None:
    # We cannot diff git here cheaply; assert content stability markers.
    if not MANIFEST.exists():
        _fail(f'missing manifest: {MANIFEST}')
    else:
        t = _read(MANIFEST)
        if not re.search(r"play\s*:\s*'\/story'", t):
            _fail("homeAssetsManifest.ts no longer has play:'/story'")
        if not re.search(r"battle\s*:\s*'\/story'", t):
            _fail("homeAssetsManifest.ts no longer has battle:'/story'")
        # forbid active reintroduction of play:'/combat' on a non-comment line
        for ln_no, line in enumerate(t.splitlines(), start=1):
            s = line.lstrip()
            if s.startswith('//') or s.startswith('*'):
                continue
            m = re.match(r"play\s*:\s*'([^']+)'", s)
            if m and m.group(1) == '/combat':
                _fail(f'homeAssetsManifest.ts active play points to /combat at line {ln_no}')

    if not STORY_TSX.exists():
        _fail(f'missing story.tsx: {STORY_TSX}')
    else:
        if '/api/story/battle' not in _read(STORY_TSX):
            _fail("story.tsx no longer references '/api/story/battle' (auto-resolve must remain unchanged)")

    if not COMBAT_TSX.exists():
        _fail(f'missing combat.tsx: {COMBAT_TSX}')
    else:
        if '/api/battle/simulate' not in _read(COMBAT_TSX):
            _fail("combat.tsx no longer references '/api/battle/simulate' (direct visual route must remain)")

    if not BATTLE_ENGINE.exists():
        _fail('backend/battle_engine.py missing (must remain untouched)')


def check_suite_runner_tuple() -> None:
    if not SUITE_RUNNER.exists():
        _fail(f'missing suite runner: {SUITE_RUNNER}')
        return
    text = _read(SUITE_RUNNER)
    if 'PUBLIC_SYNC_TAG_v29_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY' not in text:
        _fail('suite runner missing PUBLIC_SYNC_TAG_v29 sentinel')
    if 'VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY_REGISTRATION_SENTINEL' not in text:
        _fail('suite runner missing REGISTRATION_SENTINEL')
    tuple_pattern = re.compile(
        r"\(\s*'PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY'\s*,\s*"
        r"'validate_project_visual_battle_routing_contract_and_guild_war_replay_policy_v1\.py'\s*\)"
    )
    matches = tuple_pattern.findall(text)
    if len(matches) == 0:
        _fail('suite runner missing tuple for PROJECT-VISUAL-BATTLE-ROUTING-CONTRACT-AND-GUILD-WAR-REPLAY-POLICY')
    elif len(matches) > 1:
        _fail(f'suite runner has duplicate tuple (count={len(matches)}); tuple_count_required=1')


def main() -> int:
    check_contract()
    check_guild_war_policy()
    check_roadmap()
    check_proof_marker()
    check_registry_v2()
    check_doc()
    check_runtime_files_unchanged_state()
    check_suite_runner_tuple()

    if FAILS:
        print('[FAIL] PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY validator')
        for f in FAILS:
            print(f'  - {f}')
        return 1
    print('[PASS] PROJECT_VISUAL_BATTLE_ROUTING_CONTRACT_AND_GUILD_WAR_REPLAY_POLICY validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
