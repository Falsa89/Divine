"""
validate_project_story_visual_battle_wiring_contract_v1.py

Validator dedicato per:
  PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT_PACK (PHASE_1)

Safety semantics:
  - DESIGN_CONTRACT_AUDIT_ONLY.
  - No runtime Story conversion. No DB writes. No reward/EXP/story progress/economy changes.
  - Contract/Payload/Idempotency/Transition Plan/Registry v3/Doc/Validator/Suite tuple ONLY.

No fake PASS. No validator weakening. Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SVB_DIR = ROOT / 'data' / 'design' / 'story_visual_battle'
CONTRACT_JSON = SVB_DIR / 'story_visual_battle_wiring_contract_v1.json'
PAYLOAD_JSON = SVB_DIR / 'story_battle_instance_payload_contract_v1.json'
IDEMP_JSON = SVB_DIR / 'story_reward_idempotency_contract_v1.json'
TRANSITION_JSON = SVB_DIR / 'story_visual_battle_transition_plan_v1.json'
PROOF_MARKER_JSON = SVB_DIR / 'story_visual_battle_wiring_contract_proof_marker_v1.json'
REGISTRY_V3_JSON = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'battle_entrypoint_registry_v3.json'
DOC_222 = ROOT / 'docs' / 'divine' / '222_STORY_VISUAL_BATTLE_WIRING_CONTRACT.md'

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
    if d.get('mode') != 'DESIGN_CONTRACT_AUDIT_ONLY':
        _fail('contract.mode must be DESIGN_CONTRACT_AUDIT_ONLY')
    if d.get('runtime_activation_allowed_in_this_pack') is not False:
        _fail('contract.runtime_activation_allowed_in_this_pack must be false')
    desired = d.get('story_desired_state') or {}
    if desired.get('resolution') != 'visual_battle_required':
        _fail("contract.story_desired_state.resolution must be 'visual_battle_required'")
    if desired.get('player_must_see_battle') is not True:
        _fail('contract.story_desired_state.player_must_see_battle must be true')
    flow = d.get('required_future_flow') or []
    for step in (
        'create_or_reuse_battle_instance',
        'navigate_to_visual_battle_with_battle_instance_id',
        'commit_result_once',
        'grant_rewards_once',
        'advance_story_progress_once',
        'store_view_only_replay_snapshot',
    ):
        if step not in flow:
            _fail(f'contract.required_future_flow missing step: {step}')


def check_payload() -> None:
    d = _load_json(PAYLOAD_JSON)
    if not d:
        return
    fields = d.get('required_future_payload_fields') or {}
    for k in (
        'battle_instance_id', 'idempotency_key', 'mode_id', 'chapter_id', 'stage_id',
        'team_snapshot', 'enemy_snapshot', 'reward_policy', 'result_commit_policy',
        'replay_snapshot_policy',
    ):
        if k not in fields:
            _fail(f'payload.required_future_payload_fields missing key: {k}')
    if fields.get('mode_id') != 'story':
        _fail("payload.mode_id must be 'story'")
    if d.get('runtime_activation_allowed_in_this_pack') is not False:
        _fail('payload.runtime_activation_allowed_in_this_pack must be false')


def check_idempotency() -> None:
    d = _load_json(IDEMP_JSON)
    if not d:
        return
    ri = d.get('reward_idempotency') or {}
    for k in (
        'battle_instance_id_required',
        'idempotency_key_required',
        'result_commit_must_be_once_only',
        'reward_grant_must_be_once_only',
        'hero_exp_grant_must_be_once_only',
        'account_exp_grant_must_be_once_only',
        'story_progress_must_be_once_only',
        'replay_view_must_not_grant_rewards',
        'replay_view_must_not_advance_progress',
        'retry_same_request_returns_same_result',
    ):
        if ri.get(k) is not True:
            _fail(f'idempotency.reward_idempotency.{k} must be true')
    forbid = d.get('forbidden_in_this_pack') or {}
    for k in ('live_ledger_creation', 'db_writes', 'reward_grant', 'exp_grant', 'story_progress_mutation'):
        if forbid.get(k) is not True:
            _fail(f'idempotency.forbidden_in_this_pack.{k} must be true')


def check_transition_plan() -> None:
    d = _load_json(TRANSITION_JSON)
    if not d:
        return
    phases = d.get('phases') or []
    ids = [p.get('id') for p in phases if isinstance(p, dict)]
    required_ids = [
        'PHASE_1_CONTRACT',
        'PHASE_2_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT',
        'PHASE_3_STORY_VISUAL_BATTLE_SANDBOX',
        'PHASE_4_STORY_VISUAL_BATTLE_DUAL_ROUTE_CANARY',
        'PHASE_5_STORY_VISUAL_BATTLE_RUNTIME_APPLY',
        'PHASE_6_REPLAY_AND_REPORT_HARDENING',
        'PHASE_7_REMOVE_STORY_AUTORESSOLVE_DEBT',
    ]
    for rid in required_ids:
        if rid not in ids:
            _fail(f'transition_plan missing phase: {rid}')
    inv = d.get('global_safety_invariants') or {}
    for k in (
        'never_grant_reward_on_replay_view',
        'never_advance_progress_on_replay_view',
        'never_rerun_battle_for_rewards',
        'reward_grants_must_be_idempotent',
        'all_phases_require_db_write_audit',
        'all_phases_require_fallback_or_rollback',
    ):
        if inv.get(k) is not True:
            _fail(f'transition_plan.global_safety_invariants.{k} must be true')


def check_proof_marker() -> None:
    d = _load_json(PROOF_MARKER_JSON)
    if not d:
        return
    expected = {
        'mode': 'DESIGN_CONTRACT_AUDIT_ONLY',
        'phase': 'PHASE_1_STORY_VISUAL_BATTLE_CONTRACT_AND_PAYLOAD',
        'story_visual_battle_required': True,
        'story_runtime_changed': False,
        'story_tsx_changed': False,
        'combat_tsx_changed': False,
        'home_routes_changed': False,
        'battle_engine_changed': False,
        'story_battle_endpoint_changed': False,
        'battle_simulate_endpoint_changed': False,
        'runtime_conversion_done': False,
        'battle_instance_id_contract_defined': True,
        'idempotency_contract_defined': True,
        'reward_duplication_guard_defined': True,
        'exp_duplication_guard_defined': True,
        'story_progress_idempotency_defined': True,
        'replay_view_no_reward_defined': True,
        'db_writes': 0,
        'reward_logic_changed': False,
        'exp_logic_changed': False,
        'story_progress_logic_changed': False,
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


def check_registry_v3() -> None:
    d = _load_json(REGISTRY_V3_JSON)
    if not d:
        return
    entries = d.get('entries') or []
    feat = {e.get('feature'): e for e in entries if isinstance(e, dict)}
    for rf in ('home_play', 'story_stage_battle', 'direct_visual_combat_route', 'guild_war'):
        if rf not in feat:
            _fail(f'registry_v3 missing feature: {rf}')

    story = feat.get('story_stage_battle') or {}
    if story.get('desired_state') != 'visual_battle_required':
        _fail("registry_v3.story_stage_battle.desired_state must be 'visual_battle_required'")
    if story.get('status') != 'contract_ready_runtime_pending':
        _fail(f"registry_v3.story_stage_battle.status must be 'contract_ready_runtime_pending', got {story.get('status')}")
    if story.get('runtime_changed_this_pack') is not False:
        _fail('registry_v3.story_stage_battle.runtime_changed_this_pack must be false')

    gw = feat.get('guild_war') or {}
    if gw.get('status') != 'allowed_autoresolve_exception':
        _fail("registry_v3.guild_war.status must be 'allowed_autoresolve_exception'")
    if gw.get('replay_link_required') is not True:
        _fail('registry_v3.guild_war.replay_link_required must be true')

    policy = d.get('global_policy') or {}
    for k in (
        'all_battle_modes_must_show_visual_battle',
        'only_guild_war_can_autoresolve',
        'story_visual_battle_contract_ready',
        'battle_instance_id_required',
        'reward_duplication_guard_required',
        'replay_must_not_grant_rewards',
        'replay_view_must_not_grant_rewards',
    ):
        if policy.get(k) is not True:
            _fail(f'registry_v3.global_policy.{k} must be true')
    if policy.get('story_runtime_conversion_done') is not False:
        _fail('registry_v3.global_policy.story_runtime_conversion_done must be false')


def check_doc() -> None:
    if not DOC_222.exists():
        _fail(f'missing doc: {DOC_222}')


def check_runtime_files_unchanged_state() -> None:
    if not MANIFEST.exists():
        _fail(f'missing manifest: {MANIFEST}')
    else:
        t = _read(MANIFEST)
        if not re.search(r"play\s*:\s*'\/story'", t):
            _fail("homeAssetsManifest.ts no longer has play:'/story'")
        if not re.search(r"battle\s*:\s*'\/story'", t):
            _fail("homeAssetsManifest.ts no longer has battle:'/story'")

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
    if 'PUBLIC_SYNC_TAG_v30_STORY_VISUAL_BATTLE_WIRING_CONTRACT' not in text:
        _fail('suite runner missing PUBLIC_SYNC_TAG_v30 sentinel')
    if 'STORY_VISUAL_BATTLE_WIRING_CONTRACT_REGISTRATION_SENTINEL' not in text:
        _fail('suite runner missing REGISTRATION_SENTINEL')
    tuple_pattern = re.compile(
        r"\(\s*'PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT'\s*,\s*"
        r"'validate_project_story_visual_battle_wiring_contract_v1\.py'\s*\)"
    )
    matches = tuple_pattern.findall(text)
    if len(matches) == 0:
        _fail('suite runner missing tuple for PROJECT-STORY-VISUAL-BATTLE-WIRING-CONTRACT')
    elif len(matches) > 1:
        _fail(f'suite runner has duplicate tuple (count={len(matches)}); tuple_count_required=1')


def main() -> int:
    check_contract()
    check_payload()
    check_idempotency()
    check_transition_plan()
    check_proof_marker()
    check_registry_v3()
    check_doc()
    check_runtime_files_unchanged_state()
    check_suite_runner_tuple()

    if FAILS:
        print('[FAIL] PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT validator')
        for f in FAILS:
            print(f'  - {f}')
        return 1
    print('[PASS] PROJECT_STORY_VISUAL_BATTLE_WIRING_CONTRACT validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
