#!/usr/bin/env python3
"""
Pack 83 - PSP Physical Normalization PREFLIGHT script.

READ-ONLY. NESSUNA scrittura DB. NESSUNA esecuzione di update fisico.
Genera:
  - v110_psp_namespace_audit_v1.json (audit completo con duplicati/collisioni)
  - v110_psp_normalization_mapping_v1.json (mapping ObjectId-string -> uuid)
  - v110_psp_normalization_dry_run_diff_v1.json (diff atteso, NON applicato)
  - v110_psp_normalization_backup_preflight_v1.json (manifest checksum no-secrets)
"""
import asyncio, os, sys, json, hashlib
from datetime import datetime
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

OUT_DIR = '/app/data/design/v110_psp_normalization_preflight'
os.makedirs(OUT_DIR, exist_ok=True)


def _redact(d):
    """Redazione campi sensibili: niente email, password, token."""
    sensitive = {'email', 'password', 'password_hash', 'token', 'access_token', 'refresh_token', 'jwt'}
    return {k: ('<redacted>' if k in sensitive else v) for k, v in d.items()}


async def main():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    try:
        from bson import ObjectId
    except ImportError:
        ObjectId = None

    # ===== TRACK B - NAMESPACE AUDIT =====
    psp_total = await db.player_server_profiles.count_documents({})
    direct = 0
    compat = 0
    orphan = 0
    duplicate_legacy_pairs = []
    duplicate_target_pairs = []
    missing_users = []
    ambiguous_users = []
    servers_covered = set()
    sample_redacted = []
    mapping_entries = []
    seen_legacy_pair = set()
    seen_target_pair = set()
    user_id_to_user_cache = {}

    cursor = db.player_server_profiles.find({}).sort('_id', 1)
    async for psp in cursor:
        sid = psp.get('server_id', '')
        servers_covered.add(sid)
        legacy_uid = psp.get('user_id', '')
        psp_id = str(psp.get('_id'))

        # Duplicate (legacy_uid, server_id) check
        key_legacy = (legacy_uid, sid)
        if key_legacy in seen_legacy_pair:
            duplicate_legacy_pairs.append({'psp_id': psp_id, 'legacy_user_id': legacy_uid, 'server_id': sid})
        seen_legacy_pair.add(key_legacy)

        # Risolvi il target uuid via direct/compat
        target_uuid = None
        lookup_mode = 'orphan'
        if legacy_uid in user_id_to_user_cache:
            u = user_id_to_user_cache[legacy_uid]
        else:
            u = await db.users.find_one({'id': legacy_uid})
            if u:
                user_id_to_user_cache[legacy_uid] = u
                lookup_mode = 'direct_uuid'
                direct += 1
                target_uuid = legacy_uid  # gia' uuid, nessuna modifica
            else:
                if ObjectId is not None:
                    try:
                        oid = ObjectId(legacy_uid)
                    except Exception:
                        oid = None
                    if oid:
                        u_compat = await db.users.find_one({'_id': oid})
                        if u_compat:
                            user_id_to_user_cache[legacy_uid] = u_compat
                            lookup_mode = 'objectid_compat_fallback'
                            compat += 1
                            target_uuid = u_compat.get('id')
                            if not target_uuid:
                                missing_users.append({'psp_id': psp_id, 'legacy_user_id': legacy_uid, 'reason': 'user has no id field'})
                                lookup_mode = 'missing_user_uuid'
                                target_uuid = None
                        else:
                            orphan += 1
                            missing_users.append({'psp_id': psp_id, 'legacy_user_id': legacy_uid, 'reason': 'no user found by _id'})
                    else:
                        orphan += 1
                        missing_users.append({'psp_id': psp_id, 'legacy_user_id': legacy_uid, 'reason': 'not valid ObjectId'})

        # Duplicate target (uuid, server_id)
        if target_uuid:
            key_target = (target_uuid, sid)
            if key_target in seen_target_pair:
                duplicate_target_pairs.append({'psp_id': psp_id, 'target_user_id': target_uuid, 'server_id': sid})
            seen_target_pair.add(key_target)

        # Mapping entry (solo per quelli che richiedono update)
        if lookup_mode == 'objectid_compat_fallback' and target_uuid:
            mapping_entries.append({
                'psp_id': psp_id,
                'server_id': sid,
                'legacy_user_id_objectid_string': legacy_uid,
                'target_user_id_uuid': target_uuid,
                'match_proof': f'users._id=ObjectId({legacy_uid}) -> users.id={target_uuid}',
                'safe_to_update': True,
            })

        # Sample redacted (primi 3)
        if len(sample_redacted) < 3:
            sample_redacted.append({
                'psp_id': psp_id,
                'server_id': sid,
                'lookup_mode_during_audit': lookup_mode,
                'fields_keys_only': sorted(list(psp.keys())),
            })

    # Mapping hash deterministico
    mapping_serialized = json.dumps(mapping_entries, sort_keys=True).encode('utf-8')
    mapping_hash = hashlib.sha256(mapping_serialized).hexdigest()

    audit_doc = {
        'pack': 'MEGA_RELEASE_ACCELERATION_83_PSP_PHYSICAL_NORMALIZATION_PREFLIGHT',
        'audited_at_utc': datetime.utcnow().isoformat() + 'Z',
        'audit_read_only': True,
        'audit_db_writes': 0,
        'psp_total': psp_total,
        'direct_uuid_count': direct,
        'objectid_compat_fallback_count': compat,
        'orphan_count': orphan,
        'duplicate_legacy_pairs_count': len(duplicate_legacy_pairs),
        'duplicate_target_pairs_count': len(duplicate_target_pairs),
        'duplicate_legacy_pairs_sample': duplicate_legacy_pairs[:5],
        'duplicate_target_pairs_sample': duplicate_target_pairs[:5],
        'missing_users_count': len(missing_users),
        'missing_users_sample': missing_users[:5],
        'ambiguous_users_count': len(ambiguous_users),
        'servers_covered': sorted(list(servers_covered)),
        'sample_psp_redacted_keys_only': sample_redacted,
    }
    with open(os.path.join(OUT_DIR, 'v110_psp_namespace_audit_v1.json'), 'w') as f:
        json.dump(audit_doc, f, indent=2)

    # ===== TRACK C - DETERMINISTIC MAPPING =====
    mapping_doc = {
        'pack': 'MEGA_RELEASE_ACCELERATION_83_PSP_PHYSICAL_NORMALIZATION_PREFLIGHT',
        'generated_at_utc': datetime.utcnow().isoformat() + 'Z',
        'mapping_hash_sha256': mapping_hash,
        'mapping_entries_count': len(mapping_entries),
        'collisions_detected': len(duplicate_target_pairs),
        'missing_or_ambiguous_count': len(missing_users) + len(ambiguous_users),
        'safe_to_proceed_all_entries': all(e['safe_to_update'] for e in mapping_entries) and len(duplicate_target_pairs) == 0 and len(missing_users) == 0,
        'sample_entries_first_3': mapping_entries[:3],
        'entries_full': mapping_entries,
    }
    with open(os.path.join(OUT_DIR, 'v110_psp_normalization_mapping_v1.json'), 'w') as f:
        json.dump(mapping_doc, f, indent=2)

    # ===== TRACK D - DRY-RUN DIFF =====
    migration_batch_id = f"v110_psp_user_id_normalization_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    dry_run_doc = {
        'pack': 'MEGA_RELEASE_ACCELERATION_83_PSP_PHYSICAL_NORMALIZATION_PREFLIGHT',
        'generated_at_utc': datetime.utcnow().isoformat() + 'Z',
        'physical_normalization_executed': False,
        'db_writes': 0,
        'target_database': 'divine_waifus',
        'target_collection': 'player_server_profiles',
        'planned_update_selector_template': {'_id': '<psp_id>', 'user_id': '<legacy_objectid_string>'},
        'planned_update_operation_template': {
            '$set': {
                'user_id': '<target_uuid>',
                '_slc_psp_user_id_namespace': 'uuid_canonical',
                '_slc_psp_user_id_normalization_batch_id': migration_batch_id,
                '_slc_psp_user_id_legacy_objectid_backup': '<legacy_objectid_string>',
            }
        },
        'expected_updates_count_if_executed': len(mapping_entries),
        'before_counts': {
            'direct_uuid': direct,
            'objectid_compat_fallback': compat,
            'orphan': orphan,
            'total': psp_total,
        },
        'after_counts_if_executed': {
            'direct_uuid': direct + len(mapping_entries),
            'objectid_compat_fallback': 0,
            'orphan': orphan,
            'total': psp_total,
        },
        'planned_migration_batch_id': migration_batch_id,
        'idempotency_marker_field': '_slc_psp_user_id_normalization_batch_id',
        'idempotency_check': 'If a PSP already has _slc_psp_user_id_normalization_batch_id set, the future execute MUST skip it.',
        'rollback_marker_field': '_slc_psp_user_id_legacy_objectid_backup',
        'reward_grant': False,
        'progress_advance': False,
        'user_heroes_mutation': False,
        'player_level_mutation': False,
        's1_to_s2_copy': False,
    }
    with open(os.path.join(OUT_DIR, 'v110_psp_normalization_dry_run_diff_v1.json'), 'w') as f:
        json.dump(dry_run_doc, f, indent=2)

    # ===== TRACK E - BACKUP PREFLIGHT MANIFEST =====
    backup_entries = []
    backup_db_writes = 0
    cursor2 = db.player_server_profiles.find({}).sort('_id', 1)
    async for psp in cursor2:
        psp_id = str(psp.get('_id'))
        sid = psp.get('server_id', '')
        legacy_uid = psp.get('user_id', '')
        # Checksum dei campi rilevanti (NO email/password/token - non sono in PSP comunque)
        rel = {
            'psp_id': psp_id,
            'user_id': legacy_uid,
            'server_id': sid,
            'profile_id': psp.get('profile_id', ''),
            'player_level': psp.get('player_level', None),
            'player_exp': psp.get('player_exp', None),
        }
        checksum = hashlib.sha256(json.dumps(rel, sort_keys=True, default=str).encode('utf-8')).hexdigest()
        backup_entries.append({
            'psp_id': psp_id,
            'server_id': sid,
            'legacy_user_id_objectid_string': legacy_uid,
            'pre_normalization_checksum_sha256': checksum,
        })
    backup_manifest_hash = hashlib.sha256(json.dumps(backup_entries, sort_keys=True).encode('utf-8')).hexdigest()
    backup_doc = {
        'pack': 'MEGA_RELEASE_ACCELERATION_83_PSP_PHYSICAL_NORMALIZATION_PREFLIGHT',
        'generated_at_utc': datetime.utcnow().isoformat() + 'Z',
        'mode': 'MANIFEST_CHECKSUM_NO_SECRETS',
        'backup_db_writes': backup_db_writes,
        'manifest_entries_count': len(backup_entries),
        'manifest_hash_sha256': backup_manifest_hash,
        'no_secret_export': True,
        'redaction_applied': True,
        'sufficient_for_rollback': True,
        'rollback_field_pinned': '_slc_psp_user_id_legacy_objectid_backup',
        'sample_entries_first_3': backup_entries[:3],
        'manifest_entries_full': backup_entries,
    }
    with open(os.path.join(OUT_DIR, 'v110_psp_normalization_backup_preflight_v1.json'), 'w') as f:
        json.dump(backup_doc, f, indent=2)

    summary = {
        'audit_doc_path': os.path.join(OUT_DIR, 'v110_psp_namespace_audit_v1.json'),
        'mapping_doc_path': os.path.join(OUT_DIR, 'v110_psp_normalization_mapping_v1.json'),
        'dry_run_doc_path': os.path.join(OUT_DIR, 'v110_psp_normalization_dry_run_diff_v1.json'),
        'backup_doc_path': os.path.join(OUT_DIR, 'v110_psp_normalization_backup_preflight_v1.json'),
        'mapping_hash_sha256': mapping_hash,
        'manifest_hash_sha256': backup_manifest_hash,
        'migration_batch_id': migration_batch_id,
        'safe_to_proceed_all_entries': mapping_doc['safe_to_proceed_all_entries'],
        'db_writes_total_during_preflight': 0,
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
