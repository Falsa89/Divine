#!/usr/bin/env python3
"""Pack 127 — Stale READY/PASS declassification."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
DECLASS=REPO_ROOT/'data'/'design'/'system_safety'/'pack_127_stale_ready_pass_declassification.json'


def main()->int:
    errors=[]
    DECLASS.parent.mkdir(parents=True,exist_ok=True)
    if not DECLASS.exists():
        payload={
            'pack':'PACK_127','declaration':'Old READY/PASS reports are historical unless rerun under Pack 127+ gates.',
            'explicit_declassified':['PACK_118_DEVICE_READY','PACK_126_FIX_*','FASE_G_AUDIT_COVERAGE','FASE_H_CLASSIFICATION'],
            'rationale':'Audit coverage/classification ≠ runtime readiness. Device QA remains BLOCKED until PACK 127–133 pass.',
            'device_qa_status':'BLOCKED',
            'next_required_pack':'PACK_128_ROUTE_DEEPLINK_LOCKDOWN',
        }
        DECLASS.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
        print(f'OK    declassification marker created: {DECLASS.name}')
    else:
        print(f'OK    declassification marker present: {DECLASS.name}')
    data=json.loads(DECLASS.read_text(encoding='utf-8'))
    if data.get('device_qa_status') != 'BLOCKED':
        errors.append('declassification marker does not state BLOCKED')
    else:
        print('OK    device_qa_status=BLOCKED in marker')
    return _emit(errors)


def _emit(errors):
    print('\n'+'='*72)
    report={'pack':'PACK_127_STALE_READY_PASS_DECLASSIFICATION','status':'PASS' if not errors else 'FAIL','errors':errors,'validation_kind':'STATIC_DOC'}
    out=REPO_ROOT/'backend'/'scripts'/'reports'; out.mkdir(parents=True,exist_ok=True)
    (out/'pack_127_stale_ready_pass_declassification_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  stale READY/PASS declassification marker present, device_qa_status=BLOCKED')
    return 0

if __name__=='__main__': sys.exit(main())
