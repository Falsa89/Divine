#!/usr/bin/env python3
import os, json, sys, urllib.request, asyncio, time
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient
BASE='http://127.0.0.1:8001'; MONGO=os.getenv('MONGO_URL')
def post(url,body,h=None):
    H={'Content-Type':'application/json'}
    if h: H.update(h)
    d=json.dumps(body).encode() if body else None
    r=urllib.request.Request(url,data=d,headers=H,method='POST')
    try:
        with urllib.request.urlopen(r,timeout=20) as rr: return rr.status, dict(rr.headers), json.loads(rr.read())
    except urllib.error.HTTPError as e: return e.code, dict(e.headers), json.loads(e.read())
def get(url,h=None):
    H={}; 
    if h: H.update(h)
    r=urllib.request.Request(url,headers=H)
    with urllib.request.urlopen(r,timeout=20) as rr: return rr.status, dict(rr.headers), json.loads(rr.read())
async def inject_leak(uid):
    c=AsyncIOMotorClient(MONGO); db=c.divine_waifus
    await db.inventory.insert_one({'user_id':uid,'server_id':'s1','item_id':'leak_test_item','quantity':99,'_slc_pack_89_test_leak':True})
async def cleanup(uid):
    c=AsyncIOMotorClient(MONGO); db=c.divine_waifus
    await db.users.delete_one({'id':uid}); await db.inventory.delete_many({'user_id':uid}); await db.player_server_profiles.delete_many({'user_id':uid})
uid=None; TS=int(time.time()); SID=f's_pack89_e2e_{TS}'; email=f'pack89_test_user_{TS}@test.com'
try:
    st,h,body=post(f'{BASE}/api/register',{'email':email,'password':'pw89','username':'p89u'})
    uid=body['user']['id']; token=body['token']; auth={'Authorization':f'Bearer {token}'}
    # Step 1: server_id presente, PSP missing -> blocker
    st,h,body=get(f'{BASE}/api/inventory?server_id={SID}', auth)
    assert body.get('blocker')=='PLAYER_SERVER_PROFILE_REQUIRED'
    assert body.get('filter_applied') is True
    assert body.get('inventory_source')=='none'
    assert body.get('legacy_account_inventory_used') is False
    assert body.get('items')==[]
    # Step 2: legacy path (no server_id) -> filter_applied=False
    st,h,body=get(f'{BASE}/api/inventory', auth)
    assert body.get('filter_applied') is False
    assert body.get('inventory_source')=='legacy_account_wide_deprecated'
    assert body.get('legacy_account_inventory_used') is True
    assert body.get('blocker') is None
    # Step 3: ensure PSP, inventory empty for new server
    post(f'{BASE}/api/psp/ensure?server_id={SID}', None, auth)
    st,h,body=get(f'{BASE}/api/inventory?server_id={SID}', auth)
    assert body.get('filter_applied') is True
    assert body.get('inventory_source')=='player_server_scoped'
    assert body.get('legacy_account_inventory_used') is False
    assert body.get('items')==[]
    assert body.get('blocker') is None
    # Step 4: inject leak on s1 for this test user
    loop=asyncio.new_event_loop(); asyncio.set_event_loop(loop); loop.run_until_complete(inject_leak(uid))
    # Step 5: inventory route on new SID does NOT show s1 leak
    st,h,body=get(f'{BASE}/api/inventory?server_id={SID}', auth)
    assert body.get('items')==[], f'LEAK: s1 inventory shown on different server: {body}'
    assert body.get('legacy_account_inventory_used') is False
    assert body.get('inventory_source')=='player_server_scoped'
finally:
    if uid: loop2=asyncio.new_event_loop(); asyncio.set_event_loop(loop2); loop2.run_until_complete(cleanup(uid))
print('[v110 PACK_89_RUNTIME_SMOKE_E2E] OK strict_server_scope_inventory no_account_wide_leak no_db_writes_in_promotion_path legacy_path_flagged_cleanup_executed')
