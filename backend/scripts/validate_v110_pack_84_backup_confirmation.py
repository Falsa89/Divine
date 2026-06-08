#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
b = d.get('backup_confirmation', {})
assert b.get('mode') == 'MANIFEST_CHECKSUM_NO_SECRETS_PRE_WRITE'
assert b.get('manifest_hash_sha256_pinned') == 'e12b15aa0e45c3a388310b74b8d24473affde0697282d7f30d8781554986b4a2'
assert b.get('per_psp_inline_backup_field') == '_slc_psp_user_id_legacy_objectid_backup'
assert b.get('per_psp_inline_backup_written_for_count', 0) >= 1690
assert b.get('rollback_remains_possible') is True
print(f"[v110 PACK_84_BACKUP_CONFIRMATION] OK manifest_hash_pinned per_psp_backup_field_written rollback_possible")
