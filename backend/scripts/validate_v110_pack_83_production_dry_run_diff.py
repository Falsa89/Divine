#!/usr/bin/env python3
# Pack 83 - Track D: production dry-run diff.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dry = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_dry_run_diff_v1.json')))
assert dry.get('physical_normalization_executed') is False
assert dry.get('db_writes') == 0
assert dry.get('target_database') == 'divine_waifus'
assert dry.get('target_collection') == 'player_server_profiles'
assert dry.get('expected_updates_count_if_executed', 0) > 0
assert dry.get('idempotency_marker_field') == '_slc_psp_user_id_normalization_batch_id'
assert dry.get('rollback_marker_field') == '_slc_psp_user_id_legacy_objectid_backup'
assert dry.get('reward_grant') is False
assert dry.get('user_heroes_mutation') is False
assert dry.get('player_level_mutation') is False
assert dry.get('s1_to_s2_copy') is False
before = dry.get('before_counts', {})
after = dry.get('after_counts_if_executed', {})
assert before.get('total') == after.get('total'), 'total PSP count must remain same'
assert after.get('objectid_compat_fallback') == 0, 'after normalization compat must be 0'
print(f'[v110 PACK_83_PRODUCTION_DRY_RUN_DIFF] OK executed=false db_writes=0 expected_updates={dry["expected_updates_count_if_executed"]} idempotency_marker_present')
