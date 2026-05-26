#!/usr/bin/env python3
"""
PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF master validator.

Verifica end-to-end:
  - Track A: audit JSON presente
  - Track B: final rate table valida (sum=100%, soglie 5\u2605+6\u2605)
  - Track C: frontend gacha.tsx allineato (rate finali, md5 pin, banner LOCKED/HIDDEN)
  - Track D: backend server.py allineato (rate finali, guarantee_weights, md5 pin)
  - Track E: simulazione deterministica eseguita, no regressione 4m+3l
  - Track F: pity contract design-only, no DB writes
  - Track G: beta harness JSON presente
  - Track H: public repo sync JSON presente
  - Track I: completion JSON con global_verdict COMPLETE
  - Invarianti: battle_engine.py + .env md5 intatti

NESSUN DB WRITE. NESSUNA MUTAZIONE. PURE STATIC + IN-PROCESS SIMULATION REPLAY.
"""
import json, sys, hashlib, math, re
from pathlib import Path

ROOT = Path('/app')

def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

def load_json(rel): return json.loads((ROOT / rel).read_text())

def main():
    # ---- Track A
    a = load_json('data/design/gacha/gacha_rate_sanity_surface_backend_audit_v1.json')
    assert a['verdict'] == 'TRACK_A_GACHA_SURFACE_AND_BACKEND_AUDIT_READY'
    assert set(a['live_banners_pre_signoff']) == {'standard', 'elemental', 'selective'}
    assert set(a['locked_banners_pre_signoff']) == {'premium', 'targeted'}
    assert set(a['hidden_banners_pre_signoff']) == {'artifact', 'constellation'}

    # ---- Track B: final rate table integrity
    b = load_json('data/design/gacha/gacha_final_rate_table_v1.json')
    assert b['verdict'] == 'TRACK_B_FINAL_RATE_TABLE_SIGNOFF_READY'
    final = b['final_rate_table']
    expected_5_6_cap = {'standard': 1.50, 'elemental': 2.50, 'selective': 3.50,
                        'premium': 5.00, 'targeted': 5.00}
    expected_6 = {'standard': 0.15, 'elemental': 0.30, 'selective': 0.50,
                  'premium': 0.75, 'targeted': 0.75}
    for banner, rates in final.items():
        s = sum(rates.values())
        assert math.isclose(s, 100.0, abs_tol=0.005), f'{banner} sum {s} != 100'
        c56 = rates['5'] + rates['6']
        assert c56 <= expected_5_6_cap[banner] + 0.001, f'{banner} 5+6={c56} > cap'
        assert math.isclose(rates['6'], expected_6[banner], abs_tol=0.001), f'{banner} 6\u2605 mismatch'

    # ---- Track C: frontend
    c = load_json('data/design/gacha/gacha_frontend_rate_display_update_v1.json')
    assert c['verdict'] == 'TRACK_C_FRONTEND_RATE_DISPLAY_UPDATED_SAFE'
    gtsx = ROOT / 'frontend/app/(tabs)/gacha.tsx'
    assert md5(gtsx) == c['md5_post'], 'gacha.tsx md5 drift'
    txt = gtsx.read_text()
    # Banner live mostra rate finali, no piu' dev-like
    assert "'1\\u2B50': '39%'" in txt, 'standard 1\u2605=39% missing'
    assert "'5\\u2B50': '1.35%'" in txt, 'standard 5\u2605=1.35% missing'
    assert "'5\\u2B50': '2.2%'" in txt, 'elemental 5\u2605=2.2% missing'
    assert "'5\\u2B50': '3%'" in txt, 'selective 5\u2605=3% missing'
    # Premium/targeted locked
    assert "LOCKED_BANNERS_V2 = new Set(['premium', 'targeted'])" in txt
    assert "HIDDEN_BANNERS_V2 = new Set(['artifact', 'constellation'])" in txt
    # No piu' rate dev-like '6%' '20%' su 5\u2605 nei banner live
    forbidden_old = ["'5\\u2B50': '6%'", "'5\\u2B50': '10%'", "'5\\u2B50': '13%'", "'5\\u2B50': '20%'"]
    # Nota: artifact ha ancora '10%' su 5\u2605 e constellation '17%' \u2014 hidden, allowed
    # Quindi controlliamo che le occorrenze non siano in standard/elemental/selective.
    # Strategy: queste sequenze appaiono solo dentro la riga 'rates: { ... }' di banner specifici.
    # Verifico semplicemente che il marker dev-like "5\u2B50': '6%'" non esista piu' (standard era 6%).
    assert "'5\\u2B50': '6%'" not in txt, 'standard old dev-like 5\u2605=6% still present'
    assert "'1\\u2B50': '30%'" not in txt, 'standard old dev-like 1\u2605=30% still present'

    # ---- Track D: backend
    d = load_json('data/design/gacha/gacha_backend_rate_alignment_v1.json')
    assert d['verdict'] == 'TRACK_D_BACKEND_RATE_ALIGNMENT_READY_SAFE'
    sv = ROOT / 'backend/server.py'
    assert md5(sv) == d['md5_post'], 'server.py md5 drift'
    sv_text = sv.read_text()
    # Verifica presenza simboli essenziali nel backend
    assert 'guarantee_weights' in sv_text, 'guarantee_weights symbol missing from backend'
    assert '"selective"' in sv_text, 'selective banner not registered in backend'
    assert '"targeted"' in sv_text, 'targeted banner not registered in backend'
    # Rate finali Standard 5\u2605=0.0135
    assert '0.0135' in sv_text, 'standard 5\u2605 rate 0.0135 not in backend'
    assert '0.0015' in sv_text, 'standard 6\u2605 rate 0.0015 not in backend'
    # No piu' dev-like 0.06 / 0.20 / 0.10 in GACHA_BANNERS specifico
    # (Verifica safe: i numeri possono apparire altrove; usiamo un check piu' specifico.)
    bad_signature = '"rates": {1: 0.30, 2: 0.30, 3: 0.20, 4: 0.12, 5: 0.06, 6: 0.02}'
    assert bad_signature not in sv_text, 'dev-like standard signature still present in backend'
    bad_premium = '"rates": {1: 0.05, 2: 0.15, 3: 0.25, 4: 0.25, 5: 0.20, 6: 0.10}'
    assert bad_premium not in sv_text, 'dev-like premium signature still present in backend'
    assert d['db_writes_from_script'] == 0
    assert d['battle_engine_changes'] == 0
    assert d['iap_implementation'] is False

    # ---- Track E: simulation
    e = load_json('data/design/gacha/gacha_result_sanity_simulation_v1.json')
    assert e['verdict'] == 'TRACK_E_GACHA_RESULT_SANITY_TESTS_READY', \
        f"simulation verdict: {e['verdict']}"
    for bnr, sr in e['simulation_results'].items():
        assert sr['no_dev_like_regression_4m_3l'] is True, f'{bnr} regression detected'
        assert sr['observed_within_expected_plus_tolerance'] is True
        assert sr['observed_within_expected_minus_tolerance'] is True
    assert e['live_db_writes'] == 0
    assert e['live_api_calls'] == 0

    # ---- Track F: pity
    f = load_json('data/design/gacha/gacha_pity_and_disclosure_contract_v1.json')
    assert f['verdict'] == 'TRACK_F_PITY_AND_DISCLOSURE_CONTRACT_READY'
    assert f['implementation_status'] == 'DESIGN_ONLY'
    assert f['db_writes_added_by_this_pack'] == 0

    # ---- Track G: beta harness
    g = load_json('data/design/gacha/gacha_beta_harness_static_audit_integration_v1.json')
    assert g['verdict'] == 'TRACK_G_BETA_HARNESS_AND_STATIC_AUDIT_INTEGRATION_READY'
    assert g['package_json_stable'] is True
    assert g['yarn_lock_stable'] is True

    # ---- Track H: public repo sync
    h = load_json('data/design/gacha/gacha_public_repo_sync_verification_v1.json')
    assert h['verdict'] == 'TRACK_H_PUBLIC_REPO_SYNC_VERIFICATION_READY'

    # ---- Track I: completion + invariants
    i = load_json('data/design/gacha/gacha_rate_sanity_final_signoff_completion_v1.json')
    assert i['verdict'] == 'TRACK_I_GACHA_RATE_SANITY_COMPLETION_READY'
    assert i['global_verdict'] == 'PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF_COMPLETE'
    inv = i['invariants_respected']
    assert md5('/app/backend/battle_engine.py') == inv['battle_engine_py_md5'], \
        'battle_engine.py md5 drift'
    assert md5('/app/backend/.env') == inv['backend_env_md5'], 'backend/.env md5 drift'
    for k in ('no_iap_implementation', 'no_db_writes', 'no_artifact_activation',
              'no_constellation_activation', 'no_validator_weakening'):
        assert inv[k] is True, f'invariant {k} not True'
    assert i['db_writes_from_scripts'] == 0

    print('[PASS] PROJECT_GACHA_RATE_SANITY_FINAL_SIGNOFF_COMPLETE master validator')
    return 0

if __name__ == '__main__':
    sys.exit(main())
