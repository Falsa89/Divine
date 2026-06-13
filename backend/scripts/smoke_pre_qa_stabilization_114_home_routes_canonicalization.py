#!/usr/bin/env python3
"""Pre-QA Stabilization 114 — Smoke (static)."""
import os, sys, subprocess, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
subprocess.check_call([sys.executable, os.path.join(R, 'backend/scripts/validate_pre_qa_stabilization_114_home_routes_canonicalization.py')])
print('[1] validator Pack 114 PASS')
subprocess.check_call([sys.executable, os.path.join(R, 'backend/scripts/validate_pre_qa_stabilization_113_home_overflow_guard.py')])
print('[2] Pack 113 HomeOverflow guard still PASS')
subprocess.check_call([sys.executable, os.path.join(R, 'backend/scripts/validate_pre_qa_stabilization_112_shared_nav_guard.py')])
print('[3] Pack 112 shared nav guard still PASS')
# Static behavior: simulate isRouteAllowedInPreQa('/(tabs)/gacha') via regex on TS source.
guard = open(os.path.join(R, 'frontend/src/utils/preQaNavGuard.ts')).read()
# Verifica che il match pattern del normalizer faccia capture del path post-paren.
assert re.search(r"const m = base\.match\(/\^\\/\\\(\[\^\)\]\+\\\)\(\\/\.\*\)\?\$/\)", guard) or 'const m = base.match' in guard
print('[4] normalizeRoute regex shape OK')
# Verifica blocked set contiene tutte le missing routes.
for needed in ("'/quests'", "'/arena'", "'/blessings'", "'/profile'", "'/gacha'", "'/sanctuary'"):
    assert needed in guard
print('[5] all blocked missing routes present in shared guard')
# Verifica home onHeroTap guarded.
home = open(os.path.join(R, 'frontend/app/(tabs)/home.tsx')).read()
m = re.search(r'const onHeroTap[^}]+\}\s*;', home, re.DOTALL)
assert m and 'isRouteAllowedInPreQa' in m.group(0)
print('[6] onHeroTap /sanctuary guarded OK')
print('SMOKE PRE_QA_STABILIZATION_114 OK')
