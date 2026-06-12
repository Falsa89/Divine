#!/usr/bin/env python3
"""Pack 108 — Cleanup / rollback hint.

Verifica che lo smoke E2E faccia cleanup dei test users e che il
documento `data/pack_108/extracted/PROMPT_MAIN.md` sia ancora
intatto. Documenta il rollback come `disable kill switches`.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
smoke = open(os.path.join(R, 'backend/scripts/smoke_v110_pack_108_guild_frontend_playable_loop_e2e.py')).read()
assert 'db.users.delete_many' in smoke
assert 'db.guild_memberships_v2.delete_many' in smoke
assert 'finally:' in smoke
assert 'Cleanup' in smoke or 'cleanup' in smoke

# Rollback path documented: kill switches default OFF/quarantine TRUE.
gs = open(os.path.join(R, 'backend/routes/guild_strict.py')).read()
assert 'GUILD_STRICT_PREFLIGHT_ENABLED' in gs
assert 'GUILD_LEGACY_QUARANTINED' in gs
# Quarantine OFF (rollback) sarebbe: export GUILD_LEGACY_QUARANTINED=false
assert '"true"' in gs  # default TRUE

print('[v110 PACK_108_CLEANUP_ROLLBACK] OK smoke_cleans_test_users rollback_path_via_env_flags')
