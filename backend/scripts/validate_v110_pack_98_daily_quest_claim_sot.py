#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_daily_quest_claim_sot_v1.json')))
assert d['source_id']=='daily_quest_completion_claim'
assert d['daily_key_computed_server_side'] is True
assert d['completion_proof_required_server_side'] is True
assert d['ready_status']=='READY_GATED_COMPLETION_REQUIRED'
assert d['quest_id_whitelist']==['daily_quest_1','daily_quest_2','daily_quest_3']
sot=os.path.join(R,'docs/divine/118_DAILY_QUEST_CLAIM_SOT.md')
assert os.path.exists(sot)
print('[v110 PACK_98_DAILY_QUEST_CLAIM_SOT] OK doc_present completion_proof_required ready_gated')
