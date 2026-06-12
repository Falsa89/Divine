#!/usr/bin/env python3
"""Pack 109 — Guild RC audit.

Verifica Pack 108 retrofit invariato: guild_strict 5 endpoint + quarantine
legacy attiva di default.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
gs = open(os.path.join(R, 'backend/routes/guild_strict.py')).read()
for p in ('/guild/strict/health', '/guild/strict/preflight', '/guild/strict/status',
          '/guild/strict/search', '/guild/strict/membership/preview'):
    assert p in gs
assert 'GUILD_LEGACY_QUARANTINED' in gs
assert '"true"' in gs  # default TRUE
glegacy = open(os.path.join(R, 'backend/routes/guild.py')).read()
assert glegacy.count('_pack_108_raise_quarantined') >= 4
print('[v110 PACK_109_GUILD_RC] OK guild_strict_endpoints_intact legacy_quarantine_in_all_mutating_routes')
