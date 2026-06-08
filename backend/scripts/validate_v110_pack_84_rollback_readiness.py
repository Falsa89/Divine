#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
rb = d.get('rollback_readiness', {})
assert rb.get('rollback_field_present_on_all_normalized_psps') is True
assert rb.get('rollback_field_name') == '_slc_psp_user_id_legacy_objectid_backup'
assert rb.get('batch_id_field_present_on_all_normalized_psps') is True
assert rb.get('batch_id_field_name') == '_slc_psp_user_id_normalization_batch_id'
assert rb.get('rollback_script_refuse_by_default') is True
assert 'v110_psp_user_id_normalization_' in rb.get('rollback_executable_for_batch_id', '')
# Verifica live DB: tutti i 1690 PSP hanno entrambi i marker
import asyncio, sys
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
async def check():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    with_batch = await db.player_server_profiles.count_documents({'_slc_psp_user_id_normalization_batch_id': {'$exists': True}})
    with_backup = await db.player_server_profiles.count_documents({'_slc_psp_user_id_legacy_objectid_backup': {'$exists': True}})
    return with_batch, with_backup
b, bk = asyncio.get_event_loop().run_until_complete(check())
assert b == 1690, f'batch_id marker missing on some PSPs: {b}/1690'
assert bk == 1690, f'backup marker missing on some PSPs: {bk}/1690'
print(f'[v110 PACK_84_ROLLBACK_READINESS] OK batch_id_markers=1690 backup_markers=1690 rollback_script_refuse_by_default')
