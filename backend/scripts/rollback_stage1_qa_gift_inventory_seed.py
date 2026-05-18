#!/usr/bin/env python3
"""V16 SEED ROLLBACK — remove only docs with metadata.seed_task='V16'."""
from __future__ import annotations
import argparse, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    if 'user_gift_inventory' not in db.list_collection_names():
        print('user_gift_inventory absent'); return 0
    flt = {'metadata.seed_task': 'V16'}
    n = db['user_gift_inventory'].count_documents(flt)
    if args.dry_run:
        print(f'dry-run: would_delete={n}'); return 0
    res = db['user_gift_inventory'].delete_many(flt)
    print(f'deleted: {res.deleted_count}')
    # affinity_state with V16 seed metadata as well (none today, but safe)
    if 'user_affinity_state' in db.list_collection_names():
        r2 = db['user_affinity_state'].delete_many({'metadata.seed_task': 'V16'})
        print(f'affinity_state deleted: {r2.deleted_count}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
