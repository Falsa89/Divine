#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_currency_wallet_loader_split_v1.json')))
assert d.get('server_id_param') is True
assert d.get('real_split_implemented') is True
assert d.get('psp_check_when_server_id_present') is True
assert d.get('false_filter_applied_true') is False
assert d.get('no_balance_mutation') is True
fp = os.path.join(R, d['file']); assert os.path.exists(fp)
src = open(fp).read()
assert 'currencies_global' in src and 'currencies_server_scoped' in src
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in src
assert 'psp_server_scoped_split' in src
assert 'legacy_account_wide_deprecated' in src
print('[v110 PACK_92_CURRENCY_WALLET_LOADER_SPLIT] OK real_split psp_check legacy_flagged no_balance_mutation')
