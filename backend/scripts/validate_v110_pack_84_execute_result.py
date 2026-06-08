#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
e = d.get('execute_result', {})
assert e.get('planned_writes_count') == 1690
assert e.get('actual_writes_count') == 1690
assert e.get('skipped_idempotent_count') == 0
assert e.get('refused_no_match_count') == 0
assert e.get('audit_log_anomalies') == 0
assert e.get('target_db') == 'divine_waifus'
assert e.get('target_collection') == 'player_server_profiles'
assert 'v110_psp_user_id_normalization_' in e.get('batch_id', '')
assert e.get('exit_code') == 0
assert e.get('production_db_writes_count') == 1690
print(f"[v110 PACK_84_EXECUTE_RESULT] OK actual=1690 planned=1690 skipped=0 refused=0 target=divine_waifus.player_server_profiles")
