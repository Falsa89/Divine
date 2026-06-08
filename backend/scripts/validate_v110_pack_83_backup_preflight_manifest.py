#!/usr/bin/env python3
# Pack 83 - Track E: backup preflight manifest.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bk = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_backup_preflight_v1.json')))
assert bk.get('mode') == 'MANIFEST_CHECKSUM_NO_SECRETS'
assert bk.get('backup_db_writes') == 0
assert bk.get('no_secret_export') is True
assert bk.get('redaction_applied') is True
assert bk.get('sufficient_for_rollback') is True
h = bk.get('manifest_hash_sha256', '')
assert len(h) == 64
assert bk.get('manifest_entries_count', 0) > 0
assert bk.get('rollback_field_pinned') == '_slc_psp_user_id_legacy_objectid_backup'
entries = bk.get('manifest_entries_full', [])
assert len(entries) == bk['manifest_entries_count']
for e in entries[:3]:
    for k in ('psp_id', 'server_id', 'legacy_user_id_objectid_string', 'pre_normalization_checksum_sha256'):
        assert k in e
    # Verifica: nessuna chiave 'email'/'password'/'token' nei entries
    for forbidden in ('email', 'password', 'password_hash', 'token', 'access_token'):
        assert forbidden not in e, f'forbidden field {forbidden} in manifest entry'
# Documento MD esiste
assert os.path.exists(os.path.join(R, 'docs/divine/110_PSP_NORMALIZATION_BACKUP_PREFLIGHT.md'))
print(f'[v110 PACK_83_BACKUP_PREFLIGHT_MANIFEST] OK entries={bk["manifest_entries_count"]} hash={h[:12]} no_secrets=true sufficient_for_rollback=true')
