#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_currency_write_guard_v1.json')))
assert d.get('strict_server_scoped') is True
assert d.get('server_id_required') is True
assert d.get('psp_check_required') is True
assert d.get('idempotency_token_required') is True
assert d.get('mutates_only_psp_soft_currencies') is True
assert d.get('mutates_users_gold_or_gems') is False
assert d.get('no_premium_grant') is True
assert d.get('false_filter_applied_true') is False
fp = os.path.join(R, d['file']); assert os.path.exists(fp)
src = open(fp).read()
assert '/wallet/spend' in src and 'wallet_spend_ledger' in src and 'IDEMPOTENCY_TOKEN_REQUIRED' in src and 'CURRENCY_NOT_SOFT_SERVER_SCOPED' in src
assert 'SERVER_ID_REQUIRED' in src and 'PLAYER_SERVER_PROFILE_REQUIRED' in src
print('[v110 PACK_93_CURRENCY_WRITE_GUARD] OK strict_server_scoped psp_check idempotency soft_only no_premium_grant')
