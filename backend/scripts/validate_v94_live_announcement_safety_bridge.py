#!/usr/bin/env python3
"""v94 — Live announcement runtime safety bridge validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, 'data', 'design', 'live_announcements', 'v94_live_announcement_runtime_safety_bridge_v1.json')
REQ_SOURCES = {'engine.six_star_pull', 'arena.top3_change', 'guild.boss_milestone',
               'event.kill_streak', 'engine.native_six_star_star_up', 'global.ranking_change'}

def fail(m): print(f"FAIL v94_live_announcement_safety_bridge: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(B): fail(f"missing bridge: {B}")
    with open(B) as f: d = json.load(f)
    if d.get('production_broadcast') is not False: fail("production_broadcast must be false")
    if d.get('push_notification_live') is not False: fail("push_notification_live must be false")
    if d.get('real_user_pii') is not False: fail("real_user_pii must be false")
    if d.get('privacy_safe_alias_only') is not True: fail("privacy_safe_alias_only must be true")
    if d.get('qa_simulation_only') is not True: fail("qa_simulation_only must be true")
    src = {x.get('event_source') for x in d.get('event_to_announcement_bridge') or []}
    miss = REQ_SOURCES - src
    if miss: fail(f"missing event sources: {sorted(miss)}")
    for x in d.get('event_to_announcement_bridge') or []:
        if x.get('production_broadcast') is not False: fail(f"{x.get('event_source')}.production_broadcast must be false")
        if x.get('dry_run_only') is not True: fail(f"{x.get('event_source')}.dry_run_only must be true")
    rt = d.get('runtime_safety') or {}
    for k in ('engine_events_must_not_trigger_broadcast', 'reward_events_must_not_trigger_push', 'score_events_must_not_trigger_ranking_live'):
        if rt.get(k) is not True: fail(f"runtime_safety.{k} must be true")
    print("PASS v94_live_announcement_safety_bridge")

if __name__ == '__main__': main()
