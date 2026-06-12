#!/usr/bin/env python3
"""Pack 107 — Guild audit (honest documentation, no enforced quarantine).

Pack 107 e' audit-only. `routes/guild.py` legacy esiste e NON e' server-scoped
(0 occorrenze `server_id`). Il guild legacy potrebbe contenere mutation
account-wide su `users.*` che Pack 107 NON modifica.

Pack 107 documenta lo stato tramite blocker canonici in
`/api/competitive-guards/guild/preflight`:
  - GUILD_SERVER_SCOPE_REQUIRED
  - GUILD_REWARD_LIVE_DISABLED

Una futura Pack (`AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_PACK_NEXT`) potra'
applicare il retrofit server-scope alle routes esistenti.

Questo validator verifica che:
  1. routes/guild.py esiste (legacy).
  2. Pack 107 expone i blocker canonici nel preflight.
  3. La mutation legacy (se presente) NON e' attivata da Pack 107.
"""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
legacy = os.path.join(R, 'backend/routes/guild.py')
assert os.path.exists(legacy)
# Pack 107 NON ha modificato guild.py legacy (out of scope: audit-only).
# Lo stato canonical e' AUDIT_LEGACY_NOT_SERVER_SCOPED nel preflight.
cg = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()
assert 'AUDIT_LEGACY_NOT_SERVER_SCOPED' in cg
assert 'guild_reward_live_grant' in cg
assert 'GUILD_SERVER_SCOPE_REQUIRED' in cg
assert 'GUILD_REWARD_LIVE_DISABLED' in cg
assert 'deferred_next_step' in cg
assert 'AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_PACK_NEXT' in cg
# Pack 107 stesso (competitive_guards.py) NON deve mutare nulla.
for forbidden in ('db.users.update_one','db.users.insert_one','db.users.delete_one',
                  'db.guild','reward_claim_ledger.insert_one','$inc'):
    assert forbidden not in cg, f'competitive_guards Pack 107 must be read-only: {forbidden}'
print('[v110 PACK_107_GUILD_AUDIT] OK guild_legacy_exists_audited_honestly pack_107_preflight_blockers_present pack_107_read_only deferred_next_step_documented')
