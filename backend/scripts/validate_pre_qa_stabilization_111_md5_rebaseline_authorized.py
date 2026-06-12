#!/usr/bin/env python3
"""Pre-QA Stabilization 111 — R-04 MD5 rebaseline authorized validator."""
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rb = json.load(open(os.path.join(R, 'data/design/audit/pre_qa_111/md5_rebaseline_authorized.json')))
assert rb['authorization'] == 'AUTORIZZO_PRE_QA_STABILIZATION_111_REBASELINE_ROUTE_CLASSIFICATION'
assert rb['no_safety_violation_hidden_as_md5_drift'] is True
assert rb['no_fake_pass'] is True
assert rb['no_validator_weakening'] is True
entries = rb['rebaselined_files']
assert len(entries) >= 9 and len(entries) <= 12, f'expected 9-12 entries; got {len(entries)}'
for e in entries:
    for k in ('pin_file', 'field', 'old_hash', 'new_hash', 'target_file', 'reason', 'blocker_pack_110'):
        assert k in e, f'entry missing {k}: {e}'
    assert e['blocker_pack_110'].startswith('P0') or e['blocker_pack_110'].startswith('P1')
# Forbidden rebaseline check: nessun file critical e' stato toccato.
for forbidden in ('.env', 'JWT_SECRET', 'character_bible', 'gacha_rates'):
    for e in entries:
        assert forbidden.lower() not in (str(e.get('target_file', '')) + str(e.get('pin_file', ''))).lower(), f'forbidden rebaseline: {e}'
print(f'[v111 PRE_QA_111_MD5_REBASELINE_AUTHORIZED] OK {len(entries)}_entries_pack_110_linked no_forbidden_rebaseline')
