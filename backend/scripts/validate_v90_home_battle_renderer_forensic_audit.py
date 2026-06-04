#!/usr/bin/env python3
"""
v90 — Forensic audit Home battle renderer.

Verifica:
- esiste data/design/playable_mode_visual_battle_routing/v90_home_battle_renderer_forensic_audit_v1.json
- esiste docs/divine/90_HOME_BATTLE_RENDERER_FORENSIC_AUDIT.md
- l'audit indica commit/file del renderer vecchio (combat.tsx con MD5 atteso)
- l'audit indica route attuale (/combat) e architettura interna (BattleSprite, pickBattleBackground, buildBattleLayout)
- l'audit dichiara safety envelope corretta (db_writes=0, reward_live=false, endpoint_live=false, battle_engine_authoritative=false)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_JSON = os.path.join(ROOT, 'data', 'design', 'playable_mode_visual_battle_routing',
                          'v90_home_battle_renderer_forensic_audit_v1.json')
AUDIT_MD = os.path.join(ROOT, 'docs', 'divine', '90_HOME_BATTLE_RENDERER_FORENSIC_AUDIT.md')


def fail(msg: str) -> None:
    print(f"FAIL v90_home_battle_renderer_forensic_audit: {msg}")
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(AUDIT_JSON):
        fail(f"missing forensic audit JSON: {AUDIT_JSON}")
    if not os.path.isfile(AUDIT_MD):
        fail(f"missing forensic audit MD: {AUDIT_MD}")

    with open(AUDIT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data.get('pack') != 'MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING_PACK_v90':
        fail("pack mismatch")
    if data.get('audit_result') != 'OLD_RENDERER_FOUND_IN_CURRENT_REPO':
        fail("audit_result must be OLD_RENDERER_FOUND_IN_CURRENT_REPO")

    renderer = data.get('old_home_battle_renderer') or {}
    if renderer.get('file') != 'frontend/app/combat.tsx':
        fail("old renderer file must be frontend/app/combat.tsx")
    if not renderer.get('md5_locked'):
        fail("old renderer must be md5_locked")
    if renderer.get('md5') != 'fc792a05b2ada6e677d80400732ae5c3':
        fail("old renderer md5 mismatch")
    if renderer.get('component_name') != 'CombatScreen':
        fail("old renderer component must be CombatScreen")

    routing = data.get('old_home_routing_path') or {}
    if not routing.get('combat_route_active'):
        fail("/combat route must be active")
    if routing.get('combat_route_target') != '/combat':
        fail("combat_route_target must be /combat")

    arch = data.get('renderer_internal_architecture') or {}
    required_arch_keys = ['sprite_component', 'background_resolver', 'layout_system', 'animations']
    for k in required_arch_keys:
        if not arch.get(k):
            fail(f"architecture missing field: {k}")

    for src_key in ('player_team_source', 'enemy_team_source'):
        src = data.get(src_key) or {}
        if src.get('backend_endpoint') != '/api/battle/simulate':
            fail(f"{src_key} must use /api/battle/simulate")
        if src.get('v90_introduces_new_endpoint') is not False:
            fail(f"{src_key} must not introduce new endpoint")

    safety = data.get('safety_envelope') or {}
    if safety.get('db_writes') != 0:
        fail("safety db_writes must be 0")
    if safety.get('reward_live') is not False:
        fail("safety reward_live must be false")
    if safety.get('endpoint_live') is not False:
        fail("safety endpoint_live must be false")
    if safety.get('battle_engine_authoritative') is not False:
        fail("safety battle_engine_authoritative must be false")
    if safety.get('fake_pass') is not False:
        fail("safety fake_pass must be false")
    if safety.get('validator_weakening') is not False:
        fail("safety validator_weakening must be false")

    expected_verdict = 'MEGA_RELEASE_ACCELERATION_39_RESTORE_HOME_BATTLE_RENDERER_AND_REAL_MODE_ROUTING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if data.get('verdict') != expected_verdict:
        fail("verdict mismatch")

    with open(AUDIT_MD, 'r', encoding='utf-8') as f:
        md = f.read()
    for token in ('combat.tsx', 'BattleSprite', 'pickBattleBackground', 'buildBattleLayout',
                  '/api/battle/simulate', 'fc792a05b2ada6e677d80400732ae5c3'):
        if token not in md:
            fail(f"MD doc missing required token: {token}")

    print("PASS v90_home_battle_renderer_forensic_audit")


if __name__ == '__main__':
    main()
