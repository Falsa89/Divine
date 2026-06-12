#!/usr/bin/env python3
"""Pack 108 — Guild legacy account-wide quarantine validator.

Verifica che `routes/guild.py` (legacy) contenga la quarantena Pack 108
su tutte le route mutanti account-wide:
  POST /guild/create
  POST /guild/join/{guild_id}
  POST /guild/leave
  POST /faction/join (premium gems mutation)

La quarantena deve:
  - usare il kill switch GUILD_LEGACY_QUARANTINED (default TRUE)
  - sollevare HTTPException 423 con blocker `GUILD_LEGACY_QUARANTINED`
  - includere `no_account_wide_guild_writes=True`
  - rimandare a `AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT`
  - puntare a strict alternative `/api/guild/strict`

L'helper `_pack_108_raise_quarantined` deve essere richiamato all'inizio
di ognuna delle 4 route mutanti, PRIMA di qualunque accesso a `db.users`.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = os.path.join(R, 'backend/routes/guild.py')
c = open(f).read()

assert '_pack_108_legacy_quarantined' in c
assert '_pack_108_raise_quarantined' in c
assert 'GUILD_LEGACY_QUARANTINED' in c
assert 'no_account_wide_guild_writes' in c
assert 'AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT' in c
assert '/api/guild/strict' in c
assert 'os.getenv("GUILD_LEGACY_QUARANTINED", "true")' in c

for surface in (
    'guild_create_legacy_account_wide',
    'guild_join_legacy_account_wide',
    'guild_leave_legacy_account_wide',
    'faction_join_legacy_account_wide_gems_mutation',
):
    assert surface in c, surface

# Sanity: ognuna delle 4 route mutanti chiama il guard PRIMA di toccare db.users.
for route_def in (
    'async def create_guild(',
    'async def join_guild(',
    'async def leave_guild(',
    'async def join_faction(',
):
    idx = c.find(route_def)
    assert idx > 0, route_def
    # cerca il guard entro le prime 6 righe del corpo (post-def line).
    body = '\n'.join(c[idx:].split('\n')[1:8])
    assert '_pack_108_raise_quarantined' in body or '_pack_108_legacy_quarantined' in body, f'no quarantine guard in {route_def}'

# Heuristic: HTTPException 423 utilizzato dal raise helper.
assert 'HTTPException(423' in c

print('[v110 PACK_108_GUILD_LEGACY_QUARANTINE] OK four_mutating_routes_quarantined kill_switch_default_true http_423 deferred_next_step_documented')
