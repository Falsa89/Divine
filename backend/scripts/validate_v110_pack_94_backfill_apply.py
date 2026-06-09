#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_94_equipment_backfill_strict_currency_quarantine/v110_pack_94_backfill_apply_result_v1.json')
assert os.path.exists(p), 'backfill apply result missing'
d = json.load(open(p))
r = d.get('result', {})
assert r.get('mode') == 'applied'
assert r.get('docs_updated') == 28
assert r.get('coverage_pct_post') == 100.0
assert d.get('approval_present') is True
assert d.get('approval_required') == 'AUTORIZZO_V110_EQUIPMENT_SERVER_SCOPE_BACKFILL_EXECUTE_PACK_94'
print('[v110 PACK_94_BACKFILL_APPLY_RESULT] OK applied docs_updated=28 coverage_post=100% approval_present')
