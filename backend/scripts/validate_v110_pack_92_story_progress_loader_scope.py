#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_story_progress_loader_scope_v1.json')))
assert d.get('server_id_param') is True
assert d.get('reads_psp_story_progress_when_server_id_present') is True
assert d.get('no_db_write_in_strict_server_scoped_path') is True
assert d.get('no_story_progress_write_promotion_in_pack_92') is True
assert d.get('false_filter_applied_true') is False
assert d.get('reward_live') is False and d.get('progress_live') is False
fp = os.path.join(R, d['file']); assert os.path.exists(fp)
src = open(fp).read()
assert 'psp_server_scoped' in src
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in src
assert 'legacy_account_wide_deprecated' in src
print('[v110 PACK_92_STORY_PROGRESS_LOADER_SCOPE] OK psp_real_read no_strict_path_write legacy_flagged no_reward_live')
