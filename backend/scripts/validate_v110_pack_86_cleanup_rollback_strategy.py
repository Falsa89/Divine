#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_cleanup_rollback_strategy_v1.json')))
assert d.get('refuse_by_default') is True
assert d.get('dry_run_default') is True
assert d.get('deletes_only_marked_pack_86_test_artifacts') is True
assert d.get('no_deletion_of_real_production_psp') is True
safety = d.get('production_safety', {})
for k in ('refuse_if_target_count_zero','refuse_if_no_explicit_apply_flag','refuse_if_target_appears_real_user'):
    assert safety.get(k) is True, f'production_safety.{k} must be true'
# Verifica cleanup script esiste
script = os.path.join(R, d.get('cleanup_script', ''))
assert os.path.exists(script), f'cleanup script not found: {script}'
src = open(script).read()
assert 'refuse' in src.lower() or 'dry' in src.lower(), 'cleanup script must implement refuse-by-default/dry-run'
assert '--apply' in src, 'cleanup script must require explicit --apply flag'
print('[v110 PACK_86_CLEANUP_ROLLBACK_STRATEGY] OK refuse_by_default dry_run_default no_production_psp_deletion script_exists_with_apply_flag')
