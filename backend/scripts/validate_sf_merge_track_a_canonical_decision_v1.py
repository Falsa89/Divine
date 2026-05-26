#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/sf_merge/track_a_canonical_decision_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_CANONICAL_PRODUCT_DECISION_LOCK_READY'
    assert len(d['decisions']) >= 5
    ids = {x['id'] for x in d['decisions']}
    assert {'D-01','D-02','D-03','D-04','D-05'}.issubset(ids)
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert any('character-bound' in p for p in d['product_invariants'])
    print('[PASS] SF-MERGE Track A canonical decision')
    return 0
if __name__=='__main__': sys.exit(main())
