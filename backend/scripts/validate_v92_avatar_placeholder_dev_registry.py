#!/usr/bin/env python3
"""v92 — Avatar Placeholder Dev Registry validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, 'data', 'design', 'avatar_placeholders',
                   'avatar_placeholder_dev_registry_v1.json')
DOC = os.path.join(ROOT, 'docs', 'divine', '92_AVATAR_PLACEHOLDER_DEV_REGISTRY.md')

REQUIRED_AVATAR_IDS = {
    'player_avatar_hd_base_dev',
    'player_war_avatar_mini_base_dev',
    'guild_war_avatar_base_dev',
    'event_avatar_base_dev',
    'hero_room_chibi_avatar_base_dev',
    'raid_boss_avatar_placeholder_dev',
    'faction_boss_avatar_placeholder_dev',
}


def fail(msg): print(f"FAIL v92_avatar_placeholder_dev_registry: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(REG): fail(f"missing registry: {REG}")
    if not os.path.isfile(DOC): fail(f"missing doc: {DOC}")
    with open(REG, 'r', encoding='utf-8') as f: data = json.load(f)

    for flag in ('placeholder_dev_only', 'do_not_treat_as_canonical',
                 'no_monetization', 'no_cosmetic_unlock', 'no_inventory_grant'):
        if data.get(flag) is not True:
            fail(f"{flag} must be true at registry level")
    for flag in ('final_asset_ready', 'production_asset'):
        if data.get(flag) is not False:
            fail(f"{flag} must be false at registry level")

    avatars = data.get('avatars') or []
    found = {a.get('avatar_id') for a in avatars}
    missing = REQUIRED_AVATAR_IDS - found
    if missing: fail(f"missing required avatar_ids: {sorted(missing)}")
    for a in avatars:
        for must_true in ('placeholder_dev_only', 'do_not_treat_as_canonical'):
            if a.get(must_true) is not True:
                fail(f"avatar {a.get('avatar_id')}.{must_true} must be true")
        if a.get('final_asset_ready') is not False:
            fail(f"avatar {a.get('avatar_id')}.final_asset_ready must be false")
        if a.get('asset_kind') != 'placeholder_dev':
            fail(f"avatar {a.get('avatar_id')}.asset_kind must be 'placeholder_dev'")
    print("PASS v92_avatar_placeholder_dev_registry")


if __name__ == '__main__': main()
