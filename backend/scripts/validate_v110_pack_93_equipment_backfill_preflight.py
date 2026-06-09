#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_equipment_backfill_preflight_v1.json')))
assert d.get('backfill_executed_in_pack_93') is False
assert d.get('preflight_only') is True
assert d.get('no_execute_in_pack_93') is True
assert d.get('loader_blocker_remains') == 'EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED'
assert d.get('approval_string_proposed_for_backfill_execute') == 'AUTORIZZO_V110_EQUIPMENT_SERVER_SCOPE_BACKFILL_EXECUTE'
assert d.get('baseline_audit', {}).get('docs_total', 0) > 0
print('[v110 PACK_93_EQUIPMENT_BACKFILL_PREFLIGHT] OK no_execute preflight_audit approval_string_documented')
