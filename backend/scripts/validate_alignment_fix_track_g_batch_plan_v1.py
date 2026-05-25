#!/usr/bin/env python3
# ALIGNMENT_FIX Track G — concrete batch plan.
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/concrete_batch_plan_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_CONCRETE_BACKEND_FRONTEND_BATCH_PLAN_READY'
    batches = d['batches']
    assert len(batches) >= 9
    ids = {b['id'] for b in batches}
    must = {'BATCH_2','BATCH_3','BATCH_4','BATCH_5','BATCH_6','BATCH_7','BATCH_8','BATCH_9','BATCH_10'}
    missing = must - ids
    assert not missing, f'missing batches: {missing}'
    for b in batches:
        for k in ('title','frontend_changes','backend_changes','db_changes',
                  'user_approval_needed','mobile_qa','risk','dependencies'):
            assert k in b, f'batch {b["id"]} missing field: {k}'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] ALIGN-FIX Track G batch plan \u2014 batches={len(batches)}")
    return 0
if __name__ == '__main__': sys.exit(main())
