#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_frontend_write_consumer_guard_v1.json')))
assert d.get('pack_91_inventory_frontend_consumer_migration_preserved') is True
assert d.get('pack_92_frontend_server_id_sweep_preserved') is True
assert d.get('silent_s1_fallback') is False
assert d.get('no_account_wide_fallback_for_server_bound_writes') is True
assert d.get('frontend_static_guard_pack_92_preserved') is True
print('[v110 PACK_93_FRONTEND_WRITE_CONSUMER_GUARD] OK pack_91_92_preserved no_silent_s1 no_account_wide_fallback')
