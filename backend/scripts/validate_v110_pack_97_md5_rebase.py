#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_md5_rebase_v1.json')))
for f in d.get('files_added') or []:
    assert os.path.exists(os.path.join(R, f)), f
for f in d.get('files_modified') or []:
    assert os.path.exists(os.path.join(R, f)), f
assert d['no_validator_weakening'] is True
assert d['baseline_signature_preserved'] is True
print('[v110 PACK_97_MD5_REBASE] OK files_added files_modified no_validator_weakening')
