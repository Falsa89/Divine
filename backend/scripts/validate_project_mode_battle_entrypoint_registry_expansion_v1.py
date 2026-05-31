"""validate_project_mode_battle_entrypoint_registry_expansion_v1.py

MEGA_BATCH_ACCELERATION_1 TRACK C validator. Audit-only registry expansion v4.
No runtime changes.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG_V4 = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'battle_entrypoint_registry_v4.json'
EXP_DESIGN = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'mode_battle_entrypoint_registry_expansion_v1.json'
EXP_MARKER = ROOT / 'data' / 'design' / 'battle_entrypoints' / 'mode_battle_entrypoint_registry_expansion_proof_marker_v1.json'

FAILS: list[str] = []


def _fail(m: str) -> None:
    FAILS.append(m)


def main() -> int:
    if not REG_V4.exists():
        _fail(f'registry v4 missing: {REG_V4}')
        print('[FAIL] PROJECT_MODE_BATTLE_ENTRYPOINT_REGISTRY_EXPANSION validator')
        for f in FAILS:
            print('  -', f)
        return 1
    reg = json.loads(REG_V4.read_text())
    if reg.get('version') != 4:
        _fail('registry v4 version != 4')
    sup = reg.get('supersedes') or []
    if 'battle_entrypoint_registry_v3.json' not in sup:
        _fail('registry v4 does not supersede v3')
    entries = reg.get('entries') or []
    feats = {e.get('feature') for e in entries if isinstance(e, dict)}
    required = {
        'home_play', 'home_mode_battle_button', 'story_stage_battle', 'direct_visual_combat_route',
        'material_raid_battle', 'raid', 'tower', 'pvp', 'event_battle', 'boss_battle',
        'trial_battle', 'guild_war', 'arena', 'world_boss', 'dungeon', 'campaign_elite',
        'resource_raid', 'guild_boss',
    }
    missing = required - feats
    if missing:
        _fail(f'registry v4 missing entries: {sorted(missing)}')

    fmap = {e.get('feature'): e for e in entries if isinstance(e, dict)}
    story = fmap.get('story_stage_battle') or {}
    if story.get('priority') != 'P0':
        _fail('story_stage_battle.priority must be P0')
    gw = fmap.get('guild_war') or {}
    if gw.get('is_only_autoresolve_exception') is not True:
        _fail('guild_war.is_only_autoresolve_exception must be true')
    if gw.get('replay_link_required') is not True:
        _fail('guild_war.replay_link_required must be true')
    for e in entries:
        if e.get('runtime_changed_this_pack') is not False:
            _fail(f"entry {e.get('feature')} runtime_changed_this_pack must be false")

    policy = reg.get('global_policy') or {}
    for k in ('all_battle_modes_must_show_visual_battle', 'only_guild_war_can_autoresolve',
              'guild_war_requires_replay_link', 'battle_instance_id_required',
              'reward_duplication_guard_required'):
        if policy.get(k) is not True:
            _fail(f'global_policy.{k} must be true')

    if not EXP_DESIGN.exists() or not EXP_MARKER.exists():
        _fail('expansion design/marker missing')

    if FAILS:
        print('[FAIL] PROJECT_MODE_BATTLE_ENTRYPOINT_REGISTRY_EXPANSION validator')
        for f in FAILS:
            print('  -', f)
        return 1
    print('[PASS] PROJECT_MODE_BATTLE_ENTRYPOINT_REGISTRY_EXPANSION validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
