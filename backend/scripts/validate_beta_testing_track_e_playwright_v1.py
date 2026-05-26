#!/usr/bin/env python3
# BETA_TESTING Track E — Playwright harness present and parseable.
import json, sys
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_e_playwright_v1.json')
ROOT = Path('/app/frontend')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_E_PLAYWRIGHT_EXPO_WEB_SMOKE_HARNESS_READY'
    cfg = ROOT / d['config_path'].split('/', 1)[1]
    assert cfg.exists(), f'playwright config missing: {cfg}'
    cfg_text = cfg.read_text()
    assert 'defineConfig' in cfg_text
    assert 'tests/e2e' in cfg_text
    assert "width: 390" in cfg_text and "height: 844" in cfg_text
    # test files exist and have at least one test() block
    for rel in d['test_files']:
        p = Path('/app/' + rel)
        assert p.exists(), f'test file missing: {rel}'
        txt = p.read_text()
        assert 'test(' in txt or 'test.describe' in txt, f'no tests defined in {rel}'
    # package.json scripts
    pkg = json.loads((ROOT / 'package.json').read_text())
    for s in d['npm_scripts']:
        assert s in (pkg.get('scripts') or {}), f'missing npm script: {s}'
    # devDependency on @playwright/test
    dev = pkg.get('devDependencies') or {}
    assert '@playwright/test' in dev, 'missing @playwright/test devDependency'
    print('[PASS] BETA_TESTING Track E playwright harness ready')
    return 0
if __name__ == '__main__': sys.exit(main())
