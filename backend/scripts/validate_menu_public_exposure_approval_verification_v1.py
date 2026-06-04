#!/usr/bin/env python3
"""validate_menu_public_exposure_approval_verification_v1

Verifica che il file di approval verification contenga:
- approval_phrase_received = true
- approval_checksum_verified = true
- checksum calcolato == sha256(phrase + '|' + scope) (ricalcolato a runtime)
- apply_authorized = true
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-PUBLIC-EXPOSURE-APPROVAL-VERIFICATION'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'
FILE = 'data/design/navigation/menu_public_exposure_approval_verification_v1.json'


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    p = ROOT / FILE
    if not p.exists():
        fail(f'missing {FILE}')
    d = json.loads(p.read_text())

    if d.get('public_sync_tag') != TAG:
        fail('public_sync_tag mismatch')
    if d.get('approval_phrase_received') is not True:
        fail('approval_phrase_received must be true')
    if d.get('approval_checksum_required') is not True:
        fail('approval_checksum_required must be true')
    if d.get('approval_checksum_algorithm') != 'sha256':
        fail('algorithm must be sha256')
    if d.get('approval_checksum_verified') is not True:
        fail('approval_checksum_verified must be true')
    if d.get('apply_authorized') is not True:
        fail('apply_authorized must be true')
    if d.get('db_writes') != 0:
        fail('db_writes must be 0')

    phrase = d.get('approval_phrase', '')
    scope = d.get('approval_scope', '')
    expected = d.get('approval_checksum_expected', '')
    computed = hashlib.sha256(f"{phrase}|{scope}".encode()).hexdigest()
    if computed != expected:
        fail(f'checksum mismatch: computed={computed[:12]}.. expected={expected[:12]}..')
    if d.get('approval_checksum_computed') != computed:
        fail('approval_checksum_computed field mismatch')

    steps = d.get('handshake_steps_verified', [])
    if len(steps) != 6:
        fail('handshake_steps_verified must have 6 entries')
    for s in steps:
        if s.get('verified') is not True:
            fail(f'handshake step {s.get("id")} not verified')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
