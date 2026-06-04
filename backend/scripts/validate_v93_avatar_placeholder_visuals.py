#!/usr/bin/env python3
"""v93 — Avatar placeholder visuals validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAN = os.path.join(ROOT, 'data', 'design', 'avatar_placeholders', 'v93_avatar_placeholder_visual_manifest_v1.json')
COMP = os.path.join(ROOT, 'frontend', 'components', 'avatarPlaceholders', 'AvatarPlaceholderDev.tsx')

REQUIRED_IDS = {
    'player_avatar_hd_base_dev', 'player_war_avatar_mini_base_dev',
    'guild_war_avatar_base_dev', 'event_avatar_base_dev',
    'hero_room_chibi_avatar_base_dev', 'raid_boss_avatar_placeholder_dev',
    'faction_boss_avatar_placeholder_dev',
}
REQUIRED_COMPONENTS = {
    'AvatarPlaceholderHD', 'AvatarPlaceholderWarMini', 'AvatarPlaceholderGuildWar',
    'AvatarPlaceholderEvent', 'AvatarPlaceholderChibi', 'AvatarPlaceholderRaidBoss',
    'AvatarPlaceholderFactionBoss',
}

def fail(m): print(f"FAIL v93_avatar_placeholder_visuals: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(MAN): fail(f"missing manifest: {MAN}")
    if not os.path.isfile(COMP): fail(f"missing component file: {COMP}")
    with open(MAN) as f: data = json.load(f)
    if data.get('placeholder_dev_only') is not True: fail("placeholder_dev_only must be true")
    if data.get('final_asset_ready') is not False: fail("final_asset_ready must be false")
    if data.get('do_not_treat_as_canonical') is not True: fail("do_not_treat_as_canonical must be true")
    if data.get('no_monetization') is not True: fail("no_monetization must be true")
    avatars = data.get('avatars') or []
    found_ids = {a.get('avatar_id') for a in avatars}
    missing = REQUIRED_IDS - found_ids
    if missing: fail(f"manifest missing ids: {sorted(missing)}")
    with open(COMP) as f: comp = f.read()
    for c in REQUIRED_COMPONENTS:
        if f"function {c}" not in comp and f"export function {c}" not in comp:
            fail(f"component file missing function: {c}")
    if 'PLACEHOLDER_REGISTRY' not in comp:
        fail("component file must export PLACEHOLDER_REGISTRY")
    print("PASS v93_avatar_placeholder_visuals")

if __name__ == '__main__': main()
