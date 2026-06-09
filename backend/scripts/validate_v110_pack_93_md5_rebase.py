#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_md5_rebase_v1.json')))
assert d.get('replacement_invariant_functional') is True and d.get('validator_weakening') is False and d.get('fake_PASS') is False
for e in d.get('backend_runtime_files_modified', []):
    fp = os.path.join(R, e['file']); cur = hashlib.md5(open(fp,'rb').read()).hexdigest()
    assert cur == e['md5_post_pack_93'], f"md5 drift {e['file']}: {cur}"
for e in d.get('backend_runtime_files_unchanged', []):
    fp = os.path.join(R, e['file']); cur = hashlib.md5(open(fp,'rb').read()).hexdigest()
    assert cur == e['md5'], f"unchanged md5 drift {e['file']}: {cur}"
print('[v110 PACK_93_MD5_REBASE] OK backend_md5_post_pack_93_match no_validator_weakening no_fake_PASS')
