#!/usr/bin/env python3
"""v93 — War/Event avatar preview screens validator."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WAR = os.path.join(ROOT, 'frontend', 'app', 'war-avatar-layout-preview.tsx')
EVT = os.path.join(ROOT, 'frontend', 'app', 'event-avatar-layout-preview.tsx')
MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')

REQUIRED_TOKENS = ['DEV PLACEHOLDER', 'NO COSMETIC UNLOCK', 'NO INVENTORY',
                   'NO MONETIZATION', 'NO FINAL ASSET',
                   'cosmetic_unlock=false', 'inventory_grant=false']

def fail(m): print(f"FAIL v93_war_event_avatar_preview_screens: {m}"); sys.exit(1)

def main():
    for path, label in [(WAR, 'war-avatar-layout-preview.tsx'), (EVT, 'event-avatar-layout-preview.tsx')]:
        if not os.path.isfile(path): fail(f"missing screen: {label}")
        with open(path) as f: c = f.read()
        for t in REQUIRED_TOKENS:
            if t not in c: fail(f"{label} missing token: {t}")
        for pat in [r'\bMath\.random\s*\(', r'\brandom\(']:
            if re.search(pat, c): fail(f"{label} contains forbidden random pattern")
    with open(MENU) as f: menu = f.read()
    if "'/war-avatar-layout-preview'" not in menu: fail("menu missing route to /war-avatar-layout-preview")
    if "'/event-avatar-layout-preview'" not in menu: fail("menu missing route to /event-avatar-layout-preview")
    print("PASS v93_war_event_avatar_preview_screens")

if __name__ == '__main__': main()
