#!/usr/bin/env python3
"""v93 — Live announcements QA validator."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAT = os.path.join(ROOT, 'data', 'design', 'live_announcements', 'live_announcement_qa_catalog_v1.json')
RULES = os.path.join(ROOT, 'data', 'design', 'live_announcements', 'live_announcement_dynamic_event_rules_v1.json')
DOC = os.path.join(ROOT, 'docs', 'divine', '93_LIVE_ANNOUNCEMENTS_QA_AND_DYNAMIC_FEED.md')
SC = os.path.join(ROOT, 'frontend', 'app', 'live-announcements-qa.tsx')
MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')

REQ_STATIC = {'news', 'maintenance', 'event_notice', 'update_note'}
REQ_DYNAMIC = {'six_star_pull', 'native_six_star_star_up', 'arena_top3_change',
               'live_event_kill', 'live_event_kill_streak', 'global_ranking_change',
               'top_player_online', 'guild_boss_milestone', 'community_prestige_event'}
REQ_CHANNELS = {'global', 'system', 'events', 'arena', 'guild', 'community'}
REQ_TOKENS_SC = ['QA SIMULATION ONLY', 'NO PRODUCTION BROADCAST',
                 'NO PUSH NOTIFICATION LIVE', 'NO REAL USER PII',
                 'ALIAS-SAFE ONLY', 'token_bucket']

def fail(m): print(f"FAIL v93_live_announcements_qa: {m}"); sys.exit(1)

def main():
    for p in (CAT, RULES, DOC, SC): 
        if not os.path.isfile(p): fail(f"missing: {p}")
    with open(CAT) as f: c = json.load(f)
    if c.get('production_broadcast') is not False: fail("catalog production_broadcast must be false")
    if c.get('push_notification_live') is not False: fail("catalog push_notification_live must be false")
    if c.get('real_user_data_required') is not False: fail("catalog real_user_data_required must be false")
    if c.get('privacy_safe_alias_only') is not True: fail("catalog privacy_safe_alias_only must be true")
    if c.get('anti_spam_rules_present') is not True: fail("catalog anti_spam_rules_present must be true")
    if c.get('qa_simulation_only') is not True: fail("catalog qa_simulation_only must be true")
    found_static = {a.get('type') for a in (c.get('static_announcements') or [])}
    miss_s = REQ_STATIC - found_static
    if miss_s: fail(f"static missing: {sorted(miss_s)}")
    ch_found = set(c.get('channels') or [])
    miss_ch = REQ_CHANNELS - ch_found
    if miss_ch: fail(f"channels missing: {sorted(miss_ch)}")
    if not (c.get('anti_spam') or {}).get('throttle_strategy'): fail("catalog anti_spam.throttle_strategy missing")
    with open(RULES) as f: r = json.load(f)
    found_dyn = {e.get('event_type') for e in (r.get('dynamic_events') or [])}
    miss_d = REQ_DYNAMIC - found_dyn
    if miss_d: fail(f"dynamic events missing: {sorted(miss_d)}")
    if not (r.get('alias_safety') or {}).get('do_not_emit_real_user_id'):
        fail("rules alias_safety.do_not_emit_real_user_id must be true")
    with open(SC) as f: sc = f.read()
    for t in REQ_TOKENS_SC:
        if t not in sc: fail(f"screen missing token: {t}")
    for pat in [r'\bMath\.random\s*\(']:
        # Verifica linee NON-commento (escludi // e * e /*)
        for line in sc.splitlines():
            stripped = line.lstrip()
            if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
                continue
            if re.search(pat, line):
                fail("screen contains Math.random() call")
    with open(MENU) as f: menu = f.read()
    if "'/live-announcements-qa'" not in menu: fail("menu missing route to /live-announcements-qa")
    print("PASS v93_live_announcements_qa")

if __name__ == '__main__': main()
