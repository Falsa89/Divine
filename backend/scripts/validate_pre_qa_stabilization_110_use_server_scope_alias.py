#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — useServerScope alias fix validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
hook = open(os.path.join(R, 'frontend/src/hooks/useServerScope.ts')).read()
for t in ('serverId', 'selected_server_id', 'serverName', 'selected_server_name',
          'no_silent_s1_fallback', 'NO_SERVER_SELECTED', 'refreshToken', 'isReady'):
    assert t in hook, f'useServerScope missing {t}'
# No silent ||"s1" fallback.
import re
lines = [ln for ln in hook.split('\n') if not ln.lstrip().startswith('//')]
clean = '\n'.join(lines)
assert re.search(r"\|\|\s*['\"]s1['\"]", clean) is None
print('[v110 PRE_QA_110_USE_SERVER_SCOPE_ALIAS] OK serverId_alias_present selected_server_id_canonical no_silent_s1_fallback')
