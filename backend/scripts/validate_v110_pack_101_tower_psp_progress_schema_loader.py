#!/usr/bin/env python3
"""Pack 101 — PSP tower_progress schema/loader presence."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
for needle in [
    'get_tower_progress_strict',
    '_default_tower_progress',
    'player_server_profiles.find_one',
    'STRICT_MARKER_FIELD = "_slc_pack_101_strict"',
    'highest_floor',
    'rewards_claimed',
    'last_battle_at',
]:
    assert needle in src, needle


def strip_comments_and_docstrings(s: str) -> str:
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    s = re.sub(r'(?m)#.*$', '', s)
    return s

code = strip_comments_and_docstrings(src)
# Loader NON deve effettuare scritture su users.* o accedere a users.gold/gems/experience
for forbidden in ['db.users.update_one','db.users.insert_one','users.gold','users.gems','users.experience']:
    assert forbidden not in code, f'loader leak (in active code): {forbidden}'
print('[v110 PACK_101_TOWER_PSP_PROGRESS_SCHEMA_LOADER] OK psp_storage loader_pure_read default_seed marker_field no_users_mutation_in_active_code')
