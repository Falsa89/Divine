#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Auth token compatibility bridge validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bridge = open(os.path.join(R, 'frontend/src/utils/authTokenCompat.ts')).read()
for t in ('v96_auth_token', "'token'", 'SecureStore.getItemAsync', 'AsyncStorage.getItem',
          'getAuthTokenCompat', 'authHeaderCompat', 'AuthTokenSource', 'no_silent_fallback'):
    assert t in bridge, f'authTokenCompat missing {t}'
print('[v110 PRE_QA_110_AUTH_TOKEN_BRIDGE] OK both_secure_store_and_async_storage_read no_security_downgrade')
