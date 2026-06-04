#!/usr/bin/env python3
"""v98 — Live privacy/terms URLs (honest blocker)."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','compliance','v98_live_privacy_terms_url_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('status') not in ('READY_LIVE_URLS_PRESENT','BLOCKER_FOR_CLOSED_ALPHA_EXTERNAL_URLS_REQUIRED'): print('FAIL — status'); sys.exit(1)
if d.get('status')=='BLOCKER_FOR_CLOSED_ALPHA_EXTERNAL_URLS_REQUIRED':
    urls=d.get('urls') or {}
    if not all(v is None for v in urls.values()): print('FAIL — BLOCKER but urls present (no faking)'); sys.exit(1)
if not d.get('no_fake_urls'): print('FAIL — no_fake_urls'); sys.exit(1)
if not d.get('safety',{}).get('no_fake_pass'): print('FAIL — no_fake_pass'); sys.exit(1)
reqs=d.get('requirements_for_unlock') or []
if len(reqs)<3: print('FAIL — requirements_for_unlock'); sys.exit(1)
print(f'PASS — v98 live privacy/terms urls (status={d.get("status")}, honest blocker)')
sys.exit(0)
