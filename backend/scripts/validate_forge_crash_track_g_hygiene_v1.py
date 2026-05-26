#!/usr/bin/env python3
# FORGE_CRASH Track G — hygiene: test credentials + Redis suite honesty.
import json, sys, hashlib, re
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_g_hygiene_v1.json')
C = Path('/app/memory/test_credentials.md')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_G_REDIS_SUITE_NOISE_AND_TEST_CREDENTIALS_HYGIENE_READY'
    # Credentials file md5 matches
    hyg = d['hygiene_test_credentials']
    assert md5(C) == hyg['md5_post'], f'credentials md5 drift: {md5(C)} vs {hyg["md5_post"]}'
    # No plaintext password committed (file should not have a working password line)
    txt = C.read_text()
    # The previously committed plaintext was 'sfqa12345'. Must NOT appear anymore.
    assert 'sfqa12345' not in txt, 'old plaintext password STILL present in credentials file'
    # Heuristic: no `Password: <some alphanumeric 6+>` line that isn't a placeholder/comment
    # Accept ONLY a placeholder-like line for password.
    bad_password_lines = []
    for line in txt.splitlines():
        m = re.match(r'^\s*-?\s*Password\s*:\s*[`"]?([A-Za-z0-9!@#$%^&*_\-]{6,})[`"]?\s*$', line)
        if m:
            val = m.group(1).lower()
            # placeholder-ish words tolerated
            if val not in ('empty', 'placeholder', 'none', 'na', 'redacted'):
                bad_password_lines.append(line)
    assert not bad_password_lines, f'committed plaintext password detected: {bad_password_lines}'
    assert hyg['plaintext_password_committed_post_fix'] is False
    # Redis noise honestly documented
    rsn = d['redis_suite_noise']
    assert len(rsn['known_failing_validators_environmental']) >= 5
    assert rsn['fake_pass_used'] is False
    assert rsn['validator_weakening_used'] is False
    assert rsn['required_validators_intact'] is True
    print('[PASS] FORGE_CRASH Track G hygiene (no plaintext, no fake redis pass)')
    return 0
if __name__ == '__main__': sys.exit(main())
