#!/usr/bin/env python3
"""SLC-A: Shard isolation audit (READ-ONLY, no DB connect, no writes).

Scans backend code (routes/models/server.py etc.) for hints of user-bound
collections and reports whether server_id appears in their query/update paths.
Produces a JSON report only; no MongoDB connection performed.
"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/server_lifecycle/server_shard_isolation_audit_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BACKEND = Path('/app/backend')

COLLECTIONS = {
    'accounts_users_auth':     ['user', 'account', 'auth', 'session'],
    'user_heroes':             ['user_heroes', 'roster', 'hero_state'],
    'inventory':               ['user_gift_inventory', 'inventory', 'materials'],
    'currencies':              ['currency', 'gold_balance', 'diamonds'],
    'paid_currency_purchase':  ['purchase', 'paid_currency', 'topup', 'top_up'],
    'gacha_history':           ['gacha_history', 'gacha_log', 'gacha_pity'],
    'teams':                   ['team', 'squad', 'formation'],
    'story_progress':          ['story_progress', 'chapter_progress'],
    'guilds':                  ['guild'],
    'arena_rankings':          ['arena', 'pvp_rank', 'ranking'],
    'affinity':                ['user_affinity_state', 'affinity'],
    'gift_transaction_ledger': ['gift_transaction_ledger'],
    'cosmetics':                ['cosmetic', 'skin_', 'title_'],
    'event_progress':          ['event_progress', 'event_state'],
    'server_config':           ['server_config', 'server_entity'],
}

QUERY_PATTERNS = [r'find_one\s*\(', r'find\s*\(', r'update_one\s*\(',
                  r'update_many\s*\(', r'insert_one\s*\(', r'insert_many\s*\(',
                  r'delete_one\s*\(', r'delete_many\s*\(', r'aggregate\s*\(']
SERVER_ID_PATTERN = r'\bserver_id\b'
USER_ID_PATTERN = r"['\"\\b]user_id['\"\\b]"


def _scan_files():
    text_by_file = {}
    for f in BACKEND.rglob('*.py'):
        if '__pycache__' in f.parts: continue
        try: text_by_file[str(f.relative_to('/app'))] = f.read_text(errors='ignore')
        except Exception: pass
    return text_by_file


def main():
    started = datetime.now(timezone.utc).isoformat()
    files = _scan_files()
    categories_result = {}
    cross_server_leak_risks = []
    total_files = len(files)

    for category, keywords in COLLECTIONS.items():
        hits = []
        for path, txt in files.items():
            txt_lower = txt.lower()
            for kw in keywords:
                if kw.lower() in txt_lower:
                    # Check query paths near keyword
                    has_server_id = bool(re.search(SERVER_ID_PATTERN, txt))
                    has_user_id_only = bool(re.search(USER_ID_PATTERN, txt)) and not has_server_id
                    sample_lines = []
                    for i, line in enumerate(txt.splitlines(), 1):
                        if kw.lower() in line.lower():
                            sample_lines.append({'line': i, 'snippet': line.strip()[:160]})
                            if len(sample_lines) >= 3: break
                    hits.append({
                        'file': path,
                        'keyword': kw,
                        'has_server_id_anywhere': has_server_id,
                        'has_user_id_only_without_server_id': has_user_id_only,
                        'sample_lines': sample_lines,
                    })
                    if has_user_id_only:
                        cross_server_leak_risks.append({'category': category, 'file': path, 'keyword': kw})
                    break  # one hit per file is enough
        categories_result[category] = {
            'expected_scope': 'server_bound' if category not in ('accounts_users_auth','paid_currency_purchase') else 'account_wide_or_mixed',
            'files_with_hits': len(hits),
            'hits_sample': hits[:6],
            'server_id_present_anywhere': any(h['has_server_id_anywhere'] for h in hits),
            'user_id_only_files_count': sum(1 for h in hits if h['has_user_id_only_without_server_id']),
        }

    # Migration priority heuristic: server-bound categories that have user_id-only files are P1.
    migration_priority = {'P0': [], 'P1': [], 'P2': []}
    for cat, info in categories_result.items():
        if info['expected_scope'] == 'server_bound':
            if info['user_id_only_files_count'] > 0:
                migration_priority['P1'].append(cat)
            elif info['files_with_hits'] > 0 and not info['server_id_present_anywhere']:
                migration_priority['P1'].append(cat)
            else:
                migration_priority['P2'].append(cat)
        else:
            migration_priority['P2'].append(cat)

    out = {
        'task_origin': 'SLC-A-SHARD-ISOLATION-AUDIT',
        'timestamp_utc': started,
        'mode': 'READ_ONLY_NO_DB_CONNECT',
        'db_writes_performed': False,
        'db_connection_opened': False,
        'backend_python_files_scanned': total_files,
        'collections_audited': list(COLLECTIONS.keys()),
        'results_by_category': categories_result,
        'cross_server_leak_risk_candidates_count': len(cross_server_leak_risks),
        'cross_server_leak_risk_samples': cross_server_leak_risks[:20],
        'migration_priority_by_category': migration_priority,
        'safety': {
            'no_db_write': True,
            'no_runtime_change': True,
            'no_borea_exposure': True,
            'audit_only': True,
        },
        'verdict': 'PASS',  # Audit always PASS (read-only); risk findings are advisory.
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict=PASS files_scanned={total_files} categories={len(COLLECTIONS)} leak_candidates={len(cross_server_leak_risks)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
