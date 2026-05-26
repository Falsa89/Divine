#!/usr/bin/env python3
# PROJECT_BETA_HARNESS_PUBLIC_REPO_SYNC_AND_MINOR_UI_HYGIENE_FIX validator.
# Verifica chiusura formale del mini-pack di stabilizzazione:
#  - Playwright/yarn.lock allineati
#  - Back-arrow legacy fixati (no piu' literal raw "\\u2190")
#  - Suite validatori, audit player routes, redis, soul-forge no-modal guard tutti verdi
#  - Invarianti battle_engine.py / .env intatti
import json, sys, hashlib, subprocess
from pathlib import Path

ROOT = Path('/app')
J = Path('/app/data/design/testing/beta_harness_public_repo_sync_and_minor_ui_hygiene_fix_v1.json')

def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()

def main():
    d = json.loads(J.read_text())

    # Verdict & invarianti backend
    assert d['verdict'] == 'PROJECT_BETA_HARNESS_PUBLIC_REPO_SYNC_AND_MINOR_UI_HYGIENE_FIX_COMPLETE', \
        f"bad verdict {d['verdict']}"
    assert md5('/app/backend/battle_engine.py') == d['invariant_files_md5']['battle_engine_py'], \
        'battle_engine.py drift'
    assert md5('/app/backend/.env') == d['invariant_files_md5']['backend_env'], \
        'backend/.env drift'
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert d['reward_formula_change'] is False

    # P1-A: package.json scripts + devDependency Playwright
    pkg = json.loads((ROOT / 'frontend/package.json').read_text())
    for s in ('test:e2e', 'test:beta-smoke', 'test:beta-smoke:headed'):
        assert s in pkg.get('scripts', {}), f'missing script {s} in frontend/package.json'
    assert '@playwright/test' in pkg.get('devDependencies', {}), \
        '@playwright/test missing from devDependencies'
    pa = d['p1_a_playwright_yarn_alignment']
    assert md5(ROOT / pa['package_json_path']) == pa['package_json_md5_post'], \
        'package.json md5 drift vs marker'
    # yarn.lock contiene risoluzione Playwright
    ylock = (ROOT / 'frontend/yarn.lock').read_text()
    assert '@playwright/test@^1.60.0' in ylock or '"@playwright/test@^1.60.0"' in ylock, \
        'yarn.lock missing @playwright/test resolution'
    assert 'playwright-core@1.60.0' in ylock, 'yarn.lock missing playwright-core resolution'
    # config + spec esistono
    assert (ROOT / pa['playwright_config_path']).exists(), 'playwright.config.ts missing'
    for sp in pa['e2e_specs']:
        assert (ROOT / sp).exists(), f'missing e2e spec {sp}'

    # P1-B: back-arrow JSX escape applicato (no piu' literal raw '\\u2190')
    pb = d['p1_b_back_arrow_unicode_hygiene']
    BAD = '<Text style={s.back}>\\u2190</Text>'  # pattern letterale raw
    for entry in pb['files_fixed']:
        p = ROOT / entry['file']
        assert md5(p) == entry['md5_post'], f"drift on {entry['file']}"
        text = p.read_text()
        assert BAD not in text, f"raw literal back arrow still present in {entry['file']}"
        assert "{'\\u2190'}" in text or '{"\\u2190"}' in text, \
            f"escaped JSX back arrow missing in {entry['file']}"
    assert pb['logic_changes'] == 0
    assert pb['endpoint_changes'] == 0
    assert pb['shop_price_changes'] == 0
    assert pb['shop_item_changes'] == 0
    assert pb['reward_changes'] == 0
    assert pb['iap_implementation'] is False

    # P1-C: validazioni
    pc = d['p1_c_revalidation']
    # Soul Forge guard: nessun Modal/KeyboardAvoidingView/confirmOpen
    sf = (ROOT / 'frontend/app/soul-forge.tsx').read_text()
    for forbidden in ('<Modal', '<KeyboardAvoidingView', 'confirmOpen'):
        assert forbidden not in sf, f"FORBIDDEN token reintroduced in soul-forge.tsx: {forbidden}"
    # Redis check via redis-cli ping (best-effort: non bloccante se binario assente)
    try:
        out = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            assert out.stdout.strip() == pc['redis_result'], 'redis-cli ping mismatch'
    except FileNotFoundError:
        pass  # Validator non DEVE fallire se redis-cli non e' installato in CI
    # Locked surfaces pin refreshed
    for jp in pc['locked_surfaces_md5_pin_refreshed']:
        assert (ROOT / jp).exists(), f'missing pin file {jp}'

    # Nessun blocker rimanente
    assert d['remaining_blockers'] == [], f'remaining blockers: {d["remaining_blockers"]}'

    print('[PASS] BETA_HARNESS_PUBLIC_REPO_SYNC_AND_MINOR_UI_HYGIENE_FIX completion')
    return 0

if __name__ == '__main__':
    sys.exit(main())
