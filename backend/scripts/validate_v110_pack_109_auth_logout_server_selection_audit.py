#!/usr/bin/env python3
"""Pack 109 — Auth/Logout/Server Selection Audit.

Verifica che l'auth/logout/server selection siano implementati e che il
selected server scope hook esista.
"""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Auth context (React).
for p in ('frontend/src/auth/AuthContext.tsx', 'frontend/src/hooks/useServerScope.ts',
          'frontend/src/utils/serverSwitchRefreshGuard.ts'):
    fp = os.path.join(R, p)
    assert os.path.exists(fp), f'missing: {p}'
    c = open(fp).read()
    # No silent s1 fallback.
    import re
    assert re.search(r"\|\|\s*['\"]s1['\"]", c) is None, f'{p}: silent ||"s1"'
authctx = open(os.path.join(R, 'frontend/src/auth/AuthContext.tsx')).read()
for tok in ('logout', 'login'):
    assert tok in authctx.lower(), f'AuthContext missing {tok}'
print('[v110 PACK_109_AUTH_LOGOUT_SERVER_SELECTION_AUDIT] OK auth_context_logout_server_scope_hook_present no_silent_s1')
