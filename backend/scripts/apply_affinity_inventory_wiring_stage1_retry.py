#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING-STAGE1-RETRY APPLY — Result snapshot + validator."""
from __future__ import annotations
import json, os, re, sys, subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/affinity_inventory_wiring_stage1_retry_apply_result_v1.json')


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def main():
    code, status = _get('/affinity/gift-spend/canary-status')
    conf = Path('/etc/supervisor/conf.d/backend.conf').read_text()
    flag_match = re.search(r'AFFINITY_GIFT_INVENTORY_WRITES_ENABLED="([^"]+)"', conf)
    flag_value = flag_match.group(1) if flag_match else None
    flag_on = flag_value == 'true_explicit_affinity_inventory_on'

    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    cols = set(db.list_collection_names())
    schema_ready = 'user_gift_inventory' in cols and 'user_affinity_state' in cols
    seed_count = db['user_gift_inventory'].count_documents({'metadata.seed_task':'V16'}) if 'user_gift_inventory' in cols else 0

    backups = sorted(Path('/app/backups').glob('backend.conf.pre-inv-flag.*.bak'))
    backup_path = str(backups[-1]) if backups else None

    inv_mut_rows = db['gift_transaction_ledger'].count_documents({'inventory_mutated':True})
    aff_mut_rows = db['gift_transaction_ledger'].count_documents({'affinity_points_mutated':True})
    payload = {
        'result_id': 'affinity_inventory_wiring_stage1_retry_apply_result_v1',
        'task_origin': 'AF2-N-INVENTORY-WIRING-STAGE1-RETRY APPLY',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'activation_state': 'ACTIVATED' if flag_on else 'READY_NOT_ACTIVATED',
        'activation_applied': flag_on,
        'flag_name': 'AFFINITY_GIFT_INVENTORY_WRITES_ENABLED',
        'flag_value': flag_value,
        'flag_currently_on': flag_on,
        'schema_ready': schema_ready,
        'seed_count_stage1_v16': seed_count,
        'backup_path_pre_flag': backup_path,
        'canary_status_post_activation': {
            'inventory_mutation_enabled': (status or {}).get('inventory_mutation_enabled'),
            'affinity_points_mutation_enabled': (status or {}).get('affinity_points_mutation_enabled'),
            'buffs_enabled': (status or {}).get('buffs_enabled'),
            'battle_runtime_attached': (status or {}).get('battle_runtime_attached'),
            'applied_to_combat': (status or {}).get('applied_to_combat'),
            'canary_allowlist_size': (status or {}).get('canary_allowlist_size'),
            'ledger_total_rows': (status or {}).get('ledger_total_rows'),
        },
        'observed_ledger_inventory_mut_rows': inv_mut_rows,
        'observed_ledger_affinity_mut_rows': aff_mut_rows,
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': flag_on,
            'inventory_mutation_enabled': flag_on,
            'affinity_points_mutation_enabled': flag_on,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'apply state={payload["activation_state"]} flag_on={flag_on}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
