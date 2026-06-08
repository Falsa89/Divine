#!/usr/bin/env python3
# Pack 82 - Track 9: MD5 rebase summary (server.py rebased).
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
chain = d.get('md5_rebase_chain', [])
assert len(chain) >= 1
entry = chain[0]
assert entry['file'] == 'backend/server.py'
assert entry['from_md5'] == '64bde649aad1095ab09772e5f625d0df'
assert entry['authorized'] is True
m = hashlib.md5(open(os.path.join(R, 'backend/server.py'), 'rb').read()).hexdigest()
# Pack 85+: server.py MD5 evolved oltre Pack 82. Accetta sia Pack 82 to_md5 (storico) sia attuale.
import json as _j
_v100 = _j.load(open(os.path.join(R, 'data/design/closed_alpha/v100_runtime_md5_baseline_v1.json')))
assert _v100['files']['backend/server.py']['current_md5'] == m, f'v100 baseline server.py current_md5 must match actual: {m}'
hist_mds = [h.get('md5') for h in _v100['files']['backend/server.py'].get('historical_references', [])]
assert entry['to_md5'] in hist_mds or entry['to_md5'] == m, 'Pack 82 to_md5 must be current or historical'
# Tracking file (v100 baseline) aggiornato
baseline = open(os.path.join(R, 'data/design/closed_alpha/v100_runtime_md5_baseline_v1.json')).read()
assert m in baseline, 'v100 baseline not rebased to new MD5'
assert '64bde649aad1095ab09772e5f625d0df' in baseline, 'Pack 81 historical reference not preserved'
print(f'[v110 PACK_82_MD5_REBASE] OK server_py_md5={m[:12]} from_pack81={entry["from_md5"][:12]} historical_preserved=true')
