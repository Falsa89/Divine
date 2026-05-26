#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/sf_merge/track_g_regression_qa_v1.json')
SCRIPTS = Path('/app/backend/scripts')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_REGRESSION_GUARDS_AND_MOBILE_QA_READY'
    guards = d['regression_guards']
    assert len(guards) >= 5
    referenced = set()
    for g in guards:
        v = g.get('validator', '')
        # skip 'existing' annotation
        if ' (existing)' in v:
            v = v.split(' ')[0]
        if v and v.endswith('.py'):
            referenced.add(v)
    for v in referenced:
        assert (SCRIPTS / v).exists(), f'referenced validator missing: {v}'
    cl = d['mobile_qa_checklist']
    must_areas = {'soul_forge','economy','exclusive','menu','home_overflow','regression'}
    have = {e['area'] for e in cl}
    missing = must_areas - have
    assert not missing, f'missing QA areas: {missing}'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] SF-MERGE Track G regression+QA \u2014 guards={len(guards)} areas={len(have)}")
    return 0
if __name__=='__main__': sys.exit(main())
