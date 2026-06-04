#!/usr/bin/env python3
"""v93 — Guild War sandbox flow validator."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CT = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v93_guild_war_sandbox_flow_contract_v1.json')
SC = os.path.join(ROOT, 'frontend', 'app', 'guild-war-sandbox-flow.tsx')
MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')

def fail(m): print(f"FAIL v93_guild_war_sandbox_flow: {m}"); sys.exit(1)

def main():
    if not os.path.isfile(CT): fail(f"missing contract: {CT}")
    if not os.path.isfile(SC): fail(f"missing screen: {SC}")
    with open(CT) as f: data = json.load(f)
    saf = data.get('safety') or {}
    if saf.get('guild_score_mutation') != 0: fail("safety.guild_score_mutation must be 0")
    if saf.get('leaderboard_mutation') is not False: fail("safety.leaderboard_mutation must be false")
    if saf.get('real_user_pii') is not False: fail("safety.real_user_pii must be false")
    if saf.get('reward_live') is not False: fail("safety.reward_live must be false")
    with open(SC) as f: sc = f.read()
    for t in ['Guild War Sandbox', 'qa_alias_attacker_001', 'qa_alias_defender_001',
              'NO GUILD SCORE', 'NO LEADERBOARD', 'NO SEASON PROGRESS', 'NO PII',
              'guild_defense_team', 'gw_defense_team_design_v1']:
        if t not in sc: fail(f"sandbox missing token: {t}")
    if "/live-mode-pre-entry-lobby?mode=guild_war" not in sc:
        fail("sandbox must route to /live-mode-pre-entry-lobby?mode=guild_war")
    for pat in [r'\bMath\.random\s*\(', r'\brandom\(']:
        if re.search(pat, sc): fail("sandbox contains forbidden random pattern")
    with open(MENU) as f: menu = f.read()
    if "'/guild-war-sandbox-flow'" not in menu: fail("menu missing route to /guild-war-sandbox-flow")
    print("PASS v93_guild_war_sandbox_flow")

if __name__ == '__main__': main()
