#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_md5_rebase_v1.json')))
assert d.get('replacement_invariant_functional') is True
assert d.get('validator_weakening') is False
assert d.get('fake_PASS') is False
for e in d.get('backend_runtime_files_modified', []):
    fp = os.path.join(R, e['file'])
    cur = hashlib.md5(open(fp,'rb').read()).hexdigest()
    assert cur == e['md5_post_pack_92'], f"backend md5 drift on {e['file']}: {cur} vs {e['md5_post_pack_92']}"
for e in d.get('backend_runtime_files_unchanged', []):
    if 'md5' in e:
        fp = os.path.join(R, e['file'])
        cur = hashlib.md5(open(fp,'rb').read()).hexdigest()
        assert cur == e['md5'], f"unchanged backend md5 drift on {e['file']}: {cur} vs {e['md5']}"
for f in d.get('frontend_runtime_files_modified', []):
    assert os.path.exists(os.path.join(R, f)), f
print('[v110 PACK_92_MD5_REBASE] OK backend_md5_post_pack_92_match frontend_files_present no_validator_weakening no_fake_PASS')
