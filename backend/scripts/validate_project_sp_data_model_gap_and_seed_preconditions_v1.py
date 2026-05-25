#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_data_model_gap_and_seed_preconditions_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_SERVER_PROFILE_DATA_MODEL_GAP_AND_SEED_PRECONDITIONS_READY'
    assert d['audit_mode'] == 'design_only'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert d['global_markers']['TRACK_D_SERVER_PROFILE_DATA_MODEL_GAP_SEED_PRECONDITIONS_APPROVAL'] == 'true'
    cs = d['current_state']
    assert cs['server_profiles_collection_doc_count_assumption'] == 0
    assert cs['mapping_users_to_server_profile_id'] == 'DOES_NOT_EXIST'
    model = d['proposed_data_model_server_profiles']
    assert model['collection'] == 'server_profiles'
    shape = model['document_shape']
    for f in ['user_id','server_id','is_archived','account_level','last_played_at','created_at','updated_at']:
        assert f in shape, f'missing model field {f}'
    idxs = model['indexes']
    assert any(i.get('unique') is True for i in idxs)
    # Preconditions and rollback requirements present
    assert len(d['users_server_migration_preconditions']) >= 4
    assert len(d['rollback_safe_seed_requirements']) >= 4
    assert len(d['orphan_prevention']) >= 2
    print(f"[PASS] AUTH-HARDEN Track D data model gap & seed READY \u2014 indexes={len(idxs)}")
    return 0
if __name__ == '__main__': sys.exit(main())
