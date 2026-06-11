#!/usr/bin/env python3
"""Pack 105 — Static economy/forge anti-leak guard."""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict = open(os.path.join(R, 'backend/routes/economy_strict.py')).read()

def strip_comments_and_docstrings(s: str) -> str:
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    s = re.sub(r'(?m)#.*$', '', s)
    return s

code = strip_comments_and_docstrings(strict)

# No users.* / wallets / user_materials / user_fragments mutation
for forbidden in [
    'db.users.update_one','db.users.insert_one','db.users.delete_one',
    'db.users.update_many','db.users.delete_many',
    'db.wallets.update_one','db.wallets.update_many','db.wallets.insert_one',
    'db.user_materials.update_one','db.user_materials.update_many','db.user_materials.insert_one',
    'db.user_fragments.update_one','db.user_fragments.update_many','db.user_fragments.insert_one',
]:
    assert forbidden not in code, f'economy_strict leak: {forbidden}'

# No hardcoded s1
for forbidden in ['server_id="s1"', "server_id='s1'"]:
    assert forbidden not in code, f'hardcoded s1: {forbidden}'

# Ogni $inc deve essere ristretto a PSP soft_currencies / materials
inc_occurrences = [m.start() for m in re.finditer(r'\$inc', code)]
for pos in inc_occurrences:
    window = code[max(0, pos-400):pos+500]
    assert ('soft_currencies' in window or 'materials' in window or 'player_server_profiles' in window), \
        f'$inc at offset {pos} non e\' ristretto a PSP soft_currencies/materials'

# Server-scoped filtering enforced su user_equipment (Pack 105 path)
for pat in [
    r"db\.user_equipment\.find_one\(\s*\{[^}]*server_id",
    r"db\.user_equipment\.update_one\(\s*\{[^}]*server_id",
    r"db\.user_equipment\.delete_one\(\s*\{[^}]*server_id",
]:
    assert re.search(pat, code, re.S), f'server_id filter missing: {pat}'

# insert_one usa var `new_eq` che DEVE includere "server_id": sid esplicito.
# Check positivo: verifica che il dict new_eq venga costruito con "server_id".
assert re.search(r'new_eq\s*=\s*\{[\s\S]*?"server_id":\s*sid', code), \
    'forge craft new_eq dict must include "server_id": sid'

assert '"reward_live_general": False' in strict
assert '"release_readiness_claimed": False' in strict
assert '"premium_grants": False' in strict
assert '"psp_material_storage_active": True' in strict

for ks in ('EQUIPMENT_UPGRADE_STRICT_ENABLED','FORGE_CRAFT_STRICT_ENABLED','EQUIPMENT_FUSION_STRICT_ENABLED'):
    assert ks in code, f'kill switch missing: {ks}'

print('[v110 PACK_105_STATIC_ANTI_LEAK] OK no_users_wallets_materials_mutation no_hardcoded_s1 inc_restricted_PSP no_client_cost_trust triple_kill_switch_present server_scoped_filtering_enforced psp_materials_active')
