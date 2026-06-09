#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_story_progress_write_guard_v1.json')))
assert d.get('server_id_query_param_added') is True
assert d.get('blocker_when_server_id_present') == 'STORY_PROGRESS_WRITE_SERVER_SCOPE_DEFERRED'
assert d.get('legacy_path_unchanged') is True
assert d.get('no_reward_live') is True and d.get('no_progress_live') is True
assert d.get('no_battle_engine_rewrite') is True
assert d.get('false_filter_applied_true') is False
fp = os.path.join(R, d['file']); assert os.path.exists(fp)
src = open(fp).read()
assert 'STORY_PROGRESS_WRITE_SERVER_SCOPE_DEFERRED' in src
print('[v110 PACK_93_STORY_PROGRESS_WRITE_GUARD] OK server_id_aware_blocker legacy_unchanged no_reward_live')
