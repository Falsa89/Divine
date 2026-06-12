#!/usr/bin/env python3
"""Pre-QA Stabilization 111 — R-01 authTokenCompat adoption validator."""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
srv = open(os.path.join(R, 'frontend/app/servers.tsx')).read()
assert 'getAuthTokenCompat' in srv
assert 'no_auth_token_psp_ensure_deferred' in srv
assert '/api/psp/ensure' in srv and '/api/psp/starter/claim' in srv
# Bridge file exists.
bridge = open(os.path.join(R, 'frontend/src/utils/authTokenCompat.ts')).read()
assert 'SecureStore.getItemAsync' in bridge and 'AsyncStorage.getItem' in bridge
# No silent s1 fallback in adopted code.
lines = [ln for ln in srv.split('\n') if not ln.lstrip().startswith('//')]
clean = '\n'.join(lines)
assert re.search(r"\|\|\s*['\"]s1['\"]", clean) is None
# No hardcoded token / no plaintext secrets.
assert 'JWT_SECRET' not in srv
print('[v111 PRE_QA_111_AUTH_TOKEN_COMPAT_ADOPTION] OK servers_tsx_uses_bridge no_silent_s1 no_hardcoded_token')
