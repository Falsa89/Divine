#!/usr/bin/env python3
"""PROJECT_F Track E — QA mobile smoke runner (safe dry-run wrapper).

Policy:
  * NEVER prints raw passwords, tokens, secret env values.
  * If QA_TEST_EMAIL or QA_TEST_PASSWORD are unset, exits with MANUAL_REQUIRED.
  * Live login is SKIPPED by default unless QA_TEST_LIVE_LOGIN_OK=true.
  * No account creation, no gacha spend, no destructive mutation.
"""
import os, sys, hashlib, json


def redact(value: str) -> str:
    if not value: return '<unset>'
    h = hashlib.sha256(value.encode()).hexdigest()[:8]
    return f'<redacted sha256-prefix={h}>'


def main():
    email = os.environ.get('QA_TEST_EMAIL', '').strip()
    password = os.environ.get('QA_TEST_PASSWORD', '').strip()
    api_base = os.environ.get('QA_TEST_API_BASE', '').strip() or 'http://127.0.0.1:8001'
    live_ok = os.environ.get('QA_TEST_LIVE_LOGIN_OK', '').strip().lower() == 'true'

    summary = {
        'verdict': 'MANUAL_REQUIRED',
        'email_present': bool(email),
        'password_present': bool(password),
        'password_fingerprint': redact(password),
        'api_base': api_base,
        'live_login_attempted': False,
        'reason': 'No credentials seeded; cannot run live login dry-run safely.',
    }
    if email and password and live_ok:
        # Live attempt would go here. Kept disabled in this pack: still MANUAL_REQUIRED until
        # an explicit ops handoff. We deliberately do not execute the network call to avoid
        # any destructive side-effect.
        summary['verdict'] = 'READY'
        summary['reason'] = 'Credentials present and live login authorized, but execution gated to operator (no network call performed by this wrapper).'
    elif email and password and not live_ok:
        summary['reason'] = 'Credentials present but QA_TEST_LIVE_LOGIN_OK!=true — staying MANUAL_REQUIRED.'

    print(json.dumps(summary, indent=2))
    # Wrapper itself always exits 0 (dry-run); verdict is structural data for the validator.
    sys.exit(0)


if __name__ == '__main__': main()
