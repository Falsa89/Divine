#!/usr/bin/env python3
"""Pack 101 — Static tower anti-leak guard (rebased canonical post Pack 103).

CANONICAL BASELINE EVOLUTION:
  * Pack 101 baseline: NESSUN reward grant nel modulo tower (preview-only).
  * Pack 103 reconciled (approved): introdotto grant ledger-gated `tower_floor_completion_claim`,
    con triple kill switch OFF di default, server-side claim_key, PSP soft_currencies only.

Il guard rebasato continua a vietare:
  * users.* mutation (forbidden assoluto);
  * legacy tower_progress collection writes;
  * hardcoded server_id="s1";
  * reward_live_general=True;
  * release_readiness_claimed=True.

E ora richiede positivamente che:
  * il grant ledger-gated esista SOLO se accompagnato da check kill switch + idempotency;
  * il $inc sia ristretto a `soft_currencies.*` (no $inc su collezioni non-PSP).
"""
import os, re
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict=open(os.path.join(R,'backend/routes/tower_strict.py')).read()


def strip_comments_and_docstrings(s: str) -> str:
    s = re.sub(r'"""[\s\S]*?"""', '', s)
    s = re.sub(r"'''[\s\S]*?'''", '', s)
    s = re.sub(r'(?m)#.*$', '', s)
    return s

code = strip_comments_and_docstrings(strict)

# Anti-leak invariante: NESSUNA mutation su db.users.* dal codice attivo del tower strict.
for forbidden in [
    'db.users.update_one', 'db.users.insert_one', 'db.users.delete_one',
    'db.users.update_many', 'db.users.delete_many',
    # legacy tower_progress collection MAI scritta dal modulo strict.
    'db.tower_progress.insert_one', 'db.tower_progress.update_one',
    'db.tower_progress.delete_one',
]:
    assert forbidden not in code, f'tower_strict leak: {forbidden}'

# Pack 103 canonical: ogni $inc nel codice attivo deve essere ristretto a soft_currencies.* (PSP).
# Estraiamo ogni occorrenza di $inc e verifichiamo che il contesto immediatamente prima
# o subito dopo riferisca soft_currencies o player_server_profiles.
inc_occurrences = [m.start() for m in re.finditer(r'\$inc', code)]
for pos in inc_occurrences:
    window = code[max(0, pos-200):pos+400]
    assert ('soft_currencies' in window) or ('player_server_profiles' in window), \
        f'$inc occurrence at offset {pos} non e\' ristretto a PSP/soft_currencies'

# No hardcoded s1
for forbidden in ['server_id="s1"', "server_id='s1'"]:
    assert forbidden not in code, f'tower_strict hardcoded s1: {forbidden}'

# Reward live general / release readiness MUST be False explicitly in response strings
assert '"reward_live_general": False' in strict
assert '"tower_reward_live_grant": False' in strict
assert '"release_readiness_claimed": False' in strict

# Pack 103 canonical: kill switch + idempotency + ledger present in active code.
for required_pack_103 in [
    'TOWER_FLOOR_CLAIM_ENABLED',         # per-source kill switch
    'REWARD_CLAIM_LEDGER_LIVE_ENABLED',  # global ledger kill switch
    'TOWER_STRICT_EXECUTE_ENABLED',      # execute kill switch
    'idempotency_token',                 # idempotency mandatory
    'reward_claim_ledger',               # ledger collection
    'tower_floor_completion_claim',      # source id
    'PACK_103_USER_TEST_MARKER',         # test marker gate
]:
    assert required_pack_103 in code, f'pack 103 canonical guard missing: {required_pack_103}'

# Combat legacy: tower_battle/tower_status devono avere il guard prima
combat=open(os.path.join(R,'backend/routes/combat.py')).read()
assert '_pack_101_tower_legacy_block_or_raise()' in combat
assert 'TOWER_LEGACY_QUARANTINED' in combat
print('[v110 PACK_101_STATIC_TOWER_ANTI_LEAK_GUARD] OK canonical_post_pack_103 no_users_mutation no_legacy_collection_write inc_restricted_to_PSP_soft_currencies no_hardcoded_s1 legacy_quarantined ledger_gated_present')
