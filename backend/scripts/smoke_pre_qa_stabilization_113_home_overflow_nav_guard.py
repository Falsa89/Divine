#!/usr/bin/env python3
"""Pre-QA Stabilization 113 — HomeOverflow nav guard smoke (static)."""
import os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Step 1: validator passa.
subprocess.check_call([sys.executable, os.path.join(R, 'backend/scripts/validate_pre_qa_stabilization_113_home_overflow_guard.py')])
print('[1] validate_pre_qa_stabilization_113_home_overflow_guard PASS')
# Step 2: shared nav guard ancora canonical.
subprocess.check_call([sys.executable, os.path.join(R, 'backend/scripts/validate_pre_qa_stabilization_112_shared_nav_guard.py')])
print('[2] shared nav guard Pack 112 still PASS')
# Step 3: Pack 110 menu cleanup ancora robusto.
subprocess.check_call([sys.executable, os.path.join(R, 'backend/scripts/validate_pre_qa_stabilization_110_menu_cleanup.py')])
print('[3] menu cleanup Pack 110 still PASS')
# Step 4: no raw unsafe router.push fuori dal guard per le 10 route critiche.
import re
c = open(os.path.join(R, 'frontend/app/(tabs)/home.tsx')).read()
for unsafe in ('/pvp', '/events', '/shop', '/battlepass', '/raid', '/gvg', '/plaza', '/dm', '/territory'):
    # solo occorrenze dentro _allItemsRaw OR _pushPreQaGuarded.
    # Cerca raw direct: onPress={() => router.push('/X' as any)}
    pat = re.compile(rf"onPress=\{{\(\)\s*=>\s*router\.push\('{re.escape(unsafe)}'\s+as any\)\}}")
    direct = pat.findall(c)
    assert len(direct) == 0, f'raw direct unsafe push for {unsafe}: {direct}'
print('[4] no raw direct unsafe router.push for 10 critical routes OK')
# Step 5: /vip is guarded too.
vip_unguarded = re.findall(r"onPress=\{\(\)\s*=>\s*router\.push\('/vip'\s+as any\)\}", c)
assert len(vip_unguarded) == 0
print('[5] /vip raw pushes all wrapped with guard OK')
print('SMOKE PRE_QA_STABILIZATION_113 OK')
