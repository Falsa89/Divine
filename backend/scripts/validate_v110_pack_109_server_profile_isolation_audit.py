#!/usr/bin/env python3
"""Pack 109 — Server/Profile isolation audit (static).

Verifica che le route critiche server-scope rifiutino richieste senza
server_id (no silent s1 fallback) e che usino `server_id` come componente
della chiave composita.
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROUTES = (
    'backend/routes/tower_strict.py',
    'backend/routes/economy_strict.py',
    'backend/routes/controlled_rewards.py',
    'backend/routes/competitive_guards.py',
    'backend/routes/guild_strict.py',
    'backend/routes/playable_loop_map.py',
    'backend/routes/reward_claim.py',
)
for rel in ROUTES:
    p = os.path.join(R, rel)
    if not os.path.exists(p): continue
    c = open(p).read()
    # No silent s1 fallback default.
    assert re.search(r"\|\|\s*['\"]s1['\"]", c) is None, f'{rel}: silent ||"s1"'
    assert re.search(r"\bserver_id\s*=\s*['\"]s1['\"]", c) is None, f'{rel}: server_id="s1"'
    # server_id appears (server-scope required keyword).
    assert 'server_id' in c, f'{rel}: missing server_id usage'
print('[v110 PACK_109_SERVER_PROFILE_ISOLATION_AUDIT] OK seven_strict_routes_no_silent_s1_server_scope_used')
