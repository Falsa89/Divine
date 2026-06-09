#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_md5_rebase_v1.json')))
files = d.get('files_modified') or []
for f in files:
    assert os.path.exists(os.path.join(R, f)), f'file modified not found: {f}'
assert d.get('no_validator_weakening') is True
assert d.get('baseline_signature_preserved') is True
print(f'[v110 PACK_95_MD5_REBASE] OK files_modified={len(files)} no_validator_weakening baseline_signature_preserved')
