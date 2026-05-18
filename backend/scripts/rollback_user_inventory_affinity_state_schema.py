#!/usr/bin/env python3
"""V16 SCHEMA ROLLBACK — Drop user_gift_inventory and user_affinity_state.

Usage:
  python3 rollback_user_inventory_affinity_state_schema.py             # live
  python3 rollback_user_inventory_affinity_state_schema.py --dry-run    # check only
"""
from __future__ import annotations
import argparse, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    cols = set(db.list_collection_names())
    targets = ['user_gift_inventory','user_affinity_state']
    if args.dry_run:
        print(f'dry-run: collections_present={[c for c in targets if c in cols]}')
        return 0
    for c in targets:
        if c in cols:
            db[c].drop(); print(f'dropped: {c}')
        else:
            print(f'absent: {c}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
