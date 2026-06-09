#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_future_migration_write_path_plan_v1.json')))
fp = d.get('future_write_paths', [])
assert len(fp) >= 4
for e in fp:
    assert e.get('executed_in_pack_92') is False, f'unexpected execute_in_pack_92 for {e.get("name")}'
    assert 'approval_string_proposed' in e
print(f'[v110 PACK_92_FUTURE_MIGRATION_WRITE_PATH_PLAN] OK future_write_paths={len(fp)} none_executed_in_pack_92 approval_strings_documented')
