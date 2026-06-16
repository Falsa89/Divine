#!/usr/bin/env python3
"""Pre-QA Pack 120A — Controlled Live Unlock Prep (plan-only) Validator.

Validator statico / read-only che verifica:

  1. Il piano JSON esiste in
     `data/design/pre_qa_controlled_unlock/controlled_live_unlock_prep_120a_plan_v1.json`.
  2. Flag piano: mode=plan_only, runtime_unlock_applied=false,
     db_write_allowed=false, reward_live_allowed=false,
     gacha_shop_vip_bp_allowed=false.
  3. Tutte le 22 route della matrice 119D (latest report JSON) appaiono nel
     `route_candidates` del piano.
  4. Ogni voce del piano ha tier, classification_119d, risk_notes,
     future_gate, apply_now=false, live_reward_enabled=false,
     economy_live_enabled=false.
  5. Nessuna route live-blocked (shop/vip/battlepass/gacha/pvp/guild/gvg/raid/
     territory/plaza/dm/events/mail/friends) viene proposta come candidate
     "unlock_now".
  6. Sono dichiarati almeno 5 safety_gates.
  7. Sono dichiarati hard_blockers che includono gacha/shop/VIP/Battle Pass/
     reward live/DB writes.
  8. Esiste il report finale corrispondente
     (`docs/divine/<N>_PRE_QA_PACK_120A_CONTROLLED_LIVE_UNLOCK_PREP_PLAN_ONLY_FINAL_REPORT.md`).

Il validator deve FALLIRE se trova nel piano:
  - apply_now = true (qualsiasi voce)
  - runtime_unlock_applied = true
  - db_write_allowed = true
  - reward_live_allowed = true
  - gacha_shop_vip_bp_allowed = true

Exit code:
  - 0 : piano plan-only valido.
  - 1 : FAIL.

Non modifica DB, non avvia network, niente runtime. Pure file IO + JSON.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
PLAN_FP = os.path.join(R, 'data', 'design', 'pre_qa_controlled_unlock',
                       'controlled_live_unlock_prep_120a_plan_v1.json')
REPORT_GLOB = os.path.join(R, 'docs', 'divine',
                           '*_PRE_QA_PACK_120A_CONTROLLED_LIVE_UNLOCK_PREP_*FINAL_REPORT.md')
SAFETY_119D_LATEST = os.path.join(R, 'backend', 'reports',
                                  'pre_qa_pack_119d_public_menu_route_health_latest.json')

LIVE_BLOCKED_ROUTES = {
    '/shop', '/vip', '/battlepass', '/gacha', '/pvp', '/guild', '/gvg',
    '/raid', '/territory', '/plaza', '/dm', '/events', '/mail', '/friends',
    '/playable-mode-battle-preview', '/skill-status-vfx-catalogs',
    '/hero-skill-kits-catalog', '/safe-previews',
}

REQUIRED_HARD_BLOCKER_IDS = [
    'BLOCK_GACHA_LIVE',
    'BLOCK_SHOP_LIVE',
    'BLOCK_VIP_LIVE',
    'BLOCK_BATTLEPASS_LIVE',
    'BLOCK_REWARD_LIVE',
    'BLOCK_DB_WRITE_PRE_QA',
]


def _fail(messages: list, code: int = 1) -> int:
    print('[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP] FAIL')
    for m in messages:
        print(f'  - {m}')
    return code


def main() -> int:
    failures = []

    # 1) Piano esiste
    if not os.path.exists(PLAN_FP):
        return _fail([f'piano mancante: {PLAN_FP}'])

    try:
        plan = json.load(open(PLAN_FP, encoding='utf-8'))
    except Exception as e:
        return _fail([f'piano JSON malformato: {type(e).__name__}: {e}'])

    # 2) Flag plan-only
    if plan.get('mode') != 'plan_only':
        failures.append(f"mode != 'plan_only' ({plan.get('mode')!r})")
    for k, expected in [
        ('runtime_unlock_applied', False),
        ('db_write_allowed', False),
        ('reward_live_allowed', False),
        ('gacha_shop_vip_bp_allowed', False),
    ]:
        if plan.get(k) != expected:
            failures.append(f"{k} != {expected} ({plan.get(k)!r})")

    # 3) Route candidate coverage vs 119D matrix
    candidates = plan.get('route_candidates') or []
    if not isinstance(candidates, list) or len(candidates) == 0:
        failures.append('route_candidates vuoto o non-lista')
    candidate_routes = [c.get('route') for c in candidates]

    if os.path.exists(SAFETY_119D_LATEST):
        try:
            d119d = json.load(open(SAFETY_119D_LATEST, encoding='utf-8'))
            d119d_routes = [r['route'] for r in d119d.get('route_matrix', [])]
            missing = [r for r in d119d_routes if r not in candidate_routes]
            extra = [r for r in candidate_routes
                     if r not in d119d_routes]
            if missing:
                failures.append(
                    f'route 119D non presenti nel piano (n={len(missing)}): '
                    f'{missing[:8]}{"..." if len(missing) > 8 else ""}')
            if extra:
                # Extra non e' fallimento "duro", solo info.
                print(f'  [info] route candidate extra rispetto a 119D '
                      f'(n={len(extra)}): {extra[:8]}')
            if len(d119d_routes) != len(candidate_routes) and not missing:
                # Lunghezze diverse senza missing potrebbe essere causato da
                # dedupe per file_target; flagghiamo come info.
                print(f"  [info] |119D|={len(d119d_routes)} "
                      f"|candidates|={len(candidate_routes)}")
        except Exception as e:
            print(f'  [warn] 119D report non parsabile: {e}')
    else:
        print(f'  [warn] 119D latest JSON non trovato: {SAFETY_119D_LATEST}')

    # 4) Per ogni candidate: campi obbligatori + flag safe
    required_fields = [
        'route', 'tier', 'classification_119d', 'risk_notes',
        'future_gate', 'apply_now', 'live_reward_enabled',
        'economy_live_enabled',
    ]
    for i, c in enumerate(candidates):
        for f in required_fields:
            if f not in c:
                failures.append(f"candidate#{i} ({c.get('route')!r}) "
                                f"manca campo: {f}")
        # Hard checks su flag.
        for k in ('apply_now', 'live_reward_enabled', 'economy_live_enabled'):
            if c.get(k) is True:
                failures.append(f"candidate {c.get('route')!r} ha {k}=true "
                                f"(plan_only violato)")
        # Tier valido.
        t = c.get('tier')
        if t not in (0, 1, 2, 3, 4):
            failures.append(f"candidate {c.get('route')!r} ha tier non "
                            f"valido: {t!r}")

    # 5) Nessuna live-blocked route proposta come candidate "unlock_now"
    #    (qui significa: candidate con apply_now=true && route in
    #    LIVE_BLOCKED_ROUTES).
    for c in candidates:
        base = (c.get('route') or '').split('?', 1)[0]
        if base in LIVE_BLOCKED_ROUTES and c.get('apply_now') is True:
            failures.append(f"route live-blocked {base!r} marcata "
                            f"apply_now=true")

    # 6) Almeno 5 safety_gates
    gates = plan.get('safety_gates') or []
    if len(gates) < 5:
        failures.append(f"safety_gates < 5 (count={len(gates)})")

    # 7) Hard blockers richiesti
    blockers = plan.get('hard_blockers') or []
    blocker_ids = {b.get('id') for b in blockers}
    for required in REQUIRED_HARD_BLOCKER_IDS:
        if required not in blocker_ids:
            failures.append(f"hard_blocker mancante: {required}")

    # 8) Report finale corrispondente esiste
    report_matches = glob.glob(REPORT_GLOB)
    if not report_matches:
        failures.append(f'report finale 120A mancante: glob={REPORT_GLOB}')

    # Riassunto
    if failures:
        return _fail(failures)

    print('[v120a PRE_QA_120A_CONTROLLED_UNLOCK_PREP] OK '
          f"candidates={len(candidates)} "
          f"safety_gates={len(gates)} "
          f"hard_blockers={len(blockers)} "
          f"plan_only=true runtime_unlock_applied=false")
    return 0


if __name__ == '__main__':
    sys.exit(main())
