#!/usr/bin/env python3
"""v101 — Encounter/Enemy source cleanup validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_encounter_enemy_source_cleanup_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
modes = d.get('modes_covered') or []
if len(modes) < 10: print(f'FAIL \u2014 modes_covered < 10 (got {len(modes)})'); sys.exit(1)
rules = d.get('rules_applied') or {}
for k in ('no_legacy_hero_ids_in_encounters','no_random_runtime_enemies','story_tower_authored_encounters','arena_player_or_bot_teams_only','raid_boss_authored_not_random_group'):
    if not rules.get(k, False): print(f'FAIL \u2014 rule {k} not true'); sys.exit(1)
per_mode = d.get('per_mode_audit') or {}
for mode, audit in per_mode.items():
    if audit.get('legacy_refs', 1) != 0: print(f'FAIL \u2014 {mode} legacy_refs != 0'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('legacy_hero_in_encounters','random_opponent_generation','random_runtime_enemies','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 encounter/enemy source cleanup ({len(modes)} modes, 0 legacy refs)")
sys.exit(0)
