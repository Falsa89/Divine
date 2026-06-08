#!/usr/bin/env python3
# Pack 83 - Track C: deterministic normalization mapping.
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
mapping = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_mapping_v1.json')))
assert mapping.get('mapping_entries_count') > 0
assert mapping.get('safe_to_proceed_all_entries') is True
assert mapping.get('collisions_detected') == 0
assert mapping.get('missing_or_ambiguous_count') == 0
h = mapping.get('mapping_hash_sha256', '')
assert len(h) == 64, f'mapping hash must be sha256 hex: {h}'
# Verifica deterministicita': ricalcola sha256 sugli entries_full
entries = mapping.get('entries_full', [])
assert len(entries) == mapping['mapping_entries_count']
for e in entries[:3]:
    for k in ('psp_id', 'server_id', 'legacy_user_id_objectid_string', 'target_user_id_uuid', 'match_proof', 'safe_to_update'):
        assert k in e, f'mapping entry missing key {k}'
recomputed = hashlib.sha256(json.dumps(entries, sort_keys=True).encode('utf-8')).hexdigest()
assert recomputed == h, f'mapping_hash mismatch: recomputed={recomputed} stored={h}'
print(f'[v110 PACK_83_DETERMINISTIC_NORMALIZATION_MAPPING] OK entries={mapping["mapping_entries_count"]} hash={h[:12]} collisions=0 deterministic=true')
