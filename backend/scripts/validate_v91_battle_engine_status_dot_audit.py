#!/usr/bin/env python3
"""
v91_FIXED — Battle engine status/DoT/targeting audit doc validator.

Verifica:
- esiste docs/divine/91_BATTLE_ENGINE_STATUS_DOT_TARGETING_AUDIT.md
- contiene i status canonici (Burn, Poison, Bleed, Shock, Frostbite, Curse, Taunt, Cleanse, Immunity)
- contiene sezione AoE vs Taunt
- dichiara esplicitamente che v91 NON modifica l'engine (read-only audit)
- dichiara db_writes=0, reward_live=false, endpoint_live=false, battle_engine_authoritative=false
- battle_engine.py NON e' stato modificato (MD5 invariant gia' verificato da altri validator,
  qui controlliamo solo la dichiarazione nell'audit)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT = os.path.join(ROOT, 'docs', 'divine', '91_BATTLE_ENGINE_STATUS_DOT_TARGETING_AUDIT.md')


def fail(msg: str) -> None:
    print(f"FAIL v91_battle_engine_status_dot_audit: {msg}")
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(AUDIT):
        fail(f"missing audit doc: {AUDIT}")
    with open(AUDIT, 'r', encoding='utf-8') as f:
        md = f.read()

    required_statuses = ['Burn', 'Poison', 'Bleed', 'Shock', 'Frostbite',
                         'Curse', 'Taunt', 'Cleanse', 'Immunity']
    for st in required_statuses:
        if st not in md:
            fail(f"audit missing status: {st}")

    if 'AoE vs Taunt' not in md:
        fail("audit missing section 'AoE vs Taunt'")

    if 'NON modifica' not in md and 'NON eseguite in v91' not in md:
        fail("audit must declare that v91 does NOT modify the engine")

    for flag in ('db_writes: 0', 'reward_live: false',
                 'endpoint_live: false', 'battle_engine_authoritative: false'):
        if flag not in md:
            fail(f"audit missing safety flag declaration: {flag}")

    print("PASS v91_battle_engine_status_dot_audit")


if __name__ == '__main__':
    main()
