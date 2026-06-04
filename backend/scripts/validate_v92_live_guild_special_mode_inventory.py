#!/usr/bin/env python3
"""v92 — Live/Guild/Special Mode Inventory validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INV = os.path.join(ROOT, 'data', 'design', 'live_mode_testability',
                   'v92_live_guild_special_mode_inventory_audit_v1.json')
DOC = os.path.join(ROOT, 'docs', 'divine', '92_LIVE_GUILD_SPECIAL_MODE_TESTABILITY_AUDIT.md')

REQUIRED_MODE_IDS = {
    'story', 'tower', 'arena', 'training', 'raid', 'event',
    'crepuscolo_dei_titani', 'assalto_del_ragnarok', 'guild_war', 'guild_raid',
    'server_boss', 'faction_boss', 'territory', 'war_avatar_mode', 'event_avatar_mode',
}
REQUIRED_FIELDS = {
    'mode_id', 'label', 'exists_in_ui', 'exists_in_route', 'time_gated',
    'guild_required', 'avatar_required', 'battle_required', 'pre_battle_required',
    'encounter_source_type', 'currently_testable', 'qa_preview_path_needed',
}


def fail(msg): print(f"FAIL v92_live_guild_special_mode_inventory: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(INV): fail(f"missing inventory: {INV}")
    if not os.path.isfile(DOC): fail(f"missing audit doc: {DOC}")
    with open(INV, 'r', encoding='utf-8') as f: data = json.load(f)
    modes = data.get('modes') or []
    if not modes: fail("modes empty")
    found_ids = {m.get('mode_id') for m in modes}
    missing = REQUIRED_MODE_IDS - found_ids
    if missing: fail(f"missing required mode_ids: {sorted(missing)}")
    for m in modes:
        for k in REQUIRED_FIELDS:
            if k not in m:
                fail(f"mode {m.get('mode_id')} missing field: {k}")
    safety = data.get('safety') or {}
    if safety.get('db_writes') != 0: fail("safety.db_writes must be 0")
    if safety.get('reward_live') is not False: fail("safety.reward_live must be false")
    if safety.get('ranking_live') is not False: fail("safety.ranking_live must be false")
    print("PASS v92_live_guild_special_mode_inventory")


if __name__ == '__main__': main()
