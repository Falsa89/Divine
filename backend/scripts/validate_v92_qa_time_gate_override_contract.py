#!/usr/bin/env python3
"""v92 — QA Time-Gate Override Contract validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTRACT = os.path.join(ROOT, 'data', 'design', 'live_mode_testability',
                       'live_mode_qa_time_gate_override_contract_v1.json')

REQUIRED_LABELS = {'TEST MODE', 'QA TIME OVERRIDE', 'NO LIVE REWARD', 'NO RANKING APPLIED'}
REQUIRED_TARGETS = {
    'crepuscolo_dei_titani', 'assalto_del_ragnarok', 'guild_war', 'guild_raid',
    'server_boss', 'faction_boss', 'territory', 'event', 'event_avatar_mode',
}


def fail(msg): print(f"FAIL v92_qa_time_gate_override_contract: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(CONTRACT): fail(f"missing contract: {CONTRACT}")
    with open(CONTRACT, 'r', encoding='utf-8') as f: data = json.load(f)
    if data.get('qa_override_only') is not True: fail("qa_override_only must be true")
    if data.get('production_enabled') is not False: fail("production_enabled must be false")
    if data.get('reward_live') is not False: fail("reward_live must be false")
    if data.get('ranking_live') is not False: fail("ranking_live must be false")
    if data.get('event_currency_live') is not False: fail("event_currency_live must be false")
    if data.get('db_writes') != 0: fail("db_writes must be 0")
    if data.get('requires_debug_label') is not True: fail("requires_debug_label must be true")
    labels = set(data.get('required_ui_labels') or [])
    missing_labels = REQUIRED_LABELS - labels
    if missing_labels: fail(f"missing ui labels: {sorted(missing_labels)}")
    targets = data.get('override_targets') or []
    found = {t.get('mode_id') for t in targets}
    missing = REQUIRED_TARGETS - found
    if missing: fail(f"missing override targets: {sorted(missing)}")
    for t in targets:
        if t.get('production_enabled') is not False:
            fail(f"override_targets[{t.get('mode_id')}].production_enabled must be false")
        if t.get('qa_simulate_open') is not True:
            fail(f"override_targets[{t.get('mode_id')}].qa_simulate_open must be true")
    print("PASS v92_qa_time_gate_override_contract")


if __name__ == '__main__': main()
